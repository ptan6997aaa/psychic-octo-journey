from dash import html, dcc
import dash_bootstrap_components as dbc

# =============================================================================
# HELPER FUNCTIONS (UI COMPONENTS)
# =============================================================================

def make_kpi_card(label, val, color="#c23b5a"):
    """
    Generates a standard KPI card component.
    """
    return dbc.Card(
        dbc.CardBody([
            html.Div(val, style={"fontSize": "28px", "fontWeight": 700, "color": color}),
            html.Div(label, style={"color": "#555", "fontSize": "0.9rem"})
        ]), 
        className="shadow-sm", 
        style={"borderRadius": "14px"}
    )

def make_chart_card(item, width_basis=12):
    """
    Generates a card container for a Plotly Graph.
    """
    width_pct = (item['width'] / width_basis) * 100
    
    return html.Div(
        style={"width": f"{width_pct}%", "padding": "10px", "boxSizing": "border-box"},
        children=[
            dbc.Card([
                dbc.CardHeader(html.Div(item['title'], style={"fontWeight": 600})),
                dbc.CardBody(
                    dcc.Graph(
                        id=item['id'], 
                        config={"displayModeBar": False}, 
                        style={"height": "100%"}
                    ),
                    style={"padding": "10px", "height": "100%"}
                )
            ], className="shadow-sm", style={"borderRadius": "14px", "height": item['height']}) 
        ]
    )

def build_vertical_layout(config_vertical):
    cols = []
    for col_cfg in config_vertical:
        stack = html.Div(
            style={"display": "flex", "flexWrap": "wrap", "margin": "-10px"},
            children=[make_chart_card(chart, width_basis=12) for chart in col_cfg['charts']]
        )
        cols.append(dbc.Col(stack, width=col_cfg['width']))
    return dbc.Row(cols)

# =============================================================================
# MAIN LAYOUT GENERATOR
# =============================================================================

def create_layout():
    
    # 1. Define Chart Grid Configuration 
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

    # 2. Header Section
    header_section = dbc.Row(
        align="center",
        className="gy-2 mb-3",
        children=[
            dbc.Col([
                html.H3("ANIMAL SHELTER OPERATIONS ANALYSIS", style={"margin": 0, "fontWeight": 700}),
                html.Div([
                    html.Span("Interactive Dashboard: Click charts to filter.", className="me-2"),
                    html.Span(id='filter-status', className="text-primary", style={"fontSize": "0.9rem"})
                ], style={"color": "#666"})
            ], md=10),
            dbc.Col(dbc.Button("RESET FILTERS", id="btn-reset", color="secondary", className="w-100"), md=2),
        ],
    )

    # 3. KPI Container (Empty initially, populated by Callback)
    kpi_section = html.Div(
        id='kpi-container',
        style= {
            "display": "grid",
            "gridTemplateColumns": "repeat(5, 1fr)", 
            "gap": "20px", 
            "marginBottom": "20px", 
            "justifyContent": "center"
        }  
    )

    # 4. Charts
    chart_layout = build_vertical_layout(config_vertical) 

    # 5. Final Layout Assembly
    return dbc.Container(
        fluid=True,
        style={"backgroundColor": "#f5f6fa", "minHeight": "100vh", "padding": "18px"},
        children=[
            # State Management Stores
            dcc.Store(id='store-species', data='All'),
            dcc.Store(id='store-intake-type', data='All'),
            dcc.Store(id='store-year', data='All'),
            dcc.Store(id='store-outcome-status', data='All'),
            dcc.Store(id='store-outcome-type', data='All'),

            header_section,
            html.Hr(),
            kpi_section,
            chart_layout
        ]
    )