# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ALCOA+ Data Integrity Framework Dashboard** – A single-file HTML application for Eli Lilly operations teams to understand and track compliance with ALCOA+ (Attributable, Legible, Contemporaneous, Original, Accurate, Complete, Consistent, Enduring, Available) data governance principles.

This is a **client-side only** application (no backend, no build process) designed for:
- Training and reference material for pharmaceutical operations staff
- Interactive compliance dashboard with test data scenarios
- Regulatory compliance documentation

## Running the Application

**Local Development:**
```bash
# Start a simple HTTP server from the project directory
python3 -m http.server 8000

# Access in browser
http://localhost:8000/ALCOA_Plus_Guide.html
```

The file can also be opened directly in a browser (`file://` protocol) but the HTTP server approach is recommended for better security and consistency.

**Deployment:**
- The single HTML file can be deployed to any web server (Nginx, Apache, AWS S3, Netlify, etc.)
- No special server configuration needed
- Suggested path: `/alcoa-guide/ALCOA_Plus_Guide.html` or similar

## Architecture & Code Structure

**Single File Application:**
```
ALCOA_Plus_Guide.html
├── Header (branding, title)
├── Dashboard Section
│   ├── Dropdowns (Department, Timeline, Process)
│   ├── Compliance Metrics (dynamic)
│   └── Test Data Display
├── Principle Cards (A, L, C, O, A, +Complete, +Consistent, +Enduring, +Available)
│   ├── Interactive expand/collapse
│   └── Checklists (persisted via localStorage)
├── Compliance Standards Reference
├── Key Takeaways
└── Footer

Styles: <style> tag (11 KiB)
Scripts: <script> tag (3.5 KiB)
```

**Key Components:**

1. **Inline CSS** – Complete styling with:
   - Responsive grid layouts
   - Print-friendly styles
   - Mobile optimization
   - Theme colors: #667eea (primary), #1e3c72 (dark blue), #764ba2 (accent)

2. **Test Data Object** – JavaScript object containing realistic pharmaceutical test scenarios:
   - `testData` structured as: `[department][timeline][process_type] = {metrics, data}`
   - Metrics: `overallCompliance`, `attributableScore`, `integrityScore`, `findingsCount`
   - Data: Array of label/value pairs for realistic ALCOA+ contexts

3. **Dashboard Logic** – `updateDashboard()` function:
   - Reads 3 dropdown values (department, timeline, process)
   - Looks up test data
   - Updates metric cards with color-coded status (green/yellow/red)
   - Renders test data table

4. **Persistence** – localStorage saves checkbox states:
   - Each checklist item stored with key `checkbox-{id}`
   - Restored on page load
   - Allows teams to track their compliance review progress

5. **Interactive Cards** – Principle cards expand/collapse:
   - Click expand button to show requirements & checklist
   - `toggleCard()`, `expandAll()`, `collapseAll()` functions
   - CSS class `.active` controls visibility

## Common Tasks

**Add New Test Data Scenario:**
1. Edit the `testData` object in the `<script>` section
2. Follow the existing structure: add `[department][timeline][process]` path with metrics and data array
3. Test by selecting from dropdowns to verify data appears

**Update ALCOA+ Principles Content:**
1. Locate the principle card in the grid (search for "Attributable", "Legible", etc.)
2. Edit the `principle-definition` div for the summary
3. Update the `principle-details` section with updated requirements or checklist items

**Modify Styling:**
1. Edit the `<style>` tag
2. Key classes: `.dashboard-section`, `.principle-card`, `.metric-card`, `.compliance-metrics`
3. Color palette in CSS variables would improve maintainability (future enhancement)

**Test on Mobile:**
- Open browser DevTools → Toggle Device Toolbar
- The responsive grid (`grid-template-columns: repeat(auto-fit, minmax(...))`) adapts to narrow screens

**Print Compliance Report:**
- Ctrl+P (or Cmd+P on Mac) to open print dialog
- CSS includes `@media print` rules to optimize layout
- Checklists can be printed with user's selections

## Browser Compatibility

- Modern browsers: Chrome, Firefox, Safari, Edge (ES6+ support required)
- localStorage support required for checkbox persistence (all modern browsers)
- No polyfills needed for this project

## Regulatory Context

**Applies to:** FDA 21 CFR Part 11, ICH Q14, GAMP 5, ISO/IEC 27001, EU GMP Annex 11

This guide covers all 8 ALCOA+ principles with pharmaceutical operation-specific examples and compliance checklists. Test data reflects realistic scenarios from Manufacturing, QA, Laboratory, Data Management, Environmental Monitoring, and Stability Testing operations.

## Future Enhancements

If expanding this project:
- **Export functionality** – Save compliance reviews as PDF or CSV
- **Backend integration** – Connect to actual compliance database instead of static test data
- **User roles** – Different views for operators, supervisors, quality managers
- **Multi-language support** – Add translations for international teams
- **Dark mode toggle** – Accessibility improvement
- **Search/filter** – Allow searching through principles and requirements
