import pandas as pd
import numpy as np
import dash
from dash import dcc, html, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Initialize the app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = html.Div([
    html.H1("Gene and sgRNA Data Explorer", className="mt-3 mb-4"),
    
    dbc.Row([
        # Sidebar
        dbc.Col([
            html.Label("Select Genes of Interest:"),
            dcc.Dropdown(
                id='selected-genes',
                multi=True,
                placeholder="Type to search genes...",
                style={"marginBottom": "15px"}
            ),
            
            html.Label("Filter by Group:"),
            dcc.Dropdown(
                id='filter-group',
                multi=True,
                placeholder="All Groups",
                style={"marginBottom": "15px"}
            ),
            
            html.Label("Filter by Number of Replicates:"),  # Changed from "Filter by Size:"
            html.Div([
                dcc.RangeSlider(
                    id='filter-size',
                    min=0,
                    max=100,  # Will be updated dynamically
                    step=1,
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={"marginBottom": "25px"}),
            
            dbc.Button("Apply Selection", id="apply-selection", color="primary", 
                      className="mb-3", style={"width": "100%"})
        ], width=3, style={"padding": "15px", "background-color": "#f8f9fa", "borderRadius": "5px"}),
        
        # Main panel
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="Mu Data (Gene Expression)", children=[
                    html.Br(),
                    html.Button("Download Selected Mu Data", id="download-mu", 
                               className="btn btn-outline-primary mb-3"),
                    dcc.Download(id="download-mu-data"),
                    
                    # Visualization for gene expression
                    html.H4("Gene Expression by Number of Replicates"),
                    dcc.Dropdown(
                        id='mu-gene-to-plot',
                        placeholder="Select gene to plot",
                        style={"width": "50%", "marginBottom": "10px"}
                    ),
                    dcc.Graph(id='mu-group-size-plot', style={"height": "600px"}),
                    # Add explanatory note about the plot
                    html.Div("Note: Each box plot represents a different cell line.", 
                             style={"fontStyle": "italic", "color": "#666", "marginTop": "5px", "marginBottom": "15px"}),
                    
                    html.Hr(),
                    
                    dash_table.DataTable(
                        id='mu-table',
                        page_size=10,
                        style_table={'overflowX': 'auto'},
                    )
                ]),
                dbc.Tab(label="Phi Data (sgRNAs)", children=[
                    html.Br(),
                    html.Button("Download Selected Phi Data", id="download-phi", 
                               className="btn btn-outline-primary mb-3"),
                    dcc.Download(id="download-phi-data"),
                    
                    # Visualization for sgRNA activity
                    html.H4("sgRNA Activity by Number of Replicates"),
                    dcc.Dropdown(
                        id='phi-sgrna-to-plot',
                        placeholder="Select sgRNA to plot",
                        style={"width": "50%", "marginBottom": "10px"}
                    ),
                    dcc.Graph(id='phi-group-size-plot', style={"height": "600px"}),
                    # Add explanatory note about the plot points
                    html.Div("Note: Each dot represents a different cell line.", 
                             style={"fontStyle": "italic", "color": "#666", "marginTop": "5px", "marginBottom": "15px"}),
                    
                    html.Hr(),
                    
                    dash_table.DataTable(
                        id='phi-table',
                        page_size=10,
                        style_table={'overflowX': 'auto'},
                    )
                ]),
            ])
        ], width=9)
    ])
])

# Function to get unique groups and size range from the data
@callback(
    [Output('filter-group', 'options'),
     Output('filter-size', 'min'),
     Output('filter-size', 'max'),
     Output('filter-size', 'value')],
    Input('filter-group', 'id')  # Just a dummy input to trigger on load
)
def initialize_filters(dummy):
    # Read a small sample to get metadata
    mu_data = pd.read_csv("modified_mu_jg.csv", usecols=['size', 'group'])
    
    # Get unique groups
    groups = mu_data['group'].dropna().unique().tolist()
    group_options = [{"label": f"Group {g}", "value": g} for g in groups]
    
    # Get size range
    min_size = int(mu_data['size'].min())
    max_size = int(mu_data['size'].max())
    
    return group_options, min_size, max_size, [min_size, max_size]

