import React from 'react'
import { Dropzone } from './Dropzone'
import { Sparkles, Play, RefreshCw, Cpu, Layers, HelpCircle, CheckCircle2 } from 'lucide-react'

interface UploadSectionProps {
  originalFile: File | null
  revisedFile: File | null
  onSelectOriginal: (file: File | null) => void
  onSelectRevised: (file: File | null) => void
  provider: string
  onProviderChange: (provider: string) => void
  onCompare: () => void
  onLoadScenario: (scenarioId: 'scenario_1' | 'scenario_2' | 'scenario_3') => void
  loadingScenario: string | null
  comparing: boolean
  error: string | null
}

export const UploadSection: React.FC<UploadSectionProps> = ({
  originalFile,
  revisedFile,
  onSelectOriginal,
  onSelectRevised,
  provider,
  onProviderChange,
  onCompare,
  onLoadScenario,
  loadingScenario,
  comparing,
  error,
}) => {
  const isReady = originalFile !== null && revisedFile !== null

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 mb-8">
      {/* Top Bar: Section Title + Provider Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b border-slate-100 gap-4 mb-6">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <span>Upload Commercial Offers</span>
            <span className="text-xs font-normal text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
              Step 1 of 2
            </span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Select or drag two text-based PDF versions of the commercial offer to detect substantive changes.
          </p>
        </div>

        {/* AI Provider Switcher */}
        <div className="flex items-center space-x-2 shrink-0">
          <label htmlFor="provider-select" className="text-xs font-semibold text-slate-600 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-indigo-600" />
            AI Provider:
          </label>
          <select
            id="provider-select"
            value={provider}
            onChange={(e) => onProviderChange(e.target.value)}
            disabled={comparing}
            className="text-xs font-medium text-slate-800 bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer disabled:opacity-50"
          >
            <option value="auto">Auto (Gemini Flash / Fallback Mock)</option>
            <option value="mock">Demo / Mock Provider (Deterministic)</option>
            <option value="gemini">Gemini Flash (Live API Key Required)</option>
          </select>
        </div>
      </div>

      {/* Quick Scenario Loader Presets */}
      <div className="mb-6 p-3 bg-indigo-50/50 rounded-xl border border-indigo-100/80">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
          <div className="flex items-center space-x-2 text-xs font-medium text-indigo-900">
            <Sparkles className="w-4 h-4 text-indigo-600 shrink-0" />
            <span>Fast Evaluation Test Presets:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => onLoadScenario('scenario_1')}
              disabled={comparing || loadingScenario !== null}
              className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                loadingScenario === 'scenario_1'
                  ? 'bg-indigo-200 text-indigo-800'
                  : 'bg-white hover:bg-indigo-50 text-indigo-700 border border-indigo-200 hover:border-indigo-300 shadow-2xs'
              }`}
              title="Scenario 1: Renamed item, reordering, qty change, price change, removed item, delivery date change, and intentional math error"
            >
              {loadingScenario === 'scenario_1' ? (
                <RefreshCw className="w-3 h-3 animate-spin mr-1.5 text-indigo-600" />
              ) : (
                <Play className="w-3 h-3 mr-1 text-indigo-600" />
              )}
              Scenario 1: Substantive & Math Error
            </button>

            <button
              type="button"
              onClick={() => onLoadScenario('scenario_2')}
              disabled={comparing || loadingScenario !== null}
              className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                loadingScenario === 'scenario_2'
                  ? 'bg-indigo-200 text-indigo-800'
                  : 'bg-white hover:bg-indigo-50 text-indigo-700 border border-indigo-200 hover:border-indigo-300 shadow-2xs'
              }`}
              title="Scenario 2: Distinct layout and formatting but identical data (0 substantive changes)"
            >
              {loadingScenario === 'scenario_2' ? (
                <RefreshCw className="w-3 h-3 animate-spin mr-1.5 text-indigo-600" />
              ) : (
                <Layers className="w-3 h-3 mr-1 text-indigo-600" />
              )}
              Scenario 2: Formatting-Only (0 Changes)
            </button>

            <button
              type="button"
              onClick={() => onLoadScenario('scenario_3')}
              disabled={comparing || loadingScenario !== null}
              className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                loadingScenario === 'scenario_3'
                  ? 'bg-indigo-200 text-indigo-800'
                  : 'bg-white hover:bg-indigo-50 text-indigo-700 border border-indigo-200 hover:border-indigo-300 shadow-2xs'
              }`}
              title="Scenario 3: Ambiguous item without part code triggers UNCERTAIN match badge"
            >
              {loadingScenario === 'scenario_3' ? (
                <RefreshCw className="w-3 h-3 animate-spin mr-1.5 text-indigo-600" />
              ) : (
                <HelpCircle className="w-3 h-3 mr-1 text-amber-600" />
              )}
              Scenario 3: Ambiguity (Uncertain)
            </button>
          </div>
        </div>
      </div>

      {/* Dual Dropzones */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <Dropzone
          id="original-file-upload"
          label="Original Commercial Offer (PDF)"
          badgeLabel="Baseline Document"
          badgeColor="indigo"
          file={originalFile}
          onFileSelect={onSelectOriginal}
          disabled={comparing}
        />
        <Dropzone
          id="revised-file-upload"
          label="Revised Commercial Offer (PDF)"
          badgeLabel="Revision / Amendment"
          badgeColor="emerald"
          file={revisedFile}
          onFileSelect={onSelectRevised}
          disabled={comparing}
        />
      </div>

      {/* Error display if comparison or loading failed */}
      {error && (
        <div className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs font-medium text-rose-800 flex items-start space-x-2.5">
          <span className="text-rose-600 font-bold shrink-0 mt-0.5">&bull; Error:</span>
          <div className="flex-1">{error}</div>
        </div>
      )}

      {/* Action Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
        <div className="text-xs text-slate-500 flex items-center gap-1.5">
          {isReady ? (
            <span className="flex items-center text-emerald-600 font-semibold">
              <CheckCircle2 className="w-4 h-4 mr-1 text-emerald-600" />
              Both files loaded. Ready to analyze.
            </span>
          ) : (
            <span>Please select or drop both PDF files to proceed.</span>
          )}
        </div>

        <button
          type="button"
          onClick={onCompare}
          disabled={!isReady || comparing}
          className={`inline-flex items-center justify-center px-6 py-3 rounded-xl text-sm font-semibold text-white shadow-md transition-all ${
            !isReady || comparing
              ? 'bg-slate-300 cursor-not-allowed text-slate-500 shadow-none'
              : 'bg-indigo-600 hover:bg-indigo-700 active:scale-[0.99] shadow-indigo-200 hover:shadow-lg'
          }`}
        >
          {comparing ? (
            <>
              <RefreshCw className="w-4 h-4 mr-2.5 animate-spin" />
              Extracting & Comparing Offers...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 mr-2" />
              Compare Commercial Offers
            </>
          )}
        </button>
      </div>
    </div>
  )
}
