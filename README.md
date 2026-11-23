# Secure RAG Chatbot

A security-focused **Retrieval-Augmented Generation (RAG)** API built with FastAPI, PostgreSQL, pgvector, local sentence embeddings, and GapGPT. The project demonstrates how authentication, document-level authorization, privacy controls, and audit logging can be incorporated into an LLM application.

> **Project status:** Core user flows and selected security scenarios have been manually tested. This is **not** a production security certification or a claim of comprehensive prompt-injection resistance.

## Features

- **JWT authentication** and **Argon2 password hashing**.
- **Role-based access control (RBAC)** for administrative operations.
- **Document-level read permissions**; non-admin users can retrieve chunks only from documents for which they have explicit read permission.
- **PDF and TXT ingestion**, text extraction, chunking, and local embeddings (`all-MiniLM-L6-v2`).
- **Semantic search** over PostgreSQL with **pgvector**.
- **Secure RAG answers** generated through the GapGPT API.
- **PII masking** for common email, phone, and US SSN patterns, with input/context masking and an additional output-masking layer introduced during later development.
- **Defensive prompting** against instructions embedded in retrieved documents, answer-grounding guidance, and a character-based context limit.
- **Audit logging** for login, document access, uploads, chat requests, and denied role-based access.
- **Swagger UI** for manual API exploration.

## Tech stack

| Layer | Technology |
| --- | --- |
| API | Python, FastAPI |
| Persistence | PostgreSQL, SQLAlchemy, psycopg |
| Vector search | pgvector |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| LLM provider | GapGPT (OpenAI-compatible client) |
| Authentication | JWT, Argon2 |
| API documentation | Swagger UI / OpenAPI |
| Schema migrations | Alembic (where configured in the local working project) |

## Architecture

```text
Client / Swagger UI
       |
       v
FastAPI + JWT authentication
       |
       +--> Role and document permission checks
       |
       +--> Upload: PDF/TXT -> extraction -> chunks -> local embeddings
       |                                         |
       |                                         v
       |                               PostgreSQL + pgvector
       |
       +--> Chat: question -> local query embedding
                             -> permission-filtered vector search
                             -> PII masking + context limit
                             -> GapGPT
                             -> output masking -> answer + source metadata
       |
       +--> PostgreSQL audit logs
```

**Security boundary:** Document permissions are applied within the retrieval query, before retrieved content is sent to the external LLM provider. Retrieved text is treated as untrusted reference material; prompt instructions alone cannot guarantee injection resistance.

## Getting started (Windows / PowerShell)

### Prerequisites

- Python and a Python virtual environment
- PostgreSQL with the **pgvector** extension available
- A database and database user with appropriate access
- A GapGPT API key
- A `requirements.txt` or `requirements-lock.txt` matching your working project

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

If the lock file is present:

```powershell
python -m pip install -r requirements-lock.txt
```

Otherwise, use the project's maintained `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

The embedding model may need to be downloaded on first use.

### 3. Prepare the database

Create the PostgreSQL database, enable the extension, and apply the schema using the migration/setup workflow configured in **your current local copy**:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

If your local project has a working Alembic configuration and migrations, apply them with:

```powershell
python -m alembic upgrade head
```

**Note:** The older code archive reviewed for this README did not include an Alembic migration directory or its full installation files. Do not assume that migrations alone will initialize a fresh database until those files are committed and verified.

### 4. Run the API

```powershell
python -m uvicorn app.main:app --reload
```

Open:

- Swagger UI: http://127.0.0.1:8000/docs
- Health endpoint: http://127.0.0.1:8000/health

## Key endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Obtain an access token |
| `POST` | `/documents/upload` | Upload a PDF/TXT document (admin) |
| `POST` | `/chat/ask` | Ask a question with permission-filtered RAG |
| `POST` | `/chat/connection-test` | Test the LLM provider (admin) |
| `GET` | `/admin/access-check` | Verify admin-only access |
| `GET` | `/health` | Basic health check |

Additional document and administrative permission endpoints are available in Swagger UI.

### Example RAG request

After authenticating in Swagger UI, use `POST /chat/ask`:

```json
{
  "question": "What is the primary purpose of the Atlas-47 project?",
  "top_k": 5
}
```

A successful response includes an `answer` and a `sources` list with document and chunk metadata. Returned sources are retrieved context, **not proof that every generated claim is supported**.

## Security verification performed

The following outcomes were observed during manual development tests:

| Test | Observed result |
| --- | --- |
| Authorized vs. unauthorized document retrieval | Admin retrieved a restricted test document; a user without explicit read permission did not receive its sensitive test code |
| Embedded prompt-injection attempt | Model answered the legitimate document question rather than outputting the injected `HACKED` instruction |
| Missing evidence | Model replied `I do not have enough information.` instead of inventing a project budget |
| PII masking | Direct masking test replaced a sample email, phone number, and US SSN with placeholders |
| Invalid JWT | Protected endpoint returned HTTP `401` |
| Insufficient role | Admin-only endpoint returned HTTP `403`, and an `access_denied` event was logged |
| Provider error | A test of an invalid LLM model returned a generic error message rather than exposing the underlying provider error |
| End-to-end chat auditing | Successful `POST /chat/ask` returned HTTP `200` and produced a corresponding `chat` audit event |

These checks are examples, **not a complete automated regression or penetration test suite**. See `tests/` for available local test fixtures and `tests/test_queries.sql` for manual database verification queries, if those files have been added to the working repository.

## Privacy and limitations

- Masking uses known patterns; it does **not** detect every kind of PII, including all personal names or unusual identifiers.
- A context size limit based on **characters** is not a model-token budget.
- Source references identify retrieved chunks; they are not independently verified claim-level citations.
- Prompt-injection defenses reduce risk but do not eliminate it.
- The demo is intended for local development and learning. Production use would require further security reviews, automated tests, deployment hardening, secrets management, monitoring, and backup/recovery planning.


## Project layout

```text
app/
  core/                 # Configuration, database, security, dependencies
  models/               # Users, documents, chunks, permissions, audit logs
  routers/              # Authentication, documents, chat, admin API
  schemas/              # API request/response models
  services/             # Extraction, embeddings, retrieval, PII, LLM, audit
scripts/                # Embedding backfill and retrieval checks
tests/                  # Test scripts, fixtures, optional manual SQL checks
requirements.txt        # Direct dependencies
requirements-lock.txt   # Pinned installed environment
```

