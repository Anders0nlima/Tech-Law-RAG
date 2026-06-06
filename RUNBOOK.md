# 🚀 Runbook: Como Rodar, Configurar e Publicar

Este documento serve como o guia operacional do Tech-Law RAG. Siga as etapas abaixo para provisionar os recursos, rodar o ambiente de desenvolvimento, executar os testes e realizar o deploy em produção.

---

## 1. Pré-requisitos

* **Node.js** (v18+)
* **Python** (v3.11+)
* **Git**
* Contas criadas nas seguintes plataformas:
  * [OpenAI](https://platform.openai.com/) (Para acessar as APIs GPT-4o e Embeddings)
  * [Supabase](https://supabase.com/) (Banco de Dados Postgres + `pgvector`)
  * [Langfuse](https://langfuse.com/) (Opcional, para observabilidade e controle de custos)
  * [Render](https://render.com/) e [Vercel](https://vercel.com/) (Para deploy)

---

## 2. Configuração de Variáveis de Ambiente

O projeto requer um arquivo `.env` configurado. Existe um `.env.example` na raiz do projeto.

1. Faça uma cópia do arquivo de exemplo para `.env`:
   ```bash
   cp .env.example .env
   cp .env.example backend/.env
   ```
   *(Nota: Recomendamos colocar o `.env` também dentro da pasta `backend/` para que o Uvicorn o carregue automaticamente durante o desenvolvimento local.)*

2. Preencha as chaves:

### 🔑 Configurando a OpenAI
- Crie uma API Key no painel da OpenAI e insira em `OPENAI_API_KEY`.
- Deixe o modelo padrão como `text-embedding-3-small` (1536 dimensões).

### 🗄️ Configurando o Supabase
1. Crie um novo projeto no Supabase.
2. Execute a migration SQL contida na pasta `backend/app/db/` (ou pelo painel SQL do Supabase) para habilitar o `pgvector` e criar as tabelas.
3. Copie as chaves do projeto (em Project Settings -> API / Database) e insira em:
   - `SUPABASE_URL`: A URL do seu projeto.
   - `SUPABASE_SERVICE_ROLE_KEY`: A chave secreta (`service_role`).
   - `DATABASE_URL`: A connection string do PostgreSQL.

### 👁️ Configurando o Langfuse (Opcional)
- Crie um projeto no Langfuse.
- Insira as chaves `LANGFUSE_PUBLIC_KEY` e `LANGFUSE_SECRET_KEY`.

---

## 3. Rodando o Projeto Localmente

O projeto é separado em Backend (FastAPI) e Frontend (React). Você precisará de dois terminais abertos.

### 🐍 Backend
Abra um terminal e acesse a pasta `backend`:
```bash
cd backend

# Crie e ative o ambiente virtual (Windows)
python -m venv .venv
.\.venv\Scripts\activate

# Em Mac/Linux: source .venv/bin/activate

# Instale as dependências
pip install -e .[dev]

# Inicie o servidor em modo de recarregamento
uvicorn app.main:app --reload
```
A API estará rodando em `http://127.0.0.1:8000`. Acesse a documentação Swagger em `http://127.0.0.1:8000/docs`.

### ⚛️ Frontend
Abra o segundo terminal e acesse a pasta `frontend`:
```bash
cd frontend

# Instale as dependências (somente na primeira vez)
npm install

# Inicie o servidor de desenvolvimento Vite
npm run dev
```
O Frontend estará rodando em `http://localhost:5173`. O Vite já está configurado para fazer um proxy automático de requisições que começam com `/api` para a porta 8000.

---

## 4. Testes Automatizados

O backend e o frontend possuem verificações para garantir que o código esteja saudável.

### Testando o Backend
Na pasta `backend/`, com o ambiente virtual ativado:
```bash
pytest -v
```
*(Os testes usam injeção de dependência e mockam a comunicação com o banco de dados e a OpenAI).*

### Checando o Frontend
Na pasta `frontend/`:
```bash
npm run lint       # Para verificar qualidade de código
npx tsc --noEmit   # Para verificar tipagem do TypeScript
```

---

## 5. Deploy na Nuvem (Deploy Contínuo)

Com as alterações do passo de deployment realizadas, você pode publicar o sistema em poucos passos gratuitamente.

### 🚀 Deploy do Backend (Render)
1. Crie um novo **Web Service** no Render.
2. Conecte com o repositório do GitHub.
3. Escolha o ambiente: **Docker**. (O arquivo `backend/Dockerfile` instruirá o Render).
4. No campo **Root Directory**, digite: `backend`.
5. Adicione as Variáveis de Ambiente necessárias (`DATABASE_URL`, `OPENAI_API_KEY`, `FRONTEND_URL` etc).
6. O Render fará o build da imagem Docker e iniciará o Uvicorn na porta indicada.

### 🚀 Deploy do Frontend (Vercel)
1. Crie um novo projeto na Vercel e conecte o repositório.
2. Na configuração do projeto, marque a opção **Root Directory** como `frontend`.
3. O Vercel detectará automaticamente a presença do Vite.
4. Vá em **Environment Variables** e adicione a variável:
   - `VITE_API_URL`: A URL do backend publicado no Render (ex: `https://tech-law-rag-api.onrender.com`).
5. Realize o Deploy.

🎉 **Seu sistema está no ar!**
