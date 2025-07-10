# antique-scout-ai
End-to-end AI helper for antiques dealers: scrapes estate/garage sale listings, uses LangChain + Claude to score antique potential, stores in Google Sheet, shows in Glide app, emails top leads. Built in a week with Replit, Copilot, and a minimal agent loop—proof non-AI devs can ship useful AI tools.


# Antique-Scout-AI 🕰️🔍

AI-powered assistant that surfaces promising estate-sale, garage-sale, and online marketplace listings for antiques dealers.

*Built in one week by a non-AI engineer to prove how today’s no-/low-code + LLM tools can solve real problems.*

---

## ✨ What It Does
1. **Scrape** – Pulls new listings from EstateSales.net RSS (add more sources easily).
2. **Parse & Score** – LangChain calls Claude to extract fields & rate “antique potential”.
3. **Store** – Saves enriched JSON to a Google Sheet.
4. **Display** – Glide app shows leads, lets users save / share.
5. **Notify** – Email summary when high-score leads (> 3/5) appear.
6. **Automate** – Minimal LangChain Agent loops steps 1-5 on a schedule.

---

## 🏗️ Architecture

[RSS/HTML] ──► scraper.py (Replit)
│
▼
Claude via LangChain → JSON → scoring_chain.py
│
▼
Google Sheet ⇄ Glide Mobile App
│
▼
notify.py → Email Alert


## 🚀 Quick Start

```bash
git clone https://github.com/your-handle/antique-scout-ai.git
cd antique-scout-ai
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
python scraper.py           # pulls raw listings
python scoring_chain.py     # parses + scores with Claude
python notify.py            # sends email if new 3★+ leads
Note: Free tiers used throughout—Claude Haiku, Replit runner, Glide basic plan, Gmail SMTP.
```
📊 Success Metrics
≥ 5 new leads/day ingested
≤ 10 % false positives among “score ≥ 3” leads
Alert latency < 6 hrs from posting

🛣️ Roadmap
 Add Facebook Marketplace & Craigslist scraping
 Deploy agent loop on Cloud Run / HuggingFace Spaces
 SMS or WhatsApp notifications
 Fine-tune scoring prompt with dealer feedback

🙏 Acknowledgements
Replit Ghostwriter • LangChain • Anthropic Claude • Glide Apps • Microsoft Copilot inspiration.
