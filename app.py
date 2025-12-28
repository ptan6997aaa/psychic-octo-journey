from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd 
import plotly.express as px 

# Load Data
df = pd.read_csv('Animal-Shelter-Operations.csv')

# Calculations 
# KPIs
# 1. Total Intakes
# Assuming every row is a unique intake
total_intakes = len(df)

# 2. Total Outcomes
# We count rows where an outcome has occurred (Outcome Date is not null)
total_outcomes = df['Outcome Date'].count()

# 3. Avg Length of Stay
# Using the pre-calculated 'intake_duration' column
avg_los = df['intake_duration'].mean()

# 4. Total Adoptions
# Filter for specific string 'ADOPTION' in Outcome Type
total_adoptions = len(df[df['Outcome Type'] == 'ADOPTION'])

# 5. Live Release Rate (LRR)
# The dataset has a boolean column 'outcome_is_alive' which simplifies this.
# Formula: (Count of Live Outcomes / Total Outcomes)
total_live_outcomes = df['outcome_is_alive'].sum()

if total_outcomes > 0:
    live_release_rate = (total_live_outcomes / total_outcomes) * 100
else:
    live_release_rate = 0

# Charts 
# 1. Intake Species Distribution (Pie Chart)
# Group by 'Animal Type' and count rows
df_species = df['Animal Type'].value_counts().reset_index()
df_species.columns = ['Animal Type', 'Count']

fig_species = px.pie(
    df_species, 
    values='Count', 
    names='Animal Type', 
    hole=0.5, # Makes it a donut chart
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_species.update_layout(
    margin=dict(t=30, b=10, l=10, r=10),
    showlegend=False # Hide legend to save space in small cards
)
# Add labels inside the slices
fig_species.update_traces(textposition='inside', textinfo='percent+label')


# 2. Intake Type Breakdown (Bar Chart)
# Group by 'Intake Type' and count rows
df_intake = df['Intake Type'].value_counts().head(6).reset_index()
df_intake.columns = ['Intake Type', 'Count']

fig_type = px.bar(
    df_intake, 
    x='Count', 
    y='Intake Type', 
    orientation='h', # Horizontal bars are easier to read for categories
    text='Count'
)
fig_type.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis=dict(showgrid=False, showticklabels=False), # Clean look
    yaxis=dict(autorange="reversed"), # Sort Top to Bottom
    plot_bgcolor='white'
)
fig_type.update_traces(marker_color='#6c757d', textposition='outside')

# Map string IDs to actual figure objects
figure_lookup = {
    "fig_species": fig_species,
    "fig_type": fig_type,
} 

# Initialize App 
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Animal Shelter Operations Analysis"

# =============================================================================
# 1. SHARED DATA 
# =============================================================================

kpis = [
    {"label": "Total Intakes",      "value": f"{total_intakes:,.0f}",     "id": "kpi-intakes"},
    {"label": "Total Outcomes",     "value": f"{total_outcomes:,.0f}",    "id": "kpi-outcomes"},
    {"label": "Avg Length of Stay", "value": f"{avg_los:.1f}",       "id": "kpi-stay"},
    {"label": "Total Adoptions",    "value": f"{total_adoptions:,.0f}",   "id": "kpi-Adoptions"},
    {"label": "Live Release Rate",  "value": f"{live_release_rate:.1f}%", "id": "kpi-lrr"},
]

# # CONFIG OPTION A: HORIZONTAL (Standard Flex Wrapping)
# config_horizontal = [
#     # Row 1 Visual 
#     {"title": "Intake Species Distribution",  "id": "Pie-Species", "width": 4, "height": "300px"}, 
#     {"title": "Intake Type Breakdown",  "id": "Bar-Type", "width": 4, "height": "300px"}, 
#     {"title": "Pie (Type)",     "id": "c3", "width": 4, "height": "200px"}, 
#     # Row 2 Visual 
#     {"title": "Volume Trend",   "id": "c4", "width": 8, "height": "300px"},
#     {"title": "Outcomes",       "id": "c5", "width": 4, "height": "400px"}, 
# ]

