# Requirements Document: Estate Sales Aggregator Prototype

## 1 Purpose

The purpose of this document is to capture detailed requirements for a week-long proof-of-concept that aggregates estate sales and secondhand listings from multiple sources, applies NLP parsing and scoring, presents results in a simple UI, and notifies users of high-potential leads.

---

## 2 Objectives

- Build an end-to-end pipeline that ingests listings from EstateSales.net, Craigslist, and public Facebook Groups.  
- Enrich raw listings with structured JSON fields (title, price cue, location, date).  
- Score each listing on “antique potential” using an LLM.  
- Surface results in a mobile-friendly Glide app with save-lead functionality.  
- Send email alerts for top-scoring leads.

---

## 3 Scope

This prototype will:

- Focus on EstateSales.net RSS for initial ingestion.  
- Use Python scripts in Replit and LangChain for parsing and scoring.  
- Leverage Glide for front-end proof-of-concept.  
- Send notification emails via SMTP.  
- Operate within free-tier limits of chosen platforms.

Non-goals:

- Production-grade scraping robustness or error handling.  
- Full support for Facebook or Craigslist at this stage (optional future work).  
- Automated hosting/deployment beyond manual agent runs.

---

## 4 Timeline & Milestones

| Day | Activity                              | Goal & Output                                                      | Free-Tier Notes                           |
|-----|---------------------------------------|--------------------------------------------------------------------|-------------------------------------------|
| 1   | Ideate in Copilot                     | One-pager requirements doc in OneDrive                             | Copilot web free with MS account          |
| 2   | Scrape Quick-N-Dirty                  | `repo/scraper.py` prints 10 RSS listings (title, city, date)       | Replit free tier; Ghostwriter credits     |
| 3   | Tidy & Parse with LangChain           | Local JSON file with extracted fields (title, price cue, distance) | Claude 3 Haiku free on Poe                |
| 4   | Prototype Listing Scorer              | JSON list enriched with `score` key (1–5 antique potential)        | No additional cost                        |
| 5   | Build UI in Glide                     | Mobile web app with card view + “Save lead”                        | Glide free plan (< 500 rows)               |
| 6   | Add Agent Loop                        | `run_agent.py` reruns scraper & scorer daily; reports new leads    | Manual runs to avoid server costs         |
| 7   | Notifications & Polish                | Python SMTP sends summary email for high-score listings; screenshot | Gmail SMTP; no paid API                  |

---

## 5 Detailed Day-by-Day Requirements

### Day 1: Requirements Ideation

- Use Microsoft Copilot (web) to draft a one-page “requirements doc.”  
- Include feature list, data sources, alert criteria.  
- Store final doc in OneDrive.

Acceptance Criteria:

- Document covers all planned modules and data flows.  
- Accessible via shared OneDrive link.

---

### Day 2: Quick-N-Dirty RSS Scraper

- Create `scraper.py` in a new Replit repo.  
- Fetch EstateSales.net RSS, parse titles, cities, dates.  
- CLI prints out first 10 entries.

Dependencies:

- Python 3, `feedparser` or `xml.etree`.  

Acceptance Criteria:

- Running `python scraper.py` prints 10 lines of “Title | City | Date.”

---

### Day 3: Parsing with LangChain & Claude

- Wrap raw RSS text in LangChain `Document` objects.  
- Call Claude via LangChain LLMChain to extract JSON fields:
  - `title`  
  - `price_cue` (e.g., “under $50”)  
  - `distance_phrase` (e.g., “5 miles away”)  
- Persist JSON array to local file `listings.json`.

Dependencies:

- LangChain, Anthropic SDK or Poe credentials.

Acceptance Criteria:

- `listings.json` contains an array of objects with the three required keys.

---

### Day 4: Listing Scorer Prototype

- Extend the LangChain workflow: prompt Claude to assign an `antique_potential` score (1–5).  
- Append `score` field to each JSON object.

Acceptance Criteria:

- Each listing in `listings.json` has a numeric `score` key.  
- Score distribution appears reasonable (e.g., some 1s, some 5s).

---

### Day 5: Build Glide Front-End

- Import `listings.json` into Google Sheets.  
- Configure a Glide app to read from the sheet.  
- Display each row as a card with image thumbnail, title, score.  
- Add a “Save lead” button that flags the row in Sheets.

Acceptance Criteria:

- Mobile-friendly Glide URL loads list of cards.  
- Saved leads update a “Saved” column in the sheet.

---

### Day 6: Agentic Loop Setup

- In Replit, write `run_agent.py` that:
  1. Runs the scraper.  
  2. Parses and scores new listings.  
  3. Appends new rows to Google Sheet or local file.  
- Print “X new leads” summary.

Acceptance Criteria:

- Manual invocation of `python run_agent.py` performs end-to-end pipeline.  
- Summary printed to console.

---

### Day 7: Notification & Polish

- Use Copilot to draft an HTML/text email template summarizing leads with `score ≥ 4`.  
- Use Python’s `smtplib` to send an email via Gmail SMTP.  
- Capture screenshot of email and Glide app for LinkedIn post.

Acceptance Criteria:

- Email arrives in inbox with correct listing details.  
- Screenshot included in project folder.

---

## 6 Technical Environment

- Python 3.x  
- Replit for code hosting  
- LangChain framework  
- Anthropic Claude 3 Haiku (via Poe or SDK)  
- Glide no-code platform  
- Gmail SMTP for email delivery  

Non-functional constraints:

- Stay within free-tier usage.  
- Manual agent runs to minimize cloud costs.  
- Minimal external dependencies beyond open-source.

---

## 7 Deliverables & Acceptance

1. One-pager requirements doc (OneDrive).  
2. `scraper.py` repo with sample RSS output.  
3. `listings.json` with parsed fields and scores.  
4. Live Glide app link.  
5. `run_agent.py` for manual daily runs.  
6. Email template and proof of delivery.  
7. LinkedIn-ready screenshots.

All deliverables will be stored in a shared GitHub repo and linked in the OneDrive requirements doc.
