# Offers Scanner

A data pipeline that collects apartment sale offers from [tabelaofert.pl](https://tabelaofert.pl), turns the free-text listings into structured data with a local LLM, and estimates a true market price for each offer with a machine-learning model.

**Coming soon:** a conversational agent that talks with the user and recommends offers based on the collected data (the `api/` and `frontend/` folders are placeholders for it).

## How it works

Every step is a small ETL class (`extract` → `transform` → `load`) built on `PipelineTemplate`:

| Step       | Class                    | What it does                                                                                                                                              |
| ---------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Update  | `OffersUpdater`          | Re-checks the price of every stored offer and deletes offers that are gone (HTTP 410).                                                                    |
| 2. Collect | `OffersCollector`        | Scrapes the newest listings into the temporary `raw_offers` table.                                                                                        |
| 3. Format  | `OffersFormatter`        | An LLM (Ollama) extracts ~50 structured fields from each description (area, rooms, floor, heating, distances to amenities, …) and saves them to `offers`. |
| 4. Predict | `OffersPricePredictor`   | Fills `market_price` for offers that don't have one, using the trained model.                                                                             |
| 5. Train   | `OffersPredictorTrainer` | Retrains the price model on all offers and saves it to `scanner/model/pipeline.joblib`.                                                                   |

Comparing `price` with `market_price` is what shows whether an offer is under- or overpriced.

## Technologies

- **Python 3.12**, dependencies managed with **uv**
- **Requests + BeautifulSoup** — scraping
- **Ollama** (`qwen3.5:9b`) + **LangChain** — structured extraction from listing text
- **Pydantic** — schemas for the LLM output and database rows
- **PostgreSQL 17** — offers storage
- **scikit-learn** (`HistGradientBoostingRegressor`) + **pandas** — market price model
- **Apache Airflow 3** (CeleryExecutor, Redis) — scheduling
- **Docker Compose** — everything runs in containers

## Requirements

- Docker with Docker Compose
- An NVIDIA GPU with the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) — the Ollama container reserves a GPU
- Around 10 GB of free disk space (the LLM is downloaded on first start)

## Configuration

Create a `.env` file in the project root:

```env
DB_NAME=accdata
DB_USER=postgres
DB_PASS=<your password>
DB_HOST=db
DB_PORT=5432
OLLAMA_BASE_URL=http://ollama:11434

# Airflow (prod profile only)
AIRFLOW_UID=50000
AIRFLOW_PROJ_DIR=./scanner
_PIP_ADDITIONAL_REQUIREMENTS=langchain-ollama beautifulsoup4 scikit-learn==1.8.0 joblib
```

## Running

Both profiles start the shared services: **`db`** (PostgreSQL, exposed on `localhost:5433`) and **`ollama`** (LLM server on `localhost:11434`, pulls the model on first start).

### `dev` — run the pipeline once

```bash
docker compose --profile dev up --build
```

Adds the **`app`** container, which runs `scanner/main.py`: the whole pipeline once, start to finish, with logs in the terminal. Use it while working on the code.

For live reload, use watch mode — it syncs `scanner/` into the container and restarts it on every change, and rebuilds the image when `uv.lock` changes:

```bash
docker compose --profile dev watch
```

### `prod` — scheduled runs with Airflow

```bash
docker compose --profile prod up -d
```

Adds the Airflow stack: `airflow-apiserver`, `airflow-scheduler`, `airflow-dag-processor`, `airflow-worker`, `airflow-triggerer`, a one-off `airflow-init`, plus Airflow's own `postgres` (metadata) and `redis` (task queue).

1. Open the Airflow UI at <http://localhost:8080> (login `airflow` / `airflow`).
2. Unpause the `scanner` DAG — DAGs are paused when first created.

The DAG (`scanner/dags/scanner.py`) runs **daily**: collect → format → predict. On **Mondays** it also updates prices of existing offers before collecting and retrains the model at the end.

### Stopping

```bash
docker compose --profile dev --profile prod down
```

Add `-v` to also delete the volumes (database contents and the downloaded LLM).

## Database backup

The `db_backup/` folder is mounted into the `db` container. The `offers` table must already exist before restoring.

```bash
# Export the offers table to db_backup/offers.csv
docker compose exec db psql -U postgres -d accdata -c "COPY offers TO '/db_backup/offers.csv' WITH (FORMAT csv, DELIMITER ';', HEADER)"

# Restore from db_backup/offers.csv (offers already in the table are skipped)
docker compose exec db psql -U postgres -d accdata -f /db_backup/restore.sql
```

## Project structure

```
├── docker-compose.yaml      # includes the files from Docker/
├── Docker/                  # one compose file per service group
├── db_backup/               # CSV export + restore script
└── scanner/
    ├── main.py              # dev entry point: runs the pipeline once
    ├── dags/                # Airflow DAG
    ├── pipeline/            # ETL steps
    ├── components/          # scraper, LLM formatter, database manager
    ├── schemas/             # Pydantic models
    └── model/               # trained price model + training notebook
```
