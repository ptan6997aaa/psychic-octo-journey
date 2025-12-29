import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def get_kpis(df: pd.DataFrame) -> dict:
    """Calculates summary statistics for the Animal Shelter dashboard."""
    if df.empty:
        return {"intakes": "0", "outcomes": "0", "los": "0.0", "adoptions": "0", "lrr": "0.0%"}

    total_intakes = len(df)
    total_outcomes = df['Outcome Date'].count()
    avg_los = df['intake_duration'].mean()
    total_adoptions = len(df[df['Outcome Type'] == 'ADOPTION'])
    
    total_live_outcomes = df['outcome_is_alive'].sum()
    if total_outcomes > 0:
        lrr = (total_live_outcomes / total_outcomes) * 100
    else:
        lrr = 0

    return {
        "intakes": f"{total_intakes:,.0f}",
        "outcomes": f"{total_outcomes:,.0f}",
        "los": f"{avg_los:.1f}",
        "adoptions": f"{total_adoptions:,.0f}",
        "lrr": f"{lrr:.1f}%"
    }

def create_species_pie(df: pd.DataFrame):
    if df.empty: return px.pie(title="No Data")
    counts = df['Animal Type'].value_counts().reset_index()
    counts.columns = ['Animal Type', 'Count']

    fig = px.pie(counts, values='Count', names='Animal Type', hole=0.5, 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_intake_bar(df: pd.DataFrame):
    if df.empty: return px.bar(title="No Data")
    counts = df['Intake Type'].value_counts().head(6).reset_index()
    counts.columns = ['Intake Type', 'Count'] 

    fig = px.bar(counts, x='Count', y='Intake Type', orientation='h', text='Count')
    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(showgrid=False, showticklabels=False, title=None),
        yaxis=dict(autorange="reversed", title=None),
        plot_bgcolor='white'
    )
    fig.update_traces(marker_color='#6c757d', textposition='auto')
    return fig

def create_outcome_percentage(df: pd.DataFrame):
    if df.empty: return px.pie(title="No Data")
    counts = df['outcome_is_alive'].value_counts().reset_index()
    counts.columns = ['Is Alive', 'Count']
    counts['Status'] = counts['Is Alive'].map({True: 'Live', False: 'Non-Live'})

    fig = px.pie(
        counts, values='Count', names='Status', hole=0.5, color='Status',
        color_discrete_map={'Live': '#28a745', 'Non-Live': '#6c757d'} 
    )
    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
    fig.update_traces(textposition='inside', textinfo='percent+label') 
    return fig

def create_trend_chart(df: pd.DataFrame):
    if df.empty: return go.Figure()
    
    # Calculate Intake Volume
    df_intake = df.groupby(df['Intake Date'].dt.year).size().reset_index(name='Count')
    df_intake.columns = ['Year', 'Count']
    
    # Calculate Outcome Volume
    df_outcome = df.groupby(df['Outcome Date'].dt.year).size().reset_index(name='Count')
    df_outcome.columns = ['Year', 'Count']
    
    # Clean data
    df_intake = df_intake.dropna(subset=['Year'])
    df_outcome = df_outcome.dropna(subset=['Year'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_outcome['Year'], y=df_outcome['Count'], name='Outcome', mode='lines',
        line=dict(color='#198754'), fill='tozeroy', fillcolor='rgba(25,135,84,0.20)'
    ))
    fig.add_trace(go.Scatter(
        x=df_intake['Year'], y=df_intake['Count'], name='Intake', mode='lines+markers',
        line=dict(color='#0d6efd'), marker=dict(color='#0d6efd')
    ))

    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        plot_bgcolor='white',
        xaxis=dict(tickmode='linear', showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
    )
    return fig

def create_outcome_bar(df: pd.DataFrame):
    if df.empty: return px.bar(title="No Data")
    counts = df['Outcome Type'].value_counts().head(10).reset_index()
    counts.columns = ['Outcome Type', 'Count'] 

    fig = px.bar(counts, x='Count', y='Outcome Type', orientation='h', text='Count')
    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(showgrid=False, showticklabels=False, title=None),
        yaxis=dict(autorange="reversed", title=None),
        plot_bgcolor='white'
    )
    fig.update_traces(marker_color='#198754', textposition='auto') 
    return fig