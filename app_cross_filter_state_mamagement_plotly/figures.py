import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# =============================================================================
# FIGURE GENERATORS
# =============================================================================

def create_species_pie(df: pd.DataFrame, selected_species="All"):
    if df.empty: return _empty_fig("No Data")
    
    counts = df['Animal Type'].value_counts().reset_index()
    counts.columns = ['Animal Type', 'Count']

    fig = px.pie(counts, values='Count', names='Animal Type', hole=0.5, 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    
    # Highlight Selection: Pull the slice if selected
    if selected_species != "All":
        fig.update_traces(pull=[0.1 if x == selected_species else 0 for x in counts['Animal Type']])
        
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_intake_bar(df: pd.DataFrame, selected_intake="All"):
    if df.empty: return _empty_fig("No Data")
    
    counts = df['Intake Type'].value_counts().head(6).reset_index()
    counts.columns = ['Intake Type', 'Count'] 

    fig = px.bar(counts, x='Count', y='Intake Type', orientation='h', text='Count')
    
    # Highlight Selection: Grey out unselected bars
    colors = ['#0d6efd' if (selected_intake == "All" or x == selected_intake) else '#e9ecef' for x in counts['Intake Type']]
    
    fig.update_traces(marker_color=colors, textposition='auto')
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, showticklabels=False, title=None),
        yaxis=dict(autorange="reversed", title=None),
        plot_bgcolor='white'
    )
    return fig

def create_outcome_percentage(df: pd.DataFrame, selected_status="All"):
    if df.empty: return _empty_fig("No Data")
    
    counts = df['outcome_is_alive'].value_counts().reset_index()
    counts.columns = ['Is Alive', 'Count']
    counts['Status'] = counts['Is Alive'].map({True: 'Live', False: 'Non-Live'})

    fig = px.pie(
        counts, values='Count', names='Status', hole=0.5, 
        color='Status',
        color_discrete_map={'Live': '#28a745', 'Non-Live': '#6c757d'} 
    )
    
    # Highlight Selection: Pull slice
    if selected_status != "All":
        fig.update_traces(pull=[0.1 if x == selected_status else 0 for x in counts['Status']])

    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
    fig.update_traces(textposition='inside', textinfo='percent+label') 
    return fig

def create_trend_chart(df: pd.DataFrame, selected_year="All"):
    if df.empty: return _empty_fig("No Data")
    
    # Aggregation
    df_intake = df.groupby('Intake Year').size().reset_index(name='Count')
    df_outcome = df.groupby('Outcome Year').size().reset_index(name='Count')
    
    # Merge/Clean to ensure clean lines
    df_intake = df_intake.dropna(subset=['Intake Year'])
    df_outcome = df_outcome.dropna(subset=['Outcome Year'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_outcome['Outcome Year'], y=df_outcome['Count'], name='Outcome', mode='lines',
        line=dict(color='#198754'), fill='tozeroy', fillcolor='rgba(25,135,84,0.20)'
    ))
    fig.add_trace(go.Scatter(
        x=df_intake['Intake Year'], y=df_intake['Count'], name='Intake', mode='lines+markers',
        line=dict(color='#0d6efd'), marker=dict(color='#0d6efd')
    ))

    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor='white',
        xaxis=dict(tickmode='linear', showgrid=False, type='category'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
    )
    return fig

def create_outcome_bar(df: pd.DataFrame, selected_outcome="All"):
    if df.empty: return _empty_fig("No Data")
    
    counts = df['Outcome Type'].value_counts().head(10).reset_index()
    counts.columns = ['Outcome Type', 'Count'] 

    fig = px.bar(counts, x='Count', y='Outcome Type', orientation='h', text='Count')
    
    # Highlight Selection: Grey out unselected
    colors = ['#198754' if (selected_outcome == "All" or x == selected_outcome) else '#e9ecef' for x in counts['Outcome Type']]

    fig.update_traces(marker_color=colors, textposition='auto') 
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, showticklabels=False, title=None),
        yaxis=dict(autorange="reversed", title=None),
        plot_bgcolor='white'
    )
    return fig

def _empty_fig(text):
    fig = go.Figure()
    fig.add_annotation(text=text, showarrow=False)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig