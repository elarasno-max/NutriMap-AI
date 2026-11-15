"""Supervised models are trained only from supplied genuine labels; no synthetic labels are created."""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

TARGETS={"anemia":"Anemia_Risk","iodine":"Iodine_Risk"}
EXCLUDED={"Anemia_Risk","Iodine_Risk","Anemia_Prevalence","Iron_Deficiency_Prevalence","Median_Urinary_Iodine"}
FEATURE_CANDIDATES=["Province","Soil_Iron","Soil_Iodine","Soil_pH","Water_Iron","Water_Iodine","Water_Fluoride",
                    "Dietary_Iron_Intake","Dietary_Diversity","Iodized_Salt_Access"]

def train_model(df, outcome="anemia", model_type="Random Forest", model_dir="models"):
    target=TARGETS[outcome]
    if target not in df.columns: return {"trained":False,"reason":f"Required genuine target column {target} is absent."}
    features=[c for c in FEATURE_CANDIDATES if c in df.columns and c not in EXCLUDED]
    work=df[features+[target]].dropna(subset=[target]).copy()
    if len(features)==0: return {"trained":False,"reason":"No eligible predictor columns are available."}
    y=work[target].astype(str)
    counts=y.value_counts()
    if len(counts)<2 or counts.min()<4 or len(work)<12:
        return {"trained":False,"reason":"Insufficient independent labelled records/classes. Need at least 12 labelled rows, 2 classes, and 4 records in the smallest class as a minimum screening rule."}
    X=work[features]
    cat=[c for c in features if X[c].dtype=="object"]
    num=[c for c in features if c not in cat]
    pre=ColumnTransformer([("num",Pipeline([("imputer",SimpleImputer(strategy="median"))]),num),
                           ("cat",Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),cat)])
    estimator=DecisionTreeClassifier(max_depth=4,random_state=42) if model_type=="Decision Tree" else RandomForestClassifier(n_estimators=200,min_samples_leaf=2,random_state=42,class_weight="balanced")
    pipe=Pipeline([("preprocess",pre),("model",estimator)])
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.25,random_state=42,stratify=y)
    pipe.fit(Xtr,ytr); pred=pipe.predict(Xte)
    precision,recall,f1,_=precision_recall_fscore_support(yte,pred,average="weighted",zero_division=0)
    cv=None
    min_class=int(y.value_counts().min())
    folds=min(5,min_class)
    if folds>=2 and len(work)>=20:
        try: cv=[round(float(v),3) for v in cross_val_score(pipe,X,y,cv=folds,scoring="f1_weighted")]
        except Exception: cv=None
    Path(model_dir).mkdir(parents=True,exist_ok=True)
    path=Path(model_dir)/f"{outcome}_model.joblib"; joblib.dump({"pipeline":pipe,"features":features,"target":target},path)
    return {"trained":True,"path":str(path),"features":features,"target":target,"accuracy":round(accuracy_score(yte,pred),3),
            "precision":round(float(precision),3),"recall":round(float(recall),3),"f1":round(float(f1),3),
            "confusion_matrix":confusion_matrix(yte,pred).tolist(),"classification_report":classification_report(yte,pred,zero_division=0),"cv_f1":cv}

def load_model(outcome="anemia", model_dir="models"):
    path=Path(model_dir)/f"{outcome}_model.joblib"
    return joblib.load(path) if path.exists() else None
