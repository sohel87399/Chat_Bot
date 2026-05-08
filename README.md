# MAM — Multi-Agent AI System

<div align="center">

![MAM](https://img.shields.io/badge/MAM-Multi--Agent%20AI-cc785c?style=for-the-badge&logo=sparkles)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000?style=for-the-badge&logo=vercel)

**🌐 Live Demo → [chat-bot-azure-six.vercel.app](https://chat-bot-azure-six.vercel.app/)**

</div>

---

## What is MAM?

MAM is a premium AI chat interface that automatically routes your questions to the most capable agent. Ask anything — it figures out whether to answer from knowledge, search the web, pull financial data, generate an image, build a live app, or analyze a PDF.

---

## Agents

| Agent | Trigger | Capability |
|-------|---------|------------|
| 🤖 **General Agent** | Any question | Knowledge, coding, math, science, history |
| 🔍 **Web Search Agent** | News, current events, "today", "2026" | Live web search via DuckDuckGo |
| 📈 **Finance Agent** | Stock, crypto, market, price | Real-time stock data via YFinance |
| 🏗️ **Builder Agent** | Build, create, make, website, app | Generates full live apps in a split panel |
| 🎨 **Image Agent** | Draw, generate image, picture of | AI image generation via Pollinations |
| 📄 **PDF Agent** | Upload a PDF | Extracts text and answers questions about it |

---

## Features

### 💬 Chat Interface
- Claude-style dark UI with **Crimson Pro** serif font
- Persistent chat history saved to localStorage
- Search across all conversations (`Ctrl+K`)
- New chat shortcut (`Ctrl+O`)
- Light / Dark theme toggle in Settings
- Login / Signup system (localStorage-based)

### 🏗️ App Builder
- Cinematic generation experience — animated phase steps, file tree, live code stream
- **Split panel** — chat on the left, live app preview on the right
- Draggable divider to resize panels
- **Code tab** — view syntax-highlighted HTML source
- Copy HTML / Open fullscreen buttons
- Uses real Unsplash + Picsum photos (no broken placeholders)

### 🎨 Image Generation
- Free, no API key — powered by [Pollinations AI](https://pollinations.ai)
- Prompt refinement agent writes rich, detailed prompts automatically
- 3-source cascade fallback (Turbo → Flux → Picsum)
- Download and open full-size buttons

### 📄 PDF Chat
- Upload any PDF via the paperclip button
- Extracts text with `pdfplumber` + `pypdf` fallback
- Ask questions about the document — answered by the General Agent

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI + Python |
| **AI / LLM** | Groq (llama-3.3-70b-versatile) via Phidata |
| **Web Search** | DuckDuckGo Search |
| **Finance Data** | YFinance |
| **Image Generation** | Pollinations AI (free, no key) |
| **PDF Parsing** | pdfplumber + pypdf |
| **Frontend** | Vanilla HTML/CSS/JS (no framework) |
| **Fonts** | Inter + Crimson Pro (Google Fonts) |
| **Deployment** | Vercel |

---

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/sohel87399/Chat_Bot.git
cd Chat_Bot
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and add your keys:
```env
GROQ_API_KEY=your_groq_api_key_here
PHI_API_KEY=your_phi_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

Get your free Groq API key at → [console.groq.com](https://console.groq.com)

### 5. Run the server
```bash
python -m uvicorn agent:app --host 0.0.0.0 --port 8000 --reload
```

Open **[http://localhost:8000](http://localhost:8000)**

---

## Deployment on Vercel

1. Push to GitHub
2. Import repo on [vercel.com](https://vercel.com)
3. Set **Framework Preset** → `FastAPI`
4. Add environment variables:
   - `GROQ_API_KEY`
   - `PHI_API_KEY`
   - `OPENAI_API_KEY`
5. Click **Deploy**

The `vercel.json` and `main.py` entrypoint are already configured.

---

## Project Structure

```
Chat_Bot/
├── agent.py          # FastAPI app + all 6 agents + routing logic
├── main.py           # Vercel entrypoint (imports app from agent.py)
├── index.html        # Full frontend — UI, chat, builder, image renderer
├── requirements.txt  # Python dependencies
├── vercel.json       # Vercel deployment config
├── .env.example      # Environment variable template
└── .gitignore        # Excludes .env, __pycache__, .venv
```

---

## Example Prompts

```
"Explain how transformers work in AI"           → General Agent
"Latest AI news today"                          → Web Search Agent
"AAPL stock price and analyst recommendations"  → Finance Agent
"Build a todo app with dark mode"               → Builder Agent
"Generate image of a sunset over mountains"     → Image Agent
[Upload PDF] "Summarize this document"          → PDF Agent
```

---

## Screenshots

> Chat interface with split-panel app builder, cinematic generation experience, and AI image generation.

---

## License

MIT — free to use, modify, and deploy.

---

<div align="center">
  Built with ❤️ using FastAPI, Groq, and Phidata
  <br/>
  <a href="https://chat-bot-azure-six.vercel.app/">🌐 Live Demo</a> ·
  <a href="https://github.com/sohel87399/Chat_Bot">📦 GitHub</a>
</div>
