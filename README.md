# [cite_start]Tech-Law RAG: IT Compliance and Contract Analyzer [cite: 303, 304]

The technology sector deals daily with software contracts, SLAs (Service Level Agreements), NDAs, and privacy policies (e.g., GDPR/LGPD). [cite_start]This project bridges the software development world with compliance rules and regulations. [cite: 305, 306]

* **What it is:** A platform where IT companies upload vendor contracts or third-party API terms of use. [cite_start]The system analyzes the document, pointing out information security risks, privacy violations, or abusive clauses. [cite: 307, 308]
* [cite_start]**The Engine:** OpenAI API (GPT-4o) for complex legal-technological reasoning and the `text-embedding-3-small` model to transform PDFs into vectors. [cite: 309]
* [cite_start]**The Architecture:** A robust backend centralizing HTTP calls, receiving files, vectorizing them, and saving them remotely in Supabase (Cloud PostgreSQL) using the `pgvector` extension. [cite: 310]
* **The Differential:** Most RAG projects simply create a "chat with the PDF." Your differential will be generating a **Structured Dossier**. [cite_start]Instead of waiting for the user to ask something, as soon as the upload finishes, the system returns a dashboard extracting problematic clauses, classifying the risk (High, Medium, Low), and suggesting a technical rewrite based on principles of freedom of information and data protection. [cite: 311, 312]
* **Why it's marketable:** Startups and software agencies don't have the budget to hire IT lawyers to review every third-party API they integrate. [cite_start]A SaaS that automates this triage has high commercial value. [cite: 313, 314]

---

## [cite_start]Project Phases [cite: 315]

### [cite_start]Phase 1: Scope and Requirements [cite: 316]

[cite_start]**Functional Requirements (FR):** [cite: 317]
* [cite_start]**FR01:** The system must allow document uploads in PDF format (IT contracts, SLAs, Terms of Use). [cite: 319]
* [cite_start]**FR02:** The system must extract text from the PDF and convert it into vector representations (Embeddings). [cite: 320]
* [cite_start]**FR03:** The system must use an LLM to analyze clauses regarding legal norms, constitutional principles, and freedom of information, identifying risks. [cite: 321]
* [cite_start]**FR04:** The system must generate a "Risk Dossier" detailing problematic clauses, classifying the risk level (Low, Medium, High), and suggesting technical rewrites. [cite: 322]
* [cite_start]**FR05:** The dashboard must display the history of contracts analyzed by the user. [cite: 323]

[cite_start]**Non-Functional Requirements (NFR):** [cite: 324]
* [cite_start]**NFR01 (Performance):** Vectorization and dossier generation must not block the user interface (requires asynchronous processing). [cite: 325]
* [cite_start]**NFR02 (Storage):** Semantic vectors must be stored in a relational database supporting vector operations. [cite: 326]
* [cite_start]**NFR03 (Security):** The system must not retain sensitive contract data after the dossier is generated, or it must encrypt it at rest. [cite: 327]
* [cite_start]**NFR04 (Observability):** Every request made to the OpenAI model must be monitored for latency control, token costs, and potential hallucinations. [cite: 328]

### [cite_start]Phase 2: System Design and Modeling (Architecture) [cite: 329]

### [cite_start]Phase 3: Building the AI Engine [cite: 347]
[cite_start]This phase focuses exclusively on the backend and artificial intelligence, creating the bridge between the code and the remote database. [cite: 348]

* [cite_start]**Base Configuration:** Initialize the backend project in Python using FastAPI to create a fast and asynchronous API. [cite: 349]
* [cite_start]**Data Ingestion Pipeline:** Create scripts to receive the PDF, break the text into smaller blocks (Chunking strategically sized to retain legal context), and generate the Embeddings. [cite: 350]
* [cite_start]**Vector Connection:** Create the cloud project on Supabase, enable the `pgvector` extension via SQL script, and connect FastAPI to the remote database through a connection string (URL) using a library like SQLAlchemy or Psycopg. [cite: 351]
* [cite_start]**Structured Prompt Engineering:** Develop the system prompt that will instruct the LLM to act as a technical-legal auditor, focusing on data protection and IT norms, forcing the data output into a structured format (JSON) to facilitate reading on the frontend. [cite: 352]

### [cite_start]Phase 4: Full-Stack Development [cite: 353]
[cite_start]With the engine running on the backend and saving data in Supabase, it's time to integrate the visual endpoints. [cite: 354]

* [cite_start]**Backend:** Finalize the HTTP routes (endpoints for upload, checking processing status, and retrieving the finalized dossier). [cite: 355]
* **Frontend:** Boot up the React application. [cite_start]Develop a clean interface containing a Drag and Drop area for the PDF upload and the Dossier visualization screen, consuming the routes created in the backend. [cite: 356, 357]

### [cite_start]Phase 5: Observability and Deployment [cite: 358]
[cite_start]Since Supabase has already solved the database hosting, the application deployment becomes much more agile and focused on the code. [cite: 359]

* **Observability:** Integrate Langfuse into the backend (Python) to log every call made to OpenAI. [cite_start]This will prove that you know how to monitor costs and manage the LLM's "black box." [cite: 360, 361]
* **Decoupled Infrastructure:** It is no longer necessary to dockerize the database for deployment. [cite_start]If using containers, the `docker-compose.yml` will only contain the Python Backend image (FastAPI). [cite: 362, 363]
* **Deployment (Distributed Architecture):**
  * [cite_start]**Database:** Already in production on Supabase. [cite: 364]
  * [cite_start]**Backend (FastAPI):** Host on free or low-cost platforms aimed at developers, such as Render or Railway. [cite: 365]
  * [cite_start]**Frontend (React):** Deploy on platforms optimized for static interfaces, such as Vercel or Netlify. [cite: 366]

> **NOTE:** By using Vercel (Front) + Render (Back) + Supabase (Database), the ecosystem becomes fully professional and modern. [cite_start]The total cost during the job-hunting month will be at most R$ 38.00 (or R$ 0.00 if accepting Render's free tier initial 50-second delay). [cite: 367]