import React from 'react'
import { ComparisonReport, ChangeType } from '../types'
import { DollarSign, TrendingUp, TrendingDown, Clock, Cpu, Calendar, PlusCircle, MinusCircle, Edit3 } from 'lucide-react'

interface SummaryBarProps {
  report: ComparisonReport
}

export const SummaryBar: React.FC<SummaryBarProps> = ({ report }) => {
  const { summary, changes, original_document, revised_document, processing_time_ms, token_usage, estimated_cost_usd } = report

  // Grand totals
  const origTotal = summary.original_grand_total ?? original_document?.grand_total ?? null
  const revTotal = summary.revised_grand_total ?? revised_document?.grand_total ?? null
  const currency = summary.currency ?? original_document?.currency ?? 'USD'
  const priceDelta = summary.price_difference ?? (origTotal !== null && revTotal !== null ? revTotal - origTotal : null)

  const formatMoney = (val: number | null | undefined): string => {
    if (val === null || val === undefined) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency === 'USD' ? 'USD' : 'EUR',
      minimumFractionDigits: 2,
    }).format(val)
  }

  // Delivery Dates
  const origDelivery = original_document?.delivery_date
  const revDelivery = revised_document?.delivery_date
  const deliveryChanged = origDelivery && revDelivery && origDelivery !== revDelivery

  // Changes Breakdown
  const addedCount = changes.filter((c) => c.change_type === ChangeType.ADDED).length
  const removedCount = changes.filter((c) => c.change_type === ChangeType.REMOVED).length
  const modifiedCount = changes.length - (addedCount + removedCount)

  // Cost & Performance
  const timeMs = processing_time_ms ?? summary.processing_time_ms ?? 0
  const formattedTime = timeMs >= 1000 ? `${(timeMs / 1000).toFixed(2)}s` : `${timeMs}ms`
  const cost = estimated_cost_usd ?? summary.estimated_cost_usd ?? token_usage?.estimated_cost_usd ?? 0
  const formattedCost = cost > 0 ? `$${cost.toFixed(5)}` : '$0.00'

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* 1. Net Price Delta Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Grand Total Delta</span>
            <div className="p-1.5 bg-indigo-50 text-indigo-600 rounded-lg">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-900 tracking-tight">
              {formatMoney(revTotal)}
            </span>
            {origTotal !== null && (
              <span className="text-xs text-slate-400 line-through">
                {formatMoney(origTotal)}
              </span>
            )}
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-medium">
          <span className="text-slate-500">Net Impact:</span>
          {priceDelta === null || priceDelta === 0 ? (
            <span className="text-slate-600 font-semibold">&plusmn;$0.00 (No Price Change)</span>
          ) : priceDelta > 0 ? (
            <span className="inline-flex items-center text-rose-600 font-semibold">
              <TrendingUp className="w-3.5 h-3.5 mr-1" />
              +{formatMoney(priceDelta)} ({origTotal ? `+${((priceDelta / origTotal) * 100).toFixed(1)}%` : ''})
            </span>
          ) : (
            <span className="inline-flex items-center text-emerald-600 font-semibold">
              <TrendingDown className="w-3.5 h-3.5 mr-1" />
              {formatMoney(priceDelta)} ({origTotal ? `${((priceDelta / origTotal) * 100).toFixed(1)}%` : ''})
            </span>
          )}
        </div>
      </div>

      {/* 2. Substantive Changes Count */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Substantive Changes</span>
            <span className="text-xs font-bold px-2 py-0.5 bg-slate-100 text-slate-700 rounded-md">
              {changes.length} total
            </span>
          </div>
          <div className="flex items-center space-x-3 text-sm font-bold">
            <div className="flex items-center text-emerald-600">
              <PlusCircle className="w-3.5 h-3.5 mr-1" />
              <span>{addedCount} added</span>
            </div>
            <div className="flex items-center text-rose-600">
              <MinusCircle className="w-3.5 h-3.5 mr-1" />
              <span>{removedCount} removed</span>
            </div>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span className="flex items-center text-slate-600 font-medium">
            <Edit3 className="w-3.5 h-3.5 mr-1 text-indigo-500" />
            {modifiedCount} modified / scope shifts
          </span>
          <span className="text-[11px] text-slate-400">Layout ignored</span>
        </div>
      </div>

      {/* 3. Delivery Schedule & Metadata */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Delivery Schedule</span>
            <div className="p-1.5 bg-amber-50 text-amber-600 rounded-lg">
              <Calendar className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-1.5">
            <span className="text-base font-bold text-slate-900">
              {revDelivery || 'Not specified'}
            </span>
            {origDelivery && deliveryChanged && (
              <span className="text-xs text-slate-400 line-through">
                {origDelivery}
              </span>
            )}
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
          <span className="text-slate-500">Timeline status:</span>
          {deliveryChanged ? (
            <span className="text-amber-700 font-semibold bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
              Date Postponed / Shifted
            </span>
          ) : (
            <span className="text-emerald-700 font-medium">Unchanged</span>
          )}
        </div>
      </div>

      {/* 4. Efficiency & AI Token Cost */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Performance & Cost</span>
            <div className="p-1.5 bg-blue-50 text-blue-600 rounded-lg">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <div className="flex items-center space-x-1.5">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-base font-bold text-slate-800 font-mono">
                {formattedTime}
              </span>
            </div>
            <div className="text-right">
              <span className="text-sm font-bold text-emerald-700 font-mono">
                {formattedCost}
              </span>
            </div>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>Tokens:</span>
          <span className="font-mono text-[11px] text-slate-600">
            {token_usage?.total_tokens ? `${token_usage.total_tokens} (${token_usage.prompt_tokens} in / ${token_usage.completion_tokens} out)` : 'Offline benchmark'}
          </span>
        </div>
      </div>
    </div>
  )
}
