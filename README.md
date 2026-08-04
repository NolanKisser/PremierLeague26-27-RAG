# Premier League RAG Predictor

A Retrieval-Augmented Generation (RAG) platform tailored for predicting the upcoming Premier League table. It leverages PyTorch and Hugging Face `transformers` to ingest football news, transfer updates, injury reports, and historical stats, index them in a custom PyTorch-based vector store, and predict the 20-team final standings based on this contextual data.

## The Problem
Predicting the Premier League table is incredibly difficult due to the sheer volume of variables: managerial changes, unexpected transfers, long-term injuries, and pre-season form. Traditional statistical models often miss the qualitative nuance of breaking news and squad harmony.

## The Agentic RAG Solution
This platform goes beyond basic RAG by implementing **Agentic RAG with Live Web Search**. When a user asks for a table prediction:
1. The backend performs a live web search (via DuckDuckGo) for the latest Premier League news and FPL statistics.
2. It injects this fresh, real-time context into the prompt.
3. The local LLM (Ollama) analyzes the sentiment and impact of those real-world events and formulates a full 20-team prediction table for the 2026/27 season.
## Real-World Data Collection Strategies
To move beyond mock data, you can collect real-world data using the following methods:

1. **Previous Seasons & Match Stats**:
   - **Football-Data.org API**: Provides comprehensive historical match data, standings, and basic team stats.
   - **FBref (via web scraping)**: Excellent source for advanced metrics like xG (expected goals), shot-creating actions, and possession stats. You can use Python libraries like `BeautifulSoup` or `pandas` (via `read_html`) to scrape this.
2. **FIFA Player and Team Ratings**:
   - **EA Sports FC / FIFA API / Kaggle Datasets**: Kaggle regularly hosts up-to-date datasets of all player attributes, overall ratings, and potential from the FIFA video games. These can be embedded as text (e.g., "Arsenal has an overall squad rating of 85, with star player Bukayo Saka rated 87").
   - **SoFIFA scraping**: A popular site for FIFA ratings that can be scraped for the latest squad updates.
3. **News & Transfer Rumors**:
   - **NewsAPI or GNews API**: Search for articles relating to "Premier League", specific teams, or "transfers" to ingest daily news.
   - **Twitter/X API**: Great for real-time injury updates (e.g., from accounts like @FFScout or Fabrizio Romano for transfers).

## Architecture

1. **Agentic Web Search**: Dynamically queries the web for the latest Premier League news using `duckduckgo-search`.
2. **FastAPI Backend**: Provides a robust API endpoint (`/api/predict`) and serves official team PNG logos via `StaticFiles`.
3. **Local LLM Generation**: Uses a local Ollama instance to generate strictly formatted JSON predictions based on the retrieved context.
4. **Vite + Vanilla JS Frontend**: A glassmorphism-styled web interface that renders the prediction table and fetches real team crests from the backend.

## Setup and Execution

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI Backend**:
   ```bash
   uvicorn api:app --reload
   ```

3. **Start the Vite Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Ensure Ollama is running**:
   Make sure you have Ollama installed and a model available (e.g., `llama3`) running locally to process the predictions.
