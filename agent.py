import os
import tempfile
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import json

import pdfplumber
from pypdf import PdfReader

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo

GROQ_MODEL = "llama-3.3-70b-versatile"

# ── Agent 1: General purpose ──
general_agent = Agent(
    name="General Agent",
    model=Groq(id=GROQ_MODEL),
    instructions=[
        "You are a helpful AI assistant.",
        "Answer coding questions, explain concepts, write code.",
        "Answer science, math, history, and all general knowledge questions.",
        "Format code with proper markdown code blocks.",
    ],
    markdown=True,
)

# ── Agent 2: Web search ──
web_search_agent = Agent(
    name="Web Search Agent",
    model=Groq(id=GROQ_MODEL),
    tools=[DuckDuckGo(search=True, news=False)],
    instructions=[
        "Search the web for latest news and real-time information.",
        "Always include sources in your responses.",
    ],
    markdown=True,
)

# ── Agent 3: Finance ──
finance_agent = Agent(
    name="Finance Agent",
    model=Groq(id=GROQ_MODEL),
    tools=[YFinanceTools(
        stock_price=True,
        stock_fundamentals=True,
        analyst_recommendations=True,
        company_news=True,
    )],
    instructions=[
        "Provide financial data, stock prices, analyst recommendations.",
        "Use tables to present financial data clearly.",
    ],
    markdown=True,
)

# ── Agent 4: Builder Agent ──
builder_agent = Agent(
    name="Builder Agent",
    model=Groq(id=GROQ_MODEL),
    instructions=[
        "You are an elite UI/UX designer and frontend developer.",
        "When asked to build any app, website, tool, game, dashboard, or UI component, "
        "respond with a SINGLE complete self-contained HTML file.",
        "",
        "DESIGN RULES — follow these strictly:",
        "- Use stunning, modern design: gradients, glassmorphism, smooth animations, micro-interactions.",
        "- Pick a beautiful color palette (e.g. deep navy + electric blue, dark + neon green, warm cream + terracotta).",
        "- Use CSS custom properties for theming. Use flexbox and grid for layout.",
        "- Add hover effects, transitions (0.2-0.3s ease), and subtle box-shadows everywhere.",
        "- Typography: use system-ui or a Google Font loaded via @import in the <style> tag.",
        "- For images, ALWAYS use real photos from these free CDNs (no API key needed):",
        "  * Unsplash: https://images.unsplash.com/photo-{ID}?w=400&h=300&fit=crop&auto=format",
        "    Use these reliable Unsplash photo IDs for common categories:",
        "    - Products/tech: 1523275335684-37898b6baf30, 1585386959984-a4155224a1ad, 1491553895911-0055eca6402d",
        "    - Food: 1567620905732-2d1ec7ab7445, 1565299624946-b28f40a0ae38, 1540189549336-e6e99eb4b951",
        "    - Fashion: 1441986300917-64674bd600d8, 1542291026-7eec264c27ff, 1523381210434-271e8be1f52b",
        "    - Nature/travel: 1506905925346-21bda4d32df4, 1476514525535-07fb3b4ae5f1, 1469474968028-56623f02e42e",
        "    - People: 1507003211169-0a1dd7228f2d, 1494790108377-be9c29b29330, 1438761681033-6461ffad8d80",
        "    - Gaming: 1542751371-adc38448a05e, 1511512578047-dfb367046420, 1493711662062-fa541adb3fc8",
        "    - Interior/home: 1555041469-a586c61ea9bc, 1484101403633-562f891dc89a, 1493663284031-b7e3aefcae8e",
        "    - Business: 1460925895917-afdab827c52f, 1504868584819-f8e8b4b6d7e3, 1497366216548-37526070297c",
        "  * Picsum (generic beautiful photos): https://picsum.photos/seed/{word}/{width}/{height}",
        "    e.g. https://picsum.photos/seed/product1/400/300  (change seed word for different images)",
        "  * For avatars/people: https://i.pravatar.cc/150?img={1-70}",
        "  * For logos/icons: use inline SVG only",
        "  * ALWAYS set img attributes: loading='lazy' and onerror='this.src=\"https://picsum.photos/seed/fallback/400/300\"'",
        "- Make it fully functional with realistic sample data (at least 6-8 items for lists/grids).",
        "- Add interactivity: working buttons, filters, cart logic, form validation, animations.",
        "- CRITICAL: NEVER use window.prompt(), window.alert(), or window.confirm() — these pop up",
        "  outside the app and break the experience. Instead:",
        "  * For adding items (todo, notes, etc): use an inline input field always visible in the UI",
        "  * For confirmations (delete, etc): use an inline confirmation UI or just act immediately",
        "  * For alerts/messages: use a toast notification or inline status message in the app",
        "- The app must look like a real production product, not a demo.",
        "",
        "OUTPUT RULES:",
        "- Do NOT use JavaScript/CSS library CDN links (no jQuery, Bootstrap, etc). All JS and CSS must be inline.",
        "- Image CDNs (Unsplash, Picsum, Pravatar) ARE allowed and encouraged.",
        "- Start your response with exactly this marker on its own line: <!--APP-->",
        "- Then output the full HTML document starting with <!DOCTYPE html>",
        "- After the HTML ends, output exactly: <!--/APP-->",
        "- Do not add any explanation, text, or markdown before or after the markers.",
    ],
    markdown=False,
)

