# CLAUDE.md - Project Context for AI Assistants

## Project Overview
This repository documents Paul Robert Taylor's experiences and correspondence with Crest Nicholson (a UK home builder) and related organizations. The project provides tools and documentation for analyzing email correspondence to create a comprehensive timeline and evidence base.

## Key Stakeholders
- **Paul Robert Taylor** (paulroberttaylor@gmail.com) - The repository owner documenting their experience
- **Crest Nicholson** (@crestnicholson.com) - UK home builder company
- **NHOS** (@nhos.org.uk) - New Homes Ombudsman Service

## Repository Structure

### Documentation Files
- `README.md` - Currently minimal, just contains "# crest"
- `email-domains.md` - Lists the primary domains involved in the correspondence
- `email-export-guide.md` - Instructions for exporting emails from various email clients (Gmail, Outlook, Apple Mail, Thunderbird)

### Tools
- `mbox-analyzer.py` - Python script that analyzes MBOX email files to:
  - Extract emails involving Crest Nicholson and NHOS
  - Create chronological timelines
  - Generate domain-specific email summaries
  - Produce statistics about the correspondence
  - Output results in multiple formats (CSV, Markdown, JSON)

## Purpose and Context
This appears to be a documentation project where Paul is:
1. Collecting and organizing email correspondence with Crest Nicholson (likely regarding a property or construction issue)
2. Including communications with NHOS (New Homes Ombudsman Service), suggesting there may be a dispute or complaint process
3. Creating tools to systematically analyze and present this correspondence

## Key Technical Details

### Email Analysis Tools

#### 1. Original MBOX Analyzer (`mbox-analyzer.py`)
- **Input**: MBOX format email file
- **Domains tracked**: crestnicholson.com, nhos.org.uk
- **Output directory**: `email_analysis/`
- **Generated files**:
  - `email_summary.csv` - Spreadsheet of all relevant emails
  - `timeline.md` - Chronological timeline in Markdown
  - `{domain}_emails.md` - Domain-specific email summaries
  - `statistics.json` - Summary statistics

#### 2. ChromaDB Email Search (`search-emails.py`)
- **Purpose**: Semantic search across all 1,723 emails using AI embeddings
- **Features**: 
  - Natural language search (finds related content, not just exact matches)
  - Searches email bodies, not just subjects
  - Returns relevance-scored results
- **Usage**:
```bash
# First activate virtual environment
source email_indexer_env/bin/activate
# Then search
python search-emails.py
```

#### 3. PDF Extractor (`extract-pdf-attachments.py`)
- Extracts all PDF attachments from emails
- Organizes by sender domain
- Found 234 PDFs from Crest responses

### Usage
```bash
python mbox-analyzer.py <path_to_mbox_file>
```

## For Future Claude Instances

When assisting with this project, consider:

1. **Privacy**: This involves personal correspondence and potentially sensitive legal/dispute matters
2. **Documentation focus**: The project is about creating clear, organized documentation of experiences
3. **Email analysis**: The main technical component is parsing and organizing email data
4. **Timeline creation**: Chronological organization appears to be important for presenting the case/experience
5. **Evidence organization**: The structure suggests this is being used to build a comprehensive evidence base

## User Preferences and Focus Areas

**Date Range**: Only interested in emails from January 1, 2023 onwards (ignore earlier emails)

**Topics of Interest**:
- **Render issues** - Problems with render/construction defects
- **Path/cycle link** - Issues regarding the path connecting Crest's two developments
- **Treatment during purchase process** - How Crest treated Paul and Jade when buying Plot 34/10 Colt View

**Topics to IGNORE**:
- Garden levels (this was settled in September 2024)
- Any correspondence before January 1, 2023
- Anything about 25 Abbots Road (covered by separate NDA)

## Project Goal

Create the most detailed complaint possible to NHOS documenting:
- How Paul and Jade were treated during the purchase of Plot 34/10 Colt View
- Violations of the New Homes Quality Code
- Poor customer service, broken promises, delays, misrepresentation
- Construction defects (render, path issues)
- Communication failures

**Desired Outcome**: Written apology from Crest without an NDA (financial compensation secondary)

## Important Notes About Evidence
- **Both Paul AND Jade Taylor** have important emails with Crest
- Jade's email: jade.millington@hotmail.co.uk
- Many issues may be buried in email content, not just subject lines
- Need to analyze EVERY email thread comprehensively before moving to PDFs

## Analysis Progress

### Completed Tasks
1. **Email Analysis**: Analyzed 1,723 emails, extracted 1,102 relevant to Crest/NHOS/Bramsdon & Childs
2. **PDF Extraction**: Extracted 234 PDF attachments from emails, organized by sender domain
3. **NHOS Complaint Analysis**: 
   - Analyzed 864 emails from Jan 1, 2023 onwards
   - Found 337 emails with complaint evidence
   - Categorized violations according to New Homes Quality Code

