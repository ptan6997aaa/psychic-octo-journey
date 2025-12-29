import dash
from dash import Dash, html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np

# ┌──────────────────────────────────────────────────────────────────────────────┐
# │ 1. DATA LOADING & PREPROCESSING                                              │
# └──────────────────────────────────────────────────────────────────────────────┘
try:
    df = pd.read_csv('Animal-Shelter-Operations.csv')
    # Basic cleanup
    df['Intake Date'] = pd.to_datetime(df['Intake Date'], errors='coerce')
    df['Outcome Date'] = pd.to_datetime(df['Outcome Date'], errors='coerce')
    # Calculate duration if not present
    if 'intake_duration' not in df.columns:
        df['intake_duration'] = (df['Outcome Date'] - df['Intake Date']).dt.days.fillna(0)
    # Ensure boolean is boolean
    if df['outcome_is_alive'].dtype == object:
        df['outcome_is_alive'] = df['outcome_is_alive'].map({'TRUE': True, 'FALSE': False, True: True, False: False})
        
except FileNotFoundError:
    print("CSV not found. Generating Dummy Data...")
    # Generate 1000 rows of dummy data for demonstration
    np.random.seed(42)
    n = 1000
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', periods=n)
    outcome_dates = dates + pd.to_timedelta(np.random.randint(1, 60, n), unit='D')
    
    df = pd.DataFrame({
        'Animal Type': np.random.choice(['DOG', 'CAT', 'BIRD', 'OTHER'], n, p=[0.5, 0.4, 0.05, 0.05]),
        'Intake Type': np.random.choice(['STRAY', 'OWNER SURRENDER', 'PUBLIC ASSIST', 'SEIZED'], n),
        'Outcome Type': np.random.choice(['ADOPTION', 'TRANSFER', 'RETURN TO OWNER', 'EUTHANASIA', 'DIED'], n, p=[0.4, 0.3, 0.2, 0.08, 0.02]),
        'Intake Date': dates,
        'Outcome Date': outcome_dates,
        'outcome_is_alive': np.random.choice([True, False], n, p=[0.9, 0.1])
    })
    df['intake_duration'] = (df['Outcome Date'] - df['Intake Date']).dt.days

# Pre-calculate Year for filtering convenience
df['Intake Year'] = df['Intake Date'].dt.year
df['Outcome Year'] = df['Outcome Date'].dt.year

# ┌──────────────────────────────────────────────────────────────────────────────┐
# │ 2. DASH APP SETUP & LAYOUT                                                 │
# └──────────────────────────────────────────────────────────────────────────────┘

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Animal Shelter Operations Analysis"

# Layout Configuration
config_vertical = [
    {
        "width": 8, 
        "charts": [
            {"title": "Intake Species Distribution",  "id": "fig_species", "width": 6, "height": "300px"},
            {"title": "Intake Type Breakdown",  "id": "fig_intake_type", "width": 6, "height": "300px"},
            {"title": "Intake & Outcome Volume Over Time", "id": "fig_trend", "width": 12, "height": "300px"},
        ]
    },
    {
        "width": 4, 
        "charts": [
            {"title": "Live Outcomes Percentage", "id": "fig_outcomes_percentage", "width": 12, "height": "200px"},
            {"title": "Outcomes Distribution", "id": "fig_outcome_type", "width": 12, "height": "400px"},
        ]
    }
]

# Helper to create chart containers
def make_card(item, width_basis=12):
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

def build_vertical_layout():
    cols = []
    for col_cfg in config_vertical:
        stack = html.Div(
            style={"display": "flex", "flexWrap": "wrap", "margin": "-10px"},
            children=[make_card(chart, width_basis=12) for chart in col_cfg['charts']]
        )
        cols.append(dbc.Col(stack, width=col_cfg['width']))
    return dbc.Row(cols)

