import { useEffect, useState } from 'react'
import { FileText, CheckCircle2, AlertCircle, ArrowRightLeft } from 'lucide-react'

interface HealthResponse {
  status: string
  service: string
  model: string
}

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/health')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        setHealth(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
              <ArrowRightLeft className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Commercial Offer PDF Comparator</h1>
              <p className="text-xs text-slate-500">AI-First Product Builder MVP</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-400">Backend:</span>
            {loading ? (
              <span className="text-slate-400">Checking...</span>
            ) : error ? (
              <span className="flex items-center text-red-600 font-medium">
                <AlertCircle className="w-3.5 h-3.5 mr-1" /> Disconnected
              </span>
            ) : (
              <span className="flex items-center text-emerald-600 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Connected ({health?.model})
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Main content placeholder */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center max-w-2xl mx-auto">
          <div className="mx-auto w-12 h-12 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mb-4">
            <FileText className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-semibold text-slate-900 mb-2">
            Scaffolding Ready (T-001)
          </h2>
          <p className="text-sm text-slate-600 mb-6">
            Backend and Frontend boilerplates are established. Data contracts, PDF extractor, and AI pipeline will be plugged in via subsequent tickets.
          </p>
          <div className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
            Phase 1: Project Setup Complete
          </div>
        </div>
      </main>
    </div>
  )
}
