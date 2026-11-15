from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def regional_summary(df):
    numeric=df.select_dtypes(include="number").columns.tolist()
    if "Region" not in df.columns or not numeric: return pd.DataFrame()
    return df.groupby([c for c in ["Province","Region"] if c in df.columns], dropna=False)[numeric].mean(numeric_only=True).reset_index()

def make_charts(df, output_dir="outputs"):
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True); paths=[]
    charts=[("Anemia_Prevalence","Regional anemia prevalence"),("Iron_Deficiency_Prevalence","Iron-deficiency prevalence"),
            ("Soil_Iron","Soil iron (context only)"),("Water_Iron","Water iron (context only)"),
            ("Median_Urinary_Iodine","Median urinary iodine"),("Dietary_Diversity","Dietary diversity")]
    sns.set_theme(style="whitegrid")
    for col,title in charts:
        if col in df.columns and df[col].notna().any():
            fig,ax=plt.subplots(figsize=(9,4.5))
            plot=df.dropna(subset=[col]).copy()
            label="Region" if "Region" in plot.columns else plot.index.name or "Record"
            sns.barplot(data=plot,x=label,y=col,ax=ax,errorbar=None,color="#168777")
            ax.set_title(title); ax.tick_params(axis="x",rotation=35); fig.tight_layout()
            path=out/f"{col.lower()}_chart.png"; fig.savefig(path,dpi=150); plt.close(fig); paths.append(str(path))
    numeric=df.select_dtypes(include="number")
    if numeric.shape[1]>=2:
        fig,ax=plt.subplots(figsize=(9,6)); sns.heatmap(numeric.corr(),cmap="vlag",center=0,ax=ax)
        ax.set_title("Exploratory correlation (not causal)"); fig.tight_layout()
        path=out/"correlation_heatmap.png"; fig.savefig(path,dpi=150); plt.close(fig); paths.append(str(path))
    return paths
