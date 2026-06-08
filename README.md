# Tech-Law RAG: IT Compliance and Contract Analyzer

<div align="center">
<img src="https://github.com/user-attachments/assets/f1b98d04-65ba-4875-88be-6c2ceee0a75d" width="700px" />
</div>

The technology sector deals daily with software contracts, SLAs (Service Level Agreements), NDAs, and privacy policies (e.g., GDPR/LGPD). This project bridges the software development world with compliance rules and regulations.

* **What it is:** A platform where IT companies upload vendor contracts or third-party API terms of use. The system analyzes the document, pointing out information security risks, privacy violations, or abusive clauses.
* **The Engine:** Google Gemini API (`gemini-2.5-flash`) for complex legal-technological reasoning and the `gemini-embedding-2` model to transform PDFs into vectors.
* **The Architecture:** A robust backend centralizing HTTP calls, receiving files, vectorizing them, and saving them remotely in Supabase (Cloud PostgreSQL) using the `pgvector` extension.
* **The Differential:** Most RAG projects simply create a "chat with the PDF." The differential here is generating a **Structured Dossier**. Instead of waiting for the user to ask something, as soon as the upload finishes, the system returns a dashboard extracting problematic clauses, classifying the risk (High, Medium, Low), and suggesting a technical rewrite based on principles of freedom of information and data protection.
* **Why it's marketable:** Startups and software agencies don't have the budget to hire IT lawyers to review every third-party API they integrate. A SaaS that automates this triage has high commercial value.

---

## 🏗️ System Architecture & Project Phases

<div align="center">
  <img src="https://github.com/user-attachments/assets/83a31d98-b8ff-4279-b2bc-2372e5585f53" alt="Tech-Law RAG Cover" width="800" />
</div>

### Functional Requirements
* Upload IT contracts, SLAs, and Terms of Use in PDF format.
* Extract text from the PDF and convert it into vector representations (Embeddings).
* Use an LLM to analyze clauses regarding legal norms and data privacy.
* Generate a "Risk Dossier" detailing problematic clauses and risk levels.

### Base Configuration & Data Ingestion
The backend is built in Python using FastAPI for a fast, asynchronous API. Scripts handle receiving the PDF, breaking the text into smaller blocks (Strategic chunking to retain legal context), and generating Embeddings via Google GenAI SDK.

### Vector Connection
Supabase is used to host a cloud PostgreSQL database with the `pgvector` extension enabled, allowing semantic vectors to be stored in the same relational database alongside standard document metadata.

### Observability & Deployment
Langfuse is integrated into the Python backend to log every call made to the Gemini API, ensuring latency control and cost monitoring. The architecture is decoupled:
* **Database:** Supabase
* **Backend (FastAPI):** Render
* **Frontend (React/Vite):** Vercel

---

## 🧠 Learning Notes & Technical Highlights

This project demonstrates several production-ready practices beyond a simple "Hello World" RAG application:

1. **Decoupled Architecture (Headless API):**
   Isolating the Python backend from the React frontend ensures maintainability and scalability. The backend could easily be consumed by a mobile app in the future, while the frontend can be hosted cheaply on edge networks (like Vercel).

2. **Asynchronous Processing for Fluid UX:**
   Generating a complete legal dossier and embedding the document takes time. Instead of blocking the HTTP request and freezing the UI, the backend uses FastAPI `BackgroundTasks`. The API immediately returns a `pending` status, allowing the frontend to use polling and display an engaging loading state.

3. **Modern Vector Databases (`pgvector`):**
   Instead of using isolated vector databases (like Pinecone or ChromaDB), this project uses PostgreSQL with `pgvector` via Supabase. This allows the persistence of document metadata (ID, upload date, status) to live in the same database and atomic transactions as the embedding chunks.

4. **LLM Observability with Langfuse:**
   The AI "black box" is monitored using Langfuse. Every request tracks token usage, costs, and latency. This demonstrates the ability to debug LLMs and optimize costs in an enterprise-ready environment.

5. **Structured Outputs over Free Text:**
   Instead of having the AI spit out a large block of Markdown text, the system uses Pydantic models to force the LLM to return data in a strict JSON format (Structured Outputs). The frontend uses this data to render interactive dashboards, high-risk badges, and modal recommendations.

---

## 🚀 Runbook: How to Run, Configure, and Deploy

Follow the steps below to run the development environment, execute tests, and deploy to production.

### 1. Prerequisites
* **Node.js** (v18+)
* **Python** (v3.11+)
* **Git**
* Accounts created on:
  * [Google AI Studio](https://aistudio.google.com/apikey) (For Gemini API Keys)
  * [Supabase](https://supabase.com/) (Postgres Database + `pgvector`)
  * [Langfuse](https://langfuse.com/) (Optional, for observability)

### 2. Environment Variables Configuration
The project requires a `.env` file. There is an `.env.example` in the project root.

1. Create your `.env` files:
   ```bash
   cp .env.example .env
   cp .env.example backend/.env
   ```

2. Fill in the keys:
   * **Gemini:** Create an API Key in Google AI Studio and insert it into `GEMINI_API_KEY`.
   * **Supabase:** Create a new project, run the SQL migration (found in `backend/app/db/` or `supabase/migrations/`) to enable `pgvector` and create the tables. Then, insert `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `DATABASE_URL` (connection string).
   * **Langfuse:** (Optional) Insert `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`.

### 3. Running Locally

You will need two terminal windows.

#### Backend (FastAPI)
Open a terminal and access the `backend` folder:
```bash
cd backend

# Create and activate the virtual environment (Windows)
python -m venv .venv
.\.venv\Scripts\activate
# On Mac/Linux: source .venv/bin/activate

# Install dependencies
pip install -e .[dev]

# Start the server with auto-reload
uvicorn app.main:app --reload
```
The API will run at `http://127.0.0.1:8000`. You can access the Swagger docs at `http://127.0.0.1:8000/docs`.

#### Frontend (React)
Open the second terminal and access the `frontend` folder:
```bash
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```
The Frontend will run at `http://localhost:5173`. Vite is configured to automatically proxy `/api` requests to port 8000.

### 4. Automated Tests

#### Testing the Backend
Inside the `backend/` folder, with the virtual environment activated:
```bash
pytest -v
```

#### Checking the Frontend
Inside the `frontend/` folder:
```bash
npm run lint       # For code quality
npx tsc --noEmit   # For TypeScript type checking
```

### 5. Cloud Deployment

* **Backend (Render):** Create a new Web Service on Render, connect your GitHub repository, choose the **Docker** environment, set the **Root Directory** to `backend`, and add your environment variables.
* **Frontend (Vercel):** Create a new project on Vercel, connect the repository, set the **Root Directory** to `frontend`, and add the `VITE_API_URL` environment variable pointing to your Render backend URL.
