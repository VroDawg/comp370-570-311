"""Bokeh dashboard: monthly 311 response times for two zipcodes vs all of NYC.

Run with:  bokeh serve response_time_dashboard.py --port 5006
"""

import pandas as pd
from bokeh.core.properties import value
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Select
from bokeh.plotting import figure

DATA_FILE = "monthly_response_times.csv"
YEAR = 2024
MONTHS = list(range(1, 13))
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Load the small pre-computed summary (one row per zipcode per month).
df = pd.read_csv(DATA_FILE, dtype={"zipcode": str})

# Table with months as rows and zipcodes as columns; missing months become NaN,
# which Bokeh draws as a gap in the line.
table = df.pivot(index="month", columns="zipcode", values="avg_hours").reindex(MONTHS)

# Dropdown choices: every zipcode, defaulting to the two with the most incidents.
volume = df[df["zipcode"] != "ALL"].groupby("zipcode")["count"].sum()
zipcodes = sorted(volume.index)
default1, default2 = volume.sort_values(ascending=False).index[:2]


def series(zipcode):
    return {"month": MONTHS, "hours": table[zipcode].to_numpy()}


source_all = ColumnDataSource(series("ALL"))
source_1 = ColumnDataSource(series(default1))
source_2 = ColumnDataSource(series(default2))

select_1 = Select(title="Zipcode 1", value=default1, options=zipcodes)
select_2 = Select(title="Zipcode 2", value=default2, options=zipcodes)

plot = figure(
    title=f"Monthly average 311 response time, {YEAR}",
    x_axis_label=f"Month of incident creation ({YEAR})",
    y_axis_label="Average create-to-closed time (hours)",
    width=850, height=450, x_range=(0.5, 12.5),
)
plot.xaxis.ticker = MONTHS
plot.xaxis.major_label_overrides = dict(zip(MONTHS, MONTH_NAMES))

curves = [
    (source_all, "All zipcodes", "#555555"),
    (source_1, f"Zipcode 1: {default1}", "#1f77b4"),
    (source_2, f"Zipcode 2: {default2}", "#ff7f0e"),
]
for source, label, color in curves:
    plot.line("month", "hours", source=source, legend_label=label,
              line_width=2, color=color)
    plot.scatter("month", "hours", source=source, legend_label=label,
                 size=6, color=color)

plot.legend.location = "top_left"


def update(attr, old, new):
    """Swap in the pre-computed series for the newly selected zipcodes."""
    source_1.data = series(select_1.value)
    source_2.data = series(select_2.value)
    plot.legend.items[1].label = value(f"Zipcode 1: {select_1.value}")
    plot.legend.items[2].label = value(f"Zipcode 2: {select_2.value}")


select_1.on_change("value", update)
select_2.on_change("value", update)

curdoc().add_root(column(select_1, select_2, plot))
curdoc().title = "311 Response Times by Zipcode"
