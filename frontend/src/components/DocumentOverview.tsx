import React from 'react'
import { OfferDocument } from '../types'
import { FileText, Building2, User, Hash, Calendar, Layers } from 'lucide-react'

interface DocumentOverviewProps {
  originalDoc?: OfferDocument | null
  revisedDoc?: OfferDocument | null
}

export const DocumentOverview: React.FC<DocumentOverviewProps> = ({ originalDoc, revisedDoc }) => {
  if (!originalDoc && !revisedDoc) return null

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs mb-6">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
          <Layers className="w-4 h-4 text-slate-400" />
          Commercial Document Headers Overview
        </h3>
        <span className="text-[11px] text-slate-400 font-medium">Original vs Revised Metadata</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Original Document Header */}
        <div className="p-4 bg-slate-50/70 rounded-xl border border-slate-200">
          <div className="flex items-center space-x-2 text-xs font-bold text-slate-800 mb-3">
            <FileText className="w-4 h-4 text-indigo-600" />
            <span>Original Offer Baseline</span>
          </div>
          <div className="grid grid-cols-2 gap-y-2 text-xs">
            <div>
              <span className="text-[10px] uppercase text-slate-400 font-semibold block flex items-center gap-1">
                <Building2 className="w-3 h-3 text-slate-400" /> Vendor
              </span>
              <span className="font-semibold text-slate-800 truncate block">
                {originalDoc?.vendor_name || '—'}
              </span>
            </div>
            <div>
              <span className="text-[10px] uppercase text-slate-400 font-semibold block flex items-center gap-1">
                <User className="w-3 h-3 text-slate-400" /> Client
              </span>
              <span className="font-semibold text-slate-800 truncate block">
                {originalDoc?.client_name || '—'}
              </span>
            </div>
            <div>
              <span className="text-[10px] uppercase text-slate-400 font-semibold block flex items-center gap-1">
                <Hash className="w-3 h-3 text-slate-400" /> Offer ID
              </span>
              <span className="font-mono text-slate-700 font-medium truncate block">
                {originalDoc?.offer_id || '—'}
              </span>
            </div>
            <div>
              <span className="text-[10px] uppercase text-slate-400 font-semibold block flex items-center gap-1">
                <Calendar className="w-3 h-3 text-slate-400" /> Issue Date
              </span>
              <span className="text-slate-700 font-medium truncate block">
                {originalDoc?.offer_date || '—'}
              </span>
            </div>
          </div>
        </div>

        {/* Revised Document Header */}
        <div className="p-4 bg-emerald-50/30 rounded-xl border border-emerald-100">
          <div className="flex items-center space-x-2 text-xs font-bold text-emerald-900 mb-3">
            <FileText className="w-4 h-4 text-emerald-600" />
            <span>Revised Commercial Offer</span>
          </div>
          <div className="grid grid-cols-2 gap-y-2 text-xs">
            <div>
              <span className="text-[10px] uppercase text-slate-400 font-semibold block flex items-center gap-1">
                <Building2 className="w-3 h-3 text-slate-400" /> Vendor
              </span>
              <span className="font-semibold text-slate-800 truncate block">
                {revisedDoc?.vendor_name || '—'}
              </span>
            </div>
            <div>
              <span className="text-[10px] uppercase text-slate-400 font-semibold block flex items-center gap-1">
                <User className="w-3 h-3 text-slate-400" /> Client
              </span>
              <span className="font-semibold text-slate-800 truncate block">
                {revisedDoc?.client_name || '—'}
              </span>
            </div>
            <div>
              <span className="text-[10px] uppercase text-slate-400 font-semibold block flex items-center gap-1">
                <Hash className="w-3 h-3 text-slate-400" /> Offer ID
              </span>
              <span className="font-mono text-slate-700 font-medium truncate block">
                {revisedDoc?.offer_id || '—'}
              </span>
            </div>
            <div>
              <span className="text-[10px] uppercase text-slate-400 font-semibold block flex items-center gap-1">
                <Calendar className="w-3 h-3 text-slate-400" /> Issue Date
              </span>
              <span className="text-slate-700 font-medium truncate block">
                {revisedDoc?.offer_date || '—'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
