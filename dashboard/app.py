# -----------------------------------
# Imports
# -----------------------------------
import faicons as fa
import pandas as pd
from pathlib import Path
from shiny import App, reactive, render
from shiny.express import input, ui, output
from shinywidgets import output_widget, render_plotly, render_widget
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

with ui.layout_columns():
    
    with ui.card(full_screen=True):
        ui.card_header("Hospital Data")
       
        @render.data_frame
        def data_table():
            return hospital_df

    # Scatterplot showing available beds vs staffed beds
    with ui.card(full_screen=True):
        ui.card_header("Available Beds vs. Staffed Beds")

        @render_widget
        def plotly_scatterplot():
            df = filtered_data()
            if df.empty:
                return px.scatter(title="No data from filters")
            return px.scatter(
                df.assign(Year=df["Year"].astype(str)),
                x="Available Beds",
                y="Staffed Beds",
                color="Year",
                symbol="Year",
                hover_data=["Facility Name"],
                labels={
                    "Available Beds": "Available Beds",
                    "Staffed Beds": "Staffed Beds"
                }
            )
        @reactive.calc
        def filtered_data():
            is_year_match = hospital_df["Year"].astype(str).isin([str(y) for y in input.year()])
            revenue_range = input.revenue()
            is_revenue_match = (
                (hospital_df["Total Operating Rev"] >= revenue_range[0]) &
                (hospital_df["Total Operating Rev"] <= revenue_range[1])
            )
            return hospital_df[is_year_match & is_revenue_match]
        
        @reactive.effect
        @reactive.event(input.reset)
        def _():
            ui.update_slider("revenue", value=rev_rng)
            ui.update_checkbox_group(
                "year", selected=sorted(hospital_df["Year"].unique().tolist())
            )