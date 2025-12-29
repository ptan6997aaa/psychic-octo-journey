from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import figures as figs

# =============================================================================
# HELPER FUNCTIONS 
# =============================================================================

def empty_fig(title: str):
    fig = go.Figure()
    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=20, b=20))
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
    fig.add_annotation(text=title, showarrow=False, font=dict(size=14, color="#888"))
    return fig

def kpi_card(label, value, id_value=None):
    # Styling matched to your script (Simple White Card with Red Text)
    return dbc.Card(
        dbc.CardBody([
            html.Div(value, id=id_value, style={"fontSize": "28px", "fontWeight": 700, "color": "#c23b5a"}),
            html.Div(label, style={"color": "#555"})
        ]), 
        className="shadow-sm border-0", 
        style={"borderRadius": "14px"}
    )

def make_card(item, figure_lookup, width_basis=12):
    width_pct = (item['width'] / width_basis) * 100
    actual_figure = figure_lookup.get(item['id'], empty_fig(item['title'])) 
    
    return html.Div(
        style={"width": f"{width_pct}%", "padding": "10px", "boxSizing": "border-box"},
        children=[
            dbc.Card([
                dbc.CardHeader(html.Div(item['title'], style={"fontWeight": 600})),
                dbc.CardBody(
                    dcc.Graph(
                        figure=actual_figure, 
                        config={"displayModeBar": False}, 
                        style={"height": "100%"}
                    ),
                    style={"padding": "10px", "height": "100%"}
                )
            ], className="shadow-sm", style={"borderRadius": "14px", "height": item['height']}) 
        ]
    )

def build_vertical_layout(config_vertical, figure_lookup):
    cols = []
    for col_cfg in config_vertical:
        stack = html.Div(
            style={"display": "flex", "flexWrap": "wrap", "margin": "-10px"},
            children=[make_card(chart, figure_lookup, width_basis=12) for chart in col_cfg['charts']]
        )
        cols.append(dbc.Col(stack, width=col_cfg['width']))
    return dbc.Row(cols)

def build_horizontal_layout(config, figure_lookup):
    return html.Div(
        style={"display": "flex", "flexWrap": "wrap", "margin": "-10px"},
        children=[make_card(item, figure_lookup, width_basis=12) for item in config]
    )


# =============================================================================
# MAIN LAYOUT GENERATOR
# =============================================================================

def create_layout(df, kpis_data):
    
    # 1. Generate Figures
    figure_lookup = {
        "fig_species": figs.create_species_pie(df),
        "fig_intake_type": figs.create_intake_bar(df),
        "fig_trend": figs.create_trend_chart(df),
        "fig_outcomes_percentage": figs.create_outcome_percentage(df),
        "fig_outcome_type": figs.create_outcome_bar(df),
    } 

    # 2. Define Configuration 
    config_vertical = [
        {
            "width": 8, # LEFT COLUMN
            "charts": [
                {"title": "Intake Species Distribution",  "id": "fig_species", "width": 6, "height": "300px"},
                {"title": "Intake Type Breakdown",  "id": "fig_intake_type", "width": 6, "height": "300px"},
                {"title": "Intake & Outcome Volume Over Time", "id": "fig_trend", "width": 12, "height": "300px"},
            ]
        },
        {
            "width": 4, # RIGHT COLUMN
            "charts": [
                {"title": "Live Outcomes Percentage", "id": "fig_outcomes_percentage", "width": 12, "height": "200px"},
                {"title": "Outcomes Distribution", "id": "fig_outcome_type", "width": 12, "height": "400px"},
            ]
        }
    ]

    # config_horizontal = [
    #     # Row 1 Visual 
    #     {"title": "Intake Species Distribution",  "id": "Pie-Species", "width": 4, "height": "300px"}, 
    #     {"title": "Intake Type Breakdown",  "id": "Bar-Type", "width": 4, "height": "300px"}, 
    #     {"title": "Pie (Type)",     "id": "c3", "width": 4, "height": "200px"}, 
    #     # Row 2 Visual 
    #     {"title": "Volume Trend",   "id": "c4", "width": 8, "height": "300px"},
    #     {"title": "Outcomes",       "id": "c5", "width": 4, "height": "400px"}, 
    # ]

    # 3. Define KPI List
    kpis_list = [
        {"label": "Total Intakes",      "value": kpis_data["intakes"],   "id": "kpi-intakes"},
        {"label": "Total Outcomes",     "value": kpis_data["outcomes"],  "id": "kpi-outcomes"},
        {"label": "Avg Length of Stay", "value": kpis_data["los"],       "id": "kpi-stay"},
        {"label": "Total Adoptions",    "value": kpis_data["adoptions"], "id": "kpi-Adoptions"},
        {"label": "Live Release Rate",  "value": kpis_data["lrr"],       "id": "kpi-lrr"},
    ]

    # 4. Assemble Blocks
    
    # Header
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

    # KPI Grid
    kpi_section = html.Div(
        children=[kpi_card(k['label'], k['value'], k['id']) for k in kpis_list],
        style= {
            "display": "grid",
            "gridTemplateColumns": "repeat(5, 1fr)", 
            "gap": "20px", 
            "marginBottom": "20px", 
            "justifyContent": "center"
        }  
    )

    # Charts
    chart_layout = build_vertical_layout(config_vertical, figure_lookup) 
    # chart_layout = build_horizontal_layout(config_horizontal, figure_lookup) 

    # Final Container
    return dbc.Container(
        fluid=True,
        style={"backgroundColor": "#f5f6fa", "minHeight": "100vh", "padding": "18px"},
        children=[
            header_section,
            html.Hr(),
            kpi_section,
            chart_layout
        ]
    )