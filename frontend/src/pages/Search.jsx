import { useState, useEffect } from 'react'
import { Play, Calendar, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Input } from '@/components/ui/input.jsx'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export default function Search() {
  const [products, setProducts] = useState([])
  const [selectedProducts, setSelectedProducts] = useState([])
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [loading, setLoading] = useState(false)
  const [searchType, setSearchType] = useState('batch')

  useEffect(() => {
    fetchProducts()
    
    // Set default date range (last 7 days)
    const today = new Date()
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
    setDateTo(today.toISOString().split('T')[0])
    setDateFrom(lastWeek.toISOString().split('T')[0])
  }, [])

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/products`)
      const data = await response.json()
      if (data.success) {
        setProducts(data.data)
      }
    } catch (error) {
      console.error('Error fetching products:', error)
    }
  }

  const handleExecuteSearch = async () => {
    if (!dateFrom || !dateTo) {
      alert('Please select date range')
      return
    }

    if (searchType === 'single' && selectedProducts.length !== 1) {
      alert('Please select exactly one product for single search')
      return
    }

    try {
      setLoading(true)
      
      const endpoint = searchType === 'single' ? '/search/execute' : '/search/batch'
      const payload = {
        date_from: dateFrom,
        date_to: dateTo,
        ...(searchType === 'single' 
          ? { product_id: selectedProducts[0] }
          : { product_ids: selectedProducts.length > 0 ? selectedProducts : undefined }
        )
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await response.json()
      
      if (data.success) {
        alert(`Search completed! Found ${data.total_articles} articles. Job ID: ${data.job_id}`)
        window.location.href = `/results?job_id=${data.job_id}`
      } else {
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Error executing search:', error)
      alert('Error executing search')
    } finally {
      setLoading(false)
    }
  }

  const toggleProduct = (productId) => {
    if (selectedProducts.includes(productId)) {
      setSelectedProducts(selectedProducts.filter(id => id !== productId))
    } else {
      setSelectedProducts([...selectedProducts, productId])
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Literature Search</h1>
        <p className="text-muted-foreground mt-2">
          Execute PubMed searches for products with AI-powered ICSR detection
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Search Configuration</CardTitle>
              <CardDescription>Configure search parameters</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Search Type</Label>
                <div className="flex gap-2 mt-2">
                  <Button
                    variant={searchType === 'single' ? 'default' : 'outline'}
                    className="flex-1"
                    onClick={() => setSearchType('single')}
                  >
                    Single
                  </Button>
                  <Button
                    variant={searchType === 'batch' ? 'default' : 'outline'}
                    className="flex-1"
                    onClick={() => setSearchType('batch')}
                  >
                    Batch
                  </Button>
                </div>
              </div>

              <div>
                <Label htmlFor="date_from">Date From</Label>
                <Input
                  id="date_from"
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="date_to">Date To</Label>
                <Input
                  id="date_to"
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                />
              </div>

              <div className="pt-4">
                <Button
                  className="w-full"
                  onClick={handleExecuteSearch}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Execute Search
                    </>
                  )}
                </Button>
              </div>

              {selectedProducts.length > 0 && (
                <div className="text-sm text-muted-foreground">
                  {selectedProducts.length} product(s) selected
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Products Selection */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Select Products</CardTitle>
              <CardDescription>
                {searchType === 'single' 
                  ? 'Select one product for single search'
                  : 'Select products for batch search (leave empty to search all)'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {products.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No products available</p>
                  <p className="text-sm mt-1">Add products first from the Products page</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {products.map((product) => (
                    <div
                      key={product.id}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedProducts.includes(product.id)
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:bg-accent'
                      }`}
                      onClick={() => toggleProduct(product.id)}
                    >
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={selectedProducts.includes(product.id)}
                          onChange={() => toggleProduct(product.id)}
                          className="rounded border-border"
                        />
                        <div className="flex-1">
                          <div className="font-semibold text-foreground">{product.inn}</div>
                          <div className="text-sm text-muted-foreground mt-1">
                            {product.is_eu_product ? 'EU Product' : 'Standard Product'}
                            {product.territories && product.territories.length > 0 && (
                              <span> • {product.territories.join(', ')}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

