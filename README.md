# Offers Scanner

A full-stack property analytics and search system that collects apartment sale offers from [tabelaofert.pl](https://tabelaofert.pl), turns free-text listings into structured data, estimates market prices via machine learning, and provides an interactive AI conversational agent for search.

The system is split into **two primary modules**:

1. **Pipeline**: Automated ETL process for scraping, data extraction with LLM, price estimation, and ML model training.
2. **Chatbot**: Conversational agent operating on a state-graph architecture (LangGraph) to process user search preferences and recommend listings.

## 1. Pipeline Module

The **Pipeline** runs automated data processing steps built on `PipelineTemplate` (`extract` → `transform` → `load`):

| Step        | Class                    | What it does                                                                                                                              |
| ----------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 1\. Update  | `OffersUpdater`          | Re-checks the price of stored offers and removes deleted listings (HTTP 410).                                                             |
| 2\. Collect | `OffersCollector`        | Scrapes the newest listings into the temporary `raw_offers` table.                                                                        |
| 3\. Format  | `OffersFormatter`        | An LLM (Gemini API) extracts ~50 structured fields from descriptions (area, rooms, floor, heating, amenities) and saves them to `offers`. |
| 4\. Predict | `OffersPricePredictor`   | Predicts the `market_price` for offers using the trained machine learning model.                                                          |
| 5\. Train   | `OffersPredictorTrainer` | Retrains the price model on all stored offers and saves the artifact to `scanner/model/pipeline.joblib`.                                  |

Comparing `price` with `market_price` highlights whether an offer is under- or overpriced.

## 2. Chatbot Module

The **Chatbot** module runs an interactive terminal session (`main.py`) powered by a stateful graph architecture (LangGraph) to guide users through property queries:

- **Intent Routing (`route_intent`)**: Classifies messages into criteria extraction, feedback adjustment, help requests, or generic conversational responses.
- **Filter Extraction & Feedback (`extract_filters`, `extract_feedback`)**: Converts natural language requests into structured `FiltersFormat` Pydantic models (e.g., city, price range, room counts).
- **Constraint Validation (`clarify_request`, `route_after_filters`)**: Ensures mandatory criteria (such as target city) are provided before executing queries.
- **Data Retrieval & Presentation (`get_offers`, `explain_offers`)**: Queries stored offers from PostgreSQL and formats recommendations highlighting key property attributes.

## Technologies

- **Python 3.12**, dependencies managed with **uv**
- **Requests + BeautifulSoup** — scraping
- **Pydantic** — data validation schemas for LLM outputs, database rows, and search filters
- **LangChain / LangGraph** — chatbot state-graph orchestration and structured outputs
- **Google Generative AI (Gemini API)** — structured data extraction and conversational intelligence
- **PostgreSQL 17** — primary database storage
- **scikit-learn** (`HistGradientBoostingRegressor`) + **pandas** — price valuation model
- **Apache Airflow 3** (CeleryExecutor, Redis) — task orchestration and scheduling
- **Docker Compose** — multi-container deployment

## Configuration

Create a `.env` file in the project root:

```env
DB_NAME=accdata
DB_USER=postgres
DB_PASS=<your password>
DB_HOST=db
DB_PORT=5432
GEMINI_API_KEY=<your_gemini_api_key>

# Airflow (prod profile only)
AIRFLOW_UID=50000
AIRFLOW_PROJ_DIR=./scanner
_PIP_ADDITIONAL_REQUIREMENTS=langchain-google-genai beautifulsoup4 scikit-learn==1.8.0 joblib
```

## Docker profiles

The project uses Docker Compose profiles to run specific combinations of services based on your workflow.

### `chatbot`

Runs **`db` + Chatbot**. Use this profile to interact with the conversational agent using existing data in PostgreSQL without running the ETL data pipeline.

```bash
docker compose --profile chatbot up --build
```

### `scanner`

Runs **`db` + Scanner (Pipeline)**. Runs the full ETL pipeline once from start to finish (`scanner/main.py`) and stops when completed.

```bash
docker compose --profile scanner up --build
```

For live reload during pipeline development:

```bash
docker compose --profile scanner watch
```

### `scanner-airflow`

Runs **`db` + Airflow** for the scanner. Starts the PostgreSQL database and the Airflow stack (`apiserver`, `scheduler`, `dag-processor`, `worker`, `triggerer`, `redis`) to manage and execute scheduled pipeline runs.

```bash
docker compose --profile scanner-airflow up -d
```

1. Access the Airflow UI at <http://localhost:8080> (credentials: `airflow` / `airflow`).
2. Unpause the `scanner` DAG.

### `prod`

Runs **`db` + Airflow (for scanner) + Chatbot**. Launches the complete production stack, allowing Airflow to manage scheduled scanner pipeline execution while keeping the interactive chatbot active.

```bash
docker compose --profile prod up -d
```

Add `-v` to also delete persisted database volumes.

## Database Backup

The `db_backup/` directory is mounted into the `db` container.

```bash
# Export offers table to db_backup/offers.csv
docker compose exec db psql -U postgres -d accdata -c "COPY offers TO '/db_backup/offers.csv' WITH (FORMAT csv, DELIMITER ';', HEADER)"

# Restore offers table from db_backup/offers.csv
docker compose exec db psql -U postgres -d accdata -f /db_backup/restore.sql
```

## Project Structure

```
├── Docker/                  # Service compose files (airflow, chatbot, postgres, scanner)
├── chatbot/                 # Conversational AI Agent module (LangGraph)
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src/
│       ├── main.py          # Chatbot CLI entry point
│       ├── graph.py         # LangGraph execution workflow setup
│       ├── state.py         # Chatbot state management schema
│       ├── nodes/           # Graph workflow nodes (intent routing, filter extraction, response generation)
│       ├── components/      # LLM Agent wrapper & Database manager
│       ├── schemas/         # Pydantic data schemas (FiltersFormat, RouteIntentResponse)
│       └── utils/           # Helper functions
├── db_backup/               # CSV exports and database restore scripts
├── docker-compose.yaml      # Includes service definitions from Docker/
└── scanner/                 # ETL Data Pipeline module
    ├── Dockerfile
    ├── pyproject.toml
    ├── main.py              # Pipeline CLI entry point
    ├── config/              # Airflow configuration files
    ├── dags/                # Airflow DAG schedules
    ├── pipeline/            # ETL steps (Collector, Formatter, Predictor, Trainer, Updater)
    ├── components/          # Web scraper, LLM Formatter, Database manager
    ├── schemas/             # Pydantic data models (OfferFormat, RawOfferData)
    └── model/               # Trained ML price model artifact

```
