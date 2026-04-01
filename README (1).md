# 📡 MarketOS — Marketing Command Centre

An AI-powered marketing app built specifically for Indian businesses.

## 🛠️ Features
- 🔍 **Competitor Spy** — Deep strategic analysis of any competitor
- 📅 **Content Calendar** — 30-day AI-generated post plans
- 💰 **Budget Allocator** — Smart channel split with pie charts
- 📊 **Campaign Tracker** — Log campaigns, view performance charts, get AI insights
- 🔐 **Login System** — Each user's data saved separately

## 🚀 Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run locally
```bash
streamlit run app.py
```

### 3. Get your Anthropic API key
- Go to **console.anthropic.com**
- API Keys → Create Key
- Paste it in the app under ⚙️ Settings

## ☁️ Deploy to Streamlit Cloud

1. Push to GitHub (all 3 files at root)
2. Go to share.streamlit.io → New App
3. Select repo, branch: main, file: app.py
4. (Optional) Add secret: Settings → Secrets → `ANTHROPIC_API_KEY = "sk-ant-..."`
5. Deploy!

## 📁 Files
```
app.py            ← Full app (single file)
requirements.txt  ← Dependencies
README.md         ← This file
```
