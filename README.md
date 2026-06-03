# Tech-Law RAG: IT Compliance and Contract Analyzer

<div align="center">
<img src="https://github.com/user-attachments/assets/f1b98d04-65ba-4875-88be-6c2ceee0a75d" width="700px" />
</div>

The technology sector deals daily with software contracts, SLAs (Service Level Agreements), NDAs, and privacy policies (e.g., GDPR/LGPD). This project bridges the software development world with compliance rules and regulations.

* **What it is:** A platform where IT companies upload vendor contracts or third-party API terms of use. The system analyzes the document, pointing out information security risks, privacy violations, or abusive clauses.
* **The Engine:** OpenAI API (GPT-4o) for complex legal-technological reasoning and the `text-embedding-3-small` model to transform PDFs into vectors.
* **The Architecture:** A robust backend centralizing HTTP calls, receiving files, vectorizing them, and saving them remotely in Supabase (Cloud PostgreSQL) using the `pgvector` extension.
* **The Differential:** Most RAG projects simply create a "chat with the PDF." Your differential will be generating a **Structured Dossier**. Instead of waiting for the user to ask something, as soon as the upload finishes, the system returns a dashboard extracting problematic clauses, classifying the risk (High, Medium, Low), and suggesting a technical rewrite based on principles of freedom of information and data protection.
* **Why it's marketable:** Startups and software agencies don't have the budget to hire IT lawyers to review every third-party API they integrate. A SaaS that automates this triage has high commercial value.

---

## Project Phases

### Phase 1: Scope and Requirements

**Functional Requirements (FR):**
* **FR01:** The system must allow document uploads in PDF format (IT contracts, SLAs, Terms of Use).
* **FR02:** The system must extract text from the PDF and convert it into vector representations (Embeddings).
* **FR03:** The system must use an LLM to analyze clauses regarding legal norms, constitutional principles, and freedom of information, identifying risks.
* **FR04:** The system must generate a "Risk Dossier" detailing problematic clauses, classifying the risk level (Low, Medium, High), and suggesting technical rewrites.
* **FR05:** The dashboard must display the history of contracts analyzed by the user.

**Non-Functional Requirements (NFR):**
* **NFR01 (Performance):** Vectorization and dossier generation must not block the user interface (requires asynchronous processing). 
* **NFR02 (Storage):** Semantic vectors must be stored in a relational database supporting vector operations.
* **NFR03 (Security):** The system must not retain sensitive contract data after the dossier is generated, or it must encrypt it at rest.
* **NFR04 (Observability):** Every request made to the OpenAI model must be monitored for latency control, token costs, and potential hallucinations.

### Phase 2: System Design and Modeling (Architecture)

<div align="center">
  <img src="https://github.com/user-attachments/assets/83a31d98-b8ff-4279-b2bc-2372e5585f53" alt="Tech-Law RAG Cover" width="800" />
</div>

### Phase 3: Building the AI Engine
This phase focuses exclusively on the backend and artificial intelligence, creating the bridge between the code and the remote database.

* **Base Configuration:** Initialize the backend project in Python using FastAPI to create a fast and asynchronous API.
* **Data Ingestion Pipeline:** Create scripts to receive the PDF, break the text into smaller blocks (Chunking strategically sized to retain legal context), and generate the Embeddings.
* **Vector Connection:** Create the cloud project on Supabase, enable the `pgvector` extension via SQL script, and connect FastAPI to the remote database through a connection string (URL) using a library like SQLAlchemy or Psycopg.
* **Structured Prompt Engineering:** Develop the system prompt that will instruct the LLM to act as a technical-legal auditor, focusing on data protection and IT norms, forcing the data output into a structured format (JSON) to facilitate reading on the frontend.

### Phase 4: Full-Stack Development
With the engine running on the backend and saving data in Supabase, it's time to integrate the visual endpoints.

* **Backend:** Finalize the HTTP routes (endpoints for upload, checking processing status, and retrieving the finalized dossier).
* **Frontend:** Boot up the React application. Develop a clean interface containing a Drag and Drop area for the PDF upload and the Dossier visualization screen, consuming the routes created in the backend.

### Phase 5: Observability and Deployment
Since Supabase has already solved the database hosting, the application deployment becomes much more agile and focused on the code.

* **Observability:** Integrate Langfuse into the backend (Python) to log every call made to OpenAI. This will prove that you know how to monitor costs and manage the LLM's "black box."
* **Decoupled Infrastructure:** It is no longer necessary to dockerize the database for deployment. If using containers, the `docker-compose.yml` will only contain the Python Backend image (FastAPI).
* **Deployment (Distributed Architecture):**
  * **Database:** Already in production on Supabase.
  * **Backend (FastAPI):** Host on free or low-cost platforms aimed at developers, such as Render or Railway.
  * **Frontend (React):** Deploy on platforms optimized for static interfaces, such as Vercel or Netlify.

> **NOTE:** By using Vercel (Front) + Render (Back) + Supabase (Database), the ecosystem becomes fully professional and modern. The total cost during the job-hunting month will be at most R$ 38.00 (or R$ 0.00 if accepting Render's free tier initial 50-second delay).
