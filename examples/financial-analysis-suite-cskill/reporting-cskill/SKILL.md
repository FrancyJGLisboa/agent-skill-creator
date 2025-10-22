---
name: financial-reporting
description: Component skill for generating professional financial reports with charts, analysis summaries, investment recommendations, and automated distribution capabilities.
---

# Financial Reporting

This component skill creates comprehensive financial reports integrating analysis from all suite components.

## When to Use This Component Skill

Use this skill when you need to:
- Generate professional investment reports
- Create portfolio performance summaries
- Produce market analysis documents
- Automate report distribution
- Create presentations for clients/stakeholders
- Document investment recommendations

## Report Types

### Portfolio Reports
- **Performance Summary**: Returns, risk, benchmark comparison
- **Allocation Analysis**: Current vs target allocation
- **Attribution Analysis**: Source of returns
- **Risk Report**: Risk metrics and stress test results

### Market Analysis Reports
- **Market Overview**: Economic and market conditions
- **Sector Analysis**: Industry performance and outlook
- **Technical Analysis Report**: Indicators and signals
- **Opportunity Analysis**: Investment ideas and recommendations

### Client Reports
- **Investment Summary**: Portfolio status and outlook
- **Recommendation Report**: Specific investment suggestions
- **Market Commentary**: Current market perspective
- **Performance Review**: Historical performance analysis

## Report Components

### Executive Summary
- Key findings and highlights
- Performance overview
- Risk assessment
- Actionable recommendations

### Detailed Analysis
- Methodology and approach
- Data sources and validation
- Analytical techniques used
- Assumptions and limitations

### Visualizations
- Portfolio allocation charts
- Performance graphs
- Risk-return scatter plots
- Correlation heatmaps
- Technical analysis charts

### Appendices
- Raw data tables
- Technical calculations
- Methodology details
- Glossary of terms

## Usage Examples

**Portfolio performance report:**
"Generate monthly portfolio performance report for client XYZ"

**Market analysis:**
"Create quarterly market outlook report with technical analysis"

**Investment recommendations:**
"Produce investment recommendation report for tech sector allocation"

**Client presentation:**
"Create investor presentation with portfolio summary and market outlook"

## Scripts Available

- `scripts/report_generator.py` - Main report generation engine
- `scripts/chart_creator.py` - Chart and visualization creation
- `scripts/template_engine.py` - Template processing
- `scripts/pdf_exporter.py` - PDF generation and formatting
- `scripts/email_sender.py` - Automated report distribution

## Templates

### Report Templates
- `templates/portfolio_report.html` - Standard portfolio report
- `templates/market_analysis.html` - Market analysis report
- `templates/client_summary.html` - Client-facing summary
- `templates/investment_presentation.pptx` - Investment presentation

### Customization
- Company branding and logos
- Custom color schemes
- Flexible layout options
- Multi-language support

## Integration

This component skill integrates with:
- **Data Acquisition**: Provides data for analysis
- **Technical Analysis**: Supplies technical indicators and signals
- **Portfolio Optimizer**: Delivers optimization results and recommendations

## Configuration

Configuration in `config/reporting.json`:
```json
{
  "reporting": {
    "default_template": "portfolio_report",
    "company": {
      "name": "Your Company",
      "logo": "assets/logo.png",
      "brand_color": "#1f77b4"
    },
    "output": {
      "format": ["pdf", "html"],
      "include_raw_data": false,
      "chart_style": "seaborn"
    },
    "distribution": {
      "auto_send": false,
      "email_template": "templates/email.html"
    }
  }
}
```

## Output Formats

- **PDF**: Professional printable reports
- **HTML**: Interactive web reports
- **PowerPoint**: Presentation slides
- **Excel**: Data tables and calculations
- **Word**: Document format reports

## Automation Features

- **Scheduled Reports**: Automated periodic report generation
- **Alert Reports**: Trigger-based reports for market events
- **Distribution Lists**: Automatic email delivery to stakeholders
- **Archiving**: Report storage and retrieval system

## Quality Assurance

- Data validation and verification
- Calculation accuracy checks
- Consistency validation across sections
- Review and approval workflows
- Version control and audit trail

This is a **Component Skill** within the Financial Analysis Suite - specialized in professional report generation and communication.