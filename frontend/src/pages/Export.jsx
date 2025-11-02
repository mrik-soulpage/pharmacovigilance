import { useState, useEffect } from 'react'
import { Download, FileSpreadsheet, Calendar } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export default function Export() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(null)
  const [weekNumber, setWeekNumber] = useState('')

  useEffect(() => {
    fetchJobs()
    
    // Set current week number
    const now = new Date()
    const week = getWeekNumber(now)
    setWeekNumber(week.toString())
  }, [])

  const getWeekNumber = (date) => {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
    const dayNum = d.getUTCDay() || 7
    d.setUTCDate(d.getUTCDate() + 4 - dayNum)
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
  }

  const fetchJobs = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/search/jobs`)
      const data = await response.json()
      if (data.success) {
        // Only show completed jobs
        setJobs(data.data.filter(j => j.status === 'completed'))
      }
    } catch (error) {
      console.error('Error fetching jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (jobId) => {
    try {
      setExporting(jobId)
      
      const response = await fetch(`${API_BASE_URL}/export/excel/${jobId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ week_number: weekNumber }),
      })

      if (response.ok) {
        // Create blob and download
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `Literature_Tracker_Week${weekNumber}_${new Date().toISOString().split('T')[0]}.xlsx`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        
        alert('Excel file downloaded successfully!')
      } else {
        const data = await response.json()
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Error exporting:', error)
      alert('Error exporting to Excel')
    } finally {
      setExporting(null)
    }
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
      <div>
        <h1 className="text-3xl font-bold text-foreground">Export</h1>
        <p className="text-muted-foreground mt-2">
          Export search results to Excel tracker format
        </p>
      </div>

      {/* Export Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Export Configuration</CardTitle>
          <CardDescription>
            Configure export parameters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="max-w-md">
            <Label htmlFor="week_number">Week Number</Label>
            <Input
              id="week_number"
              value={weekNumber}
              onChange={(e) => setWeekNumber(e.target.value)}
              placeholder="XX"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Week number for the Excel tracker (e.g., 42, XX)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Available Jobs */}
      <Card>
        <CardHeader>
          <CardTitle>Available Search Jobs</CardTitle>
          <CardDescription>
            Select a completed search job to export
          </CardDescription>
        </CardHeader>
        <CardContent>
          {jobs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileSpreadsheet className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No completed search jobs available</p>
              <p className="text-sm mt-1">Complete a search first to export results</p>
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.map((job) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-accent transition-colors"
                >
                  <div className="flex-1">
                    <div className="font-semibold text-foreground">
                      {job.job_type === 'batch' ? 'Batch Search' : 'Single Search'}
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {job.total_products} products • {job.total_articles} articles
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                      <Calendar className="w-3 h-3" />
                      {job.date_from && job.date_to && (
                        <span>{job.date_from} to {job.date_to}</span>
                      )}
                      <span>• Created: {new Date(job.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <Button
                    onClick={() => handleExport(job.id)}
                    disabled={exporting === job.id}
                  >
                    {exporting === job.id ? (
                      <>
                        <Download className="w-4 h-4 mr-2 animate-pulse" />
                        Exporting...
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4 mr-2" />
                        Export to Excel
                      </>
                    )}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Export Format Information */}
      <Card>
        <CardHeader>
          <CardTitle>Excel Tracker Format</CardTitle>
          <CardDescription>
            Information about the exported Excel file
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-sm">
            <div>
              <h3 className="font-semibold mb-2">Included Sheets</h3>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li><strong>Week {weekNumber}:</strong> Main tracker with all search results and AI analysis</li>
                <li><strong>Legends:</strong> Column descriptions and field definitions</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Included Columns (30+)</h3>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Product information (INN, search strategy, territories)</li>
                <li>Article metadata (PMID, title, authors, journal, DOI)</li>
                <li>ICSR classification and description</li>
                <li>Ownership exclusion analysis</li>
                <li>Safety information classification</li>
                <li>Workflow tracking fields</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-2">AI-Generated Fields</h3>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>ICSR detection (Y/N/NA)</li>
                <li>ICSR description with adverse events</li>
                <li>Ownership exclusion assessment</li>
                <li>Safety information classification</li>
                <li>Confidence scores</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