# Define Layout
app.layout = dbc.Container(
    fluid=True,
    style={"backgroundColor": "#f5f6fa", "minHeight": "100vh", "padding": "18px"},
    children=[
        # --- STATE MANAGEMENT ---
        dcc.Store(id='store-species', data='All'),
        dcc.Store(id='store-intake-type', data='All'),
        dcc.Store(id='store-year', data='All'),
        dcc.Store(id='store-outcome-status', data='All'),
        dcc.Store(id='store-outcome-type', data='All'),

        # --- HEADER ---
        dbc.Row([
            dbc.Col([
                html.H3("ANIMAL SHELTER OPERATIONS ANALYSIS", style={"margin": 0, "fontWeight": 700}),
                html.Div([
                    html.Span("Interactive Dashboard: Click charts to filter.", className="me-2"),
                    html.Span(id='filter-status', className="text-primary", style={"fontSize": "0.9rem"})
                ], style={"color": "#666"})
            ], md=10),
            dbc.Col(dbc.Button("RESET FILTERS", id="btn-reset", color="secondary", className="w-100"), md=2),
        ], className="gy-2 mb-3", align="center"),

        html.Hr(),

        # --- KPI SECTION ---
        html.Div(
            id='kpi-container',
            style={"display": "grid", "gridTemplateColumns": "repeat(5, 1fr)", "gap": "20px", "marginBottom": "20px", "justifyContent": "center"}
        ),

        # --- CHARTS SECTION ---
        build_vertical_layout()
    ]
)

# ┌──────────────────────────────────────────────────────────────────────────────┐
# │ 3. CALLBACKS: INTERACTIVITY & CROSS-FILTERING                                │
# └──────────────────────────────────────────────────────────────────────────────┘

# Callback 1: Handle User Clicks (Update Store)
@app.callback(
    [
        Output('store-species', 'data'),
        Output('store-intake-type', 'data'),
        Output('store-year', 'data'),
        Output('store-outcome-status', 'data'),
        Output('store-outcome-type', 'data'),
    ],
    [
        Input('btn-reset', 'n_clicks'),
        Input('fig_species', 'clickData'),
        Input('fig_intake_type', 'clickData'),
        Input('fig_trend', 'clickData'),
        Input('fig_outcomes_percentage', 'clickData'),
        Input('fig_outcome_type', 'clickData'),
    ],
    [
        State('store-species', 'data'),
        State('store-intake-type', 'data'),
        State('store-year', 'data'),
        State('store-outcome-status', 'data'),
        State('store-outcome-type', 'data'),
    ]
)
def update_filters(n_reset, c_species, c_intake, c_trend, c_status, c_outcome, 
                   cur_species, cur_intake, cur_year, cur_status, cur_outcome):
    
    ctx = callback_context
    if not ctx.triggered:
        return "All", "All", "All", "All", "All"
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'btn-reset':
        return "All", "All", "All", "All", "All"

    # Helper for Toggle Logic
    def toggle(new_val, current_val):
        return "All" if new_val == current_val else new_val

    if trigger_id == 'fig_species' and c_species:
        val = c_species['points'][0]['label']
        return toggle(val, cur_species), cur_intake, cur_year, cur_status, cur_outcome

    if trigger_id == 'fig_intake_type' and c_intake:
        # Bar chart orientation h: y is the category label
        val = c_intake['points'][0]['y'] 
        return cur_species, toggle(val, cur_intake), cur_year, cur_status, cur_outcome

    if trigger_id == 'fig_trend' and c_trend:
        # Trend chart x axis is Year
        val = c_trend['points'][0]['x']
        return cur_species, cur_intake, toggle(val, cur_year), cur_status, cur_outcome

    if trigger_id == 'fig_outcomes_percentage' and c_status:
        # Pie chart label is "Live" or "Non-Live"
        val = c_status['points'][0]['label']
        return cur_species, cur_intake, cur_year, toggle(val, cur_status), cur_outcome

    if trigger_id == 'fig_outcome_type' and c_outcome:
        val = c_outcome['points'][0]['y']
        return cur_species, cur_intake, cur_year, cur_status, toggle(val, cur_outcome)

    return cur_species, cur_intake, cur_year, cur_status, cur_outcome


