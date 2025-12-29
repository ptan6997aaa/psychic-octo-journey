from dash import Dash, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

import data_loader
import layout
import figures as figs


# 1) Load data once (server-side)
df = data_loader.load_data()

# 2) Initialize app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Animal Shelter Operations Analysis"

# 3) Layout
app.layout = layout.create_layout()


# ------------------------------------------------------------------------------
# Callback 1: Handle clicks / reset (update filter stores)
# ------------------------------------------------------------------------------
@app.callback(
    [
        Output("store-species", "data"),
        Output("store-intake-type", "data"),
        Output("store-year", "data"),
        Output("store-outcome-status", "data"),
        Output("store-outcome-type", "data"),
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
    prevent_initial_call=True,
)
def update_filters(
    n_reset,
    c_species,
    c_intake,
    c_trend,
    c_status,
    c_outcome,
    cur_species,
    cur_intake,
    cur_year,
    cur_status,
    cur_outcome,
):
    ctx = callback_context
    if not ctx.triggered:
        return cur_species, cur_intake, cur_year, cur_status, cur_outcome

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "btn-reset":
        return "All", "All", "All", "All", "All"

    def toggle(new_val, current_val):
        return "All" if new_val == current_val else new_val

    if trigger_id == "fig_species" and c_species:
        val = c_species["points"][0].get("label")
        if val is None:
            return cur_species, cur_intake, cur_year, cur_status, cur_outcome
        return toggle(val, cur_species), cur_intake, cur_year, cur_status, cur_outcome

    if trigger_id == "fig_intake_type" and c_intake:
        val = c_intake["points"][0].get("y")
        if val is None:
            return cur_species, cur_intake, cur_year, cur_status, cur_outcome
        return cur_species, toggle(val, cur_intake), cur_year, cur_status, cur_outcome

    if trigger_id == "fig_trend" and c_trend:
        val = c_trend["points"][0].get("x")
        if val is None:
            return cur_species, cur_intake, cur_year, cur_status, cur_outcome
        # normalize year to int when possible
        try:
            val = int(val)
        except Exception:
            pass
        return cur_species, cur_intake, toggle(val, cur_year), cur_status, cur_outcome

    if trigger_id == "fig_outcomes_percentage" and c_status:
        val = c_status["points"][0].get("label")
        if val is None:
            return cur_species, cur_intake, cur_year, cur_status, cur_outcome
        return cur_species, cur_intake, cur_year, toggle(val, cur_status), cur_outcome

    if trigger_id == "fig_outcome_type" and c_outcome:
        val = c_outcome["points"][0].get("y")
        if val is None:
            return cur_species, cur_intake, cur_year, cur_status, cur_outcome
        return cur_species, cur_intake, cur_year, cur_status, toggle(val, cur_outcome)

    return cur_species, cur_intake, cur_year, cur_status, cur_outcome


# ------------------------------------------------------------------------------
# Callback 2: Update KPI + charts based on stores
# ------------------------------------------------------------------------------
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

    status_txt = (
        f" | Species: {sel_species}"
        f" | Intake: {sel_intake}"
        f" | Year: {sel_year}"
        f" | Status: {sel_status}"
        f" | Outcome: {sel_outcome}"
    )

    # KPIs: apply ALL filters
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
            color="#198754" if float(kpi_vals["lrr"].replace("%", "") or 0) > 90 else "#c23b5a",
        ),
    ]

    # Charts: apply filters EXCEPT self
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
    app.run(debug=True, port=8053)
