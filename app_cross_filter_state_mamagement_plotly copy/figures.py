import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def apply_filters(df: pd.DataFrame, selections: dict, ignore_dims=None) -> pd.DataFrame:
    """
    selections keys: species, intake, year, status, outcome
    ignore_dims is a list of those keys to ignore for a specific chart.
    """
    ignore_dims = ignore_dims or []
    d = df

    sel_species = selections.get("species", "All")
    sel_intake = selections.get("intake", "All")
    sel_year = selections.get("year", "All")
    sel_status = selections.get("status", "All")
    sel_outcome = selections.get("outcome", "All")

    if "species" not in ignore_dims and sel_species != "All":
        d = d[d["Animal Type"] == sel_species]

    if "intake" not in ignore_dims and sel_intake != "All":
        d = d[d["Intake Type"] == sel_intake]

    if "year" not in ignore_dims and sel_year != "All":
        try:
            y = int(sel_year)
            d = d[d["Intake Year"] == y]
        except Exception:
            # If something unexpected got stored, do nothing rather than crash
            pass

    if "status" not in ignore_dims and sel_status != "All":
        is_alive = True if sel_status == "Live" else False
        d = d[d["outcome_is_alive"] == is_alive]

    if "outcome" not in ignore_dims and sel_outcome != "All":
        d = d[d["Outcome Type"] == sel_outcome]

    return d


def get_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"intakes": "0", "outcomes": "0", "los": "0.0", "adoptions": "0", "lrr": "0.0%"}

    total_intakes = len(df)
    total_outcomes = df["Outcome Date"].count()
    avg_los = float(df["intake_duration"].mean()) if total_intakes > 0 else 0.0
    total_adoptions = int((df["Outcome Type"] == "ADOPTION").sum())
    total_live_outcomes = int(df["outcome_is_alive"].sum())

    lrr = (total_live_outcomes / total_outcomes * 100) if total_outcomes > 0 else 0.0

    return {
        "intakes": f"{total_intakes:,.0f}",
        "outcomes": f"{total_outcomes:,.0f}",
        "los": f"{avg_los:.1f}",
        "adoptions": f"{total_adoptions:,.0f}",
        "lrr": f"{lrr:.1f}%",
    }


def _no_data_fig(msg: str = "No Data") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False)
    fig.update_layout(template="plotly_white", margin=dict(t=10, b=10, l=10, r=10))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def create_species_pie(df: pd.DataFrame, selected="All") -> go.Figure:
    if df.empty:
        return _no_data_fig()

    counts = df["Animal Type"].value_counts().reset_index()
    counts.columns = ["Animal Type", "Count"]

    fig = px.pie(
        counts,
        values="Count",
        names="Animal Type",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    if selected != "All":
        fig.update_traces(pull=[0.1 if x == selected else 0 for x in counts["Animal Type"]])

    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
    return fig


def create_intake_bar(df: pd.DataFrame, selected="All") -> go.Figure:
    if df.empty:
        return _no_data_fig()

    counts = df["Intake Type"].value_counts().head(6).reset_index()
    counts.columns = ["Intake Type", "Count"]

    fig = px.bar(counts, x="Count", y="Intake Type", orientation="h", text="Count")

    colors = [
        "#0d6efd" if (selected == "All" or x == selected) else "#e9ecef"
        for x in counts["Intake Type"]
    ]
    fig.update_traces(marker_color=colors, textposition="auto")
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, showticklabels=False, title=None),
        yaxis=dict(autorange="reversed", title=None),
    )
    return fig


def create_trend_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _no_data_fig()

    trend_in = df.groupby("Intake Year").size().reset_index(name="Count").dropna(subset=["Intake Year"])
    trend_out = df.groupby("Outcome Year").size().reset_index(name="Count").dropna(subset=["Outcome Year"])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=trend_out["Outcome Year"].astype(int).astype(str),
            y=trend_out["Count"],
            name="Outcome",
            mode="lines",
            line=dict(color="#198754"),
            stackgroup="one",
            fillcolor="rgba(25,135,84,0.2)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=trend_in["Intake Year"].astype(int).astype(str),
            y=trend_in["Count"],
            name="Intake",
            mode="lines+markers",
            line=dict(color="#0d6efd"),
        )
    )

    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="white",
        legend=dict(orientation="h", y=1.1),
        xaxis=dict(type="category", showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor="#e9ecef", title=None),
    )
    return fig


def create_outcome_percentage(df: pd.DataFrame, selected="All") -> go.Figure:
    if df.empty:
        return _no_data_fig()

    counts = df["outcome_is_alive"].value_counts().reset_index()
    counts.columns = ["Is Alive", "Count"]
    counts["Status"] = counts["Is Alive"].map({True: "Live", False: "Non-Live"})

    fig = px.pie(
        counts,
        values="Count",
        names="Status",
        hole=0.5,
        color="Status",
        color_discrete_map={"Live": "#28a745", "Non-Live": "#6c757d"},
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    if selected != "All":
        fig.update_traces(pull=[0.1 if x == selected else 0 for x in counts["Status"]])

    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
    return fig


def create_outcome_bar(df: pd.DataFrame, selected="All") -> go.Figure:
    if df.empty:
        return _no_data_fig()

    counts = df["Outcome Type"].value_counts().head(10).reset_index()
    counts.columns = ["Outcome Type", "Count"]

    fig = px.bar(counts, x="Count", y="Outcome Type", orientation="h", text="Count")

    colors = [
        "#198754" if (selected == "All" or x == selected) else "#e9ecef"
        for x in counts["Outcome Type"]
    ]
    fig.update_traces(marker_color=colors, textposition="auto")
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, showticklabels=False, title=None),
        yaxis=dict(autorange="reversed", title=None),
    )
    return fig
