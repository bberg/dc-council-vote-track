# DC Council Vote Track - Public Scorecard Website Roadmap

## Vision Statement

**MyDCVote** - A civic transparency platform that empowers DC residents to understand how their elected council members vote on issues that matter to them personally. Users describe their values and priorities in plain language, and AI analyzes legislation to predict how the user would vote, then scores each council member against the user's predicted positions.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Database Schema](#database-schema)
4. [Data Pipeline](#data-pipeline)
5. [AI Bill Analysis Engine](#ai-bill-analysis-engine)
6. [User Value Matching System](#user-value-matching-system)
7. [Frontend Application](#frontend-application)
8. [API Specification](#api-specification)
9. [Daily Update System](#daily-update-system)
10. [Implementation Phases](#implementation-phases)
11. [Technology Stack](#technology-stack)
12. [Security & Privacy](#security--privacy)
13. [Cost Estimates](#cost-estimates)
14. [Success Metrics](#success-metrics)

---

## Executive Summary

### The Problem

DC residents have limited visibility into how their council members vote. The existing LIMS system is designed for legislative professionals, not everyday citizens. Vote records are fragmented across API responses and PDF documents, making it nearly impossible for residents to:

- Understand what bills actually mean in plain language
- Know how their representatives voted on issues they care about
- Compare council members' voting records against their personal values
- Track alignment over time

### The Solution

A public web application that:

1. **Aggregates** all DC Council voting data into a unified database
2. **Analyzes** each bill using AI to extract topics, implications, and plain-language summaries
3. **Matches** users' stated values to relevant legislation
4. **Predicts** how the user would vote on each bill based on their values
5. **Scores** each council member against the user's predicted votes
6. **Updates** daily with new legislation and votes

### Key Innovation: Value-Based Scoring

Unlike traditional scorecards that use predefined issue categories, our system lets users describe what they care about in their own words:

> "I care about affordable housing, protecting small businesses, environmental sustainability, and keeping taxes low for middle-class families."

The AI then:
1. Analyzes all bills for relevance to these values
2. Predicts how someone with these values would vote
3. Calculates alignment scores for each council member

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  Value Input    │  │  Scorecard      │  │  Bill Explorer              │  │
│  │  • Free text    │  │  • Rankings     │  │  • Search/filter            │  │
│  │  • Categories   │  │  • Comparisons  │  │  • AI summaries             │  │
│  │  • Sliders      │  │  • Trends       │  │  • Vote history             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WEB APPLICATION                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Next.js Frontend (React + TypeScript)                              │    │
│  │  • Server-side rendering for SEO                                    │    │
│  │  • Real-time scorecard calculations                                 │    │
│  │  • Responsive design (mobile-first)                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  API Layer (Next.js API Routes / FastAPI)                           │    │
│  │  • RESTful endpoints                                                │    │
│  │  • Rate limiting                                                    │    │
│  │  • Caching layer (Redis)                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CORE SERVICES                                   │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────┐    │
│  │  Bill Analysis    │  │  Value Matching   │  │  Score Calculator     │    │
│  │  Service          │  │  Service          │  │  Service              │    │
│  │  ──────────────   │  │  ──────────────   │  │  ──────────────       │    │
│  │  • Topic extract  │  │  • NLP parsing    │  │  • Alignment calc     │    │
│  │  • Summarization  │  │  • Embedding gen  │  │  • Weighted scoring   │    │
│  │  • Impact assess  │  │  • Similarity     │  │  • Historical trends  │    │
│  │  • Vote predict   │  │  • Vote inference │  │  • Comparisons        │    │
│  └───────────────────┘  └───────────────────┘  └───────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AI INFRASTRUCTURE                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Claude API (Anthropic)                                             │    │
│  │  • Bill summarization and plain-language explanation                │    │
│  │  • Topic/category extraction                                        │    │
│  │  • Value-to-vote inference                                          │    │
│  │  • Impact assessment                                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Embedding Service (OpenAI/Voyage/Local)                            │    │
│  │  • Bill text embeddings                                             │    │
│  │  • User value embeddings                                            │    │
│  │  • Semantic similarity search                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                      │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────┐    │
│  │  PostgreSQL       │  │  Redis            │  │  Vector Store         │    │
│  │  ──────────────   │  │  ──────────────   │  │  ──────────────       │    │
│  │  • Bills          │  │  • Session cache  │  │  • Bill embeddings    │    │
│  │  • Votes          │  │  • API cache      │  │  • Value embeddings   │    │
│  │  • Members        │  │  • Rate limits    │  │  • Similarity index   │    │
│  │  • Users          │  │  • Job queues     │  │                       │    │
│  │  • Scores         │  │                   │  │                       │    │
│  └───────────────────┘  └───────────────────┘  └───────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA INGESTION                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Daily Sync Worker (Cron/GitHub Actions)                            │    │
│  │  • LIMS API polling                                                 │    │
│  │  • PDF vote extraction (OCR)                                        │    │
│  │  • Delta detection                                                  │    │
│  │  • AI analysis trigger                                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  LIMS API (DC Council)                                              │    │
│  │  • Bills, votes, members                                            │    │
│  │  • Rate limited (0.3s delay)                                        │    │
│  │  • Bearer token auth                                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Core Tables

```sql
-- ============================================
-- LEGISLATION
-- ============================================

CREATE TABLE council_periods (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,           -- e.g., "Council Period 26"
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE
);

CREATE TABLE council_members (
    id SERIAL PRIMARY KEY,
    lims_id VARCHAR(50) UNIQUE,
    name VARCHAR(100) NOT NULL,
    name_variations JSONB,               -- ["Phil Mendelson", "Chairman Mendelson"]
    ward VARCHAR(20),                    -- "Ward 1", "At-Large", "Chairman"
    party VARCHAR(50),
    photo_url TEXT,
    bio TEXT,
    contact_info JSONB,
    social_media JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE member_terms (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES council_members(id),
    council_period_id INTEGER REFERENCES council_periods(id),
    position VARCHAR(100),               -- "Councilmember", "Chairman"
    committees JSONB,
    UNIQUE(member_id, council_period_id)
);

CREATE TABLE bills (
    id SERIAL PRIMARY KEY,
    legislation_number VARCHAR(20) UNIQUE NOT NULL,  -- "B26-0001"
    legislation_id VARCHAR(50),
    council_period_id INTEGER REFERENCES council_periods(id),

    -- Basic Info
    title TEXT NOT NULL,
    short_title VARCHAR(500),
    short_description TEXT,
    full_text TEXT,

    -- Classification
    category VARCHAR(100),
    sub_category VARCHAR(100),
    legislation_type VARCHAR(50),        -- "Bill", "Resolution", "Ceremonial"

    -- Sponsors
    introducers JSONB,                   -- Array of member names/IDs
    co_sponsors JSONB,
    at_request_of VARCHAR(200),

    -- Dates
    introduction_date DATE,
    committee_referral_date DATE,
    final_vote_date DATE,
    enacted_date DATE,
    effective_date DATE,

    -- Status
    status VARCHAR(100),
    current_stage VARCHAR(100),

    -- Committee Info
    committees_referred_to JSONB,
    committee_hearing_date DATE,
    committee_markup_date DATE,

    -- External References
    lims_url TEXT,
    legislation_document_url TEXT,
    other_documents JSONB,
    linked_legislation JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_synced_at TIMESTAMP
);

CREATE TABLE bill_actions (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES bills(id),

    action_type VARCHAR(100) NOT NULL,   -- "Introduction", "Committee Vote", "Final Reading"
    action_date DATE,
    description TEXT,

    -- Vote Information
    vote_result VARCHAR(50),             -- "Approved", "Disapproved", "Withdrawn"
    vote_type VARCHAR(50),               -- "Voice Vote", "Roll Call"

    -- Source Tracking
    source_type VARCHAR(50),             -- "LIMSProvided", "PDFExtracted"
    attachment_url TEXT,
    pdf_path TEXT,

    -- Metadata
    lims_meeting_id VARCHAR(50),
    video_link TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    action_id INTEGER REFERENCES bill_actions(id),
    member_id INTEGER REFERENCES council_members(id),
    bill_id INTEGER REFERENCES bills(id),

    vote VARCHAR(20) NOT NULL,           -- "Yes", "No", "Present", "Absent"

    -- Denormalized for query performance
    council_period_id INTEGER REFERENCES council_periods(id),
    action_date DATE,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(action_id, member_id)
);

-- ============================================
-- AI ANALYSIS
-- ============================================

CREATE TABLE bill_analysis (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES bills(id) UNIQUE,

    -- AI-Generated Content
    plain_language_summary TEXT,
    detailed_summary TEXT,
    key_provisions JSONB,                -- Array of provision summaries

    -- Topic Classification
    primary_topics JSONB,                -- ["Housing", "Budget"]
    secondary_topics JSONB,
    topic_scores JSONB,                  -- {"Housing": 0.95, "Budget": 0.72}

    -- Impact Assessment
    affected_groups JSONB,               -- ["Renters", "Small Businesses"]
    fiscal_impact TEXT,
    neighborhood_impact JSONB,

    -- Political Analysis
    progressive_score DECIMAL(3,2),      -- -1.0 to 1.0 scale
    controversy_score DECIMAL(3,2),      -- 0.0 to 1.0
    bipartisan_indicator BOOLEAN,

    -- Embeddings (stored in vector DB, referenced here)
    embedding_id VARCHAR(100),

    -- Metadata
    model_version VARCHAR(50),
    analyzed_at TIMESTAMP DEFAULT NOW(),
    confidence_score DECIMAL(3,2)
);

CREATE TABLE topic_taxonomy (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES topic_taxonomy(id),
    description TEXT,
    keywords JSONB,                      -- Keywords that indicate this topic
    embedding_id VARCHAR(100)
);

-- Seed topics
INSERT INTO topic_taxonomy (name, description, keywords) VALUES
('Housing', 'Legislation affecting housing policy', '["housing", "rent", "tenant", "landlord", "affordable", "eviction"]'),
('Public Safety', 'Crime, policing, emergency services', '["police", "crime", "safety", "emergency", "fire", "ems"]'),
('Education', 'Schools, education funding, students', '["school", "education", "student", "teacher", "DCPS"]'),
('Transportation', 'Transit, roads, bikes, pedestrians', '["metro", "bus", "bike", "pedestrian", "traffic", "parking"]'),
('Environment', 'Climate, sustainability, green initiatives', '["climate", "environment", "green", "sustainable", "pollution"]'),
('Budget & Taxes', 'Fiscal policy, taxation, spending', '["budget", "tax", "spending", "fiscal", "revenue"]'),
('Healthcare', 'Health services, public health', '["health", "hospital", "medical", "mental health"]'),
('Economic Development', 'Business, jobs, development', '["business", "jobs", "economic", "development", "employment"]'),
('Civil Rights', 'Equality, discrimination, rights', '["rights", "discrimination", "equality", "civil rights"]'),
('Government Operations', 'Internal government functions', '["government", "procurement", "administration"]');

-- ============================================
-- USER DATA
-- ============================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,

    -- Authentication (optional - can be anonymous)
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),

    -- Anonymous tracking
    anonymous_id UUID UNIQUE DEFAULT gen_random_uuid(),

    -- Profile
    display_name VARCHAR(100),
    ward VARCHAR(20),
    neighborhood VARCHAR(100),

    -- Preferences
    email_notifications BOOLEAN DEFAULT FALSE,
    notification_frequency VARCHAR(20) DEFAULT 'weekly',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP
);

CREATE TABLE user_values (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),

    -- Free-text values statement
    values_statement TEXT,               -- User's own words

    -- Parsed/structured values
    parsed_topics JSONB,                 -- AI-extracted topics from statement
    topic_weights JSONB,                 -- {"Housing": 0.8, "Environment": 0.6}

    -- Embedding for similarity matching
    embedding_id VARCHAR(100),

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_value_topics (
    id SERIAL PRIMARY KEY,
    user_value_id INTEGER REFERENCES user_values(id),
    topic_id INTEGER REFERENCES topic_taxonomy(id),

    importance DECIMAL(3,2),             -- 0.0 to 1.0
    stance VARCHAR(20),                  -- "support", "oppose", "neutral"

    UNIQUE(user_value_id, topic_id)
);

CREATE TABLE user_bill_predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    user_value_id INTEGER REFERENCES user_values(id),
    bill_id INTEGER REFERENCES bills(id),

    -- AI Prediction
    predicted_vote VARCHAR(20),          -- "Yes", "No", "Abstain"
    confidence DECIMAL(3,2),
    reasoning TEXT,

    -- Relevance
    relevance_score DECIMAL(3,2),        -- How relevant is this bill to user's values
    matching_topics JSONB,

    -- User Override (if they disagree with prediction)
    user_override_vote VARCHAR(20),
    override_reason TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_value_id, bill_id)
);

-- ============================================
-- SCORECARDS
-- ============================================

CREATE TABLE user_scorecards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    user_value_id INTEGER REFERENCES user_values(id),
    member_id INTEGER REFERENCES council_members(id),
    council_period_id INTEGER REFERENCES council_periods(id),

    -- Scores
    alignment_score DECIMAL(5,2),        -- 0-100 percentage
    total_relevant_votes INTEGER,
    aligned_votes INTEGER,
    opposed_votes INTEGER,

    -- Breakdown by topic
    topic_scores JSONB,                  -- {"Housing": 85.5, "Environment": 72.0}

    -- Trend
    trend_direction VARCHAR(20),         -- "improving", "declining", "stable"
    trend_magnitude DECIMAL(3,2),

    calculated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_value_id, member_id, council_period_id)
);

CREATE TABLE scorecard_details (
    id SERIAL PRIMARY KEY,
    scorecard_id INTEGER REFERENCES user_scorecards(id),
    bill_id INTEGER REFERENCES bills(id),
    vote_id INTEGER REFERENCES votes(id),

    user_predicted_vote VARCHAR(20),
    member_actual_vote VARCHAR(20),
    is_aligned BOOLEAN,
    relevance_weight DECIMAL(3,2),

    contribution_to_score DECIMAL(5,2)
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_bills_council_period ON bills(council_period_id);
CREATE INDEX idx_bills_status ON bills(status);
CREATE INDEX idx_bills_introduction_date ON bills(introduction_date);
CREATE INDEX idx_votes_member ON votes(member_id);
CREATE INDEX idx_votes_bill ON votes(bill_id);
CREATE INDEX idx_votes_action_date ON votes(action_date);
CREATE INDEX idx_user_values_user ON user_values(user_id);
CREATE INDEX idx_user_scorecards_user ON user_scorecards(user_id);
CREATE INDEX idx_user_scorecards_member ON user_scorecards(member_id);
CREATE INDEX idx_bill_analysis_topics ON bill_analysis USING GIN(primary_topics);
```

### Vector Store Schema (Pinecone/pgvector)

```python
# Bill Embeddings
{
    "id": "bill_B26-0001",
    "values": [0.123, -0.456, ...],  # 1536-dim embedding
    "metadata": {
        "bill_id": 1,
        "legislation_number": "B26-0001",
        "title": "Housing Affordability Act",
        "primary_topics": ["Housing", "Budget"],
        "council_period": 26,
        "introduction_date": "2025-01-15"
    }
}

# User Value Embeddings
{
    "id": "user_value_123",
    "values": [0.789, -0.012, ...],
    "metadata": {
        "user_id": 456,
        "topics": ["Housing", "Environment"],
        "created_at": "2025-01-20"
    }
}
```

---

## Data Pipeline

### Daily Sync Process

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DAILY SYNC WORKFLOW                               │
│                    (Runs at 2:00 AM EST)                             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: FETCH NEW DATA FROM LIMS                                    │
│ ─────────────────────────────────────────────────────────────────── │
│ • Call BulkData endpoint for current council period                 │
│ • Compare against existing bills in database                        │
│ • Identify new bills and updated bills                              │
│ • Rate limit: 0.3s between requests                                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: FETCH BILL DETAILS                                          │
│ ─────────────────────────────────────────────────────────────────── │
│ • For each new/updated bill:                                        │
│   - Fetch LegislationDetails from LIMS                              │
│   - Download any new PDF attachments                                │
│   - Extract votes from PDFs using OCR                               │
│   - Store raw data in staging tables                                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: PROCESS AND NORMALIZE                                       │
│ ─────────────────────────────────────────────────────────────────── │
│ • Normalize council member names                                    │
│ • Deduplicate votes (API vs PDF sources)                            │
│ • Link actions to bills                                             │
│ • Update main tables                                                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: AI ANALYSIS (For new bills only)                            │
│ ─────────────────────────────────────────────────────────────────── │
│ • Generate plain-language summary                                   │
│ • Extract topics and categories                                     │
│ • Assess impact and affected groups                                 │
│ • Generate embeddings                                               │
│ • Store in bill_analysis table                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: RECALCULATE USER SCORECARDS                                 │
│ ─────────────────────────────────────────────────────────────────── │
│ • Identify users affected by new votes                              │
│ • Generate vote predictions for new bills                           │
│ • Recalculate alignment scores                                      │
│ • Update scorecard tables                                           │
│ • Queue notification emails                                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: CLEANUP AND REPORTING                                       │
│ ─────────────────────────────────────────────────────────────────── │
│ • Archive old staging data                                          │
│ • Generate sync report                                              │
│ • Log any errors or anomalies                                       │
│ • Send admin notification                                           │
└─────────────────────────────────────────────────────────────────────┘
```

### Sync Worker Implementation

```python
# sync_worker.py

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import logging

from services.lims_client import LIMSClient
from services.pdf_extractor import PDFVoteExtractor
from services.ai_analyzer import BillAnalyzer
from services.scorecard_calculator import ScorecardCalculator
from database import Database

logger = logging.getLogger(__name__)

class DailySyncWorker:
    def __init__(self, config: Dict):
        self.lims = LIMSClient(config['lims_token'])
        self.pdf_extractor = PDFVoteExtractor()
        self.analyzer = BillAnalyzer(config['anthropic_api_key'])
        self.scorer = ScorecardCalculator()
        self.db = Database(config['database_url'])

    async def run_sync(self):
        """Main sync entry point"""
        sync_id = await self.db.create_sync_log()

        try:
            # Step 1: Fetch new data
            new_bills, updated_bills = await self.fetch_lims_updates()
            logger.info(f"Found {len(new_bills)} new, {len(updated_bills)} updated bills")

            # Step 2: Process bills
            for bill in new_bills + updated_bills:
                await self.process_bill(bill)

            # Step 3: AI Analysis for new bills
            for bill in new_bills:
                await self.analyze_bill(bill)

            # Step 4: Recalculate scorecards
            affected_users = await self.get_affected_users(new_bills + updated_bills)
            for user in affected_users:
                await self.recalculate_scorecard(user)

            # Step 5: Complete
            await self.db.complete_sync_log(sync_id, success=True)

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            await self.db.complete_sync_log(sync_id, success=False, error=str(e))
            raise

    async def fetch_lims_updates(self) -> tuple[List, List]:
        """Fetch updates from LIMS API"""
        current_period = await self.db.get_current_council_period()

        # Get all bills from LIMS
        lims_bills = await self.lims.get_bulk_data(
            category_id=1,  # Bills
            council_period_id=current_period.id
        )

        # Compare with database
        existing = await self.db.get_bill_sync_status()

        new_bills = []
        updated_bills = []

        for bill in lims_bills:
            if bill['legislationNumber'] not in existing:
                new_bills.append(bill)
            elif bill['lastModified'] > existing[bill['legislationNumber']]:
                updated_bills.append(bill)

        return new_bills, updated_bills

    async def process_bill(self, bill_data: Dict):
        """Process a single bill"""
        # Fetch full details
        details = await self.lims.get_legislation_details(
            bill_data['legislationNumber']
        )

        # Process each action
        for action in details.get('actions', []):
            # Check for PDF attachments with votes
            if action.get('attachment') and 'vote' in action.get('action', '').lower():
                pdf_path = await self.lims.download_attachment(action['attachment'])
                votes = await self.pdf_extractor.extract_votes(pdf_path)
                action['extracted_votes'] = votes

        # Save to database
        await self.db.upsert_bill(details)

    async def analyze_bill(self, bill_data: Dict):
        """Run AI analysis on a bill"""
        analysis = await self.analyzer.analyze(bill_data)
        await self.db.save_bill_analysis(bill_data['legislationNumber'], analysis)
```

---

## AI Bill Analysis Engine

### Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BILL ANALYSIS PIPELINE                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ SUMMARIZATION   │  │ CLASSIFICATION  │  │ IMPACT ANALYSIS │
│ ─────────────── │  │ ─────────────── │  │ ─────────────── │
│ • Plain language│  │ • Topic tags    │  │ • Who affected  │
│ • Key provisions│  │ • Category      │  │ • Fiscal impact │
│ • What it does  │  │ • Subcategory   │  │ • Neighborhoods │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                    ┌─────────────────┐
                    │ EMBEDDING GEN   │
                    │ ─────────────── │
                    │ • Bill content  │
                    │ • For similarity│
                    └─────────────────┘
```

### Claude Prompts

```python
# prompts/bill_analysis.py

SUMMARIZATION_PROMPT = """
You are an expert at explaining DC Council legislation to everyday residents.

Analyze this bill and provide:

1. **Plain Language Summary** (2-3 sentences): What does this bill do in simple terms?
   Avoid jargon. Write for someone with no legal or political background.

2. **Key Provisions** (3-5 bullet points): What are the main things this bill would change or create?

3. **Who It Affects**: Which groups of DC residents would be most impacted by this bill?
   Be specific (e.g., "renters in Ward 7", "small business owners", "parents of school-age children")

4. **Practical Impact**: How might this bill affect someone's daily life if passed?

Bill Information:
- Number: {legislation_number}
- Title: {title}
- Description: {short_description}
- Full Text: {full_text}
- Sponsors: {introducers}
- Status: {status}

Respond in JSON format:
{{
    "plain_summary": "...",
    "key_provisions": ["...", "..."],
    "affected_groups": ["...", "..."],
    "practical_impact": "..."
}}
"""

TOPIC_CLASSIFICATION_PROMPT = """
You are classifying DC Council legislation into topic categories.

Available topics:
{topic_list}

For this bill, identify:
1. Primary topics (1-3 most relevant)
2. Secondary topics (any others that apply)
3. Confidence score for each (0.0 to 1.0)

Bill: {title}
Description: {short_description}
Key provisions: {key_provisions}

Respond in JSON:
{{
    "primary_topics": [
        {{"topic": "Housing", "confidence": 0.95}},
        ...
    ],
    "secondary_topics": [
        {{"topic": "Budget & Taxes", "confidence": 0.6}},
        ...
    ]
}}
"""

STANCE_INFERENCE_PROMPT = """
You are helping predict how a DC resident with specific values would vote on legislation.

The resident has described their values as:
"{user_values_statement}"

We've identified these priorities from their statement:
{parsed_priorities}

Bill being considered:
- Title: {bill_title}
- Summary: {bill_summary}
- Key provisions: {key_provisions}
- Affected groups: {affected_groups}

Based on the resident's stated values, predict:
1. How they would likely vote (Yes/No/Abstain)
2. Confidence level (0.0 to 1.0)
3. Reasoning (2-3 sentences explaining why this aligns or conflicts with their values)
4. Relevance score (0.0 to 1.0) - how relevant is this bill to their stated values?

Important: Be balanced and consider that reasonable people with similar values might
disagree. Only predict "Yes" or "No" with high confidence if the bill clearly aligns
or conflicts with their stated priorities.

Respond in JSON:
{{
    "predicted_vote": "Yes|No|Abstain",
    "confidence": 0.85,
    "reasoning": "This bill directly addresses...",
    "relevance_score": 0.9,
    "matching_values": ["affordable housing", "tenant protections"]
}}
"""
```

### Analysis Service

```python
# services/ai_analyzer.py

from anthropic import Anthropic
from typing import Dict, List
import json

class BillAnalyzer:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    async def analyze(self, bill: Dict) -> Dict:
        """Complete analysis of a bill"""

        # Run analyses in parallel where possible
        summary_task = self.summarize(bill)
        topics_task = self.classify_topics(bill)

        summary = await summary_task
        topics = await topics_task

        # Generate embedding after we have the summary
        embedding = await self.generate_embedding(bill, summary)

        return {
            "summary": summary,
            "topics": topics,
            "embedding_id": embedding['id']
        }

    async def summarize(self, bill: Dict) -> Dict:
        """Generate plain-language summary"""
        prompt = SUMMARIZATION_PROMPT.format(
            legislation_number=bill['legislationNumber'],
            title=bill['title'],
            short_description=bill.get('shortDescription', ''),
            full_text=bill.get('fullText', '')[:10000],  # Truncate if needed
            introducers=', '.join(bill.get('introducers', [])),
            status=bill.get('status', '')
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)

    async def predict_user_vote(
        self,
        user_values: str,
        parsed_priorities: List[str],
        bill: Dict,
        bill_analysis: Dict
    ) -> Dict:
        """Predict how a user would vote based on their values"""

        prompt = STANCE_INFERENCE_PROMPT.format(
            user_values_statement=user_values,
            parsed_priorities=json.dumps(parsed_priorities),
            bill_title=bill['title'],
            bill_summary=bill_analysis['summary']['plain_summary'],
            key_provisions=json.dumps(bill_analysis['summary']['key_provisions']),
            affected_groups=json.dumps(bill_analysis['summary']['affected_groups'])
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)
```

---

## User Value Matching System

### How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER VALUE PROCESSING                             │
└─────────────────────────────────────────────────────────────────────┘

USER INPUT:
"I care about making DC more affordable for middle-class families.
I support small local businesses over big chains. I think we need
better public transit and less car traffic. I'm worried about
climate change and want DC to be a leader on green initiatives.
I also believe in police reform and community safety programs."

                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: PARSE VALUES                                                │
│ ─────────────────────────────────────────────────────────────────── │
│ AI extracts structured values:                                      │
│                                                                     │
│ • Affordability (Housing, Taxes) - High Priority                    │
│ • Small Business Support - Medium Priority                          │
│ • Public Transit - High Priority                                    │
│ • Environmental Sustainability - High Priority                      │
│ • Police Reform - Medium Priority                                   │
│ • Community Safety - Medium Priority                                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: GENERATE EMBEDDING                                          │
│ ─────────────────────────────────────────────────────────────────── │
│ Create vector representation of user's values for similarity search │
│ Embedding captures semantic meaning, not just keywords              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: FIND RELEVANT BILLS                                         │
│ ─────────────────────────────────────────────────────────────────── │
│ • Semantic search: Find bills with similar embeddings               │
│ • Topic matching: Find bills tagged with user's priority topics     │
│ • Keyword search: Find bills mentioning specific terms              │
│ • Combine and rank by relevance score                               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: PREDICT USER VOTES                                          │
│ ─────────────────────────────────────────────────────────────────── │
│ For each relevant bill:                                             │
│ • AI analyzes bill against user's stated values                     │
│ • Predicts Yes/No/Abstain with confidence score                     │
│ • Provides reasoning                                                │
│                                                                     │
│ Example outputs:                                                    │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ B26-0042: Green Building Standards Act                          │ │
│ │ Predicted Vote: YES (confidence: 0.92)                          │ │
│ │ Reason: Directly aligns with stated priority on environmental   │ │
│ │ sustainability and DC climate leadership.                       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ B26-0089: Police Funding Increase Act                           │ │
│ │ Predicted Vote: NO (confidence: 0.71)                           │ │
│ │ Reason: Conflicts with stated support for police reform and     │ │
│ │ community safety programs over traditional policing.            │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: CALCULATE ALIGNMENT SCORES                                  │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│ For each council member:                                            │
│                                                                     │
│ Score = Σ (relevance_weight × alignment) / Σ relevance_weight      │
│                                                                     │
│ Where:                                                              │
│ • relevance_weight = how relevant the bill is to user's values     │
│ • alignment = 1 if member vote matches prediction, 0 if not        │
│                                                                     │
│ Example Result:                                                     │
│ ┌───────────────────────────────────────────────────────────────┐   │
│ │  Council Member          │ Alignment │ Relevant Votes         │   │
│ │  ───────────────────────────────────────────────────────────  │   │
│ │  Brianne Nadeau (Ward 1) │   87%     │ 23 of 26 aligned       │   │
│ │  Charles Allen (Ward 6)  │   84%     │ 22 of 26 aligned       │   │
│ │  Brooke Pinto (Ward 2)   │   76%     │ 20 of 26 aligned       │   │
│ │  ...                     │   ...     │ ...                    │   │
│ └───────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Scoring Algorithm

```python
# services/scorecard_calculator.py

from typing import List, Dict
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class VoteComparison:
    bill_id: int
    bill_title: str
    user_predicted_vote: str
    member_actual_vote: str
    relevance_weight: float
    confidence: float
    is_aligned: bool

@dataclass
class MemberScore:
    member_id: int
    member_name: str
    alignment_score: float
    total_relevant_votes: int
    aligned_votes: int
    opposed_votes: int
    topic_breakdown: Dict[str, float]
    vote_details: List[VoteComparison]

class ScorecardCalculator:

    def calculate_scorecard(
        self,
        user_values: 'UserValues',
        predictions: List['UserBillPrediction'],
        votes: List['Vote']
    ) -> List[MemberScore]:
        """
        Calculate alignment scores for all council members
        based on user's predicted votes vs actual votes.
        """

        # Group votes by member
        member_votes = self._group_votes_by_member(votes)

        # Build prediction lookup
        prediction_map = {p.bill_id: p for p in predictions}

        scores = []

        for member_id, member_name in self._get_all_members():
            member_vote_list = member_votes.get(member_id, [])

            comparisons = []
            topic_scores = {}

            for vote in member_vote_list:
                prediction = prediction_map.get(vote.bill_id)

                if not prediction or prediction.relevance_score < 0.3:
                    # Skip bills not relevant to user's values
                    continue

                # Determine alignment
                is_aligned = self._votes_align(
                    prediction.predicted_vote,
                    vote.vote
                )

                comparison = VoteComparison(
                    bill_id=vote.bill_id,
                    bill_title=vote.bill_title,
                    user_predicted_vote=prediction.predicted_vote,
                    member_actual_vote=vote.vote,
                    relevance_weight=prediction.relevance_score,
                    confidence=prediction.confidence,
                    is_aligned=is_aligned
                )
                comparisons.append(comparison)

                # Track by topic
                for topic in prediction.matching_topics:
                    if topic not in topic_scores:
                        topic_scores[topic] = {'aligned': 0, 'total': 0}
                    topic_scores[topic]['total'] += 1
                    if is_aligned:
                        topic_scores[topic]['aligned'] += 1

            # Calculate weighted alignment score
            if comparisons:
                weighted_sum = sum(
                    c.relevance_weight * c.confidence * (1 if c.is_aligned else 0)
                    for c in comparisons
                )
                weight_total = sum(
                    c.relevance_weight * c.confidence
                    for c in comparisons
                )
                alignment_score = (weighted_sum / weight_total) * 100
            else:
                alignment_score = None  # Not enough data

            # Calculate topic breakdown
            topic_breakdown = {
                topic: (data['aligned'] / data['total']) * 100
                for topic, data in topic_scores.items()
                if data['total'] > 0
            }

            scores.append(MemberScore(
                member_id=member_id,
                member_name=member_name,
                alignment_score=round(alignment_score, 1) if alignment_score else None,
                total_relevant_votes=len(comparisons),
                aligned_votes=sum(1 for c in comparisons if c.is_aligned),
                opposed_votes=sum(1 for c in comparisons if not c.is_aligned),
                topic_breakdown=topic_breakdown,
                vote_details=comparisons
            ))

        # Sort by alignment score (highest first)
        scores.sort(key=lambda s: s.alignment_score or 0, reverse=True)

        return scores

    def _votes_align(self, predicted: str, actual: str) -> bool:
        """
        Determine if votes align.
        - Yes/Yes = aligned
        - No/No = aligned
        - Yes/No or No/Yes = not aligned
        - Abstain predictions match Present/Absent
        - Absent actual votes are excluded from scoring
        """
        if actual == 'Absent':
            return None  # Exclude from calculation

        if predicted == 'Abstain':
            return actual == 'Present'

        return predicted == actual
```

---

## Frontend Application

### Page Structure

```
/                           # Landing page with value input
/scorecard                  # Main scorecard view (after values entered)
/scorecard/[memberId]       # Individual member detail page
/bills                      # Bill explorer/search
/bills/[billId]             # Individual bill detail
/compare                    # Side-by-side member comparison
/about                      # About the project
/methodology                # How scoring works
/api-docs                   # Public API documentation
```

### Key Components

```typescript
// components/ValueInput.tsx
// Free-text input where users describe what they care about

interface ValueInputProps {
  onSubmit: (values: string) => void;
  initialValue?: string;
}

export function ValueInput({ onSubmit, initialValue }: ValueInputProps) {
  const [values, setValues] = useState(initialValue || '');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const examplePrompts = [
    "I care about affordable housing and protecting renters from unfair evictions.",
    "I want DC to be business-friendly with lower taxes and less regulation.",
    "Environmental sustainability and climate action are my top priorities.",
    "I support police reform and investing in community safety programs.",
    "Education funding and support for DCPS teachers matters most to me."
  ];

  return (
    <div className="value-input-container">
      <h2>What matters to you?</h2>
      <p className="subtitle">
        Describe your values and priorities in your own words.
        We'll analyze DC Council votes to see which members align with you.
      </p>

      <textarea
        value={values}
        onChange={(e) => setValues(e.target.value)}
        placeholder="Example: I care about making DC more affordable for working families. I support small businesses and want better public transit..."
        rows={5}
        className="values-textarea"
      />

      <div className="example-prompts">
        <span>Try an example:</span>
        {examplePrompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => setValues(prompt)}
            className="example-btn"
          >
            {prompt.slice(0, 40)}...
          </button>
        ))}
      </div>

      <button
        onClick={() => {
          setIsAnalyzing(true);
          onSubmit(values);
        }}
        disabled={values.length < 20 || isAnalyzing}
        className="submit-btn"
      >
        {isAnalyzing ? 'Analyzing...' : 'See My Scorecard'}
      </button>
    </div>
  );
}
```

```typescript
// components/ScorecardGrid.tsx
// Main scorecard display showing all council members ranked

interface ScorecardGridProps {
  scores: MemberScore[];
  userValues: string;
  onMemberClick: (memberId: number) => void;
}

export function ScorecardGrid({ scores, userValues, onMemberClick }: ScorecardGridProps) {
  return (
    <div className="scorecard-container">
      <div className="scorecard-header">
        <h1>Your DC Council Scorecard</h1>
        <p className="values-summary">Based on: "{userValues.slice(0, 100)}..."</p>
        <button className="edit-values-btn">Edit My Values</button>
      </div>

      <div className="scorecard-grid">
        {scores.map((score, rank) => (
          <MemberCard
            key={score.member_id}
            score={score}
            rank={rank + 1}
            onClick={() => onMemberClick(score.member_id)}
          />
        ))}
      </div>

      <div className="scorecard-legend">
        <h3>How to read this scorecard</h3>
        <p>
          We analyzed {scores[0]?.total_relevant_votes || 0} votes on bills
          relevant to your stated values. The percentage shows how often each
          council member voted the way we predict you would have voted.
        </p>
      </div>
    </div>
  );
}

function MemberCard({ score, rank, onClick }: MemberCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'score-high';
    if (score >= 60) return 'score-medium';
    return 'score-low';
  };

  return (
    <div className="member-card" onClick={onClick}>
      <div className="rank">#{rank}</div>
      <img src={score.photo_url} alt={score.member_name} />
      <h3>{score.member_name}</h3>
      <p className="ward">{score.ward}</p>

      <div className={`score ${getScoreColor(score.alignment_score)}`}>
        {score.alignment_score}%
      </div>

      <p className="vote-summary">
        {score.aligned_votes} of {score.total_relevant_votes} votes aligned
      </p>

      <div className="topic-breakdown">
        {Object.entries(score.topic_breakdown).slice(0, 3).map(([topic, pct]) => (
          <div key={topic} className="topic-score">
            <span className="topic-name">{topic}</span>
            <div className="topic-bar">
              <div className="topic-fill" style={{ width: `${pct}%` }} />
            </div>
            <span className="topic-pct">{Math.round(pct)}%</span>
          </div>
        ))}
      </div>

      <button className="details-btn">View Details →</button>
    </div>
  );
}
```

```typescript
// components/BillExplorer.tsx
// Searchable, filterable list of all bills with AI summaries

interface BillExplorerProps {
  userValues?: string;
  showRelevanceScores?: boolean;
}

export function BillExplorer({ userValues, showRelevanceScores }: BillExplorerProps) {
  const [bills, setBills] = useState<Bill[]>([]);
  const [filters, setFilters] = useState({
    topic: 'all',
    status: 'all',
    search: '',
    sortBy: 'relevance' | 'date' | 'status'
  });

  return (
    <div className="bill-explorer">
      <div className="filters">
        <input
          type="search"
          placeholder="Search bills..."
          value={filters.search}
          onChange={(e) => setFilters({...filters, search: e.target.value})}
        />

        <select
          value={filters.topic}
          onChange={(e) => setFilters({...filters, topic: e.target.value})}
        >
          <option value="all">All Topics</option>
          <option value="housing">Housing</option>
          <option value="transportation">Transportation</option>
          {/* ... more topics */}
        </select>

        <select value={filters.sortBy}>
          {showRelevanceScores && (
            <option value="relevance">Most Relevant to You</option>
          )}
          <option value="date">Most Recent</option>
          <option value="activity">Most Active</option>
        </select>
      </div>

      <div className="bill-list">
        {bills.map(bill => (
          <BillCard
            key={bill.id}
            bill={bill}
            showRelevance={showRelevanceScores}
          />
        ))}
      </div>
    </div>
  );
}

function BillCard({ bill, showRelevance }: BillCardProps) {
  return (
    <div className="bill-card">
      <div className="bill-header">
        <span className="bill-number">{bill.legislation_number}</span>
        <span className="bill-status">{bill.status}</span>
        {showRelevance && bill.relevance_score && (
          <span className="relevance-badge">
            {Math.round(bill.relevance_score * 100)}% relevant to you
          </span>
        )}
      </div>

      <h3>{bill.title}</h3>

      <p className="plain-summary">{bill.analysis?.plain_summary}</p>

      <div className="bill-topics">
        {bill.analysis?.primary_topics.map(topic => (
          <span key={topic} className="topic-tag">{topic}</span>
        ))}
      </div>

      <div className="bill-meta">
        <span>Introduced: {formatDate(bill.introduction_date)}</span>
        <span>Sponsor: {bill.introducers[0]}</span>
      </div>

      {bill.final_vote && (
        <div className="vote-result">
          <strong>Final Vote:</strong> {bill.final_vote.result}
          <button className="see-votes-btn">See how they voted →</button>
        </div>
      )}
    </div>
  );
}
```

### Mobile-First Design

```css
/* styles/scorecard.css */

/* Base mobile styles */
.scorecard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  padding: 1rem;
}

.member-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.score {
  font-size: 3rem;
  font-weight: bold;
  margin: 1rem 0;
}

.score-high { color: #22c55e; }
.score-medium { color: #f59e0b; }
.score-low { color: #ef4444; }

/* Tablet */
@media (min-width: 768px) {
  .scorecard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .scorecard-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    padding: 2rem;
  }
}

/* Large desktop */
@media (min-width: 1280px) {
  .scorecard-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

---

## API Specification

### Public REST API

```yaml
openapi: 3.0.0
info:
  title: MyDCVote Public API
  version: 1.0.0
  description: Public API for DC Council voting data and scorecards

servers:
  - url: https://api.mydcvote.org/v1

paths:
  /bills:
    get:
      summary: List all bills
      parameters:
        - name: council_period
          in: query
          schema:
            type: integer
          description: Filter by council period (default: current)
        - name: topic
          in: query
          schema:
            type: string
          description: Filter by topic
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, passed, failed, withdrawn]
        - name: search
          in: query
          schema:
            type: string
          description: Full-text search
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
      responses:
        '200':
          description: List of bills
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Bill'
                  pagination:
                    $ref: '#/components/schemas/Pagination'

  /bills/{legislationNumber}:
    get:
      summary: Get bill details
      parameters:
        - name: legislationNumber
          in: path
          required: true
          schema:
            type: string
          example: B26-0001
      responses:
        '200':
          description: Bill details with analysis
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BillDetail'

  /bills/{legislationNumber}/votes:
    get:
      summary: Get votes for a bill
      responses:
        '200':
          description: Vote breakdown by action
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/VoteAction'

  /members:
    get:
      summary: List council members
      parameters:
        - name: council_period
          in: query
          schema:
            type: integer
        - name: active_only
          in: query
          schema:
            type: boolean
            default: true
      responses:
        '200':
          description: List of council members

  /members/{memberId}:
    get:
      summary: Get member details
      responses:
        '200':
          description: Member profile and voting summary

  /members/{memberId}/votes:
    get:
      summary: Get all votes by a member
      parameters:
        - name: council_period
          in: query
          schema:
            type: integer
        - name: topic
          in: query
          schema:
            type: string
      responses:
        '200':
          description: Member's voting record

  /scorecard:
    post:
      summary: Generate personalized scorecard
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - values_statement
              properties:
                values_statement:
                  type: string
                  description: User's description of their values
                  example: "I care about affordable housing and environmental sustainability"
                council_period:
                  type: integer
                  description: Council period to analyze (default: current)
      responses:
        '200':
          description: Personalized scorecard
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Scorecard'

  /topics:
    get:
      summary: List all topic categories
      responses:
        '200':
          description: Topic taxonomy

components:
  schemas:
    Bill:
      type: object
      properties:
        legislation_number:
          type: string
        title:
          type: string
        short_description:
          type: string
        status:
          type: string
        introduction_date:
          type: string
          format: date
        primary_topics:
          type: array
          items:
            type: string
        plain_summary:
          type: string

    BillDetail:
      allOf:
        - $ref: '#/components/schemas/Bill'
        - type: object
          properties:
            full_text:
              type: string
            analysis:
              $ref: '#/components/schemas/BillAnalysis'
            actions:
              type: array
              items:
                $ref: '#/components/schemas/VoteAction'

    BillAnalysis:
      type: object
      properties:
        plain_summary:
          type: string
        key_provisions:
          type: array
          items:
            type: string
        affected_groups:
          type: array
          items:
            type: string
        topic_scores:
          type: object
          additionalProperties:
            type: number

    VoteAction:
      type: object
      properties:
        action_type:
          type: string
        action_date:
          type: string
          format: date
        vote_result:
          type: string
        votes:
          type: array
          items:
            type: object
            properties:
              member_name:
                type: string
              vote:
                type: string
                enum: [Yes, No, Present, Absent]

    Scorecard:
      type: object
      properties:
        generated_at:
          type: string
          format: date-time
        values_summary:
          type: string
        parsed_priorities:
          type: array
          items:
            type: string
        member_scores:
          type: array
          items:
            $ref: '#/components/schemas/MemberScore'

    MemberScore:
      type: object
      properties:
        member_id:
          type: integer
        member_name:
          type: string
        ward:
          type: string
        alignment_score:
          type: number
        total_relevant_votes:
          type: integer
        aligned_votes:
          type: integer
        topic_breakdown:
          type: object
          additionalProperties:
            type: number

    Pagination:
      type: object
      properties:
        total:
          type: integer
        limit:
          type: integer
        offset:
          type: integer
        has_more:
          type: boolean
```

---

## Daily Update System

### GitHub Actions Workflow

```yaml
# .github/workflows/daily-sync.yml

name: Daily LIMS Sync

on:
  schedule:
    # Run at 2:00 AM EST (7:00 AM UTC)
    - cron: '0 7 * * *'
  workflow_dispatch:  # Allow manual trigger

env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  LIMS_API_TOKEN: ${{ secrets.LIMS_API_TOKEN }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

jobs:
  sync:
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y tesseract-ocr poppler-utils

      - name: Install Python dependencies
        run: pip install -r requirements.txt

      - name: Run sync
        run: python -m scripts.daily_sync

      - name: Upload sync report
        uses: actions/upload-artifact@v4
        with:
          name: sync-report-${{ github.run_id }}
          path: reports/sync-*.json

      - name: Notify on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Daily LIMS sync failed! Check GitHub Actions for details."
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

  analyze-new-bills:
    needs: sync
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run AI analysis on new bills
        run: python -m scripts.analyze_new_bills
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  recalculate-scorecards:
    needs: analyze-new-bills
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Recalculate affected scorecards
        run: python -m scripts.recalculate_scorecards

      - name: Invalidate CDN cache
        run: |
          curl -X POST "https://api.cloudflare.com/client/v4/zones/${{ secrets.CF_ZONE_ID }}/purge_cache" \
            -H "Authorization: Bearer ${{ secrets.CF_API_TOKEN }}" \
            -H "Content-Type: application/json" \
            --data '{"purge_everything":true}'
```

### Monitoring Dashboard

```python
# scripts/monitoring.py

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
import json

@dataclass
class SyncMetrics:
    sync_id: str
    started_at: datetime
    completed_at: datetime
    status: str
    new_bills: int
    updated_bills: int
    new_votes: int
    bills_analyzed: int
    scorecards_updated: int
    errors: List[str]

class SyncMonitor:
    def __init__(self, db):
        self.db = db

    async def get_dashboard_data(self) -> dict:
        """Get data for monitoring dashboard"""

        # Last 7 days of syncs
        recent_syncs = await self.db.query("""
            SELECT * FROM sync_logs
            WHERE started_at > NOW() - INTERVAL '7 days'
            ORDER BY started_at DESC
        """)

        # Data freshness
        last_successful = await self.db.query_one("""
            SELECT completed_at FROM sync_logs
            WHERE status = 'success'
            ORDER BY completed_at DESC LIMIT 1
        """)

        # Data totals
        totals = await self.db.query_one("""
            SELECT
                COUNT(*) as total_bills,
                COUNT(DISTINCT member_id) as total_members,
                (SELECT COUNT(*) FROM votes) as total_votes,
                (SELECT COUNT(*) FROM users) as total_users,
                (SELECT COUNT(*) FROM user_scorecards) as total_scorecards
            FROM bills
        """)

        # Analysis coverage
        analysis_coverage = await self.db.query_one("""
            SELECT
                COUNT(*) as analyzed,
                (SELECT COUNT(*) FROM bills) as total
            FROM bill_analysis
        """)

        return {
            "recent_syncs": [self._format_sync(s) for s in recent_syncs],
            "data_freshness": {
                "last_sync": last_successful['completed_at'].isoformat(),
                "hours_ago": (datetime.utcnow() - last_successful['completed_at']).total_seconds() / 3600
            },
            "totals": dict(totals),
            "analysis_coverage": {
                "analyzed": analysis_coverage['analyzed'],
                "total": analysis_coverage['total'],
                "percentage": (analysis_coverage['analyzed'] / analysis_coverage['total']) * 100
            }
        }
```

---

## Implementation Phases

### Phase 1: Data Foundation
**Goal:** Reliable data pipeline and database

**Deliverables:**
- [ ] PostgreSQL database with full schema
- [ ] Migrate existing CSV data to database
- [ ] Daily sync worker with LIMS API
- [ ] PDF vote extraction integration
- [ ] Data validation and quality checks
- [ ] Admin monitoring dashboard

**Technical Tasks:**
1. Set up PostgreSQL database (Supabase or Railway)
2. Create database migrations
3. Write data import scripts for existing CSVs
4. Refactor dc_council.py into modular services
5. Set up GitHub Actions for daily sync
6. Build basic admin dashboard

### Phase 2: AI Analysis Engine
**Goal:** Every bill analyzed and categorized

**Deliverables:**
- [ ] Bill summarization service
- [ ] Topic classification system
- [ ] Impact assessment generation
- [ ] Embedding generation and storage
- [ ] Batch processing for existing bills
- [ ] Incremental analysis for new bills

**Technical Tasks:**
1. Set up Anthropic API integration
2. Design and test prompts
3. Set up vector database (Pinecone or pgvector)
4. Build analysis pipeline
5. Process all existing bills
6. Integrate with daily sync

### Phase 3: User Value System
**Goal:** Users can input values and get predictions

**Deliverables:**
- [ ] Value parsing service
- [ ] User value embedding generation
- [ ] Bill relevance scoring
- [ ] Vote prediction engine
- [ ] User account system (optional, can be anonymous)
- [ ] Value editing and refinement

**Technical Tasks:**
1. Build value parsing prompts
2. Implement semantic similarity search
3. Build prediction API endpoint
4. Create user data model
5. Implement session/anonymous tracking

### Phase 4: Scorecard Calculator
**Goal:** Accurate, explainable alignment scores

**Deliverables:**
- [ ] Scoring algorithm implementation
- [ ] Topic-level breakdown
- [ ] Historical trend calculation
- [ ] Comparison tools
- [ ] Score explanation generation

**Technical Tasks:**
1. Implement scoring algorithm
2. Build scorecard caching layer
3. Create comparison logic
4. Generate human-readable explanations

### Phase 5: Web Application
**Goal:** Public-facing website

**Deliverables:**
- [ ] Landing page with value input
- [ ] Scorecard display
- [ ] Member detail pages
- [ ] Bill explorer
- [ ] Comparison view
- [ ] Mobile-responsive design
- [ ] SEO optimization

**Technical Tasks:**
1. Set up Next.js project
2. Build component library
3. Implement all pages
4. Add error handling and loading states
5. Performance optimization
6. Deploy to Vercel

### Phase 6: Public API & Polish
**Goal:** Production-ready public service

**Deliverables:**
- [ ] Public REST API
- [ ] API documentation
- [ ] Rate limiting
- [ ] Usage analytics
- [ ] Email notifications
- [ ] Social sharing
- [ ] Accessibility audit

**Technical Tasks:**
1. Build public API layer
2. Generate OpenAPI documentation
3. Implement rate limiting (Redis)
4. Add analytics tracking
5. Build email notification system
6. WCAG accessibility compliance

---

## Technology Stack

### Recommended Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Frontend** | Next.js 14 + TypeScript | SSR for SEO, great DX, Vercel deployment |
| **Styling** | Tailwind CSS | Rapid development, consistent design |
| **Backend** | Next.js API Routes / FastAPI | Simple for MVP, can split later |
| **Database** | PostgreSQL (Supabase) | Reliable, good tooling, free tier |
| **Vector DB** | pgvector extension | Keep everything in one DB |
| **Cache** | Redis (Upstash) | Fast, serverless-friendly |
| **AI** | Claude API (Anthropic) | Best reasoning for value matching |
| **Embeddings** | OpenAI text-embedding-3-small | Cost-effective, good quality |
| **Hosting** | Vercel | Easy deployment, good free tier |
| **Cron Jobs** | GitHub Actions | Free, reliable, good logging |
| **Monitoring** | Sentry + Axiom | Error tracking + logs |

### Cost Estimates (Monthly)

| Service | Free Tier | Estimated Usage | Est. Cost |
|---------|-----------|-----------------|-----------|
| Vercel | 100GB bandwidth | ~50GB | $0 |
| Supabase | 500MB DB, 1GB storage | ~200MB | $0 |
| Upstash Redis | 10K commands/day | ~5K | $0 |
| Claude API | - | ~500K tokens/month | $15 |
| OpenAI Embeddings | - | ~10M tokens/month | $1 |
| Domain | - | 1 domain | $12/yr |
| **Total** | | | **~$17/mo** |

At scale (1000+ daily users):

| Service | Est. Cost |
|---------|-----------|
| Vercel Pro | $20 |
| Supabase Pro | $25 |
| Upstash Pro | $10 |
| Claude API | $100 |
| OpenAI | $20 |
| **Total** | **~$175/mo** |

---

## Security & Privacy

### Data Protection

1. **No PII Collection Required**
   - Users can use the service anonymously
   - Only store values statement and session ID
   - No real names or addresses needed

2. **Optional Accounts**
   - Email-only registration
   - Password hashing with bcrypt
   - No social login (reduces data exposure)

3. **Data Retention**
   - Anonymous sessions: 30 days
   - Registered accounts: Until deleted
   - Users can delete their data anytime

### API Security

1. **Rate Limiting**
   - 100 requests/minute for anonymous
   - 1000 requests/minute for registered
   - Scorecard generation: 10/hour (AI cost control)

2. **Input Validation**
   - Sanitize all user input
   - Limit values statement to 2000 characters
   - Validate all query parameters

3. **HTTPS Everywhere**
   - Force HTTPS redirects
   - HSTS headers
   - Secure cookies

### Public Data Disclaimer

```
This website uses publicly available data from the DC Council's
Legislative Information Management System (LIMS). All voting records
and legislation information is public record.

AI-generated summaries and predictions are for informational purposes
only and may contain errors. Always refer to official sources for
authoritative information.
```

---

## Success Metrics

### Key Performance Indicators

1. **User Engagement**
   - Monthly active users
   - Scorecards generated per month
   - Return visitor rate
   - Average session duration

2. **Data Quality**
   - Bill analysis coverage (target: 100%)
   - Vote extraction accuracy (target: >98%)
   - Data freshness (target: <24 hours)

3. **System Health**
   - Daily sync success rate (target: >99%)
   - API response time (target: <200ms p95)
   - Uptime (target: >99.9%)

4. **Public Impact**
   - Media mentions
   - API consumers
   - Social shares
   - User feedback/testimonials

### Analytics Events to Track

```typescript
// Key events to track
const events = {
  // User journey
  'values_entered': { values_length: number, topics_detected: string[] },
  'scorecard_viewed': { member_count: number },
  'member_detail_viewed': { member_id: number, from_scorecard: boolean },
  'bill_viewed': { bill_id: string, from_search: boolean },

  // Engagement
  'values_edited': { previous_length: number, new_length: number },
  'comparison_created': { member_ids: number[] },
  'bill_search': { query: string, filters: object, results_count: number },

  // Sharing
  'scorecard_shared': { platform: string },
  'member_score_shared': { member_id: number, platform: string }
};
```

---

## Appendix

### LIMS API Reference

**Base URL:** `https://lims.dccouncil.us/api/v2/PublicData/`

**Authentication:** Bearer token in Authorization header

**Endpoints Used:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/members/{councilPeriodId}` | GET | List council members |
| `/BulkData/{categoryId}/{councilPeriodId}` | POST | List all legislation |
| `/LegislationDetails/{legislationNumber}` | GET | Full bill details |

**Rate Limits:** ~3 requests/second recommended

### Topic Taxonomy (Initial)

```
Housing
├── Affordable Housing
├── Tenant Rights
├── Rent Control
├── Homeownership
└── Homelessness

Public Safety
├── Policing
├── Criminal Justice Reform
├── Emergency Services
├── Gun Violence Prevention
└── Community Safety

Transportation
├── Public Transit (Metro/Bus)
├── Bike Infrastructure
├── Pedestrian Safety
├── Parking
├── Traffic Management
└── Electric Vehicles

Environment
├── Climate Action
├── Clean Energy
├── Green Buildings
├── Parks & Recreation
├── Pollution Control
└── Sustainability

Education
├── DCPS Funding
├── Charter Schools
├── Early Childhood
├── Higher Education
├── Teacher Support
└── Student Services

Budget & Taxes
├── Tax Policy
├── Government Spending
├── Fees & Fines
├── Economic Development
└── Small Business

Healthcare
├── Public Health
├── Mental Health
├── Substance Abuse
├── Healthcare Access
└── Health Equity

Civil Rights
├── LGBTQ+ Rights
├── Racial Equity
├── Immigration
├── Disability Rights
├── Voting Rights
└── Workers' Rights

Government
├── Ethics & Transparency
├── Elections
├── Agency Operations
├── Procurement
└── Statehood
```

---

## Next Steps

1. **Immediate:** Set up development environment and database
2. **This Week:** Import existing data, validate schema
3. **Next Week:** Build AI analysis pipeline, process bills
4. **Following Weeks:** Build web frontend, launch beta

---

*Last Updated: January 2026*
*Version: 1.0*
