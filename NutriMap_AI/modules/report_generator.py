from io import BytesIO
from datetime import date
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def regional_pdf(row, recommendations, source_note="User-supplied dataset"):
    buff=BytesIO(); doc=SimpleDocTemplate(buff,pagesize=A4); styles=getSampleStyleSheet(); story=[]
    story += [Paragraph("NutriMap AI – Regional Nutrition Intelligence Report",styles["Title"]),Spacer(1,10)]
    story.append(Paragraph(f"Region: {row.get('Region','Unknown')} | Generated: {date.today().isoformat()}",styles["Normal"]))
    story.append(Paragraph(f"Province: {row.get('Province','N/A')} | Source: {source_note}",styles["Normal"])); story.append(Spacer(1,12))
    fields=[("Anemia planning score",row.get("Anemia_Risk_Score","Insufficient data")),("Anemia category",row.get("Anemia_Risk_Category","Insufficient data")),
            ("Iodine planning score",row.get("Iodine_Risk_Score","Insufficient data")),("Iodine category",row.get("Iodine_Risk_Category","Insufficient data"))]
    t=Table([["Indicator","Value"]]+[[a,str(b)] for a,b in fields],colWidths=[220,220]); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e7f2ee")),("GRID",(0,0),(-1,-1),.4,colors.grey),("PADDING",(0,0),(-1,-1),7)])); story.append(t)
    story += [Spacer(1,12),Paragraph("Available supporting measurements",styles["Heading2"])]
    for key in ["Anemia_Prevalence","Iron_Deficiency_Prevalence","Median_Urinary_Iodine","Dietary_Iron_Intake","Dietary_Diversity","Iodized_Salt_Access","Soil_Iron","Water_Iron"]:
        if key in row and pd.notna(row[key]): story.append(Paragraph(f"{key}: {row[key]}",styles["Normal"]))
    story += [Spacer(1,10),Paragraph("Planning recommendations",styles["Heading2"])]
    for rec in recommendations: story.append(Paragraph("• "+rec,styles["Normal"]))
    story += [Spacer(1,10),Paragraph("Limitations and disclaimer",styles["Heading2"]),Paragraph(
        "Scores are transparent, configurable planning-priority indicators, not clinical diagnoses or validated probabilities of disease. "
        "Demonstration data are synthetic and must not be interpreted as Pakistani district statistics. Soil and water measurements do not prove human deficiency. "
        "Interpret results only at the geographic and population resolution supported by the source data. Seek qualified public-health review before decisions.",styles["Normal"])]
    doc.build(story); buff.seek(0); return buff