# CONFIG OPTION B: VERTICAL (Independent Columns)
config_vertical = [
    {
        "width": 8, # LEFT COLUMN
        "charts": [
            {"title": "Intake Species Distribution",  "id": "fig_species", "width": 6, "height": "300px"},
            {"title": "Intake Type Breakdown",  "id": "fig_type", "width": 6, "height": "300px"},
            {"title": "Volume Trend Over Time",      "id": "c4", "width": 12, "height": "300px"},
        ]
    },
    {
        "width": 4, # RIGHT COLUMN
        "charts": [
            {"title": "Live Outcomes Percentage",    "id": "c3", "width": 12, "height": "200px"},
            {"title": "Outcomes Distribution",       "id": "c5", "width": 12, "height": "400px"},
        ]
    }
]

# =============================================================================
# 2. HELPER FUNCTIONS 
# =============================================================================

def empty_fig(title: str):
    fig = go.Figure()
    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=20, b=20))
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
    fig.add_annotation(text=title, showarrow=False, font=dict(size=14, color="#888"))
    return fig

def kpi_card(label, value, id_value=None):
    return dbc.Card(
        dbc.CardBody([
            html.Div(value, id=id_value, style={"fontSize": "28px", "fontWeight": 700, "color": "#c23b5a"}),
            html.Div(label, style={"color": "#555"})
        ]), className="shadow-sm", style={"borderRadius": "14px"}
    )

def make_card(item, width_basis=12):
    width_pct = (item['width'] / width_basis) * 100
    actual_figure = figure_lookup.get(item['id'], empty_fig(item['title'])) 
    
    return html.Div(
        style={
            "width": f"{width_pct}%", 
            "padding": "10px", 
            "boxSizing": "border-box"
        },
        children=[
            dbc.Card([
                dbc.CardHeader(html.Div(item['title'], style={"fontWeight": 600})),
                dbc.CardBody(
                    dcc.Graph(
                        id=item['id'], 
                        figure=actual_figure, 
                        config={"displayModeBar": False}, 
                        style={"height": "100%"}
                    ),
                    style={"padding": "10px", "height": "100%"} # Ensure body fills card
                )
            ], className="shadow-sm", style={"borderRadius": "14px", "height": item['height']}) 
        ]
    )

# =============================================================================
# 3. LAYOUT BUILDERS (Logic A)
# =============================================================================

def build_horizontal_layout():
    """Builds the single-row wrapping layout."""
    return html.Div(
        style={"display": "flex", "flexWrap": "wrap", "margin": "-10px"},
        children=[make_card(item, width_basis=12) for item in config_horizontal]
    )

def build_vertical_layout():
    """Builds the multi-column independent layout."""
    cols = []
    for col_cfg in config_vertical:
        stack = html.Div(
            style={"display": "flex", "flexWrap": "wrap", "margin": "-10px"},
            children=[make_card(chart, width_basis=12) for chart in col_cfg['charts']]
        )
        cols.append(dbc.Col(stack, width=col_cfg['width']))
    return dbc.Row(cols)

# =============================================================================
# 4. APP ASSEMBLY (Structure B)
# =============================================================================

# --- Block: Header ---
header_section = dbc.Row(
    align="center",
    className="gy-2 mb-3",
    children=[
        dbc.Col([
            html.H3("ANIMAL SHELTER OPERATIONS ANALYSIS", style={"margin": 0, "fontWeight": 700}),
            html.Div("A high-level view of shelter demand and performance", style={"color": "#666"})
        ], md=10),
        dbc.Col(dbc.Button("RESET", id="btn-reset", color="secondary", className="w-100"), md=2),
    ],
)

# --- Block: KPI Grid ---
kpi_section = html.Div(
    # Loop through logic list (kpis), create visual cards (kpi_card)
    children=[kpi_card(k['label'], k['value'], k['id']) for k in kpis],
    style= {
        "display": "grid",
        "gridTemplateColumns": "repeat(5, 1fr)", 
        "gap": "20px", 
        "marginBottom": "20px", 
        "justifyContent": "center"
    }  
)

# ---------------------------------------------------------
# !!! DEVELOPER SWITCH !!! 
# ---------------------------------------------------------

# MODE 1: Horizontal Wrap
# chart_layout = build_horizontal_layout()

# MODE 2: Vertical Columns 
chart_layout = build_vertical_layout()

# ---------------------------------------------------------

app.layout = dbc.Container(
    fluid=True,
    style={"backgroundColor": "#f5f6fa", "minHeight": "100vh", "padding": "18px"},
    children=[
        header_section,
        html.Hr(),
        kpi_section,
        chart_layout
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