FINANCE_KEYWORDS = [
    "stock", "price", "share", "market", "nasdaq", "nyse", "ticker",
    "analyst", "recommendation", "earnings", "revenue", "pe ratio",
    "dividend", "portfolio", "invest", "fund", "etf", "crypto",
    "bitcoin", "equity", "valuation", "ipo", "financial", "finance",
    "fundamental", "company news", "quarterly", "annual report"
]

NEWS_KEYWORDS = [
    "latest news", "current news", "today", "breaking", "recent",
    "update", "headline", "happened", "this week", "this year",
    "2025", "2026", "right now", "currently", "live"
]

BUILD_KEYWORDS = [
    "build", "create", "make", "develop", "code",
    "website", "app", "application", "webpage", "page", "ui",
    "component", "dashboard", "landing page", "portfolio", "calculator",
    "todo", "form", "shopping cart", "e-commerce", "game", "tool",
    "timer", "clock", "quiz", "survey", "login page", "signup page",
    "chat ui", "kanban", "weather app", "music player",
]

IMAGE_GEN_KEYWORDS = [
    "generate image", "generate a image", "generate an image",
    "create image", "create a image", "create an image",
    "make image", "make a image", "make an image",
    "generate photo", "generate a photo", "generate picture", "generate a picture",
    "draw", "paint", "illustrate", "sketch",
    "show me a picture", "show me an image", "show me a photo",
    "visualize", "render an image", "render a",
    "image of", "picture of", "photo of", "artwork of",
    "generate art", "create art", "make art",
    "a image that", "an image that", "a picture that", "a photo of",
]

# ── Agent 5: Image Prompt Refiner ──
image_prompt_agent = Agent(
    name="Image Prompt Agent",
    model=Groq(id=GROQ_MODEL),
    instructions=[
        "You are an expert Stable Diffusion / Flux image generation prompt engineer.",
        "When given a user's image request, rewrite it as a single detailed prompt.",
        "RULES:",
        "- Keep the EXACT subject the user described — never change or replace it.",
        "- Add rich visual details: lighting, time of day, weather, colors, textures.",
        "- Add style descriptors: photorealistic, cinematic, 8K, sharp focus, detailed.",
        "- Add camera/composition: wide shot, portrait, golden hour, bokeh background.",
        "- Keep it under 150 words, all on ONE line.",
        "- Output ONLY the prompt — no explanation, no quotes, no preamble, no labels.",
        "Example input: 'a person standing under a tree'",
        "Example output: A person standing peacefully under a large oak tree, "
        "dappled sunlight filtering through green leaves, golden hour lighting, "
        "lush green grass, soft bokeh background, photorealistic, cinematic, "
        "8K resolution, sharp focus, warm color palette",
    ],
    markdown=False,
)

