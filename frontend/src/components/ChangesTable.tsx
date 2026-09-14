import React, { useState } from 'react'
import { DetectedChange, ChangeType, ConfidenceLevel } from '../types'
import {
  CheckCircle2,
  AlertTriangle,
  Bookmark,
  CheckCheck,
  Search,
  Filter,
  ArrowRight,
  Sparkles,
} from 'lucide-react'

interface ChangesTableProps {
  changes: DetectedChange[]
  onOpenCitation: (change: DetectedChange) => void
  currency?: string
}

export const ChangesTable: React.FC<ChangesTableProps> = ({
  changes,
  onOpenCitation,
  currency = 'USD',
}) => {
  const [selectedFilter, setSelectedFilter] = useState<string>('ALL')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [uncertainOnly, setUncertainOnly] = useState<boolean>(false)

  // Filter categories
  const filterOptions = [
    { key: 'ALL', label: 'All Changes', count: changes.length },
    {
      key: ChangeType.ADDED,
      label: 'Added',
      count: changes.filter((c) => c.change_type === ChangeType.ADDED).length,
    },
    {
      key: ChangeType.REMOVED,
      label: 'Removed',
      count: changes.filter((c) => c.change_type === ChangeType.REMOVED).length,
    },
    {
      key: ChangeType.RENAMED,
      label: 'Renamed',
      count: changes.filter((c) => c.change_type === ChangeType.RENAMED).length,
    },
    {
      key: ChangeType.QUANTITY_CHANGED,
      label: 'Quantity',
      count: changes.filter((c) => c.change_type === ChangeType.QUANTITY_CHANGED).length,
    },
    {
      key: ChangeType.UNIT_PRICE_CHANGED,
      label: 'Price',
      count: changes.filter((c) => c.change_type === ChangeType.UNIT_PRICE_CHANGED).length,
    },
    {
      key: ChangeType.TOTAL_CHANGED,
      label: 'Totals',
      count: changes.filter((c) => c.change_type === ChangeType.TOTAL_CHANGED).length,
    },
    {
      key: ChangeType.DELIVERY_DATE_CHANGED,
      label: 'Delivery Date',
      count: changes.filter((c) => c.change_type === ChangeType.DELIVERY_DATE_CHANGED).length,
    },
  ]

  // Filter logic
  const filteredChanges = changes.filter((item) => {
    // Type filter
    if (selectedFilter !== 'ALL' && item.change_type !== selectedFilter) {
      return false
    }

    // Uncertainty filter
    if (uncertainOnly && item.confidence !== ConfidenceLevel.UNCERTAIN) {
      return false
    }

    // Search query
    if (searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase()
      const origName = (item.item_name_original || '').toLowerCase()
      const revName = (item.item_name_revised || '').toLowerCase()
      const expl = (item.explanation || '').toLowerCase()
      if (!origName.includes(q) && !revName.includes(q) && !expl.includes(q)) {
        return false
      }
    }

    return true
  })

  // Format complex or simple values
  const renderValueDiff = (change: DetectedChange) => {
    const { change_type, original_value, revised_value } = change

    const formatVal = (val: unknown): string => {
      if (val === null || val === undefined) return '—'
      const currSymbol = currency === 'EUR' ? '€' : '$'
      if (typeof val === 'number') {
        if (change_type === ChangeType.UNIT_PRICE_CHANGED || change_type === ChangeType.TOTAL_CHANGED) {
          return `${currSymbol}${val.toLocaleString('en-US', { minimumFractionDigits: 2 })}`
        }
        return val.toString()
      }
      if (typeof val === 'object') {
        // e.g. { quantity: 1, unit_price: 500, total_price: 500 }
        const obj = val as Record<string, unknown>
        const parts = []
        if (obj.quantity) parts.push(`Qty: ${obj.quantity}`)
        if (obj.unit_price) parts.push(`${currSymbol}${Number(obj.unit_price).toFixed(2)}`)
        if (obj.total_price) parts.push(`Total: ${currSymbol}${Number(obj.total_price).toFixed(2)}`)
        return parts.join(' • ') || JSON.stringify(val)
      }
      return String(val)
    }

    if (change_type === ChangeType.ADDED) {
      return (
        <span className="inline-flex items-center text-emerald-700 font-semibold text-xs bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
          + {formatVal(revised_value)}
        </span>
      )
    }

    if (change_type === ChangeType.REMOVED) {
      return (
        <span className="inline-flex items-center text-rose-700 font-semibold text-xs bg-rose-50 px-2 py-0.5 rounded border border-rose-100 line-through">
          {formatVal(original_value)}
        </span>
      )
    }

    return (
      <div className="flex items-center space-x-1.5 text-xs">
        <span className="text-slate-400 line-through truncate max-w-[130px]" title={formatVal(original_value)}>
          {formatVal(original_value)}
        </span>
        <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
        <span className="text-indigo-700 font-bold truncate max-w-[150px]" title={formatVal(revised_value)}>
          {formatVal(revised_value)}
        </span>
      </div>
    )
  }

  // Type badge styling
  const renderTypeBadge = (type: ChangeType) => {
    switch (type) {
      case ChangeType.ADDED:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            ADDED
          </span>
        )
      case ChangeType.REMOVED:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
            REMOVED
          </span>
        )
      case ChangeType.RENAMED:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-purple-50 text-purple-700 border border-purple-200">
            RENAMED
          </span>
        )
      case ChangeType.QUANTITY_CHANGED:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
            QUANTITY
          </span>
        )
      case ChangeType.UNIT_PRICE_CHANGED:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
            UNIT PRICE
          </span>
        )
      case ChangeType.TOTAL_CHANGED:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
            TOTAL AMOUNT
          </span>
        )
      case ChangeType.DELIVERY_DATE_CHANGED:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
            DELIVERY DATE
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
            {type}
          </span>
        )
    }
  }

  // Confidence badge styling
  const renderConfidenceBadge = (confidence: ConfidenceLevel) => {
    if (confidence === ConfidenceLevel.CONFIRMED) {
      return (
        <span
          className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200"
          title="High confidence match confirmed by semantic specifications"
        >
          <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" />
          CONFIRMED
        </span>
      )
    }
    return (
      <span
        className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-900 border border-amber-300 animate-pulse"
        title="Ambiguous match requiring human clarification"
      >
        <AlertTriangle className="w-3 h-3 mr-1 text-amber-700" />
        UNCERTAIN
      </span>
    )
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header & Filter Toolbar */}
      <div className="p-5 border-b border-slate-200 bg-white">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <span>Substantive Commercial Changes</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100">
                {filteredChanges.length} shown
              </span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Material alterations in scope, pricing, quantities, or delivery terms. Formatting &amp; layout variations are excluded.
            </p>
          </div>

          {/* Search and Uncertainty filter */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative min-w-[200px]">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search items..."
                className="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <button
              type="button"
              onClick={() => setUncertainOnly(!uncertainOnly)}
              className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                uncertainOnly
                  ? 'bg-amber-100 border-amber-300 text-amber-900 shadow-xs'
                  : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-600" />
              Uncertain Only
            </button>
          </div>
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center space-x-1 overflow-x-auto pt-4 border-t border-slate-100 mt-4 no-scrollbar">
          <Filter className="w-3.5 h-3.5 text-slate-400 mr-2 shrink-0" />
          {filterOptions.map((opt) => (
            <button
              key={opt.key}
              onClick={() => setSelectedFilter(opt.key)}
              className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium shrink-0 transition-colors ${
                selectedFilter === opt.key
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {opt.label}
              <span
                className={`ml-1.5 text-[10px] px-1.5 py-0.2 rounded-full ${
                  selectedFilter === opt.key ? 'bg-indigo-700 text-white' : 'bg-slate-100 text-slate-500'
                }`}
              >
                {opt.count}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Changes List / Table */}
      {changes.length === 0 ? (
        /* Zero Substantive Changes State (Scenario 2: Formatting-only) */
        <div className="p-12 text-center bg-emerald-50/20">
          <div className="mx-auto w-12 h-12 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mb-3">
            <CheckCheck className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 mb-1">
            Zero Substantive Changes Detected
          </h3>
          <p className="text-xs text-slate-600 max-w-md mx-auto leading-relaxed">
            The documents are commercially identical. All line items, quantities, unit prices, delivery terms, and grand totals match exactly despite differences in layout, whitespace, or typography.
          </p>
          <div className="mt-4 inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <Sparkles className="w-3 h-3 mr-1.5" />
            Clean Formatting-Only Match
          </div>
        </div>
      ) : filteredChanges.length === 0 ? (
        <div className="p-8 text-center text-slate-500 text-xs">
          No changes found matching the current search query and filter criteria.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <th className="py-3 px-4">Change Category</th>
                <th className="py-3 px-4">Item Scope</th>
                <th className="py-3 px-4">Values &amp; Delta</th>
                <th className="py-3 px-4">Explanation</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4 text-right">Source Citations</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {filteredChanges.map((change, idx) => {
                const isAdded = change.change_type === ChangeType.ADDED
                const isRemoved = change.change_type === ChangeType.REMOVED

                return (
                  <tr
                    key={idx}
                    className={`hover:bg-slate-50/70 transition-colors ${
                      change.confidence === ConfidenceLevel.UNCERTAIN ? 'bg-amber-50/30' : ''
                    }`}
                  >
                    {/* Category Badge */}
                    <td className="py-3.5 px-4 align-top whitespace-nowrap">
                      {renderTypeBadge(change.change_type)}
                    </td>

                    {/* Item Scope */}
                    <td className="py-3.5 px-4 align-top max-w-[240px]">
                      {isAdded ? (
                        <div className="font-semibold text-slate-900">
                          {change.item_name_revised || 'New Line Item'}
                        </div>
                      ) : isRemoved ? (
                        <div className="font-medium text-slate-700 line-through">
                          {change.item_name_original || 'Removed Item'}
                        </div>
                      ) : change.item_name_original === change.item_name_revised ? (
                        <div className="font-semibold text-slate-900">
                          {change.item_name_revised || change.item_name_original || 'Document Property'}
                        </div>
                      ) : (
                        <div>
                          <div className="font-medium text-slate-400 line-through text-[11px]">
                            {change.item_name_original}
                          </div>
                          <div className="font-semibold text-slate-900 mt-0.5">
                            {change.item_name_revised}
                          </div>
                        </div>
                      )}
                    </td>

                    {/* Values & Delta */}
                    <td className="py-3.5 px-4 align-top whitespace-nowrap">
                      {renderValueDiff(change)}
                    </td>

                    {/* Explanation */}
                    <td className="py-3.5 px-4 align-top max-w-[320px] text-slate-600 leading-relaxed">
                      {change.explanation}
                    </td>

                    {/* Confidence Badge */}
                    <td className="py-3.5 px-4 align-top whitespace-nowrap">
                      {renderConfidenceBadge(change.confidence)}
                    </td>

                    {/* Dual Source Reference Button */}
                    <td className="py-3.5 px-4 align-top text-right whitespace-nowrap">
                      <button
                        type="button"
                        onClick={() => onOpenCitation(change)}
                        className="inline-flex items-center px-2.5 py-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700 bg-indigo-50 hover:bg-indigo-100/80 rounded-lg border border-indigo-200 transition-colors shadow-2xs"
                        title="View exact page citations and verbatim source text"
                      >
                        <Bookmark className="w-3 h-3 mr-1 text-indigo-500" />
                        View Source
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