# Callback 2: Update UI (KPIs and Charts) based on Stores
@app.callback(
    [
        Output('filter-status', 'children'),
        Output('kpi-container', 'children'),
        Output('fig_species', 'figure'),
        Output('fig_intake_type', 'figure'),
        Output('fig_trend', 'figure'),
        Output('fig_outcomes_percentage', 'figure'),
        Output('fig_outcome_type', 'figure'),
    ],
    [
        Input('store-species', 'data'),
        Input('store-intake-type', 'data'),
        Input('store-year', 'data'),
        Input('store-outcome-status', 'data'),
        Input('store-outcome-type', 'data'),
    ]
)
def update_ui(sel_species, sel_intake, sel_year, sel_status, sel_outcome):
    
    # 1. Status Text
    status_txt = f" | Species: {sel_species} | Intake: {sel_intake} | Year: {sel_year} | Status: {sel_status} | Outcome: {sel_outcome}"

    # 2. Filtering Function (Cross-Filtering Logic)
    def get_filtered_df(ignore_dims=[]):
        d = df.copy()
        if 'species' not in ignore_dims and sel_species != "All":
            d = d[d['Animal Type'] == sel_species]
        if 'intake' not in ignore_dims and sel_intake != "All":
            d = d[d['Intake Type'] == sel_intake]
        if 'year' not in ignore_dims and sel_year != "All":
            # For simplicity, filtering by Intake Year. 
            # Real-world apps might use a complex Date Table logic.
            d = d[d['Intake Year'] == int(sel_year)]
        if 'status' not in ignore_dims and sel_status != "All":
            is_alive_bool = True if sel_status == "Live" else False
            d = d[d['outcome_is_alive'] == is_alive_bool]
        if 'outcome' not in ignore_dims and sel_outcome != "All":
            d = d[d['Outcome Type'] == sel_outcome]
        return d

    # 3. Calculate KPIs (Apply ALL filters)
    kpi_df = get_filtered_df()
    
    t_intakes = len(kpi_df)
    t_outcomes = kpi_df['Outcome Date'].count()
    avg_los = kpi_df['intake_duration'].mean() if not kpi_df.empty else 0
    t_adoptions = len(kpi_df[kpi_df['Outcome Type'] == 'ADOPTION'])
    
    t_live = kpi_df['outcome_is_alive'].sum()
    lrr = (t_live / t_outcomes * 100) if t_outcomes > 0 else 0

    def create_kpi_card(label, val, color="#c23b5a"):
        return dbc.Card(
            dbc.CardBody([
                html.Div(val, style={"fontSize": "28px", "fontWeight": 700, "color": color}),
                html.Div(label, style={"color": "#555", "fontSize": "0.9rem"})
            ]), className="shadow-sm", style={"borderRadius": "14px"}
        )

    kpi_cards = [
        create_kpi_card("Total Intakes", f"{t_intakes:,.0f}"),
        create_kpi_card("Total Outcomes", f"{t_outcomes:,.0f}"),
        create_kpi_card("Avg Length of Stay", f"{avg_los:.1f} days"),
        create_kpi_card("Total Adoptions", f"{t_adoptions:,.0f}"),
        create_kpi_card("Live Release Rate", f"{lrr:.1f}%", color="#198754" if lrr > 90 else "#c23b5a"),
    ]

    # 4. Generate Charts (Apply filters EXCEPT self)
    
    # --- Chart 1: Species (Ignore Species Filter) ---
    d_species = get_filtered_df(ignore_dims=['species'])
    if d_species.empty:
        fig_species = go.Figure().add_annotation(text="No Data", showarrow=False)
    else:
        counts = d_species['Animal Type'].value_counts().reset_index()
        counts.columns = ['Animal Type', 'Count']
        fig_species = px.pie(counts, values='Count', names='Animal Type', hole=0.5, 
                             color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_species.update_traces(textposition='inside', textinfo='percent+label')
        # Pull selection
        if sel_species != "All":
            fig_species.update_traces(pull=[0.1 if x == sel_species else 0 for x in counts['Animal Type']])
        fig_species.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)

    # --- Chart 2: Intake Type (Ignore Intake Filter) ---
    d_intake = get_filtered_df(ignore_dims=['intake'])
    if d_intake.empty:
        fig_intake = go.Figure().add_annotation(text="No Data", showarrow=False)
    else:
        counts = d_intake['Intake Type'].value_counts().head(6).reset_index()
        counts.columns = ['Intake Type', 'Count']
        fig_intake = px.bar(counts, x='Count', y='Intake Type', orientation='h', text='Count')
        # Opacity selection
        colors = ['#0d6efd' if (sel_intake == "All" or x == sel_intake) else '#e9ecef' for x in counts['Intake Type']]
        fig_intake.update_traces(marker_color=colors, textposition='auto')
        fig_intake.update_layout(margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor='white',
                                 xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(autorange="reversed"))

    # --- Chart 3: Trend (Ignore Year Filter) ---
    d_trend = get_filtered_df(ignore_dims=['year'])
    if d_trend.empty:
        fig_trend = go.Figure().add_annotation(text="No Data", showarrow=False)
    else:
        # Aggregation
        trend_in = d_trend.groupby('Intake Year').size().reset_index(name='Count')
        trend_out = d_trend.groupby('Outcome Year').size().reset_index(name='Count')
        
        fig_trend = go.Figure()
        # Outcome Area
        fig_trend.add_trace(go.Scatter(x=trend_out['Outcome Year'], y=trend_out['Count'], name='Outcome',
                                       mode='lines', line=dict(color='#198754'), stackgroup='one', fillcolor='rgba(25,135,84,0.2)'))
        # Intake Line
        fig_trend.add_trace(go.Scatter(x=trend_in['Intake Year'], y=trend_in['Count'], name='Intake',
                                       mode='lines+markers', line=dict(color='#0d6efd')))
        
        fig_trend.update_layout(margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor='white',
                                legend=dict(orientation="h", y=1.1),
                                xaxis=dict(type='category', showgrid=False))
        # Highlight selection requires complex shape logic, omitting for simplicity in line chart

    # --- Chart 4: Outcomes Status (Ignore Status Filter) ---
    d_status = get_filtered_df(ignore_dims=['status'])
    if d_status.empty:
        fig_status = go.Figure().add_annotation(text="No Data", showarrow=False)
    else:
        counts = d_status['outcome_is_alive'].value_counts().reset_index()
        counts.columns = ['Is Alive', 'Count']
        counts['Status'] = counts['Is Alive'].map({True: 'Live', False: 'Non-Live'})
        
        fig_status = px.pie(counts, values='Count', names='Status', hole=0.5,
                            color='Status', color_discrete_map={'Live': '#28a745', 'Non-Live': '#6c757d'})
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        if sel_status != "All":
             fig_status.update_traces(pull=[0.1 if x == sel_status else 0 for x in counts['Status']])
        fig_status.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)

    # --- Chart 5: Outcome Type (Ignore Outcome Filter) ---
    d_outcome = get_filtered_df(ignore_dims=['outcome'])
    if d_outcome.empty:
        fig_outcome = go.Figure().add_annotation(text="No Data", showarrow=False)
    else:
        counts = d_outcome['Outcome Type'].value_counts().head(10).reset_index()
        counts.columns = ['Outcome Type', 'Count']
        fig_outcome = px.bar(counts, x='Count', y='Outcome Type', orientation='h', text='Count')
        
        colors = ['#198754' if (sel_outcome == "All" or x == sel_outcome) else '#e9ecef' for x in counts['Outcome Type']]
        fig_outcome.update_traces(marker_color=colors, textposition='auto')
        fig_outcome.update_layout(margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor='white',
                                  xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(autorange="reversed"))

    return status_txt, kpi_cards, fig_species, fig_intake, fig_trend, fig_status, fig_outcome

# ┌──────────────────────────────────────────────────────────────────────────────┐
# │ 4. 新增回调：重置 clickData (解决无法再次点击取消的问题)                       │
# └──────────────────────────────────────────────────────────────────────────────┘

@app.callback(
    [
        Output('fig_species', 'clickData'),
        Output('fig_intake_type', 'clickData'),
        Output('fig_trend', 'clickData'),
        Output('fig_outcomes_percentage', 'clickData'),
        Output('fig_outcome_type', 'clickData'),
    ],
    [
        Input('store-species', 'data'),
        Input('store-intake-type', 'data'),
        Input('store-year', 'data'),
        Input('store-outcome-status', 'data'),
        Input('store-outcome-type', 'data'),
    ]
)
def reset_click_data(a, b, c, d, e):
    """
    当 Store 更新后（意味着筛选已完成），
    强制将所有图表的 clickData 重置为 None。
    这样下一次点击同一个元素时，是从 None -> Value，
    从而确保能触发 update_filters 回调。
    """
    return None, None, None, None, None


if __name__ == "__main__":
    app.run(debug=True, port=8051)