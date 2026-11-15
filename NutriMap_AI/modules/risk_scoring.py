"""Transparent planning-priority scores; not diagnosis or validated disease probabilities."""
import pandas as pd
from .config import ANEMIA_WEIGHTS, IODINE_WEIGHTS, SCALES, RISK_BANDS

def _indicator_risk(value, column):
    if pd.isna(value) or column not in SCALES: return None
    cfg=SCALES[column]; lo,hi=float(cfg["min"]),float(cfg["max"])
    if hi<=lo: return None
    scaled=max(0.0,min(1.0,(float(value)-lo)/(hi-lo)))
    if cfg["direction"]=="lower": scaled=1.0-scaled
    return scaled*100.0

def classify(score):
    if score is None: return "Insufficient data"
    if score <= RISK_BANDS["low_max"]: return "Low Risk"
    if score <= RISK_BANDS["moderate_max"]: return "Moderate Risk"
    return "High Risk"

def calculate_score(row, weights):
    contributions={}; used_weights={}
    for col,weight in weights.items():
        if col in row.index:
            risk=_indicator_risk(row[col],col)
            if risk is not None:
                contributions[col]=round(risk,1); used_weights[col]=float(weight)
    if not used_weights: return {"score":None,"category":"Insufficient data","contributors":{},"coverage":0.0}
    total=sum(used_weights.values())
    score=sum(contributions[c]*(used_weights[c]/total) for c in contributions)
    return {"score":round(score,1),"category":classify(score),"contributors":contributions,
            "coverage":round(total/sum(weights.values())*100,1)}

def add_risk_scores(df):
    out=df.copy(); anemia=[]; iodine=[]
    for _,row in out.iterrows():
        anemia.append(calculate_score(row,ANEMIA_WEIGHTS)); iodine.append(calculate_score(row,IODINE_WEIGHTS))
    out["Anemia_Risk_Score"]=[x["score"] for x in anemia]
    out["Anemia_Risk_Category"]=[x["category"] for x in anemia]
    out["Iodine_Risk_Score"]=[x["score"] for x in iodine]
    out["Iodine_Risk_Category"]=[x["category"] for x in iodine]
    return out
