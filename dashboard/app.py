# -----------------------------------
# Imports
# -----------------------------------
import faicons as fa
import pandas as pd
from pathlib import Path
from shiny import App, reactive, render
from shiny.express import input, ui, output
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
                .replace(r"[\$%,]", "", regex=True)  # remove $ and commas
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
# UI sidebar
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
    ui.input_checkbox_group(
        "year",
        "Year",
        sorted(hospital_df["Year"].unique().tolist()),
        selected=sorted(hospital_df["Year"].unique().tolist()),
        inline=True,
    )
    ui.input_action_button("reset", "Reset filter"),
    open="desktop"

# ----------------------------------
# Icons
# ----------------------------------
ICONS = {
    "hospital": fa.icon_svg("hospital"),
    "money": fa.icon_svg("wallet"),
    "percent": fa.icon_svg("percent"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

# ----------------------------------
# UI setup
# ----------------------------------
with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["hospital"], theme="bg-gradient-purple-pink"):
        "Number of Hospitals"

        @render.express
        def total_hospitals():
            str(hospital_df.shape[0])
        
    with ui.value_box(showcase=ICONS["money"], theme="bg-gradient-pink-purple"):
        "Average Revenue"

        @render.express
        def avg_revenue():
            f"${hospital_df['Total Operating Rev'].mean():,.2f}"
        
    with ui.value_box(showcase=ICONS["percent"], theme="bg-gradient-purple-pink"):
        "Average Operating Margin"

        @render.express
        def avg_margin():
            f"{hospital_df['Operating Margin'].mean():.2%}"
        
