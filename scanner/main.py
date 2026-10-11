
from components.DatabaseManager import DatabaseManager

from pipeline.OffersCollector import OffersCollector
from pipeline.OffersFormatter import OffersFormatter
from pipeline.OffersPricePredictor import OffersPricePredictor
from pipeline.OffersPredictorTrainer import OffersPredictorTrainer
from pipeline.OffersUpdater import OffersUpdater

import os
from dotenv import load_dotenv
from schemas.RawOfferData import RawOfferData

load_dotenv()

if __name__ == "__main__":
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    UPDATE_PRICES = True
    TRAIN_PIPELINE = True


    with DatabaseManager(db_name, db_user, db_pass, db_host, db_port) as db:

        if UPDATE_PRICES:
            print("Updating prices for existing offers")
            OffersUpdater(db).run()

        print("Scanning for new offers")
        db.clear_table(OffersCollector.TABLE)
        OffersCollector(db, mode="NEW", limit=5).run()
    
        print("Formatting new offers")
        OffersFormatter(db).run()
        db.clear_table(OffersCollector.TABLE)

        if TRAIN_PIPELINE:
            print("Training new model")
            OffersPredictorTrainer(db).run()
           
        print("Market price predicting")
        OffersPricePredictor(db).run()
