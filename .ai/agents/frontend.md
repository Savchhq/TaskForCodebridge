# Frontend Agent Guide

## Role & Responsibilities
* Implement the React + Vite + Tailwind CSS interface.
* Create a clean two-PDF upload experience (drag-and-drop or file pickers).
* Build comparison diff views showing:
  * Key summary metrics (total changes, net price difference, delivery date delta).
  * Arithmetic warning banners (highlighting source PDF calculation errors).
  * Line item table with badges for ADDED, REMOVED, MODIFIED, and UNCERTAIN.
  * Source reference drawer or tooltip (page number + verbatim quote).

## Context To Read Before Working
1. `.ai/PROJECT_CONTEXT.md`
2. `.ai/CURRENT_STATE.md`
3. `.ai/agents/frontend.md`
4. The assigned ticket.

## Guidelines
* Keep the UI intuitive, clean, and responsive.
* Clearly differentiate `CONFIRMED` changes (green/blue badges) from `UNCERTAIN` changes (amber/warning badges).
* Handle loading, error, and empty states gracefully.