# Initialize the gene selection dropdown
@callback(
    Output('selected-genes', 'options'),
    Input('selected-genes', 'search_value'),
    State('selected-genes', 'value'),  # Add this to preserve current selections
    prevent_initial_call=True
)
def update_gene_options(search_value, current_value):
    # Read header only from mu_data to get column names
    mu_cols = pd.read_csv("modified_mu_jg.csv", nrows=1).columns.tolist()
    
    # Extract gene names by excluding first and last two columns
    gene_names = mu_cols[1:-2]
    
    # Filter genes based on search value
    if search_value:
        filtered_genes = [gene for gene in gene_names if search_value.lower() in gene.lower()]
    else:
        filtered_genes = gene_names[:100]  # Limit initial load to 100 genes
    
    # Make sure current selections are always included in options
    if current_value:
        # Ensure all currently selected genes appear in options even if they don't match search
        selected_genes_not_in_filtered = [gene for gene in current_value if gene not in filtered_genes]
        filtered_genes = filtered_genes + selected_genes_not_in_filtered
    
    return [{"label": gene, "value": gene} for gene in filtered_genes]

# Create a mapping of sgRNAs to genes
def get_sgrna_gene_map():
    # Read header only from phi_data to get column names
    phi_cols = pd.read_csv("modified_phi_ig.csv", nrows=1).columns.tolist()
    
    # Extract sgRNA columns by excluding first and last two columns
    sgrna_cols = phi_cols[1:-2]
    
    # Extract gene names from sgRNA columns (everything before the underscore)
    sgrna_genes = [col.split('_')[0] if '_' in col else col for col in sgrna_cols]
    
    # Create a mapping of sgRNA columns to their corresponding genes
    sgrna_gene_map = pd.DataFrame({
        'sgrna_col': sgrna_cols,
        'gene': sgrna_genes
    })
    
    return sgrna_gene_map

# Load data based on user selection
@callback(
    [Output('mu-table', 'data'),
     Output('mu-table', 'columns'),
     Output('phi-table', 'data'),
     Output('phi-table', 'columns'),
     Output('mu-gene-to-plot', 'options'),
     Output('phi-sgrna-to-plot', 'options')],
    Input('apply-selection', 'n_clicks'),
    [State('selected-genes', 'value'),
     State('filter-group', 'value'),
     State('filter-size', 'value')],
    prevent_initial_call=True
)
def update_tables(n_clicks, selected_genes, selected_groups, size_range):
    if not selected_genes:
        return [], [], [], [], [], []
    
    # Read column names from mu_data
    mu_cols = pd.read_csv("modified_mu_jg.csv", nrows=1).columns.tolist()
    
    # Determine columns to read from mu_data
    first_col = [mu_cols[0]]  # First column (design)
    gene_cols = [col for col in mu_cols if col in selected_genes]
    last_cols = mu_cols[-2:]  # Last two columns (size and group)
    
    selected_mu_cols = first_col + gene_cols + last_cols
    
    # Read only the needed columns from mu_data
    selected_mu_data = pd.read_csv("modified_mu_jg.csv", usecols=selected_mu_cols)
    
    # Apply filters
    if size_range:
        min_size, max_size = size_range
        selected_mu_data = selected_mu_data[(selected_mu_data['size'] >= min_size) & 
                                          (selected_mu_data['size'] <= max_size)]
    
    if selected_groups:
        selected_mu_data = selected_mu_data[selected_mu_data['group'].isin(selected_groups)]
    
    # Get sgRNA to gene mapping
    sgrna_gene_map = get_sgrna_gene_map()
    
    # Find sgRNA columns that match the selected genes
    selected_sgrna_cols = sgrna_gene_map[sgrna_gene_map['gene'].isin(selected_genes)]['sgrna_col'].tolist()
    
    # Read column names from phi_data
    phi_cols = pd.read_csv("modified_phi_ig.csv", nrows=1).columns.tolist()
    
    # Determine columns to read from phi_data
    first_col = [phi_cols[0]]  # First column (design)
    last_cols = phi_cols[-2:]  # Last two columns (size and group)
    
    selected_phi_cols = first_col + selected_sgrna_cols + last_cols
    
    # Read only the needed columns from phi_data
    selected_phi_data = pd.read_csv("modified_phi_ig.csv", usecols=selected_phi_cols)
    
    # Apply filters
    if size_range:
        min_size, max_size = size_range
        selected_phi_data = selected_phi_data[(selected_phi_data['size'] >= min_size) & 
                                            (selected_phi_data['size'] <= max_size)]
    
    if selected_groups:
        selected_phi_data = selected_phi_data[selected_phi_data['group'].isin(selected_groups)]
    
    # Format for DataTable
    mu_columns = [{"name": col, "id": col} for col in selected_mu_data.columns]
    phi_columns = [{"name": col, "id": col} for col in selected_phi_data.columns]
    
    # Create options for the plot dropdowns
    mu_plot_options = [{"label": gene, "value": gene} for gene in gene_cols]
    phi_plot_options = [{"label": sgrna, "value": sgrna} for sgrna in selected_sgrna_cols]
    
    return (selected_mu_data.to_dict('records'), mu_columns, 
            selected_phi_data.to_dict('records'), phi_columns,
            mu_plot_options, phi_plot_options)

