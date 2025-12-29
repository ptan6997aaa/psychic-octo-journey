from dash import Dash, Input, Output, State, callback_context, html
import dash_bootstrap_components as dbc
import data_loader
import layout
import figures as figs

# 1. Load Data
df = data_loader.load_data()

# 2. Initialize App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Animal Shelter Operations Analysis"
app.layout = layout.create_layout()

# =============================================================================
# CALLBACK 1: HANDLE USER CLICKS -> UPDATE STORES
# =============================================================================
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
        val = c_intake['points'][0]['y'] 
        return cur_species, toggle(val, cur_intake), cur_year, cur_status, cur_outcome

    if trigger_id == 'fig_trend' and c_trend:
        # Trend chart x axis is Year
        val = c_trend['points'][0]['x']
        return cur_species, cur_intake, toggle(val, cur_year), cur_status, cur_outcome

    if trigger_id == 'fig_outcomes_percentage' and c_status:
        val = c_status['points'][0]['label']
        return cur_species, cur_intake, cur_year, toggle(val, cur_status), cur_outcome

    if trigger_id == 'fig_outcome_type' and c_outcome:
        val = c_outcome['points'][0]['y']
        return cur_species, cur_intake, cur_year, cur_status, toggle(val, cur_outcome)

    return cur_species, cur_intake, cur_year, cur_status, cur_outcome


# =============================================================================
# CALLBACK 2: UPDATE UI (KPIs and Charts) based on STORES
# =============================================================================
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

    # 2. Filtering Function
    def get_filtered_df(ignore_dims=[]):
        d = df.copy()
        if 'species' not in ignore_dims and sel_species != "All":
            d = d[d['Animal Type'] == sel_species]
        if 'intake' not in ignore_dims and sel_intake != "All":
            d = d[d['Intake Type'] == sel_intake]
        if 'year' not in ignore_dims and sel_year != "All":
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

    # Helper for KPI cards
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

    # 4. Generate Figures (Call figures.py logic)
    # We pass the subset of data (ignoring self-filter) AND the current selection for highlighting
    
    fig_species = figs.create_species_pie(get_filtered_df(ignore_dims=['species']), sel_species)
    fig_intake = figs.create_intake_bar(get_filtered_df(ignore_dims=['intake']), sel_intake)
    fig_trend = figs.create_trend_chart(get_filtered_df(ignore_dims=['year']), sel_year)
    fig_outcomes_percentage = figs.create_outcome_percentage(get_filtered_df(ignore_dims=['status']), sel_status)
    fig_outcome_type = figs.create_outcome_bar(get_filtered_df(ignore_dims=['outcome']), sel_outcome)

    return status_txt, kpi_cards, fig_species, fig_intake, fig_trend, fig_outcomes_percentage, fig_outcome_type

if __name__ == "__main__":
    app.run(debug=True, port=8052)