import { useState, useEffect } from 'react'
import { Settings, CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export default function Configuration() {
  const [config, setConfig] = useState({
    pubmed_configured: false,
    openai_configured: false,
    pubmed_email: '',
    openai_model: 'gpt-4.1-mini',
    max_articles_per_search: 100,
  })
  const [testResults, setTestResults] = useState({
    pubmed: null,
    openai: null,
  })
  const [testing, setTesting] = useState({ pubmed: false, openai: false })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchConfig()
  }, [])

  const fetchConfig = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/config`)
      const data = await response.json()
      if (data.success) {
        setConfig(data.data)
      }
    } catch (error) {
      console.error('Error fetching config:', error)
    } finally {
      setLoading(false)
    }
  }

  const testPubMed = async () => {
    try {
      setTesting({ ...testing, pubmed: true })
      const response = await fetch(`${API_BASE_URL}/config/test-pubmed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      const data = await response.json()
      setTestResults({ ...testResults, pubmed: data.success })
    } catch (error) {
      console.error('Error testing PubMed:', error)
      setTestResults({ ...testResults, pubmed: false })
    } finally {
      setTesting({ ...testing, pubmed: false })
    }
  }

  const testOpenAI = async () => {
    try {
      setTesting({ ...testing, openai: true })
      const response = await fetch(`${API_BASE_URL}/config/test-openai`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      const data = await response.json()
      setTestResults({ ...testResults, openai: data.success })
    } catch (error) {
      console.error('Error testing OpenAI:', error)
      setTestResults({ ...testResults, openai: false })
    } finally {
      setTesting({ ...testing, openai: false })
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
        <h1 className="text-3xl font-bold text-foreground">Configuration</h1>
        <p className="text-muted-foreground mt-2">
          Manage system configuration and API credentials
        </p>
      </div>

      {/* API Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* PubMed Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>PubMed API</CardTitle>
            <CardDescription>
              Configure PubMed API for literature searches
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${config.pubmed_configured ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm">
                {config.pubmed_configured ? 'Configured' : 'Not Configured'}
              </span>
            </div>

            <div>
              <Label>API Key</Label>
              <Input
                type="password"
                placeholder="Enter PubMed API key"
                disabled
                value={config.pubmed_configured ? '••••••••••••' : ''}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Set via environment variable: PUBMED_API_KEY
              </p>
            </div>

            <div>
              <Label>Email</Label>
              <Input
                value={config.pubmed_email}
                disabled
              />
              <p className="text-xs text-muted-foreground mt-1">
                Set via environment variable: PUBMED_EMAIL
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Button
                onClick={testPubMed}
                disabled={testing.pubmed || !config.pubmed_configured}
                className="flex-1"
              >
                {testing.pubmed ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Testing...
                  </>
                ) : (
                  'Test Connection'
                )}
              </Button>
              {testResults.pubmed !== null && (
                <div className="flex items-center gap-1">
                  {testResults.pubmed ? (
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500" />
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* OpenAI Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>OpenAI API</CardTitle>
            <CardDescription>
              Configure OpenAI API for AI-powered analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${config.openai_configured ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm">
                {config.openai_configured ? 'Configured' : 'Not Configured'}
              </span>
            </div>

            <div>
              <Label>API Key</Label>
              <Input
                type="password"
                placeholder="Enter OpenAI API key"
                disabled
                value={config.openai_configured ? '••••••••••••' : ''}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Set via environment variable: OPENAI_API_KEY
              </p>
            </div>

            <div>
              <Label>Model</Label>
              <Input
                value={config.openai_model}
                disabled
              />
              <p className="text-xs text-muted-foreground mt-1">
                Set via environment variable: OPENAI_MODEL
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Button
                onClick={testOpenAI}
                disabled={testing.openai || !config.openai_configured}
                className="flex-1"
              >
                {testing.openai ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Testing...
                  </>
                ) : (
                  'Test Connection'
                )}
              </Button>
              {testResults.openai !== null && (
                <div className="flex items-center gap-1">
                  {testResults.openai ? (
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500" />
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Application Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Application Settings</CardTitle>
          <CardDescription>
            Configure application behavior and limits
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Max Articles Per Search</Label>
              <Input
                type="number"
                value={config.max_articles_per_search}
                disabled
              />
              <p className="text-xs text-muted-foreground mt-1">
                Set via environment variable: MAX_ARTICLES_PER_SEARCH
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Environment Variables Guide */}
      <Card>
        <CardHeader>
          <CardTitle>Environment Variables Guide</CardTitle>
          <CardDescription>
            How to configure the application
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">Local Deployment</h3>
              <p className="text-sm text-muted-foreground mb-2">
                Create a <code className="bg-muted px-1 py-0.5 rounded">.env</code> file in the backend directory:
              </p>
              <pre className="bg-muted p-4 rounded-lg text-xs overflow-x-auto">
{`PUBMED_API_KEY=your-pubmed-api-key
PUBMED_EMAIL=your-email@example.com
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4.1-mini
MAX_ARTICLES_PER_SEARCH=100`}
              </pre>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Cloud Deployment</h3>
              <p className="text-sm text-muted-foreground">
                Set environment variables in your cloud platform's configuration panel (AWS, Azure, GCP, etc.)
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

