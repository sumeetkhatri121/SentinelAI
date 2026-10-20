# SentinelAI — Render Frontend & Edge Gateway

Ye project **SentinelAI** ka ultra-lightweight frontend aur edge proxy hai jo **Render Free Tier (512MB RAM)** ke liye optimized hai.

---

## 🏗️ Architecture

```
[User Browser]
       │
       ▼
[Render Free Tier (Frontend / Web Service)]
       │  (RAM: ~25MB, Build Time: ~15s)
       │  Forwards queries directly
       ▼
[Hugging Face Space Backend]
https://huggingface.co/spaces/NOT-OMEGA/SentinelAI
Direct API: https://not-omega-sentinelai.hf.space
(Heavy C++17 AVX2 SIMD Engine, Luhn PII Redaction, RAG Corpus, Hybrid BM25)
```

---

## 🚀 Render pe Deploy Karne ke 2 Aasan Tarike

### Tarika 1: Render Web Service (Recommended)
1. GitHub pe ek new repo banayein (e.g. `render-sentinelai`) aur iss folder ki files push karein:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of SentinelAI frontend"
   git remote add origin https://github.com/<your-username>/render-sentinelai.git
   git push -u origin main
   ```
2. **Render Dashboard** (`dashboard.render.com`) par jayein -> **New +** -> **Web Service**.
3. Apni repo select karein:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. Deploy par click karein! (Ye sirf 15-20 seconds mein build aur live ho jayega).

---

### Tarika 2: Render Static Site (100% Free Forever, Zero Sleep)
Kyunki `index.html` seedha Hugging Face Space API (`https://not-omega-sentinelai.hf.space`) se CORS ke through connect karta hai:
1. Render Dashboard par **New +** -> **Static Site** select karein.
2. Repo connect karein:
   - **Publish directory**: `.` (ya `static`)
3. Deploy par click karein! Koi server run nahi hoga, zero memory use hogi, aur site 24/7 bina sleep hue live rahegi.

---

## 💻 Local Run Karne ka Tarika
Aap iss folder mein command run kar sakte hain:
```bash
pip install -r requirements.txt
python main.py
```
Aur browser mein open karein:
`http://localhost:8000`

Ya phir seedha `index.html` par double click karke bhi use kar sakte hain!
