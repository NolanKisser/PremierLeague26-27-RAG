# Premier League RAG Predictor

A Retrieval-Augmented Generation (RAG) platform tailored for predicting the upcoming Premier League table. It leverages PyTorch and Hugging Face `transformers` to ingest football news, transfer updates, injury reports, and historical stats, index them in a custom PyTorch-based vector store, and predict the 20-team final standings based on this contextual data.

## The Problem
Predicting the Premier League table is incredibly difficult due to the sheer volume of variables: managerial changes, unexpected transfers, long-term injuries, and pre-season form. Traditional statistical models often miss the qualitative nuance of breaking news and squad harmony.

## The RAG Solution
This platform ingests various sources of textual data (news articles, team press releases, fan sentiment analysis). When a user asks for a table prediction, the Predictor checks the most relevant and recent news from the vector database, analyzes the sentiment and impact of those events, and adjusts its baseline 20-team prediction accordingly.

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

1. **Document Ingestion**: Parses and chunks news articles and statistics.
2. **PyTorch Embedder**: Uses Hugging Face `transformers` to convert chunks into dense vector embeddings.
3. **PyTorch Vector Store**: A custom PyTorch tensor-based vector database that performs fast cosine-similarity search.
4. **Predictor**: Retrieves the most relevant news context based on the query and formulates a full 20-team prediction table.

## Setup and Execution

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the prototype**:
   ```bash
   python main.py
   ```
   *This script will automatically generate sample news/stats data for all 20 teams, index them, and predict the final table based on this context.*

