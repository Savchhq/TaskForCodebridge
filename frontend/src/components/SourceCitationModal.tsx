import React, { useEffect } from 'react'
import { DetectedChange, ChangeType, ConfidenceLevel } from '../types'
import { X, FileText, Bookmark, Check, Copy, AlertTriangle } from 'lucide-react'

interface SourceCitationModalProps {
  change: DetectedChange | null
  onClose: () => void
}

export const SourceCitationModal: React.FC<SourceCitationModalProps> = ({ change, onClose }) => {
  const [copiedField, setCopiedField] = React.useState<'orig' | 'rev' | null>(null)

  // ESC key listener to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!change) return null

  const handleCopy = (text: string, field: 'orig' | 'rev') => {
    navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  const isAdded = change.change_type === ChangeType.ADDED
  const isRemoved = change.change_type === ChangeType.REMOVED

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-2xl w-full overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
              <Bookmark className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold text-slate-900">Dual Source Location Reference</h3>
                <span
                  className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                    change.confidence === ConfidenceLevel.CONFIRMED
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-amber-50 text-amber-700 border border-amber-200'
                  }`}
                >
                  {change.confidence}
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Verbatim citation and page location from the analyzed PDF offers
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            title="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Change Context Banner */}
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs">
            <div className="flex items-center justify-between text-slate-500 mb-1">
              <span className="font-semibold uppercase tracking-wider text-[10px]">Change Scope</span>
              <span className="font-mono text-slate-600 font-semibold">{change.change_type}</span>
            </div>
            <p className="text-slate-800 font-medium">
              {change.explanation}
            </p>
          </div>

          {/* Side-by-side Dual Source Citations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Original Document Citation */}
            <div className="flex flex-col rounded-xl border border-slate-200 overflow-hidden bg-white">
              <div className="bg-slate-50 px-3.5 py-2 border-b border-slate-200 flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-indigo-600" />
                  Original Offer
                </span>
                {change.original_source_ref ? (
                  <span className="text-[11px] font-mono font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                    Page {change.original_source_ref.page_number}
                  </span>
                ) : (
                  <span className="text-[11px] text-slate-400">N/A</span>
                )}
              </div>

              <div className="p-3.5 flex-1 flex flex-col justify-between text-xs">
                {isAdded ? (
                  <div className="text-slate-400 italic py-4 text-center">
                    Not present in original document (Item newly added in revision)
                  </div>
                ) : change.original_source_ref ? (
                  <>
                    <div className="bg-slate-900 text-slate-100 p-3 rounded-lg font-mono text-[11px] leading-relaxed break-words shadow-inner">
                      <span className="text-emerald-400 mr-1">&ldquo;</span>
                      {change.original_source_ref.snippet}
                      <span className="text-emerald-400 ml-1">&rdquo;</span>
                    </div>
                    <div className="mt-3 flex justify-end">
                      <button
                        type="button"
                        onClick={() => handleCopy(change.original_source_ref!.snippet, 'orig')}
                        className="inline-flex items-center text-[11px] text-slate-500 hover:text-indigo-600 font-medium transition-colors"
                      >
                        {copiedField === 'orig' ? (
                          <>
                            <Check className="w-3 h-3 mr-1 text-emerald-600" />
                            Copied to clipboard
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3 mr-1" />
                            Copy quote
                          </>
                        )}
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="text-slate-400 italic py-4 text-center">
                    Header / Document-level change
                  </div>
                )}
              </div>
            </div>

            {/* Revised Document Citation */}
            <div className="flex flex-col rounded-xl border border-slate-200 overflow-hidden bg-white">
              <div className="bg-slate-50 px-3.5 py-2 border-b border-slate-200 flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-emerald-600" />
                  Revised Offer
                </span>
                {change.revised_source_ref ? (
                  <span className="text-[11px] font-mono font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                    Page {change.revised_source_ref.page_number}
                  </span>
                ) : (
                  <span className="text-[11px] text-slate-400">N/A</span>
                )}
              </div>

              <div className="p-3.5 flex-1 flex flex-col justify-between text-xs">
                {isRemoved ? (
                  <div className="text-slate-400 italic py-4 text-center">
                    Removed from revised document
                  </div>
                ) : change.revised_source_ref ? (
                  <>
                    <div className="bg-slate-900 text-slate-100 p-3 rounded-lg font-mono text-[11px] leading-relaxed break-words shadow-inner">
                      <span className="text-emerald-400 mr-1">&ldquo;</span>
                      {change.revised_source_ref.snippet}
                      <span className="text-emerald-400 ml-1">&rdquo;</span>
                    </div>
                    <div className="mt-3 flex justify-end">
                      <button
                        type="button"
                        onClick={() => handleCopy(change.revised_source_ref!.snippet, 'rev')}
                        className="inline-flex items-center text-[11px] text-slate-500 hover:text-emerald-600 font-medium transition-colors"
                      >
                        {copiedField === 'rev' ? (
                          <>
                            <Check className="w-3 h-3 mr-1 text-emerald-600" />
                            Copied to clipboard
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3 mr-1" />
                            Copy quote
                          </>
                        )}
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="text-slate-400 italic py-4 text-center">
                    Header / Document-level change
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Uncertainty Notice if applicable */}
          {change.confidence === ConfidenceLevel.UNCERTAIN && (
            <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 flex items-start space-x-2.5 text-xs text-amber-900">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Human Review Flag:</span> This match was flagged as uncertain because the item naming or scope could not be matched with high confidence. Review both citations above to confirm or adjust before signing.
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-white hover:bg-slate-100 text-slate-700 font-semibold text-xs rounded-lg border border-slate-300 transition-colors shadow-2xs"
          >
            Close Citation
          </button>
        </div>
      </div>
    </div>
  )
}
