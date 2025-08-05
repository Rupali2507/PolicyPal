# ✨ PolicyPal: AI-Powered Policy Document Q&A ✨

Unlock the full potential of your policy documents! **PolicyPal** lets you effortlessly upload your PDFs and ask complex, natural language questions. Powered by a **local Large Language Model (LLM)** and built with modern microservice architecture, PolicyPal delivers human-like, reasoned answers—instantly telling you if a claim is approved or rejected, and why.

## 🚀 Why PolicyPal?

- **Instant Answers:** No more searching through dense PDFs.
- **Smart & Secure:** Local AI keeps your documents private.
- **Seamless Experience:** Upload, ask, and get actionable responses.
- **Modern Tech Stack:** React, Node.js, FastAPI, LangChain, and Ollama for top performance.

## 🛠️ Architecture Overview

| Component         | Description                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------ |
| 🎨 **Frontend**   | Elegant React UI for authentication, uploads, and Q&A.                                     |
| 🚪 **Backend**    | Node.js + Express server: Orchestrates API calls, authentication, and database management. |
| 🧠 **ML Service** | Python (FastAPI, LangChain): Handles the AI magic using local LLMs via Ollama.             |

**Data Flow:** React Client ➡️ Node.js Server ➡️ Python ML Service

## 🗝️ Prerequisites

Make sure your toolkit is ready:

- **Node.js** v18.0+ ([Download](https://nodejs.org/))
- **Python** v3.10+ ([Download](https://python.org/))
- **Ollama** (for local LLMs) ([Download](https://ollama.com/))

## 🚦 Quickstart Guide

**Clone and Prepare:**

```bash
git clone
cd PolicyPal
```

### 1️⃣ ML Service (AI Engine)

```bash
cd doc_qa_backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt

# Grab the AI model (one-time only)
ollama pull gemma:2b
```

### 2️⃣ Node.js Backend

```bash
cd ../Server
npm install
```

**Configure Environment:**

- Copy `.env.example` ➡️ `.env`
- Fill in:
  - `MONGODB_URI=mongodb+srv://:@cluster.mongodb.net/`
  - `JWT_SECRET=your_super_secret_key_for_jwt`
  - `PORT=5000`
  - `NODE_ENV=development`

### 3️⃣ React Frontend

```bash
cd ../Client
npm install
```

## 🏃 Run the Trio

Fire up each service **in its own terminal** for smooth operation!

**Terminal 1: ML Service**

```bash
cd doc_qa_backend
# Activate your environment!
uvicorn app.main:app --reload
# → Now running at: http://localhost:8000
```

**Terminal 2: Node.js Backend**

```bash
cd Server
npm start
# → API at: http://localhost:5000
```

**Terminal 3: React Frontend**

```bash
cd Client
npm start
# → MAGIC at: http://localhost:1234
```

## 🧑💻 How to Use

1. Visit [http://localhost:1234](http://localhost:1234)
2. **Sign up** or **Log in**
3. Upload a policy PDF and get ready to chat with your document!
4. Use the “Ask Questions About a Document” form—type your question, hit **Get Answer**.
5. Get instant, intelligent, clause-level responses.

## 💡 Pro Tips

- For best speed & privacy, use on a powerful local machine.
- Combine with custom LLMs on Ollama for tailored industry domains.

## 🎉 Happy Building with PolicyPal!

From insurance claim reviews to legal audits, **PolicyPal** makes understanding your policies effortless, accurate, and even a bit fun.  
**Cut through the jargon. Get to your answer. Be policy-smart—with PolicyPal!**

_Unleash the power of AI on your documents—because you deserve answers as classy and sharp as you are._
