# CLAUDE.md - DC Council Vote Track

## Project Overview

**DC Council Vote Track** is a civic transparency tool that aggregates voting records from the DC Council's Legislative Information Management System (LIMS) API and supplementary PDF documents. It transforms fragmented legislative data into a unified, analyzable format enabling citizens to hold their elected representatives accountable.

### Mission Statement
To democratize access to DC Council voting records, making it easy for residents to understand how their elected officials vote on issues that matter to them.

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                │
├─────────────────────────────────────────────────────────────────────┤
│  LIMS API (Primary)              │  PDF Documents (Secondary)       │
│  • Bill metadata                 │  • Amendment votes               │
│  • Council member info           │  • Committee of the Whole votes  │
│  • Vote results (when available) │  • Roll call records             │
└───────────────┬─────────────────────────────────┬───────────────────┘
                │                                 │
                ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      dc_council.py                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ API Integration │  │ PDF/OCR Engine  │  │ Data Normalization  │  │
│  │ • Rate limiting │  │ • pdf2image     │  │ • Name matching     │  │
│  │ • Auth handling │  │ • pytesseract   │  │ • Vote consolidation│  │
│  │ • Checkpointing │  │ • Pixel analysis│  │ • CSV generation    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
└───────────────┬─────────────────────────────────┬───────────────────┘
                │                                 │
                ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA OUTPUTS                                   │
