import { useState, useEffect } from 'react'
import { Plus, Upload, Trash2, Edit, Search } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Badge } from '@/components/ui/badge.jsx'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export default function Products() {
  const [products, setProducts] = useState([])
  const [filteredProducts, setFilteredProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [importDialogOpen, setImportDialogOpen] = useState(false)
  const [formData, setFormData] = useState({
    inn: '',
    search_strategy: '',
    is_eu_product: false,
    territories: '',
    dosage_forms: '',
    routes_of_administration: '',
    marketing_status: 'Active',
  })

  useEffect(() => {
    fetchProducts()
  }, [])

  useEffect(() => {
    if (searchTerm) {
      const filtered = products.filter(p =>
        p.inn.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.search_strategy.toLowerCase().includes(searchTerm.toLowerCase())
      )
      setFilteredProducts(filtered)
    } else {
      setFilteredProducts(products)
    }
  }, [searchTerm, products])

  const fetchProducts = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/products`)
      const data = await response.json()
      if (data.success) {
        setProducts(data.data)
        setFilteredProducts(data.data)
      }
    } catch (error) {
      console.error('Error fetching products:', error)
      alert('Error fetching products')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      const payload = {
        ...formData,
        territories: formData.territories ? formData.territories.split(',').map(t => t.trim()) : [],
        dosage_forms: formData.dosage_forms ? formData.dosage_forms.split(',').map(d => d.trim()) : [],
        routes_of_administration: formData.routes_of_administration ? formData.routes_of_administration.split(',').map(r => r.trim()) : [],
      }

      const response = await fetch(`${API_BASE_URL}/products`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await response.json()
      
      if (data.success) {
        alert('Product created successfully!')
        setDialogOpen(false)
        resetForm()
        fetchProducts()
      } else {
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Error creating product:', error)
      alert('Error creating product')
    }
  }

  const handleImport = async (e) => {
    e.preventDefault()
    const fileInput = e.target.elements.file
    const file = fileInput.files[0]
    
    if (!file) {
      alert('Please select a file')
      return
    }

    try {
      const text = await file.text()
      const data = JSON.parse(text)
      
      const response = await fetch(`${API_BASE_URL}/products/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })

      const result = await response.json()
      
      if (result.success) {
        alert(`Successfully imported ${result.imported} products (${result.skipped} skipped)`)
        setImportDialogOpen(false)
        fetchProducts()
      } else {
        alert(`Error: ${result.error}`)
      }
    } catch (error) {
      console.error('Error importing products:', error)
      alert('Error importing products. Please check the file format.')
    }
  }

  const handleDelete = async (id, inn) => {
    if (!confirm(`Are you sure you want to delete product "${inn}"?`)) {
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/products/${id}`, {
        method: 'DELETE',
      })

      const data = await response.json()
      
      if (data.success) {
        alert('Product deleted successfully!')
        fetchProducts()
      } else {
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Error deleting product:', error)
      alert('Error deleting product')
    }
  }

  const resetForm = () => {
    setFormData({
      inn: '',
      search_strategy: '',
      is_eu_product: false,
      territories: '',
      dosage_forms: '',
      routes_of_administration: '',
      marketing_status: 'Active',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Products</h1>
          <p className="text-muted-foreground mt-2">
            Manage pharmaceutical products for literature monitoring
          </p>
        </div>
        <div className="flex gap-2">
          <Dialog open={importDialogOpen} onOpenChange={setImportDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Upload className="w-4 h-4 mr-2" />
                Import
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Import Products</DialogTitle>
                <DialogDescription>
                  Upload a JSON file containing product data
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleImport}>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="file">JSON File</Label>
                    <Input id="file" name="file" type="file" accept=".json" required />
                    <p className="text-xs text-muted-foreground mt-1">
                      Expected format: Array of product objects
                    </p>
                  </div>
                </div>
                <DialogFooter className="mt-6">
                  <Button type="button" variant="outline" onClick={() => setImportDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Import</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Product
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Add New Product</DialogTitle>
                <DialogDescription>
                  Enter product details for literature monitoring
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="inn">INN (International Nonproprietary Name) *</Label>
                    <Input
                      id="inn"
                      value={formData.inn}
                      onChange={(e) => setFormData({ ...formData, inn: e.target.value })}
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="search_strategy">Search Strategy *</Label>
                    <Textarea
                      id="search_strategy"
                      value={formData.search_strategy}
                      onChange={(e) => setFormData({ ...formData, search_strategy: e.target.value })}
                      rows={3}
                      required
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      PubMed Boolean search query
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="is_eu_product"
                      checked={formData.is_eu_product}
                      onChange={(e) => setFormData({ ...formData, is_eu_product: e.target.checked })}
                      className="rounded border-border"
                    />
                    <Label htmlFor="is_eu_product">EU Product (Complex Search Strategy)</Label>
                  </div>

                  <div>
                    <Label htmlFor="territories">Territories (comma-separated)</Label>
                    <Input
                      id="territories"
                      value={formData.territories}
                      onChange={(e) => setFormData({ ...formData, territories: e.target.value })}
                      placeholder="US, UK, DE, FR"
                    />
                  </div>

                  <div>
                    <Label htmlFor="dosage_forms">Dosage Forms (comma-separated)</Label>
                    <Input
                      id="dosage_forms"
                      value={formData.dosage_forms}
                      onChange={(e) => setFormData({ ...formData, dosage_forms: e.target.value })}
                      placeholder="Tablet, Capsule, Injection"
                    />
                  </div>

                  <div>
                    <Label htmlFor="routes">Routes of Administration (comma-separated)</Label>
                    <Input
                      id="routes"
                      value={formData.routes_of_administration}
                      onChange={(e) => setFormData({ ...formData, routes_of_administration: e.target.value })}
                      placeholder="Oral, Intravenous"
                    />
                  </div>

                  <div>
                    <Label htmlFor="marketing_status">Marketing Status</Label>
                    <select
                      id="marketing_status"
                      value={formData.marketing_status}
                      onChange={(e) => setFormData({ ...formData, marketing_status: e.target.value })}
                      className="w-full px-3 py-2 border border-border rounded-md"
                    >
                      <option value="Active">Active</option>
                      <option value="Inactive">Inactive</option>
                      <option value="Pending">Pending</option>
                    </select>
                  </div>
                </div>
                <DialogFooter className="mt-6">
                  <Button type="button" variant="outline" onClick={() => { setDialogOpen(false); resetForm(); }}>
                    Cancel
                  </Button>
                  <Button type="submit">Create Product</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search products by INN or search strategy..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Products List */}
      <Card>
        <CardHeader>
          <CardTitle>Products ({filteredProducts.length})</CardTitle>
          <CardDescription>Configured pharmaceutical products for monitoring</CardDescription>
        </CardHeader>
        <CardContent>
          {filteredProducts.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>No products found</p>
              <p className="text-sm mt-1">Add products to start monitoring literature</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredProducts.map((product) => (
                <div
                  key={product.id}
                  className="p-4 border border-border rounded-lg hover:bg-accent transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-lg text-foreground">{product.inn}</h3>
                        {product.is_eu_product && (
                          <Badge variant="secondary">EU Product</Badge>
                        )}
                        <Badge variant="outline">{product.marketing_status}</Badge>
                      </div>
                      
                      <div className="mt-2 text-sm text-muted-foreground">
                        <p className="font-mono text-xs bg-muted p-2 rounded mt-2">
                          {product.search_strategy}
                        </p>
                      </div>

                      {product.territories && product.territories.length > 0 && (
                        <div className="mt-2 flex items-center gap-2 text-sm">
                          <span className="text-muted-foreground">Territories:</span>
                          <div className="flex gap-1">
                            {product.territories.map((t, i) => (
                              <Badge key={i} variant="outline" className="text-xs">{t}</Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {product.dosage_forms && product.dosage_forms.length > 0 && (
                        <div className="mt-1 flex items-center gap-2 text-sm">
                          <span className="text-muted-foreground">Forms:</span>
                          <span className="text-foreground">{product.dosage_forms.join(', ')}</span>
                        </div>
                      )}
                    </div>

                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(product.id, product.inn)}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

