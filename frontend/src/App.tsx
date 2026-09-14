import { useState, useEffect } from 'react'
import { Navbar } from './components/Navbar'
import { UploadSection } from './components/UploadSection'
import { SummaryBar } from './components/SummaryBar'
import { MathDiscrepancyAlert } from './components/MathDiscrepancyAlert'
import { DocumentOverview } from './components/DocumentOverview'
import { ChangesTable } from './components/ChangesTable'
import { SourceCitationModal } from './components/SourceCitationModal'
import { ComparisonReport, DetectedChange } from './types'
import { checkBackendHealth, compareOffers, fetchSampleFile, HealthInfo } from './services/api'
import { ArrowDown, ShieldCheck, CheckCircle } from 'lucide-react'

export default function App() {
  // Backend health status
  const [health, setHealth] = useState<HealthInfo | null>(null)
  const [healthLoading, setHealthLoading] = useState<boolean>(true)
  const [healthError, setHealthError] = useState<string | null>(null)

  // Files & comparison configuration
  const [originalFile, setOriginalFile] = useState<File | null>(null)
  const [revisedFile, setRevisedFile] = useState<File | null>(null)
  const [provider, setProvider] = useState<string>('auto')

  // Execution states
  const [comparing, setComparing] = useState<boolean>(false)
  const [loadingScenario, setLoadingScenario] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Comparison Results
  const [report, setReport] = useState<ComparisonReport | null>(null)
  const [activeCitationChange, setActiveCitationChange] = useState<DetectedChange | null>(null)

  // Check health on mount
  useEffect(() => {
    checkBackendHealth()
      .then((data) => {
        setHealth(data)
        setHealthLoading(false)
      })
      .catch((err) => {
        setHealthError(err.message)
        setHealthLoading(false)
      })
  }, [])

  // Quick Preset Scenarios Loader
  const handleLoadScenario = async (scenarioId: 'scenario_1' | 'scenario_2' | 'scenario_3') => {
    try {
      setLoadingScenario(scenarioId)
      setError(null)

      let origName = 'offer_v1.pdf'
      let revName = 'offer_v2_substantive.pdf'

      if (scenarioId === 'scenario_2') {
        revName = 'offer_v1_reformatted.pdf'
      } else if (scenarioId === 'scenario_3') {
        revName = 'offer_v2_ambiguous.pdf'
      }

      const [origF, revF] = await Promise.all([
        fetchSampleFile(origName),
        fetchSampleFile(revName),
      ])

      setOriginalFile(origF)
      setRevisedFile(revF)

      // Automatically execute comparison for maximum demo convenience
      setComparing(true)
      const res = await compareOffers(origF, revF, provider)
      setReport(res)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err)
      setError(`Failed to load scenario: ${msg}`)
    } finally {
      setLoadingScenario(null)
      setComparing(false)
    }
  }

  // Trigger Comparison
  const handleCompare = async () => {
    if (!originalFile || !revisedFile) {
      setError('Please provide both the original and revised PDF documents.')
      return
    }

    try {
      setComparing(true)
      setError(null)
      const res = await compareOffers(originalFile, revisedFile, provider)
      setReport(res)
      // Scroll down to results smoothly
      setTimeout(() => {
        const resultsEl = document.getElementById('comparison-results')
        if (resultsEl) {
          resultsEl.scrollIntoView({ behavior: 'smooth' })
        }
      }, 100)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err)
      setError(msg)
    } finally {
      setComparing(false)
    }
  }

  // Reset comparison
  const handleReset = () => {
    setReport(null)
    setError(null)
    setOriginalFile(null)
    setRevisedFile(null)
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans antialiased selection:bg-indigo-500 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        health={health}
        healthLoading={healthLoading}
        healthError={healthError}
        selectedProvider={provider}
        onReset={handleReset}
        hasReport={report !== null}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <UploadSection
          originalFile={originalFile}
          revisedFile={revisedFile}
          onSelectOriginal={setOriginalFile}
          onSelectRevised={setRevisedFile}
          provider={provider}
          onProviderChange={setProvider}
          onCompare={handleCompare}
          onLoadScenario={handleLoadScenario}
          loadingScenario={loadingScenario}
          comparing={comparing}
          error={error}
        />

        {/* Results Section */}
        {report && (
          <div id="comparison-results" className="space-y-6 animate-in fade-in duration-300">
            {/* Results Title Banner */}
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <div className="flex items-center space-x-2">
                <div className="p-1.5 bg-indigo-600 text-white rounded-lg">
                  <ArrowDown className="w-4 h-4" />
                </div>
                <h2 className="text-lg font-bold text-slate-900 tracking-tight">
                  Comparison &amp; Audit Results
                </h2>
              </div>
              <div className="flex items-center space-x-2 text-xs text-slate-500">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>Deterministic Zero-Hallucination Audit</span>
              </div>
            </div>

            {/* 1. Summary Metrics Bar */}
            <SummaryBar report={report} />

            {/* 2. Arithmetic Discrepancy Alert */}
            <MathDiscrepancyAlert
              originalAudit={report.original_audit}
              revisedAudit={report.revised_audit}
              currency={report.summary.currency || report.original_document?.currency || 'USD'}
            />

            {/* 3. Document Headers Overview */}
            <DocumentOverview
              originalDoc={report.original_document}
              revisedDoc={report.revised_document}
            />

            {/* 4. Substantive Changes Table */}
            <ChangesTable
              changes={report.changes}
              onOpenCitation={setActiveCitationChange}
              currency={report.summary.currency || report.original_document?.currency || 'USD'}
            />
          </div>
        )}
      </main>

      {/* Dual Source Reference Modal */}
      <SourceCitationModal
        change={activeCitationChange}
        onClose={() => setActiveCitationChange(null)}
      />

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 mt-12 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            Codebridge AI-First Product Builder &bull; Commercial Offer Comparison Engine
          </div>
          <div className="flex items-center space-x-3 text-slate-500">
            <span className="flex items-center">
              <CheckCircle className="w-3.5 h-3.5 mr-1 text-emerald-600" />
              Verifiable Dual Citations
            </span>
            <span>&bull;</span>
            <span>FastAPI + React 18 + Gemini Flash</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