├─────────────────────────────────────────────────────────────────────┤
│  Pickle Files (Intermediate)     │  CSV Output (Final)              │
│  data/<type>_<period>/*.pkl      │  outputListOfVotes_<t>_<p>.csv   │
│  • Full Bill objects             │  • Flattened records             │
│  • Enables restart               │  • One row per action            │
│  • Preserves all data            │  • Ready for analysis            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

```bash
# System dependencies
sudo apt-get install tesseract-ocr poppler-utils

# Python dependencies
pip install requests pdf2image pytesseract
```

### Obtain API Token
1. Register at https://lims.dccouncil.us/developerRegistration
2. Receive your developer API token via email

### Run Data Collection

```bash
# Syntax: python3 dc_council.py <token> <councilPeriodId> <legislationType>

# Example: Collect all bills from Council Period 24
python3 dc_council.py YOUR_TOKEN_HERE 24 1

# Council Period Reference:
# Period 20: 2013-2014
# Period 21: 2015-2016
# Period 22: 2017-2018
# Period 23: 2019-2020
# Period 24: 2021-2022
# Period 25: 2023-2024
# Period 26: 2025-2026 (current)
```

---

## Codebase Structure

```
dc-council-vote-track/
├── dc_council.py                    # Main data collection script (546 lines)
├── README.md                        # User-facing documentation
├── claude.md                        # AI assistant guide (this file)
├── test.png                         # PDF processing visualization
├── outputListOfVotes_1_23.csv       # Sample output (Council Period 23)
└── data/                            # Generated during execution
    └── <type>_<councilPeriodId>/    # e.g., 1_24/
        ├── B24-0001.pkl             # Serialized Bill objects
        ├── B24-0002.pkl
        └── ...
```

---

## Key Components

### Bill Class (`dc_council.py`)

The central data structure representing a piece of legislation.

```python
class Bill:
    id                  # Legislation number (e.g., "B24-0760")
    data                # Full bill details from LIMS API
    councilMembers      # List of council members for the period
    newActions          # Actions parsed from PDFs

    # Key Methods:
    getLegislationDetails()   # Fetch bill details from LIMS
    processActions()          # Process all actions including PDFs
    getActionResults()        # Extract votes from single action/PDF
    reformatVotes()           # Normalize council member names
```

### Core Functions

| Function | Purpose |
|----------|---------|
| `callAPI(endpoint, token, method)` | LIMS API wrapper with rate limiting |
| `getCouncilMembers(token, periodId)` | Fetch council member roster |
| `getBulkData(token, type, periodId)` | Retrieve all legislation metadata |
| `processListOfBills(listOfBills, ...)` | Main processing loop with checkpointing |
| `readPDF(path)` | OCR-based vote extraction from PDFs |
| `outputListOfBillsResults(...)` | Generate final CSV output |

### PDF Vote Extraction Algorithm

The `readPDF()` function performs sophisticated vote extraction from scanned documents:

1. **Detection**: Search for "RollCall.html" text indicating vote page
2. **Column Location**: Find X-coordinates of "Yes", "No", "Present", "Absent" headers
3. **Name Detection**: Locate council member names via OCR
4. **Vote Reading**: Analyze pixel RGB values at intersection points
   - Pixel sum < 700 (dark blue dot) = vote cast
   - Pixel sum >= 700 (white/blank) = no vote
5. **Name Normalization**: Match extracted names to official roster

---

## Data Schema

### Output CSV Columns (61 total)

**Bill Metadata (31 columns):**
- `legislationNumber`, `legislationId`, `title`, `shortDescription`
- `status`, `category`, `subCategory`
- `introducers`, `coSponsors`, `atTheRequestOf`
- `introductionDate`, `committeeReferralDate`, `committeesReferredTo`
- `mayoralReview`, `congressionalReview`, and more...

**Action Details (14 columns):**
- `action`, `actionDate`, `attachment`, `attachmentType`
- `voteResult`, `voteType`, `voteProcessingType`
- `lims_bill_code`, `lims_meeting_id`, `pdf_path`, `pdf_extracted_votes`

**Individual Council Member Votes (16 columns):**
- One column per council member
- Values: `"Yes"`, `"No"`, `"Present"`, `"Absent"`, `"Unknown"`

### Vote Processing Types

| Type | Meaning |
|------|---------|
| `LIMSProvided` | Vote data directly from LIMS API |
| `decodeFromPDFSuccess` | Successfully extracted from PDF via OCR |
| `decodeFromPDFNoResult` | PDF analyzed but no votes found |
| `decodeFromPDFMultipleVote` | Multiple votes extracted from single PDF |
| `decodeFromPDFAttempt` | PDF processing attempted |
| `noAttachment` | No PDF attachment to process |

---

## API Reference

### LIMS API

**Base URL:** `https://lims.dccouncil.us/api/v2/PublicData/`

**Authentication:** Bearer token in Authorization header

**Rate Limiting:** 0.3 second minimum delay between requests (enforced in code)

**Key Endpoints:**
- `GET /members/{councilPeriodId}` - Council member roster
- `POST /BulkData/{categoryId}/{councilPeriodId}` - All legislation
- `GET /LegislationDetails/{legislationNumber}` - Single bill details

**Documentation:** https://lims.dccouncil.us/api/help/index.html

---

## Development Guidelines

### When Modifying dc_council.py

1. **Preserve Checkpointing**: The script uses pickle files and CSV tracking for fault tolerance. Ensure any changes maintain this capability.

2. **Respect Rate Limits**: The LIMS API has rate limits. The 0.3s delay in `callAPI()` is intentional.

3. **Handle PDF Variations**: The OCR algorithm is calibrated for specific PDF layouts. Test thoroughly with new council periods.

4. **Name Matching**: Council member names vary between sources. The `reformatVotes()` function handles normalization.

### Code Style

- Python 3 compatible (with Python 2 fallback for pickle)
- Use descriptive variable names
- Add comments for complex logic, especially in PDF processing
- Maintain existing error handling patterns

### Testing

```bash
# Test with a single council period
python3 dc_council.py $TOKEN 23 1

# Verify output
head -5 outputListOfVotes_1_23.csv

# Check for processing errors in pickled data
python3 -c "import pickle; b = pickle.load(open('data/1_23/B23-0001.pkl', 'rb')); print(b.data)"
```

---

## Common Issues & Solutions

### Issue: OCR Fails to Detect Votes

**Symptoms:** `voteProcessingType` shows `decodeFromPDFNoResult` for documents with votes

**Solutions:**
1. Check PDF quality and resolution
2. Verify Tesseract is installed: `tesseract --version`
3. Adjust pixel threshold in `readPDF()` (currently 700)
4. Review `test.png` for visual debugging

### Issue: API Rate Limit Errors

**Symptoms:** HTTP 429 or connection timeouts

**Solutions:**
1. Increase delay in `callAPI()` from 0.3s to 0.5s+
2. Add exponential backoff for retries
3. Run during off-peak hours

### Issue: Council Member Name Mismatch

**Symptoms:** Votes attributed to wrong members or showing as "Unknown"

**Solutions:**
1. Check `reformatVotes()` mapping
2. Add new name variations to the matching logic
3. Verify council roster for the period

### Issue: Script Crashes Mid-Processing

**Solutions:**
1. Simply re-run the script - it will resume from last checkpoint
2. Check pickle files for corruption
3. Review the progress CSV for status markers

---

## Future Development Areas

### Near-term Enhancements
- [ ] Add support for all legislation types (Resolutions, Ceremonial, etc.)
- [ ] Implement parallel API requests with proper rate limiting
- [ ] Add logging with configurable verbosity
- [ ] Create data validation and quality checks

### Medium-term Goals
- [ ] Database backend (PostgreSQL/SQLite) for better querying
- [ ] Automated daily updates via cron/scheduler
- [ ] REST API for programmatic access
- [ ] Historical trend analysis tools

### Long-term Vision
- [ ] Web-based scorecard interface
- [ ] User accounts with personalized tracking
- [ ] Category/issue tagging with ML
- [ ] Comparison tools and visualizations
- [ ] Mobile application

---

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch from `main`
3. Make changes with clear commit messages
4. Test with at least one council period
5. Update documentation if needed
6. Submit PR with description of changes

### Commit Message Format

```
<type>: <short description>

[optional body with more details]

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- refactor: Code restructuring
- test: Test additions/changes
```

---

## Environment Variables

Consider setting these for convenience:

```bash
export DC_LIMS_TOKEN="your_api_token_here"
export DC_COUNCIL_PERIOD="26"  # Current period
```

---

## Related Resources

- **DC Council Website:** https://dccouncil.us/
- **LIMS Portal:** https://lims.dccouncil.us/
- **LIMS API Documentation:** https://lims.dccouncil.us/api/help/index.html
- **Open Data DC:** https://opendata.dc.gov/

---

## License & Acknowledgments

This project aggregates publicly available government data to promote civic transparency. The LIMS API and all legislative data are provided by the Council of the District of Columbia.

---

## Contact & Support

For issues with this tool, please:
1. Check the Common Issues section above
2. Review existing GitHub issues
3. Open a new issue with:
   - Python version
   - Council period and legislation type
   - Error messages and logs
   - Steps to reproduce