def route_query(user_input: str):
    text = user_input.lower()
    is_image   = any(kw in text for kw in IMAGE_GEN_KEYWORDS)
    is_build   = any(kw in text for kw in BUILD_KEYWORDS)
    is_finance = any(kw in text for kw in FINANCE_KEYWORDS)
    is_news    = any(kw in text for kw in NEWS_KEYWORDS)

    if is_image:
        return None, "Image Agent", "🎨"
    elif is_build:
        return builder_agent, "Builder Agent", "🏗️"
    elif is_finance:
        return finance_agent, "Finance Agent", "📈"
    elif is_news:
        return web_search_agent, "Web Search Agent", "🔍"
    else:
        return general_agent, "General Agent", "🤖"

# ── FastAPI app ──
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

@app.post("/chat")
def chat(req: ChatRequest):
    agent, agent_name, agent_icon = route_query(req.message)

    # ── Image generation path ──
    if agent_name == "Image Agent":
        def generate_image_stream():
            meta = json.dumps({"agent": "Image Agent", "icon": "🎨"})
            yield f"data: {meta}\n\n"

            # Refine the prompt
            refined = ""
            response = image_prompt_agent.run(req.message, stream=True)
            for chunk in response:
                if chunk.content:
                    refined += chunk.content
            refined = refined.strip()

            # Extract short keyword slug for URL-safe APIs
            encoded_full = urllib.parse.quote(refined)
            # Short version: first 8 words for APIs that need short prompts
            short = " ".join(refined.split()[:8])
            encoded_short = urllib.parse.quote(short)
            seed = abs(hash(refined)) % 999999

            # Multiple free image sources — frontend tries each until one loads
            image_urls = [
                # 1. Pollinations turbo (faster, more reliable than flux)
                f"https://image.pollinations.ai/prompt/{encoded_full}?width=1024&height=1024&seed={seed}&model=turbo&nologo=true",
                # 2. Pollinations flux fallback
                f"https://image.pollinations.ai/prompt/{encoded_short}?width=1024&height=1024&seed={seed}&model=flux&nologo=true",
                # 3. Picsum with seed (always works, random photo)
                f"https://picsum.photos/seed/{seed}/1024/1024",
            ]

            data = json.dumps({"image_url": image_urls[0], "image_urls": image_urls, "prompt": refined})
            yield f"data: {data}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate_image_stream(), media_type="text/event-stream")

    # ── All other agents ──
    def generate():
        meta = json.dumps({"agent": agent_name, "icon": agent_icon})
        yield f"data: {meta}\n\n"

        response = agent.run(req.message, stream=True)
        for chunk in response:
            if chunk.content:
                data = json.dumps({"text": chunk.content})
                yield f"data: {data}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/health")
def health():
    return {"status": "ok"}


# ── PDF Chat Endpoint ──
@app.post("/chat-with-pdf")
async def chat_with_pdf(
    file: UploadFile = File(...),
    message: str = Form(...)
):
    # Save uploaded PDF to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Extract text from PDF
    pdf_text = ""
    try:
        with pdfplumber.open(tmp_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    pdf_text += f"\n--- Page {i+1} ---\n{page_text}"

        # Fallback to pypdf if pdfplumber gets nothing
        if not pdf_text.strip():
            reader = PdfReader(tmp_path)
            for i, page in enumerate(reader.pages):
                pdf_text += f"\n--- Page {i+1} ---\n{page.extract_text() or ''}"

    finally:
        os.unlink(tmp_path)  # clean up temp file

    if not pdf_text.strip():
        pdf_text = "[Could not extract text — this may be a scanned PDF]"

    # Build a context-aware prompt
    prompt = f"""The user has uploaded a PDF. Here is its extracted text:

<pdf_content>
{pdf_text[:12000]}
</pdf_content>

User's question: {message}

Answer based on the PDF content above."""

    def generate():
        meta = json.dumps({"agent": "PDF Agent", "icon": "📄"})
        yield f"data: {meta}\n\n"

        response = general_agent.run(prompt, stream=True)
        for chunk in response:
            if chunk.content:
                data = json.dumps({"text": chunk.content})
                yield f"data: {data}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