# Create gene expression plot for each combination of group and size
@callback(
    Output('mu-group-size-plot', 'figure'),
    [Input('mu-gene-to-plot', 'value'),
     Input('mu-table', 'data')],
    prevent_initial_call=True
)
def update_mu_group_size_plot(gene, table_data):
    if not gene or not table_data:
        return go.Figure().update_layout(title="Select a gene to visualize")
    
    df = pd.DataFrame(table_data)
    
    # Check if we have group and size information
    if 'group' not in df.columns or 'size' not in df.columns:
        return go.Figure().update_layout(title="Data does not contain group or size information")
    
    # Convert group and size to string for better display
    df['group'] = df['group'].astype(str)
    df['size'] = df['size'].astype(str)
    
    # Create combined box plot with all groups shown side by side for each size
    fig = px.box(
        df, 
        x='size',
        y=gene,
        color='group',
        points='all',  # Show all points
        hover_data=['design'],  # Include sample name in hover
        title=f"Expression of {gene} across cellines",  # Updated title
        category_orders={'size': sorted(df['size'].unique(), key=lambda x: int(x))},  # Sort sizes numerically
        height=600
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Number of Replicates",  # Changed from "Size"
        yaxis_title="Expression Level",
        showlegend=False,  # Remove or hide the legend
        boxmode='group'  # Group boxes by size
    )
    
    return fig

# Create sgRNA activity plot for each combination of group and size
@callback(
    Output('phi-group-size-plot', 'figure'),
    [Input('phi-sgrna-to-plot', 'value'),
     Input('phi-table', 'data')],
    prevent_initial_call=True
)
def update_phi_group_size_plot(sgrna, table_data):
    if not sgrna or not table_data:
        return go.Figure().update_layout(title="Select an sgRNA to visualize")
    
    df = pd.DataFrame(table_data)
    
    # Check if we have size information
    if 'size' not in df.columns:
        return go.Figure().update_layout(title="Data does not contain size information")
    
    # Convert size to string for better display
    df['size'] = df['size'].astype(str)
    
    # Create box plot without group coloring
    fig = px.box(
        df, 
        x='size',
        y=sgrna,
        points='all',
        hover_data=['design'],
        title=f"Activity of sgRNA {sgrna} across cell lines",
        category_orders={'size': sorted(df['size'].unique(), key=lambda x: int(x))},
        height=600
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Number of Replicates",
        yaxis_title="sgRNA Activity",
        boxmode='group'
    )
    
    return fig

# Download handlers
@callback(
    Output("download-mu-data", "data"),
    Input("download-mu", "n_clicks"),
    State('mu-table', 'data'),
    prevent_initial_call=True
)
def download_mu_data(n_clicks, data):
    if not data:
        return dash.no_update
    
    df = pd.DataFrame(data)
    return dcc.send_data_frame(df.to_csv, "selected_mu_data.csv", index=False)

@callback(
    Output("download-phi-data", "data"),
    Input("download-phi", "n_clicks"),
    State('phi-table', 'data'),
    prevent_initial_call=True
)
def download_phi_data(n_clicks, data):
    if not data:
        return dash.no_update
    
    df = pd.DataFrame(data)
    return dcc.send_data_frame(df.to_csv, "selected_phi_data.csv", index=False)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)