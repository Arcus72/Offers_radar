
import os
import pendulum
from airflow.decorators import dag, task

from components.DatabaseManager import DatabaseManager
from schemas.RawOfferData import RawOfferData
from pipeline.OffersCollector import OffersCollector
from pipeline.OffersFormatter import OffersFormatter
from pipeline.OffersPricePredictor import OffersPricePredictor
from pipeline.OffersPredictorTrainer import OffersPredictorTrainer
from pipeline.OffersUpdater import OffersUpdater


def get_db():
    return DatabaseManager(
        os.getenv("DB_NAME"), os.getenv("DB_USER"), os.getenv("DB_PASS"),
        os.getenv("DB_HOST"), os.getenv("DB_PORT"),
    )


@dag(
    dag_id="scanner",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Warsaw"),
    catchup=False,
    max_active_runs=1,
)
def offers_scanner():

    @task.short_circuit(ignore_downstream_trigger_rules=False)
    def only_monday():
        return pendulum.now("Europe/Warsaw").weekday() == 0  # 0 = Monday

    @task
    def update_prices():
        with get_db() as db:
            OffersUpdater(db).run()

    @task(trigger_rule="none_failed")
    def extract_offers():
        with get_db() as db:
            db.drop_table(OffersCollector.TABLE)
            db.create_table(RawOfferData, OffersCollector.TABLE)
            OffersCollector(db, mode="LATEST").run()

    @task
    def transform_offers():
        with get_db() as db:
            OffersFormatter(db).run()
            print("Formatted new offers and saved to database")
            db.drop_table(OffersCollector.TABLE)

    @task
    def fill_market_prices():
        with get_db() as db:
            OffersPricePredictor(db).run()

    @task
    def train_model():
        with get_db() as db:
            OffersPredictorTrainer(db).run()

    (
        only_monday.override(task_id="monday_before_update")()
        >> update_prices()
        >> extract_offers()
        >> transform_offers()
        >> fill_market_prices()
        >> only_monday.override(task_id="monday_before_training")()
        >> train_model()
    )


offers_scanner()