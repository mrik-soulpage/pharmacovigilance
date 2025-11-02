import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { FileText, AlertCircle, CheckCircle2, Info, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export default function Results() {
  const [searchParams] = useSearchParams()
  const jobId = searchParams.get('job_id')
  
  const [job, setJob] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    if (jobId) {
      fetchResults()
    }
  }, [jobId])

  const fetchResults = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/search/jobs/${jobId}/results`)
      const data = await response.json()
      
      if (data.success) {
        setJob(data.job)
        setResults(data.results)
      }
    } catch (error) {
      console.error('Error fetching results:', error)
    } finally {
      setLoading(false)
    }
  }

  const getConfidenceBadge = (score) => {
    if (score >= 0.85) {
      return <Badge className="bg-green-500">High ({(score * 100).toFixed(0)}%)</Badge>
    } else if (score >= 0.60) {
      return <Badge className="bg-yellow-500">Medium ({(score * 100).toFixed(0)}%)</Badge>
    } else {
      return <Badge className="bg-red-500">Low ({(score * 100).toFixed(0)}%)</Badge>
    }
  }

  const filteredResults = results.filter(result => {
    if (filter === 'all') return true
    if (filter === 'icsr') return result.is_icsr === true
    if (filter === 'relevant') return result.other_safety_info === true && result.is_icsr !== true
    if (filter === 'irrelevant') return result.other_safety_info === false
    return true
  })

  const stats = {
    total: results.length,
    icsrs: results.filter(r => r.is_icsr === true).length,
    relevant: results.filter(r => r.other_safety_info === true && r.is_icsr !== true).length,
    irrelevant: results.filter(r => r.other_safety_info === false).length,
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
          <p className="text-muted-foreground">No search job found</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Search Results</h1>
        <p className="text-muted-foreground mt-2">
          Review AI-analyzed articles from literature search
        </p>
      </div>

      {/* Job Info */}
      <Card>
        <CardHeader>
          <CardTitle>Search Job Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-muted-foreground">Job Type</div>
              <div className="font-semibold">{job.job_type}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Status</div>
              <div className="font-semibold">{job.status}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Products</div>
              <div className="font-semibold">{job.total_products}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Articles</div>
              <div className="font-semibold">{job.total_articles}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{stats.total}</div>
            <div className="text-sm text-muted-foreground">Total Articles</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-red-600">{stats.icsrs}</div>
            <div className="text-sm text-muted-foreground">ICSRs</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">{stats.relevant}</div>
            <div className="text-sm text-muted-foreground">Relevant Safety Info</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-gray-600">{stats.irrelevant}</div>
            <div className="text-sm text-muted-foreground">Irrelevant</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Tabs value={filter} onValueChange={setFilter}>
        <TabsList>
          <TabsTrigger value="all">All ({stats.total})</TabsTrigger>
          <TabsTrigger value="icsr">ICSRs ({stats.icsrs})</TabsTrigger>
          <TabsTrigger value="relevant">Relevant ({stats.relevant})</TabsTrigger>
          <TabsTrigger value="irrelevant">Irrelevant ({stats.irrelevant})</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Results List */}
      <div className="space-y-4">
        {filteredResults.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              No results found for this filter
            </CardContent>
          </Card>
        ) : (
          filteredResults.map((result) => (
            <Card key={result.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline">{result.product.inn}</Badge>
                      {result.is_icsr && (
                        <Badge className="bg-red-500">ICSR</Badge>
                      )}
                      {result.confidence_score && getConfidenceBadge(result.confidence_score)}
                    </div>
                    <CardTitle className="text-lg">{result.article.title}</CardTitle>
                    <CardDescription className="mt-2">
                      {result.article.authors} • {result.article.journal} • {result.article.publication_year}
                    </CardDescription>
                  </div>
                  {result.article.pmid && (
                    <Button variant="outline" size="sm" asChild>
                      <a
                        href={`https://pubmed.ncbi.nlm.nih.gov/${result.article.pmid}/`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <ExternalLink className="w-4 h-4 mr-2" />
                        PubMed
                      </a>
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Abstract */}
                {result.article.abstract && (
                  <div>
                    <div className="text-sm font-semibold mb-1">Abstract</div>
                    <div className="text-sm text-muted-foreground">
                      {result.article.abstract}
                    </div>
                  </div>
                )}

                {/* ICSR Information */}
                {result.is_icsr && (
                  <div className="p-4 bg-red-50 dark:bg-red-950 rounded-lg border border-red-200 dark:border-red-800">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                      <div className="flex-1">
                        <div className="font-semibold text-red-900 dark:text-red-100">ICSR Detected</div>
                        {result.icsr_description && (
                          <div className="text-sm text-red-800 dark:text-red-200 mt-1">
                            {result.icsr_description}
                          </div>
                        )}
                        {result.ownership_excluded !== null && (
                          <div className="text-sm mt-2">
                            <span className="font-semibold">Ownership Excluded: </span>
                            {result.ownership_excluded ? 'Yes' : 'No'}
                            {result.exclusion_reason && (
                              <span className="text-red-700 dark:text-red-300"> - {result.exclusion_reason}</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Safety Information */}
                {result.other_safety_info !== null && (
                  <div className={`p-4 rounded-lg border ${
                    result.other_safety_info
                      ? 'bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800'
                      : 'bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-800'
                  }`}>
                    <div className="flex items-start gap-2">
                      {result.other_safety_info ? (
                        <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5" />
                      ) : (
                        <Info className="w-5 h-5 text-gray-600 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <div className={`font-semibold ${
                          result.other_safety_info
                            ? 'text-green-900 dark:text-green-100'
                            : 'text-gray-900 dark:text-gray-100'
                        }`}>
                          {result.other_safety_info ? 'Relevant Safety Information' : 'Irrelevant'}
                        </div>
                        {result.safety_info_justification && (
                          <div className={`text-sm mt-1 ${
                            result.other_safety_info
                              ? 'text-green-800 dark:text-green-200'
                              : 'text-gray-700 dark:text-gray-300'
                          }`}>
                            {result.safety_info_justification}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Metadata */}
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span>PMID: {result.article.pmid}</span>
                  {result.article.doi && <span>DOI: {result.article.doi}</span>}
                  {result.article.pmcid && <span>PMC: {result.article.pmcid}</span>}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

