from components.OffersScraper import OffersScraper
from pipeline.PipelineTemplate import PipelineTemplate
import time

class OffersUpdater(PipelineTemplate):
    def __init__(self, db):
        self.db = db
        self.all_offers_id = []
        self.to_update_ids = []
        self.to_delete_ids = []

    def extract(self):
        self.all_offers_id = self.db.get_all_offers_id()

    def transform(self):
        offer_i = 1
        total_offers_amount = len(self.all_offers_id)
        for offer_id in self.all_offers_id:
            print(f"Updating: {offer_i}/{total_offers_amount}")
            scraper = OffersScraper.from_offer_id(offer_id)
            if scraper:
                new_price = scraper.get_price()
                if new_price:
                    self.to_update_ids.append((offer_id, new_price))
            else:
                code = OffersScraper.get_status_code(offer_id)
                if code in [410]:
                    self.to_delete_ids.append(offer_id)
                    print("DELETED")
            offer_i += 1
            time.sleep(1)

    def load(self):
        if self.to_update_ids:
            self.db.update_column(self.to_update_ids, "price")
        
        if self.to_delete_ids:
            self.db.delete_values(self.to_delete_ids, "offer_id")

