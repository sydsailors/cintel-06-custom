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
# Load the dataset
# -----------------------------------
app_dir = Path(__file__).parent
csv_path = app_dir / "four-quarter-summary-hospital-utilization-operating-revenue-and-profit-margins-.csv"
hospital_df = pd.read_csv(csv_path)

