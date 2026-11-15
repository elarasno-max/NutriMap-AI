from pathlib import Path
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from modules.data_loader import load_demo_data
from modules.data_cleaning import validate_dataset, clean_dataset, missing_summary
from modules.risk_scoring import add_risk_scores
from modules.data_analysis import regional_summary, make_charts
from modules.risk_map import create_risk_map
from modules.recommendations import generate_recommendations
from modules.report_generator import regional_pdf
from modules.ml_models import train_model

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="NutriMap AI",page_icon="🌱",layout="wide")
st.markdown("""<style>
.stApp{background:#f6f9f8}.block-container{padding-top:1.5rem}.metric-card{background:white;border:1px solid #e5eeea;border-radius:14px;padding:16px}
h1,h2,h3{color:#142d3c}.stButton>button{border-radius:9px;background:#087f70;color:white;border:0}
</style>""",unsafe_allow_html=True)
st.title("🌱 NutriMap AI")
st.caption("Regional Micro-Nutrient Risk Predictor | Public-health planning support, not a diagnostic tool")
if "data" not in st.session_state:
    st.session_state.data=load_demo_data(); st.session_state.demo=True
with st.sidebar:
    st.header("NutriMap AI")
    page=st.radio("Navigation",["Overview","Regional Explorer","Data Quality & Upload","Analysis","Model Lab","About & Sources"])
    st.divider(); st.caption("Dataset")
    upload=st.file_uploader("Upload regional CSV",type=["csv"])
    if upload is not None:
        try:
            candidate=pd.read_csv(upload); report=validate_dataset(candidate)
            if report["valid"]:
                st.session_state.data=candidate; st.session_state.demo=False; st.success("Dataset loaded")
            else: st.error("Dataset not loaded: "+"; ".join(report["issues"]))
        except Exception as e: st.error(f"Could not read CSV: {e}")
    st.caption("Initial view uses synthetic demonstration data." if st.session_state.demo else "Using uploaded data.")

df,clean_log=clean_dataset(st.session_state.data)
df=add_risk_scores(df)
if "Province" not in df: df["Province"]="Unknown"
provinces=["All"]+sorted(df["Province"].dropna().astype(str).unique().tolist())
with st.sidebar:
    province=st.selectbox("Province filter",provinces)
    years=sorted(df["Survey_Year"].dropna().astype(int).unique().tolist()) if "Survey_Year" in df else []
    year=st.selectbox("Survey year",["All"]+years)
filtered=df.copy()
if province!="All": filtered=filtered[filtered.Province.astype(str)==province]
if year!="All": filtered=filtered[filtered.Survey_Year==year]

def kpi(label,value):
    st.markdown(f'<div class="metric-card"><div style="color:#60756f;font-size:13px">{label}</div><div style="font-size:27px;font-weight:700;color:#123b3b">{value}</div></div>',unsafe_allow_html=True)

if page=="Overview":
    st.subheader("Regional nutrition intelligence")
    if st.session_state.demo: st.warning("DEMONSTRATION MODE — all sample measurements are synthetic and do not represent real Pakistani regions or populations.")
    total=len(filtered); high=int((filtered.Anemia_Risk_Category=="High Risk").sum()); moderate=int((filtered.Anemia_Risk_Category=="Moderate Risk").sum()); low=int((filtered.Anemia_Risk_Category=="Low Risk").sum())
    cols=st.columns(5)
    for c,(lab,val) in zip(cols,[("Regions analyzed",total),("High priority",high),("Moderate priority",moderate),("Low priority",low),("Coverage",f"{(filtered.Anemia_Risk_Score.notna().mean()*100):.0f}%" if total else "0%")]):
        with c:kpi(lab,val)
    st.markdown("### Pakistan regional risk view")
    risk_type=st.selectbox("Map layer",["Anemia","Iodine","Iron-deficiency context"])
    if risk_type=="Anemia": rc,sc="Anemia_Risk_Category","Anemia_Risk_Score"
    elif risk_type=="Iodine": rc,sc="Iodine_Risk_Category","Iodine_Risk_Score"
    else: rc,sc="Anemia_Risk_Category","Anemia_Risk_Score"
    fmap=create_risk_map(filtered,rc,sc)
    st_folium(fmap,use_container_width=True,height=470)
    st.caption("Markers are plotted at the coordinates supplied in the dataset. They are not district boundaries.")
    st.markdown("### Regional snapshot")
    show=[c for c in ["Region","Province","Anemia_Risk_Score","Anemia_Risk_Category","Iodine_Risk_Score","Iodine_Risk_Category"] if c in filtered]
    st.dataframe(filtered[show],use_container_width=True,hide_index=True)
