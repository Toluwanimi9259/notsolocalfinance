# Finance AI Assistant 💰🤖

A premium, production-ready personal finance assistant powered by **Mistral Nemo** and **Qdrant**. This application allows users to upload their bank statements (CSV/PDF), automatically embeds the data into a vector database, and uses a multi-agent tool-calling system to provide deep financial insights.

## 🚀 Recent Accomplishments & Progress

We have transformed this from a local prototype into a secure, multi-tenant web application.

### 🔐 Security & Identity
- **Stateless GitHub OAuth**: Replaced local password management with a secure, stateless GitHub OAuth2 flow. No user passwords are stored locally.
- **JWT-Based Sessions**: Implemented JSON Web Tokens for session management, ensuring fast and secure authenticated requests.
- **Identity Isolation**: Engineered the system to use GitHub IDs as unique identifiers, ensuring total data isolation in the vector database.

### 🏛️ Architectural Evolution
- **From OpenAI to Pydantic AI**: Successfully transitioned the entire agent logic from raw, unstructured OpenAI API calls to the **Pydantic AI** framework. This provided:
    - **Type-Safe Tools**: Unified tool-calling using Python type hints.
    - **Structured Dependencies**: Clean separation of RAG and Auth context.
    - **Better Reasoning**: Native support for advanced models like Mistral and Gemini via OpenRouter.
- **Mistral Nemo Integration**: Upgraded the core agent to use Mistral Nemo (via OpenRouter) for superior reasoning and financial tool use.
- **20+ Specialized Tools**: Equipped the agent with tools for spending velocity, anomaly detection, merchant comparison, and subscription tracking.
- **RAG (Retrieval-Augmented Generation)**: Integrated Qdrant with local FastEmbed support for high-speed semantic search across years of financial data.

### 📊 Data Processing
- **Robust Multi-Format Parsing**: Built an advanced ingestion engine that handles complex PDF layouts and CSV bank statements with varying schemas.
- **Automatic Schema Mapping**: The parser automatically identifies date, description, and currency columns using a fuzzy-matching alias system.
- **Smart Formatting**: Standardizes all dates into YYYY-MM-DD for accurate time-series analysis by the AI.

### 🎨 User Experience
- **Premium Dashboard**: A sleek, dark-mode interface with glassmorphism aesthetics and real-time chat.
- **Action-Oriented Feedback**: Instant parsing feedback and a dedicated transaction loading indicator.

## 🛠️ Setup & Local Development

### 1. Requirements
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [Qdrant](https://qdrant.tech/documentation/quick-start/) (Vector Database - running on port 6333)

### 2. Environment Variables
Create a `.env` file based on `.env.example`:
```env
OPENROUTER_API_KEY=your_key
GITHUB_CLIENT_ID=your_id
GITHUB_CLIENT_SECRET=your_secret
JWT_SECRET_KEY=some_long_random_string
QDRANT_HOST=http://localhost
QDRANT_PORT=6333
```

### 3. Running the App
```powershell
uv sync
uv run uvicorn main:app --port 7536 --reload
```

## 📈 Roadmap
- [ ] Interactive spending charts (Chart.js)
- [ ] Exportable financial reports
- [ ] Multi-currency conversion support
