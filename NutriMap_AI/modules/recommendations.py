def generate_recommendations(row):
    items=[]
    def val(k):
        try: return float(row[k])
        except (KeyError,TypeError,ValueError): return None
    anemia=val("Anemia_Risk_Score"); iodine=val("Iodine_Risk_Score")
    if anemia is not None and anemia>33:
        items += ["Promote access to diverse, iron-containing foods using locally appropriate nutrition guidance.",
                  "Encourage population-level anemia screening and referral through qualified public-health services.",
                  "Review food-fortification coverage and awareness with relevant authorities."]
    if iodine is not None and iodine>33:
        items += ["Review household access to adequately iodized salt and support iodine-nutrition awareness.",
                  "Consider population-level iodine monitoring with qualified public-health partners."]
    if val("Soil_Iron") is not None or val("Water_Iron") is not None or val("Soil_Iodine") is not None or val("Water_Iodine") is not None:
        items += ["Treat environmental mineral measurements as contextual evidence only; arrange confirmatory soil/water testing with qualified laboratories.",
                  "Consult agricultural experts before considering crop or soil interventions; environmental values do not establish human deficiency."]
    if not items: items=["Insufficient evidence for a targeted recommendation. Improve representative dietary and population-health data coverage first."]
    return items
