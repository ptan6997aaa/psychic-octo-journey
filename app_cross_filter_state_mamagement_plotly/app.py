from dash import Dash, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

# Custom imports
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
# MERGED CALLBACK: HANDLE CLICKS -> UPDATE STORES -> RESET CLICKS
# =============================================================================
@app.callback(
    [
        # 1. Outputs: The Stores (Data State)
        Output("store-species", "data"),
        Output("store-intake-type", "data"),
        Output("store-year", "data"),
        Output("store-outcome-status", "data"),
        Output("store-outcome-type", "data"),
        
        # 2. Outputs: The ClickData (Reset to None immediately)
        Output("fig_species", "clickData"),
        Output("fig_intake_type", "clickData"),
        Output("fig_trend", "clickData"),
        Output("fig_outcomes_percentage", "clickData"),
        Output("fig_outcome_type", "clickData"),
    ],
    [
        Input("btn-reset", "n_clicks"),
        Input("fig_species", "clickData"),
        Input("fig_intake_type", "clickData"),
        Input("fig_trend", "clickData"),
        Input("fig_outcomes_percentage", "clickData"),
        Input("fig_outcome_type", "clickData"),
    ],
    [
        State("store-species", "data"),
        State("store-intake-type", "data"),
        State("store-year", "data"),
        State("store-outcome-status", "data"),
        State("store-outcome-type", "data"),
    ],
)
def update_filters_and_reset(n_reset, c_species, c_intake, c_trend, c_status, c_outcome, 
                             cur_species, cur_intake, cur_year, cur_status, cur_outcome):
    
    # Default: No change
    stores = (cur_species, cur_intake, cur_year, cur_status, cur_outcome)
    # Always reset clickData to None to allow re-clicking the same bar
    resets = (None, None, None, None, None)

    ctx = callback_context
    if not ctx.triggered:
        return stores + resets

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # RESET BUTTON
    if trigger_id == "btn-reset":
        return ("All", "All", "All", "All", "All") + resets

    # HELPER: Toggle Logic
    def toggle(new_val, current_val):
        return "All" if str(new_val) == str(current_val) else new_val

    # GRAPH CLICKS
    # We calculate the new stores, and append the 'resets' tuple at the end
    
    if trigger_id == "fig_species" and c_species:
        val = c_species["points"][0].get("label")
        if val: 
            return (toggle(val, cur_species), cur_intake, cur_year, cur_status, cur_outcome) + resets

    if trigger_id == "fig_intake_type" and c_intake:
        val = c_intake["points"][0].get("y")
        if val: 
            return (cur_species, toggle(val, cur_intake), cur_year, cur_status, cur_outcome) + resets

    if trigger_id == "fig_trend" and c_trend:
        val = c_trend["points"][0].get("x")
        if val:
            try:
                val = int(val)
            except ValueError:
                pass
            return (cur_species, cur_intake, toggle(val, cur_year), cur_status, cur_outcome) + resets

    if trigger_id == "fig_outcomes_percentage" and c_status:
        val = c_status["points"][0].get("label")
        if val: 
            return (cur_species, cur_intake, cur_year, toggle(val, cur_status), cur_outcome) + resets

    if trigger_id == "fig_outcome_type" and c_outcome:
        val = c_outcome["points"][0].get("y")
        if val: 
            return (cur_species, cur_intake, cur_year, cur_status, toggle(val, cur_outcome)) + resets

    # Fallback: return current state + resets
    return stores + resets


# =============================================================================
# CALLBACK 2: UPDATE UI (KPIs and Charts)
# =============================================================================
@app.callback(
    [
        Output("filter-status", "children"),
        Output("kpi-container", "children"),
        Output("fig_species", "figure"),
        Output("fig_intake_type", "figure"),
        Output("fig_trend", "figure"),
        Output("fig_outcomes_percentage", "figure"),
        Output("fig_outcome_type", "figure"),
    ],
    [
        Input("store-species", "data"),
        Input("store-intake-type", "data"),
        Input("store-year", "data"),
        Input("store-outcome-status", "data"),
        Input("store-outcome-type", "data"),
    ],
)
def update_ui(sel_species, sel_intake, sel_year, sel_status, sel_outcome):
    
    selections = {
        "species": sel_species,
        "intake": sel_intake,
        "year": sel_year,
        "status": sel_status,
        "outcome": sel_outcome,
    }

    # 1. Update Status Text
    status_txt = (f" | Species: {sel_species} | Intake: {sel_intake} | "
                  f"Year: {sel_year} | Status: {sel_status} | Outcome: {sel_outcome}")

    # 2. KPIs
    kpi_df = figs.apply_filters(df, selections, ignore_dims=[])
    kpi_vals = figs.get_kpis(kpi_df)

    kpi_cards = [
        layout.make_kpi_card("Total Intakes", kpi_vals["intakes"]),
        layout.make_kpi_card("Total Outcomes", kpi_vals["outcomes"]),
        layout.make_kpi_card("Avg Length of Stay", f'{kpi_vals["los"]} days'),
        layout.make_kpi_card("Total Adoptions", kpi_vals["adoptions"]),
        layout.make_kpi_card(
            "Live Release Rate", 
            kpi_vals["lrr"], 
            color="#198754" if float(kpi_vals["lrr"].replace("%", "") or 0) > 90 else "#c23b5a"
        ),
    ]

    # 3. Figures (Cross-filtering: ignore self)
    d_species = figs.apply_filters(df, selections, ignore_dims=["species"])
    fig_species = figs.create_species_pie(d_species, selected=sel_species)

    d_intake = figs.apply_filters(df, selections, ignore_dims=["intake"])
    fig_intake = figs.create_intake_bar(d_intake, selected=sel_intake)

    d_trend = figs.apply_filters(df, selections, ignore_dims=["year"])
    fig_trend = figs.create_trend_chart(d_trend)

    d_status = figs.apply_filters(df, selections, ignore_dims=["status"])
    fig_status = figs.create_outcome_percentage(d_status, selected=sel_status)

    d_outcome = figs.apply_filters(df, selections, ignore_dims=["outcome"])
    fig_outcome = figs.create_outcome_bar(d_outcome, selected=sel_outcome)

    return status_txt, kpi_cards, fig_species, fig_intake, fig_trend, fig_status, fig_outcome


if __name__ == "__main__":
    app.run(debug=True, port=8052)