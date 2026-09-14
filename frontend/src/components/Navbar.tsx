import React from 'react'
import { ArrowRightLeft, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react'
import { HealthInfo } from '../services/api'

interface NavbarProps {
  health: HealthInfo | null
  healthLoading: boolean
  healthError: string | null
  selectedProvider: string
  onReset?: () => void
  hasReport?: boolean
}

export const Navbar: React.FC<NavbarProps> = ({
  health,
  healthLoading,
  healthError,
  selectedProvider,
  onReset,
  hasReport,
}) => {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Logo & Title */}
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-600 text-white rounded-xl shadow-xs">
            <ArrowRightLeft className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-slate-900 tracking-tight">
                Commercial Offer PDF Comparator
              </h1>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100">
                MVP
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Substantive change detection &bull; Dual source citations &bull; Arithmetic audit
            </p>
          </div>
        </div>

        {/* Status Badges & Controls */}
        <div className="flex items-center space-x-3 text-xs">
          {/* Provider Badge */}
          <div className="hidden sm:flex items-center px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md border border-slate-200">
            <span className="text-slate-400 mr-1.5 font-medium">Provider:</span>
            <span className="font-semibold text-slate-800 capitalize">{selectedProvider}</span>
          </div>

          {/* Backend Connection */}
          <div className="flex items-center px-2.5 py-1 bg-slate-50 rounded-md border border-slate-200">
            <span className="text-slate-400 mr-1.5 font-medium">Backend:</span>
            {healthLoading ? (
              <span className="text-slate-400 flex items-center">
                <RefreshCw className="w-3 h-3 animate-spin mr-1 text-slate-400" />
                Connecting...
              </span>
            ) : healthError ? (
              <span className="flex items-center text-rose-600 font-medium" title={healthError}>
                <AlertCircle className="w-3.5 h-3.5 mr-1" />
                Offline
              </span>
            ) : (
              <span className="flex items-center text-emerald-600 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                Ready {health?.model ? `(${health.model})` : ''}
              </span>
            )}
          </div>

          {/* Reset / New Comparison button */}
          {hasReport && onReset && (
            <button
              onClick={onReset}
              className="flex items-center px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-md transition-colors"
              title="Reset comparison"
            >
              <RefreshCw className="w-3 h-3 mr-1.5" />
              New Comparison
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
