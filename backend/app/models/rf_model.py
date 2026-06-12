## app/models/rf_model.py
import joblib
import pandas as pd

class RandomForestPDFModel:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)
        self.feature_names = ['/JavaScript', '/JS', '/Launch', '/OpenAction', '/AA', '/AcroForm', '/XFA', '/URI', '/EmbeddedFile', '/RichMedia']

    def predict(self, pdf_feature_dict):
        df = pd.DataFrame([pdf_feature_dict], columns=self.feature_names)
        prediction = self.model.predict(df)[0]
        proba = self.model.predict_proba(df)[0]
        return prediction, proba
