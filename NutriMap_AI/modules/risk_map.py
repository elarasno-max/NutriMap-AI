import folium
from folium.plugins import Fullscreen

def create_risk_map(df, risk_column="Anemia_Risk_Category", score_column="Anemia_Risk_Score", province=None, category=None):
    data=df.copy()
    if province and province!="All": data=data[data["Province"]==province]
    if category and category!="All": data=data[data[risk_column]==category]
    m=folium.Map(location=[30.5,69.3],zoom_start=5,tiles="CartoDB positron")
    Fullscreen().add_to(m)
    colors={"Low Risk":"#2e9d65","Moderate Risk":"#f0ad35","High Risk":"#d94b4b","Insufficient data":"#87919b"}
    for _,r in data.dropna(subset=["Latitude","Longitude"]).iterrows():
        cat=str(r.get(risk_column,"Insufficient data")); score=r.get(score_column)
        popup=f"<b>{r.get('Region','Unknown')}</b><br>Province: {r.get('Province','N/A')}<br>Category: {cat}<br>Score: {score if score is not None else 'N/A'}<br>Source: {r.get('Data_Source','Not provided')}"
        for c in ["Anemia_Prevalence","Iron_Deficiency_Prevalence","Median_Urinary_Iodine","Dietary_Diversity"]:
            if c in r.index and str(r[c])!="nan": popup+=f"<br>{c}: {r[c]}"
        folium.CircleMarker([float(r["Latitude"]),float(r["Longitude"])],radius=9,color=colors.get(cat,"#87919b"),fill=True,fill_opacity=.8,
                            tooltip=f"{r.get('Region','Region')} — {cat}",popup=folium.Popup(popup,max_width=320)).add_to(m)
    legend="<div style='position:fixed;bottom:25px;left:25px;z-index:9999;background:white;padding:10px 14px;border:1px solid #bbb;border-radius:8px;font-size:13px'><b>Planning-priority category</b><br><span style='color:#2e9d65'>●</span> Low Risk<br><span style='color:#f0ad35'>●</span> Moderate Risk<br><span style='color:#d94b4b'>●</span> High Risk<br><span style='color:#87919b'>●</span> Insufficient data</div>"
    m.get_root().html.add_child(folium.Element(legend))
    return m
