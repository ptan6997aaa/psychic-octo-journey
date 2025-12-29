from dash import Dash
import dash_bootstrap_components as dbc
import data_loader
import layout
import figures as figs

# 1. Load Data
df = data_loader.load_data()
kpis = figs.get_kpis(df)

# 2. Initialize App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Animal Shelter Operations Analysis"

# 3. Set Layout
app.layout = layout.create_layout(df, kpis)

if __name__ == "__main__":
    app.run(debug=True, port=8050)