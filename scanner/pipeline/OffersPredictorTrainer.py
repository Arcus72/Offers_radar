from pipeline.PipelineTemplate import PipelineTemplate
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.ensemble import HistGradientBoostingRegressor

from pathlib import Path
import pandas as pd
import joblib


class OffersPredictorTrainer (PipelineTemplate):
    TABLE = "offers"
    PIPELINE_PATH = Path(__file__).parent.parent / "model" / "pipeline.joblib"
    def __init__(self, db):
        self.db = db
        self.pipeline = None
        self.all_offers = []

    def extract(self):
        self.all_offers = self.db.get_all_data(self.TABLE)
        
    def transform(self):
        

        df = pd.DataFrame(self.all_offers)
        df.dropna(subset=["price"], inplace=True)
        X = df.drop(columns=['price'])
        y = df['price']

        cat_cols = ["city","type","building_type","building_material","kitchen_type","parking", "condition","heating"]
        num_cols = ["area","rooms","bed_rooms","bathrooms","floor","building_floors","build_year","balcony_area","rent_fee","school_dist","kindergarten_dist","university_dist","shop_dist","public_transport_dist","park_dist","medical_dist","pharmacy_dist","city_center_dist"]
        bool_cols = ["lift","has_balcony","storage_room","accessible","fenced","monitoring", "school","kindergarten","university","shop","public_transport","park","medical", "pharmacy","city_center"]

        to_float = FunctionTransformer(pd.DataFrame.astype, kw_args={"dtype": float})  # None -> NaN, True/False -> 1/0
        cat_pipe = make_pipeline(
            FunctionTransformer(pd.DataFrame.mask, kw_args={"cond": pd.isna, "other": float("nan")}),  # None -> NaN
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
        )

        pipeline = Pipeline([
            ("preprocessor", ColumnTransformer([("num", to_float, num_cols),
                                                ("cat", cat_pipe, cat_cols),
                                                ("bool", to_float, bool_cols)])),
            ("model", HistGradientBoostingRegressor(random_state=42)),
        ])

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        r2   = r2_score(y_test, y_pred)
        mae  = mean_absolute_error(y_test, y_pred)
        rmse = root_mean_squared_error(y_test, y_pred)

        print(f"R2: {r2:.3f} | MAE: {mae:,.0f} | RMSE: {rmse:,.0f}")

        self.pipeline = pipeline


    def load(self):
        if not self.pipeline:
            raise ValueError("Pipeline is not trained yet. Call train_model() first.")
        joblib.dump(self.pipeline, self.PIPELINE_PATH)