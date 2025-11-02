import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import { 
  FileSearch, 
  Database, 
  Settings, 
  Download, 
  Activity,
  Menu,
  X
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import './App.css'

// Import pages
import Dashboard from './pages/Dashboard'
import Products from './pages/Products'
import Search from './pages/Search'
import Results from './pages/Results'
import Configuration from './pages/Configuration'
import Export from './pages/Export'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const navigation = [
    { name: 'Dashboard', path: '/', icon: Activity },
    { name: 'Products', path: '/products', icon: Database },
    { name: 'Search', path: '/search', icon: FileSearch },
    { name: 'Results', path: '/results', icon: FileSearch },
    { name: 'Export', path: '/export', icon: Download },
    { name: 'Configuration', path: '/configuration', icon: Settings },
  ]

  return (
    <Router>
      <div className="flex h-screen bg-background">
        {/* Sidebar */}
        <aside
          className={`${
            sidebarOpen ? 'w-64' : 'w-0'
          } bg-card border-r border-border transition-all duration-300 overflow-hidden`}
        >
          <div className="flex flex-col h-full">
            {/* Logo */}
            <div className="p-6 border-b border-border">
              <h1 className="text-xl font-bold text-foreground">
                PharmaVigilance
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Literature Monitoring
              </p>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-2">
              {navigation.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    }`
                  }
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                </NavLink>
              ))}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-border">
              <p className="text-xs text-muted-foreground text-center">
                PoC Version 1.0
              </p>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <header className="bg-card border-b border-border px-6 py-4 flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-foreground">
                Pharmacovigilance Literature Monitoring System
              </h2>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 overflow-auto p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/products" element={<Products />} />
              <Route path="/search" element={<Search />} />
              <Route path="/results" element={<Results />} />
              <Route path="/export" element={<Export />} />
              <Route path="/configuration" element={<Configuration />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App

