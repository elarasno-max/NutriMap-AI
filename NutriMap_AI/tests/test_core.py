import unittest
import pandas as pd
from modules.data_loader import load_demo_data
from modules.data_cleaning import validate_dataset,clean_dataset
from modules.risk_scoring import add_risk_scores
from modules.recommendations import generate_recommendations

class TestNutriMap(unittest.TestCase):
    def test_demo_load_and_validation(self):
        df=load_demo_data(); self.assertTrue(validate_dataset(df)["valid"])
    def test_clean_duplicates_and_types(self):
        df=load_demo_data(); df=pd.concat([df,df.iloc[[0]]],ignore_index=True)
        cleaned,log=clean_dataset(df); self.assertEqual(log["duplicates_removed"],1)
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned["Latitude"]))
    def test_scores_created(self):
        out=add_risk_scores(load_demo_data()); self.assertIn("Anemia_Risk_Category",out)
        self.assertTrue(out["Anemia_Risk_Score"].notna().all())
    def test_missing_measurements_not_fabricated(self):
        df=load_demo_data().iloc[[0]].copy(); df["Anemia_Prevalence"]=None; df["Iron_Deficiency_Prevalence"]=None; df["Dietary_Iron_Intake"]=None; df["Dietary_Diversity"]=None
        out=add_risk_scores(df); self.assertEqual(out.iloc[0]["Anemia_Risk_Category"],"Insufficient data")
    def test_recommendations(self):
        row=add_risk_scores(load_demo_data()).iloc[0]; self.assertTrue(len(generate_recommendations(row))>0)

if __name__=="__main__": unittest.main()
