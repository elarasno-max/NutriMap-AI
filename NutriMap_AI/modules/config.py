"""Configurable demonstration settings. These are NOT clinical cut-offs."""
RISK_BANDS = {"low_max": 33.0, "moderate_max": 66.0}
# Provisional weights are used only to demonstrate transparent aggregation.
ANEMIA_WEIGHTS = {
    "Anemia_Prevalence": 0.40,
    "Iron_Deficiency_Prevalence": 0.35,
    "Dietary_Iron_Intake": 0.15,
    "Dietary_Diversity": 0.10,
}
IODINE_WEIGHTS = {
    "Median_Urinary_Iodine": 0.65,
    "Iodized_Salt_Access": 0.35,
}
# Display scaling ranges are configurable and not clinical reference ranges.
# Prevalence/access are percentages; dietary intake is mg/day; urinary iodine is ug/L.
SCALES = {
    "Anemia_Prevalence": {"min": 0, "max": 60, "direction": "higher"},
    "Iron_Deficiency_Prevalence": {"min": 0, "max": 60, "direction": "higher"},
    "Dietary_Iron_Intake": {"min": 0, "max": 30, "direction": "lower"},
    "Dietary_Diversity": {"min": 0, "max": 10, "direction": "lower"},
    "Median_Urinary_Iodine": {"min": 0, "max": 300, "direction": "lower"},
    "Iodized_Salt_Access": {"min": 0, "max": 100, "direction": "lower"},
}
REQUIRED_COLUMNS = ["Region", "Province", "District", "Latitude", "Longitude", "Survey_Year"]
OPTIONAL_COLUMNS = [
    "Soil_Iron", "Soil_Iodine", "Soil_pH", "Water_Iron", "Water_Iodine", "Water_Fluoride",
    "Dietary_Iron_Intake", "Dietary_Diversity", "Iodized_Salt_Access",
    "Anemia_Prevalence", "Iron_Deficiency_Prevalence", "Median_Urinary_Iodine",
    "Anemia_Risk", "Iodine_Risk", "Population_Group", "Measurement_Date", "Data_Source",
]
NUMERIC_COLUMNS = ["Latitude", "Longitude", "Survey_Year", "Soil_Iron", "Soil_Iodine", "Soil_pH",
    "Water_Iron", "Water_Iodine", "Water_Fluoride", "Dietary_Iron_Intake", "Dietary_Diversity",
    "Iodized_Salt_Access", "Anemia_Prevalence", "Iron_Deficiency_Prevalence", "Median_Urinary_Iodine"]
