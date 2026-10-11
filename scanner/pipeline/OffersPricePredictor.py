from pathlib import Path
import pandas as pd
import joblib


from schemas.OfferFormat import OfferFormat
from pipeline.PipelineTemplate import PipelineTemplate


class OffersPricePredictor(PipelineTemplate):
    TABLE = "offers"
    PIPELINE_PATH = Path(__file__).parent.parent / "model" / "pipeline.joblib"

    def __init__(self, db):
        self.db = db
        self.pipeline = joblib.load(self.PIPELINE_PATH)
        self.market_prices = []

    def extract(self):
        self.rows = self.db.get_missing_market_price(self.TABLE)

    def transform(self) :
        if not self.rows:
            return 

        expected_columns = self.pipeline.feature_names_in_

        # Reorder columns to match the model's expected input
        offer_df = pd.DataFrame(self.rows, columns=expected_columns)

        # Make prediction
        self.market_prices = self.pipeline.predict(offer_df).round().astype(int).tolist()
        
     
    def load(self):
        if not self.market_prices:
            return

        offer_ids = [offer["offer_id"] for offer in self.rows]
        self.db.update_column(list(zip(offer_ids, self.market_prices)), "market_price", self.TABLE)

        