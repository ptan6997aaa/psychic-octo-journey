from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


# Chart layout configuration (same “2-column” structure you used)
CONFIG_VERTICAL = [
    {
        "width": 8,
        "charts": [
            {"title": "Intake Species Distribution", "id": "fig_species", "width": 6, "height": "300px"},
            {"title": "Intake Type Breakdown", "id": "fig_intake_type", "width": 6, "height": "300px"},
            {"title": "Intake & Outcome Volume Over Time", "id": "fig_trend", "width": 12, "height": "300px"},
        ],
    },
    {
        "width": 4,
        "charts": [
            {"title": "Live Outcomes Percentage", "id": "fig_outcomes_percentage", "width": 12, "height": "200px"},
            {"title": "Outcomes Distribution", "id": "fig_outcome_type", "width": 12, "height": "400px"},
        ],
    },
]


def empty_fig(title: str = "Loading...") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=20, b=20))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.add_annotation(text=title, showarrow=False, font=dict(size=14, color="#888"))
    return fig


def make_kpi_card(label: str, value: str, color: str = "#c23b5a") -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(value, style={"fontSize": "28px", "fontWeight": 700, "color": color}),
                html.Div(label, style={"color": "#555", "fontSize": "0.9rem"}),
            ]
        ),
        className="shadow-sm border-0",
        style={"borderRadius": "14px"},
    )


def _make_chart_card(item, width_basis=12):
    width_pct = (item["width"] / width_basis) * 100
    return html.Div(
        style={"width": f"{width_pct}%", "padding": "10px", "boxSizing": "border-box"},
        children=[
            dbc.Card(
                [
                    dbc.CardHeader(html.Div(item["title"], style={"fontWeight": 600})),
                    dbc.CardBody(
                        dcc.Graph(
                            id=item["id"],
                            figure=empty_fig(),
                            config={"displayModeBar": False},
                            style={"height": "100%"},
                        ),
                        style={"padding": "10px", "height": "100%"},
                    ),
                ],
                className="shadow-sm",
                style={"borderRadius": "14px", "height": item["height"]},
            )
        ],
    )


def _build_vertical_layout():
    cols = []
    for col_cfg in CONFIG_VERTICAL:
        stack = html.Div(
            style={"display": "flex", "flexWrap": "wrap", "margin": "-10px"},
            children=[_make_chart_card(chart, width_basis=12) for chart in col_cfg["charts"]],
        )
        cols.append(dbc.Col(stack, width=col_cfg["width"]))
    return dbc.Row(cols)


def create_layout():
    return dbc.Container(
        fluid=True,
        style={"backgroundColor": "#f5f6fa", "minHeight": "100vh", "padding": "18px"},
        children=[
            # ---- Stores (cross-filter state) ----
            dcc.Store(id="store-species", data="All"),
            dcc.Store(id="store-intake-type", data="All"),
            dcc.Store(id="store-year", data="All"),
            dcc.Store(id="store-outcome-status", data="All"),
            dcc.Store(id="store-outcome-type", data="All"),
            # ---- Header ----
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("ANIMAL SHELTER OPERATIONS ANALYSIS", style={"margin": 0, "fontWeight": 700}),
                            html.Div(
                                [
                                    html.Span("Interactive Dashboard: Click charts to filter.", className="me-2"),
                                    html.Span(id="filter-status", className="text-primary", style={"fontSize": "0.9rem"}),
                                ],
                                style={"color": "#666"},
                            ),
                        ],
                        md=10,
                    ),
                    dbc.Col(dbc.Button("RESET FILTERS", id="btn-reset", color="secondary", className="w-100"), md=2),
                ],
                className="gy-2 mb-3",
                align="center",
            ),
            html.Hr(),
            # ---- KPI Container (populated by callback) ----
            html.Div(
                id="kpi-container",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(5, 1fr)",
                    "gap": "20px",
                    "marginBottom": "20px",
                    "justifyContent": "center",
                },
            ),
            # ---- Charts ----
            _build_vertical_layout(),
        ],
    )
