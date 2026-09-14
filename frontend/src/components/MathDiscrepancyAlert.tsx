import React from 'react'
import { AuditReport } from '../types'
import { AlertTriangle, AlertOctagon, ShieldAlert } from 'lucide-react'

interface MathDiscrepancyAlertProps {
  originalAudit: AuditReport
  revisedAudit: AuditReport
  currency?: string
}

export const MathDiscrepancyAlert: React.FC<MathDiscrepancyAlertProps> = ({
  originalAudit,
  revisedAudit,
  currency = 'USD',
}) => {
  const origDiscrepancies = originalAudit.discrepancies || []
  const revDiscrepancies = revisedAudit.discrepancies || []
  const hasErrors = !originalAudit.is_valid || !revisedAudit.is_valid || origDiscrepancies.length > 0 || revDiscrepancies.length > 0

  if (!hasErrors) {
    return null
  }

  const formatAmount = (num: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency === 'USD' ? 'USD' : 'EUR',
      minimumFractionDigits: 2,
    }).format(num)
  }

  return (
    <div className="mb-6 rounded-xl border-2 border-amber-300 bg-amber-50/90 p-5 shadow-xs">
      <div className="flex items-start space-x-3.5">
        <div className="p-2 bg-amber-500 text-white rounded-lg shrink-0 mt-0.5 shadow-2xs">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-amber-950 flex items-center gap-2">
              <span>Source Document Arithmetic Discrepancy Detected</span>
              <span className="text-[11px] font-semibold bg-amber-200 text-amber-900 px-2 py-0.5 rounded-full">
                Attention Required
              </span>
            </h3>
          </div>
          <p className="text-xs text-amber-900 mt-1 leading-relaxed">
            The deterministic arithmetic auditor detected calculation inconsistencies printed in the source PDF offer. 
            Under the zero-hallucination policy, the system preserves and reports the printed figures while highlighting the mathematical discrepancy.
          </p>

          <div className="mt-4 space-y-3">
            {/* Original Document Discrepancies */}
            {origDiscrepancies.length > 0 && (
              <div className="bg-white/80 rounded-lg p-3 border border-amber-200">
                <div className="flex items-center space-x-1.5 text-xs font-bold text-amber-950 mb-2">
                  <ShieldAlert className="w-4 h-4 text-amber-700" />
                  <span>Original Document ({originalAudit.document_name}):</span>
                </div>
                <div className="space-y-2">
                  {origDiscrepancies.map((disc, i) => (
                    <div key={i} className="text-xs grid grid-cols-1 sm:grid-cols-3 gap-2 p-2 bg-amber-50/60 rounded border border-amber-100">
                      <div>
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Location</span>
                        <span className="font-semibold text-slate-800">{disc.location}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Printed Value</span>
                        <span className="font-bold text-rose-700">{formatAmount(disc.actual_value)}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Deterministic Expected</span>
                        <span className="font-bold text-emerald-700">{formatAmount(disc.expected_value)}</span>
                      </div>
                      <div className="sm:col-span-3 text-[11px] text-amber-900 italic mt-0.5">
                        &ldquo;{disc.message}&rdquo;
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Revised Document Discrepancies */}
            {revDiscrepancies.length > 0 && (
              <div className="bg-white/80 rounded-lg p-3 border border-amber-200">
                <div className="flex items-center space-x-1.5 text-xs font-bold text-amber-950 mb-2">
                  <AlertOctagon className="w-4 h-4 text-rose-600" />
                  <span>Revised Document ({revisedAudit.document_name}):</span>
                </div>
                <div className="space-y-2">
                  {revDiscrepancies.map((disc, i) => (
                    <div key={i} className="text-xs grid grid-cols-1 sm:grid-cols-3 gap-2 p-2 bg-amber-50/60 rounded border border-amber-100">
                      <div>
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Location</span>
                        <span className="font-semibold text-slate-800">{disc.location}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Printed Value in PDF</span>
                        <span className="font-bold text-rose-700">{formatAmount(disc.actual_value)}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Deterministic Expected (Qty &times; Price)</span>
                        <span className="font-bold text-emerald-700">{formatAmount(disc.expected_value)}</span>
                      </div>
                      <div className="sm:col-span-3 text-[11px] text-amber-900 italic mt-0.5">
                        &ldquo;{disc.message}&rdquo;
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
