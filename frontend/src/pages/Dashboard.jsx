import { useState, useEffect } from 'react'
import { Activity, Database, FileSearch, AlertCircle, CheckCircle2, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalSearchJobs: 0,
    totalArticles: 0,
    pendingReviews: 0,
  })
  const [recentJobs, setRecentJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch products
      const productsRes = await fetch(`${API_BASE_URL}/products`)
      const productsData = await productsRes.json()
      
      // Fetch search jobs
      const jobsRes = await fetch(`${API_BASE_URL}/search/jobs`)
      const jobsData = await jobsRes.json()
      
      setStats({
        totalProducts: productsData.count || 0,
        totalSearchJobs: jobsData.count || 0,
        totalArticles: jobsData.data?.reduce((sum, job) => sum + (job.total_articles || 0), 0) || 0,
        pendingReviews: 0, // Calculate from results if needed
      })
      
      setRecentJobs(jobsData.data?.slice(0, 5) || [])
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      title: 'Total Products',
      value: stats.totalProducts,
      icon: Database,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Search Jobs',
      value: stats.totalSearchJobs,
      icon: FileSearch,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Total Articles',
      value: stats.totalArticles,
      icon: Activity,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Pending Reviews',
      value: stats.pendingReviews,
      icon: Clock,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ]

  const getStatusBadge = (status) => {
    const statusConfig = {
      completed: { icon: CheckCircle2, color: 'text-green-600', bg: 'bg-green-100' },
      running: { icon: Clock, color: 'text-blue-600', bg: 'bg-blue-100' },
      failed: { icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-100' },
      pending: { icon: Clock, color: 'text-gray-600', bg: 'bg-gray-100' },
    }
    
    const config = statusConfig[status] || statusConfig.pending
    const Icon = config.icon
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
        <Icon className="w-3 h-3" />
        {status}
      </span>
    )
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
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Overview of your pharmacovigilance literature monitoring activities
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => (
          <Card key={stat.title} className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Search Jobs */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Search Jobs</CardTitle>
          <CardDescription>Latest literature search activities</CardDescription>
        </CardHeader>
        <CardContent>
          {recentJobs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileSearch className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No search jobs yet</p>
              <p className="text-sm mt-1">Start by creating a search from the Search page</p>
            </div>
          ) : (
            <div className="space-y-4">
              {recentJobs.map((job) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-accent transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-foreground">
                        {job.job_type === 'batch' ? 'Batch Search' : 'Single Search'}
                      </span>
                      {getStatusBadge(job.status)}
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {job.total_products} products • {job.total_articles} articles
                      {job.date_from && job.date_to && (
                        <span> • {job.date_from} to {job.date_to}</span>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Created: {new Date(job.created_at).toLocaleString()}
                    </div>
                  </div>
                  <Button variant="outline" size="sm" asChild>
                    <a href={`/results?job_id=${job.id}`}>View Results</a>
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks and operations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button className="h-auto py-6 flex flex-col gap-2" asChild>
              <a href="/search">
                <FileSearch className="w-6 h-6" />
                <span>New Search</span>
              </a>
            </Button>
            <Button variant="outline" className="h-auto py-6 flex flex-col gap-2" asChild>
              <a href="/products">
                <Database className="w-6 h-6" />
                <span>Manage Products</span>
              </a>
            </Button>
            <Button variant="outline" className="h-auto py-6 flex flex-col gap-2" asChild>
              <a href="/export">
                <Activity className="w-6 h-6" />
                <span>Export Results</span>
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

