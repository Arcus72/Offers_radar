from components.OffersScraper import OffersScraper
from schemas.RawOfferData import RawOfferData

from typing import Literal
from pipeline.PipelineTemplate import PipelineTemplate


class OffersCollector(PipelineTemplate):
    TABLE = "raw_offers"

    def __init__(self, db, mode: Literal["TOTAL", "NEW", "LATEST"] = "LATEST", limit = 100):
        # Mode explain:
        # TOTAL - collecting ends when total amount of entries (new + old) reach limit
        # New - collecting ends when total amount of new entries reach limit
        # LATEST - collection end when new offer is already in database
        self.db = db
        self.mode = mode
        self.limit = limit
        self.collected_offers_id = db.get_all_offers_id("offers")
        print(f"Collected offers id: {len(self.collected_offers_id)}")
        print(list(self.collected_offers_id)[:10])
        self.new_offers: list[RawOfferData] = []


    def is_limit_reached(self):
        if self.mode == "NEW":
            if len(self.new_offers) >= self.limit:
                return True

        if self.mode == "TOTAL":
            if len(self.collected_offers_id) >= self.limit:
                return True

        return False

    def show_progress(self, page, link_i,   offer_id):
        print(f"\n\nFetching new entry. Page: {page}, offer: {link_i}, offer's id: {offer_id}")
        if self.mode == "NEW":
            print(f"new: {len(self.new_offers)}, stop at: {self.limit}")
        elif self.mode == "TOTAL":
            print(f"total: {len(self.collected_offers_id)}, stop at: {self.limit}")
        else:
            print(f"new: {len(self.new_offers)}")
        

    def extract(self):

        if self.is_limit_reached():
            return 

        # 100 pages * 30 offers = 3000 entries
        page = 1
        while True:
            url = f"https://tabelaofert.pl/sprzedaz/mieszkania?sort=najnowsze&rynek=wtorny&page={page}"
            offers_links = OffersScraper.get_offers(url)

            if offers_links is None:
                print("Failed to fetch offers page. Skipping.")
                page += 1
                continue

            if len(offers_links) == 0:
                print("Koniec stron!!!")
                return

            for link_i, link in enumerate(offers_links, start=1):
                offer_id = int(link.split(",")[-1])

                self.show_progress(page, link_i, offer_id)

                if offer_id in self.collected_offers_id:
                    if self.mode == "LATEST":
                        return self
                    print("id w db. Skipping.")
                    continue

                offer = OffersScraper.from_offer_id(offer_id)

                if offer is None:
                    print("Scalping -> Failed to fetch data. Skipping.")
                    continue

                self.new_offers.append(RawOfferData(**offer.get_all_data()))
                self.collected_offers_id.add(offer_id)

                if self.is_limit_reached():
                    return

            page += 1

        return

    def transform(self):
        return 


    def load(self) -> list[int]:
        saved = self.db.insert_many(self.new_offers, table=self.TABLE)
        print(f"Saved {len(saved)} new offers to database")