elif page=="Regional Explorer":
    st.subheader("Regional explorer")
    regions=filtered.Region.dropna().astype(str).unique().tolist() if "Region" in filtered else []
    if not regions: st.info("No region names available.")
    else:
        selected=st.selectbox("Select region",regions); row=filtered[filtered.Region.astype(str)==selected].iloc[0]
        c1,c2=st.columns(2)
        with c1:kpi("Anemia planning score",row.get("Anemia_Risk_Score") if pd.notna(row.get("Anemia_Risk_Score")) else "Insufficient data")
        with c2:kpi("Iodine planning score",row.get("Iodine_Risk_Score") if pd.notna(row.get("Iodine_Risk_Score")) else "Insufficient data")
        st.write("**Data quality:** scores use only available eligible indicators; missing indicators are omitted and coverage is reduced.")
        st.json({k:(None if pd.isna(v) else v) for k,v in row.to_dict().items() if k not in ["geometry"]})
        st.markdown("### Evidence-linked planning suggestions")
        recs=generate_recommendations(row)
        for rec in recs: st.markdown("- "+rec)
        pdf=regional_pdf(row,recs,"Synthetic demonstration dataset" if st.session_state.demo else "Uploaded dataset")
        st.download_button("Download regional PDF report",pdf,file_name=f"{selected.replace(' ','_')}_nutrimap_report.pdf",mime="application/pdf")
        st.download_button("Download selected region CSV",filtered[filtered.Region.astype(str)==selected].to_csv(index=False),file_name="regional_record.csv",mime="text/csv")
elif page=="Data Quality & Upload":
    st.subheader("Dataset validation and cleaning")
    st.write("Required geography: Region, Province, District, Latitude, Longitude, Survey_Year. Optional fields may be missing when not measured.")
    validation=validate_dataset(st.session_state.data)
    if validation["valid"]: st.success("Required columns are present.")
    else: st.error("; ".join(validation["issues"]))
    cleaned,log=clean_dataset(st.session_state.data)
    st.write(f"Rows: {len(st.session_state.data)} → {len(cleaned)} | Exact duplicates removed: {log['duplicates_removed']}")
    st.markdown("**Missing values**"); st.dataframe(missing_summary(cleaned),use_container_width=True)
    st.markdown("**Cleaned preview**"); st.dataframe(cleaned.head(30),use_container_width=True)
    st.download_button("Download cleaned CSV",cleaned.to_csv(index=False),"nutrimap_cleaned.csv","text/csv")
    st.info("Out-of-range values are marked missing rather than silently corrected. Verify units and source metadata before analysis.")
elif page=="Analysis":
    st.subheader("Exploratory data analysis")
    st.dataframe(regional_summary(filtered),use_container_width=True)
    if st.button("Generate charts"):
        paths=make_charts(filtered,str(ROOT/"outputs")); st.session_state.chart_paths=paths
    for path in st.session_state.get("chart_paths",[]):
        st.image(path,use_container_width=True)
        with open(path,"rb") as f: st.download_button(f"Download {Path(path).name}",f.read(),Path(path).name,"image/png",key=path)
elif page=="Model Lab":
    st.subheader("Supervised machine-learning lab")
    st.warning("Models are disabled until genuine target labels are supplied. The app never creates labels from its own risk scores.")
    outcome=st.selectbox("Outcome",["anemia","iodine"]); model=st.selectbox("Algorithm",["Decision Tree","Random Forest"])
    if st.button("Train model"):
        result=train_model(st.session_state.data,outcome,model,str(ROOT/"models")); st.session_state.last_model_result=result
    result=st.session_state.get("last_model_result")
    if result:
        if result.get("trained"):
            st.success(f"Model saved: {result['path']}")
            st.json({k:v for k,v in result.items() if k not in ["classification_report"]})
            st.text(result["classification_report"])
        else: st.info(result.get("reason","Model not trained."))
    st.caption("For high-stakes use, prefer geographic/temporal holdout validation and independent external validation. The included baseline split is a development check, not proof of generalization.")
elif page=="About & Sources":
    st.subheader("Data sources and responsible use")
    sources=[("Pakistan National Nutrition Survey 2018","https://www.unicef.org/pakistan/reports/national-nutrition-survey-2018","National nutrition survey; consult report tables/microdata documentation for indicator, population and geographic availability."),
    ("Pakistan Demographic and Health Survey","https://dhsprogram.com/","Survey reports and datasets; access and variable availability depend on survey round."),
    ("WHO Nutrition Landscape Information System","https://www.who.int/data/nutrition/nlis","Country-level nutrition indicators and metadata; not necessarily district-level."),
    ("ISRIC SoilGrids","https://soilgrids.org/","Modelled global soil properties at mapped depth intervals; check property coverage, units and uncertainty."),
    ("FAOSTAT","https://www.fao.org/faostat/","Country-level food/agriculture statistics; not a substitute for local dietary intake measurements."),
    ("Pakistan Bureau of Statistics","https://www.pbs.gov.pk/","Official statistical publications and survey information."),
    ("Pakistan Council of Research in Water Resources","https://www.pcrwr.gov.pk/","Water-resource and water-quality publications; verify analyte, sampling location, date and units.")]
    for name,url,desc in sources: st.markdown(f"**[{name}]({url})**  \n{desc}")
    st.markdown("### Important interpretation rules")
    st.markdown("- Soil/water mineral measurements are contextual and do not prove human micronutrient deficiency.\n- Do not infer district values from provincial averages.\n- Synthetic demonstration values are not observations.\n- Scores are configurable planning-priority indicators, not diagnosis or validated disease probability.\n- Only genuine, documented outcome labels can be used for supervised training.")
    st.markdown("### Units to document")
    st.markdown("Soil mineral: mg/kg (record extraction method/depth); water minerals: mg/L or µg/L as specified by lab; dietary iron: mg/person/day; prevalence/access: percent; urinary iodine: µg/L. Never combine values with different units without conversion and provenance.")