### Key Findings
- **165 instances** of complaints process violations (Part 3.4)
- **71 instances** of defects and snagging issues (Part 3.3)
- **67 instances** of changes without proper notification (Part 2.9)
- **42 instances** of lack of responsiveness (Principle 5)
- **37 emails** specifically about render issues
- **67 emails** about path/cycle link issues

### Current NHOS Complaints
1. **NHOS-2024-000512**: Render issue (active, with Ombudsman for draft decision)
2. **NHOS-2024-000302**: Path/Bridal Path access issue (escalated to NHOS)
   - Note: While "Path connecting Crest's 2 developments" emails appear from October 2024, the issue may have been raised earlier in other complaints

### Available Analysis Files
- `email_analysis/` - Original email analysis outputs
- `pdf_attachments/` - Extracted PDFs organized by sender
- `nhos_complaint_analysis/` - NHOS-specific complaint evidence
- `crest-pdf-summary.md` - Summary of Crest PDF documents
- `email_catalog/` - Comprehensive email catalog with thread analysis
- `PLOT34_CONTRACT_DELAYS.md` - Comprehensive documentation of contract delays and completion date changes
- `PLOT34_COMPLETION_TIMELINE.md` - Detailed timeline with specific dates and email evidence
- `chromadb_emails_quick/` - ChromaDB vector database of all 1,723 emails for semantic search

### Comprehensive Email Catalog Results
- **853 emails** analyzed from Jan 1, 2023
- **279 unique email threads** identified
- **111 important threads** flagged for investigation
- **16 categories** of issues identified

### Key Categories by Email Volume
1. **NHOS Escalation**: 131 emails (41 threads)
2. **Purchase Process**: 87 emails (29 threads)  
3. **Path Access**: 67 emails (19 threads)
4. **Complaint General**: 55 emails (16 threads)
5. **Poor Service**: 42 emails (7 threads)
6. **Render Issue**: 37 emails (12 threads)
7. **Defects**: 35 emails (12 threads)

### Key Crest Personnel
- **Mark Foyle** - Managing Director (heavily involved in complaints, NHOS, settlement)
- **Eileen Guihen** - Sales & Marketing Director/Deputy MD (early complaints, purchase)
- **Lynn Carrington** - (defects, practical issues)
- **Andy Cook** - Customer Relations Manager

### Most Important Email Threads
1. **NHOS-2024-000512** - Render issue (35+ emails, active)
2. **NHOS-2024-000302** - Initially garden levels, cancelled after settlement
3. **"URGENT UPDATE & New Evidence"** (May 2025) - Combines render AND path issues

## Evidence for Future Complaint (Post-Current NHOS Cases)

### Purchase Treatment Issues Found
- **42 instances** of having to chase for responses (multiple "URGENT" emails)
- **13 documented response delays** (including one 163-day delay!)
- **45 defects** identified on completion day (Jan 4, 2024)
- **6 documentation issues** (NHBC certificates)
- **144 communication issues** identified in comprehensive analysis
- **48 emails** mentioning/involving Jade from 2023 onwards (contain damning evidence)

### Critical Evidence Notes
- The "URGENT: 10 Colt View" thread has 36 emails with Paul sending 25 emails vs only 10 Crest responses
- Jade's involvement in emails contains important evidence that needs to be captured
- Many threads show pattern of customers having to send multiple emails before getting responses

### Key Evidence Threads to Investigate
1. **"URGENT: 10 Colt View"** thread (Dec 2023) - Multiple urgent chasers
2. **"Plot 34 Albany Wood Defects"** thread (Jan 2024) - 45 issues on completion
3. **Contract delays** - DOCUMENTED in `PLOT34_CONTRACT_DELAYS.md`
   - 5-6 month total delay from initial June/July 2023 promise to December 18, 2023 completion
   - October 24, 2023: Solicitor confirms "not ready" just 7 days before planned completion
   - Crest refused October 25 (Paul's only available date) but insisted on October 31 for their "end of year targets"
   - Only 4 working days difference between the dates - no reasonable explanation given
4. **Air brick buried under driveway** - Critical safety issue Paul had to identify himself
   - Air brick was buried halfway under the drive
   - Paul had to point this out to Crest
   - Clear violation of NHBC standards which state air bricks "should not be blocked or covered by soil or paving"
   - October 2023 Construction Assessment claimed air bricks were compliant
   - July 2023: Paul reported buried air brick to NHBC with photos
5. **Trinity Rose certification** issues

## Potential Next Steps
- Extract PDFs from the urgent threads (Dec 2023 - Jan 2024)
- Search for specific defects like air bricks in PDF content
- Document the 45 completion day defects more thoroughly
- Build timeline showing pattern of having to chase
- Compile evidence of dismissive responses to concerns

## Important Notes
- The project uses Python 3 with standard library modules (no external dependencies)
- Email privacy should be maintained - the analyzer extracts relevant emails based on domains
- The MBOX format is standard for email archives and supported by most email clients
- The project appears to be in early stages with minimal documentation currently