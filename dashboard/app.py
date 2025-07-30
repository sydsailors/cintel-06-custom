# -----------------------------------
# Imports
# -----------------------------------
import faicons as fa
import pandas as pd
from pathlib import Path
from shiny import App, reactive, render
from shiny.express import input, ui
from shinywidgets import output_widget, render_plotly
import plotly.express as px
from faicons import icon_svg

# -----------------------------------
# Function to clean CSV columns
# -----------------------------------
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = (
                df[col]
                .replace(r"[\$,]", "", regex=True)  # remove $ and commas
                .replace("", None)  # convert empty strings to None
            )
            df[col] = pd.to_numeric(df[col], errors="ignore")  # convert if possible
    return df

# -----------------------------------
# Load the dataset
# -----------------------------------
app_dir = Path(__file__).parent
csv_path = app_dir / "four-quarter-summary-hospital-utilization-operating-revenue-and-profit-margins-.csv"
hospital_df = pd.read_csv(csv_path)
hospital_df = clean_dataframe(hospital_df)

rev_rng = (
    hospital_df["Total Operating Rev"].min(),
    hospital_df["Total Operating Rev"].max()
)

# -----------------------------------
# UI setup
# -----------------------------------
ui.page_opts(title="Hospital Utilization - Four Quarter Summary", fillable=True)

with ui.sidebar():
    ui.input_slider(
        "revenue",
        "Total Operating Revenue",
        min=rev_rng[0], 
        max=rev_rng[1],
        value=rev_rng,
        pre="$",
    )