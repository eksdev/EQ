import os
import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
from assets.fundamental import get_metrics
from assets.func.portfoliooptimizer import PortfolioOptimizer
from assets.sectorseparate import sectorseparate
import stripe

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Fundamental Tab Setup
FUND_COLUMNS = [
    "Ticker", "P/E", "Insider Own", "Market Cap", "Forward P/E", "Short Interest", "Income", "Sales", "ROE", "ROA", "Beta", "Employees", "Sales Y/Y TTM"
]
FUND_COLUMNS_DEFS = [{"name": col, "id": col} for col in FUND_COLUMNS]

# Portfolio Optimizer Tab Setup
PORTFOLIO_COLUMNS = [
    {"name": "Ticker", "id": "Ticker"},
    {"name": "Allocation (%)", "id": "Allocation (%)"}
]

# Set your Stripe secret key
stripe.api_key = "sk_test_51QbkRK4SsxaWFVRwopdUF8UxbQ9IMVUXNpKujX22w3t13Nk7zim0pMgwzCmCBkxYfSullTwqaFNMl4S5ZUgS3xpJ00IKPUYN8v"

# Path to the CSV file
file_path = 'assets/COMPREHENSIVE.csv'

# Load sector data
try:
    sector_dataframes = sectorseparate(file_path)
except Exception as e:
    print(f"Error loading sector data: {e}")
    sector_dataframes = {}

# Prepare top 5 data for specified sectors
def get_top_5_by_sector(dataframes, sectors):
    top_5_tables = {}
    for sector in sectors:
        if sector in dataframes:
            top_5_tables[sector] = dataframes[sector].head(5)
    return top_5_tables

selected_sectors = ["Consumer Defensive", "Consumer Cyclical"]
top_5_by_sector = get_top_5_by_sector(sector_dataframes, selected_sectors)

# Initialize the Dash app with suppress_callback_exceptions
app = dash.Dash(__name__, suppress_callback_exceptions=True)


app.layout = html.Div([
    html.Img(
        src='/assets/EIQ2.png',
        className="float-effect",
        style={
            'width': '200px', 'height': 'auto', 'display': 'block',
            'marginLeft': 'auto', 'marginRight': 'auto', 'padding': '1rem'
        }
    ),

    dcc.Store(id='metrics-store', data=[]),
    dcc.Store(id='tickers-store', data=[]),

    dcc.Tabs([
        # Home Tab
        dcc.Tab(label="Home", children=[
        html.Div([
            html.H1(
                "Welcome to EQuity",
                className="fade-in-up",
                style={"textAlign": "center", "color": "var(--color-primary)", "marginTop": "1rem"}
            ),
            html.Div([
                html.Div([
                    html.P(
                        [
                            html.B("EQuity ", style={"fontWeight": "bold", "color": "var(--color-primary)"}),
                            "is a Quantitative Market Research Group based in Rhode Island, committed to ",
                            html.Span("revolutionizing ", style={"color": "var(--color-secondary)", "fontWeight": "bold"}),
                            "the way investors approach portfolio optimization. Our mission is to ",
                            html.Span("consistently outperform traditional portfolio returns ", style={"fontStyle": "italic"}),
                            "by employing a comprehensive mix of proprietary and well-established methodologies."
                        ],
                        className="fade-in-up",
                        style={"textAlign": "justify", "marginBottom": "1rem", "fontSize": "1.2rem", "lineHeight": "1.8"}
                    ),
                    html.P(
                        [
                            "Our approach is deeply rooted in advanced statistical and computational techniques. By leveraging tools ",
                            "such as ", html.B("machine learning algorithms, predictive analytics,"), " and momentum-based trading strategies, we strive ",
                            "to identify trends and inefficiencies that may elude conventional investment practices. We analyze a diverse ",
                            "range of financial indicators, including valuation metrics, growth potential, risk factors, and market sentiment, ",
                            "to craft strategies that deliver sustainable and optimized returns."
                        ],
                        className="fade-in-up",
                        style={"textAlign": "justify", "marginBottom": "1rem", "fontSize": "1.2rem", "lineHeight": "1.8"}
                    ),
                    html.P(
                        [
                            "In addition to identifying undervalued assets, our methods include robust sector-specific analyses, allowing us ",
                            "to recognize emerging growth opportunities across diverse industries. Through the integration of proprietary ",
                            "screening engines and time-tested economic principles, EQuity ensures that each investment decision is grounded ",
                            "in rigorous research and a forward-looking perspective. By combining defensive strategies with targeted growth ",
                            "initiatives, we provide clients with a dynamic framework for navigating volatile market conditions."
                        ],
                        className="fade-in-up",
                        style={"textAlign": "justify", "marginBottom": "1rem", "fontSize": "1.2rem", "lineHeight": "1.8"}
                    )
                ], style={"padding": "1rem", "backgroundColor": "var(--color-surface)", "borderRadius": "8px", "boxShadow": "var(--shadow-medium)"})
            ], style={"padding": "2rem"})
        ], style={"padding": "2rem", "backgroundColor": "var(--color-background)"})
    ]),

        # All-Inclusive Guide Tab
        dcc.Tab(label="All-Inclusive Guide", children=[
            html.Div([
                html.H2("Our Guide to Equities", className="fade-in-up", style={"textAlign": "center", "color": "var(--color-primary)"}),
                html.P(
                    [
                        "Discover how EQuity uses advanced analysis platforms to provide stock picks. These picks come with ",
                        "detailed insights, proprietary metrics, and explanations tailored to all stages of investor. For ",
                        html.Span("only $10", style={"fontWeight": "bold", "textDecoration": "underline", "color": "var(--color-secondary)"}),
                        ", gain access to our all-inclusive guide to analyzing stocks and a breakdown of the crypto market. This includes a dissection of specific ",
                        "companies from financial and technical perspectives, as well as access to the proprietary formulas we use to screen for stocks."
                    ],
                    className="fade-in-up",
                    style={"textAlign": "center", "margin": "1rem", "fontSize": "1.1rem", "lineHeight": "1.8"}
                ),
                html.Div([
                    html.H3("Features Include:", style={"color": "var(--color-secondary)"}),
                    html.Ul([
                        html.Li("Data-driven stock selections leveraging AI.", className="hoverable"),
                        html.Li("Comprehensive financial and technical analyses.", className="hoverable"),
                        html.Li("Insights into the crypto market with actionable strategies.", className="hoverable"),
                    ], style={"lineHeight": "1.8", "padding": "1rem", "border": "1px solid var(--color-border)", "borderRadius": "8px"})
                ], style={"backgroundColor": "var(--color-surface)", "padding": "1.5rem", "boxShadow": "var(--shadow-light)"}),
                html.Div([
                    html.Button(
                        "Buy Now", id="buy-now-button",
                        className="button-ripple",
                        style={
                            "padding": "0.75rem 1.5rem",
                            "backgroundColor": "var(--color-primary)",
                            "color": "#fff",
                            "border": "none",
                            "borderRadius": "var(--radius-base)",
                            "boxShadow": "var(--shadow-hover)"
                        }
                    )
                ], style={"textAlign": "center", "marginTop": "2rem"}),
                html.Div(id="payment-confirmation", style={"marginTop": "1rem", "color": "green", "textAlign": "center"})
            ], style={"padding": "2rem", "backgroundColor": "var(--color-background)"})
        ]),

        # Sector Analysis Tab
        dcc.Tab(label="Sector Analysis", children=[
            html.Div([
                html.H2("Top 5 Symbols by Sector", style={"textAlign": "center", "color": "var(--color-primary)", "animation": "fadeInUp 0.5s ease"}),
                html.Div(
                    children=[
                        html.P(
                            [
                                html.Span("How We Select Top Stocks: ", style={"fontWeight": "bold", "color": "var(--color-primary)"}),
                                "Our selection process begins with SEC filings, evaluating all stock symbols with ",
                                html.Span("positive earnings and EBIT Growth over the last year. ", style={"fontStyle": "italic"}),
                                "Stocks are then filtered based on critical metrics such as ",
                                html.B("P/E ratio and other financial fundamentals. "),
                                "The proprietary ",
                                html.Span("VALUE RATIO ", style={"fontWeight": "bold", "textDecoration": "underline"}),
                                "is used to prioritize stocks with high risk-normalized earnings relative to their scale, ensuring balanced opportunities."
                            ],
                            className="fade-in-up",
                            style={"textAlign": "justify", "marginBottom": "2rem", "backgroundColor": "var(--color-surface)",
                                   "padding": "1rem", "borderRadius": "8px", "border": "1px solid var(--color-border)"}
                        )
                    ]
                ),
                html.Div([
                    html.Div([
                        html.H3(f"{sector}", style={"color": "var(--color-primary)"}),
                        dash_table.DataTable(
                            columns=[{"name": col, "id": col} for col in df.columns],
                            data=(df.sort_values(by='VALUE RATIO', ascending=(sector == "Basic Materials"))
                                  .head(5)
                                  .to_dict('records')),  # Sort ascending for "Basic Materials" and descending for others
                            style_table={'marginBottom': '1rem', 'overflowX': 'auto'},
                            style_cell={'textAlign': 'center', 'padding': '5px'},
                            style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'}
                        )
                    ], style={'marginBottom': '2rem'}) for sector, df in sector_dataframes.items()
                ])
            ], style={'padding': '1rem'})
        ]),

        # Portfolio Optimizer Tab
        dcc.Tab(label="Portfolio Optimizer", children=[
            html.Div([
                html.H2("Portfolio Optimizer", style={"textAlign": "center", "color": "var(--color-primary)", "animation": "fadeInUp 0.5s ease"}),
                html.Div([
                    html.H3("Program Outline:", style={"color": "var(--color-secondary)"}),
                    html.Ul([
                        html.Li("1. Gather Max Data for all Symbols", className="hoverable"),
                        html.Li("2. Runs Monte Carlo on Portfolio Weights", className="hoverable"),
                        html.Li("3. Seeks to Minimize Coefficient of Variation", className="hoverable"),
                    ], style={"margin": "1rem", "lineHeight": "1.8"})
                ], style={"padding": "1rem", "backgroundColor": "var(--color-surface)", "borderRadius": "8px"}),

                html.Div([
                    dcc.Input(
                        id='add-ticker-input',
                        type='text',
                        placeholder='Enter ticker symbol',
                        className="fade-in-up",
                        style={'marginRight': '1rem', 'marginTop': '2rem'}
                    ),
                    html.Button("Add Ticker", id='add-ticker-button', className="button-ripple", style={'marginTop': '1rem'}),
                ], style={'marginBottom': '1rem'}),

                dash_table.DataTable(
                    id='tickers-table',
                    columns=[{"name": "Ticker", "id": "Ticker"}],
                    data=[],
                    style_cell={'textAlign': 'center', 'padding': '5px'},
                    style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
                ),

                html.Div([
                    html.Button("Run", id='run-optimizer', className="button-ripple", style={'marginRight': '1rem'}),
                    html.Button("Reset", id='reset-optimizer', className="button-ripple", style={'marginRight': '1rem'}),
                    html.Button("Download CSV", id='download-optimizer-csv', className="button-ripple", style={'marginLeft': '1rem'}),
                ], style={'marginBottom': '1rem'}),

                html.Div(id='portfolio-output', style={'whiteSpace': 'pre-wrap', 'padding': '1rem', 'backgroundColor': 'var(--color-surface)', 'boxShadow': 'var(--shadow-medium)', 'borderRadius': '8px'}),
                html.Div(id='file-links', style={'marginTop': '1rem'}),
                dcc.Download(id='download-portfolio-csv')
            ], style={'padding': '2rem', 'backgroundColor': 'var(--color-background)'})
        ]),
    ])
])

# Callbacks for Portfolio Optimizer CSV Download
@app.callback(
    Output('download-portfolio-csv', 'data'),
    Input('download-optimizer-csv', 'n_clicks'),
    State('portfolio-output', 'children'),
    prevent_initial_call=True
)
def download_portfolio_csv(n_clicks, portfolio_output):
    if portfolio_output:
        df = pd.DataFrame(portfolio_output)
        return dcc.send_data_frame(df.to_csv, "portfolio_allocation.csv")
    return None

@app.callback(
    Output("payment-confirmation", "children"),
    Input("buy-now-button", "n_clicks"),
    prevent_initial_call=True
)
def handle_buy_now(n_clicks):
    if dash.callback_context.triggered_id == "buy-now-button":
        try:
            # Create a Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": "price_1QbknF4SsxaWFVRwwkdeyLWs",  # Correct price_id
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url="https://your-success-url.com",  # Replace with your success URL
                cancel_url="https://your-cancel-url.com",    # Replace with your cancel URL
            )

            # Redirect the user to the Stripe Checkout Session URL
            return html.A(
                "Redirecting to Stripe Checkout...",
                href=session.url,
                target="_blank",
                style={"color": "var(--color-primary)", "fontWeight": "bold"}
            )

        except Exception as e:
            return f"Error creating checkout session: {e}"


# Callbacks for Fundamental Tab
@app.callback(
    Output('metrics-store', 'data'),
    Output('metrics-table', 'data'),
    [Input('fetch-button', 'n_clicks'), Input('reset-button', 'n_clicks')],
    [State('ticker-input', 'value'), State('metrics-store', 'data')],
    prevent_initial_call=True
)
def update_table(n_fetch, n_reset, ticker, current_data):
    if dash.callback_context.triggered_id == 'reset-button':
        return [], []
    elif dash.callback_context.triggered_id == 'fetch-button' and ticker:
        metrics_df = get_metrics(ticker)
        metrics_df = metrics_df[metrics_df['Metric'].isin([
            'Market Cap', 'Forward P/E', 'P/E', 'Insider Own', 'Short Interest',
            'Income', 'Sales', 'ROE', 'ROA', 'Beta', 'Employees', 'Sales Y/Y TTM'
        ])]

        if metrics_df.empty:
            metrics_list = [None] * len(FUND_COLUMNS[1:])
        else:
            metrics_list = metrics_df['Value'].tolist()
        row_dict = {col: metrics_list[i] if i < len(metrics_list) else None for i, col in enumerate(FUND_COLUMNS[1:])}
        row_dict['Ticker'] = ticker.upper()
        updated_data = current_data + [row_dict]
        return updated_data, updated_data
    return dash.no_update, dash.no_update

@app.callback(
    Output('download-csv', 'data'),
    Input('download-button', 'n_clicks'),
    State('metrics-store', 'data'),
    prevent_initial_call=True
)
def download_csv(n_clicks, data):
    if data:
        df = pd.DataFrame(data)
        return dcc.send_data_frame(df.to_csv, "fundamental_analysis.csv")
    return None

# Callbacks for Portfolio Optimizer Tab
@app.callback(
    Output('tickers-store', 'data'),
    Output('tickers-table', 'data'),
    [Input('add-ticker-button', 'n_clicks'), Input('reset-optimizer', 'n_clicks')],
    [State('add-ticker-input', 'value'), State('tickers-store', 'data')],
    prevent_initial_call=True
)
def update_ticker_table(n_add, n_reset, ticker, current_data):
    if dash.callback_context.triggered_id == 'reset-optimizer':
        return [], []
    elif dash.callback_context.triggered_id == 'add-ticker-button' and ticker:
        updated_data = current_data + [{"Ticker": ticker.upper()}]
        return updated_data, updated_data
    return dash.no_update, dash.no_update

@app.callback(
    [Output('portfolio-output', 'children'), Output('file-links', 'children')],
    Input('run-optimizer', 'n_clicks'),
    State('tickers-store', 'data'),
    prevent_initial_call=True
)
def run_portfolio_optimizer(n_clicks, tickers_data):
    if not tickers_data:
        return "Error: No tickers added.", ""

    symbols = [row['Ticker'] for row in tickers_data]
    try:
        optimizer = PortfolioOptimizer(symbols, period='5y', num_portfolios=10000, simulations=15)
        averaged_allocation = optimizer.average_allocations()

        if averaged_allocation.empty:
            raise ValueError("Optimizer returned an empty result.")

        # Save allocation DataFrame to a CSV file
        file_path = "outputs/allocation.csv"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        averaged_allocation.to_csv(file_path, index=False)

        # Create a link to the saved file
        file_link = html.A("Download Allocation CSV", href=f"/download/{file_path}", target="_blank", style={'textDecoration': 'none', 'color': 'blue'})

        # Display the DataTable
        table = dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in averaged_allocation.columns],
            data=averaged_allocation.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '5px'},
            style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'}
        )

        return table, file_link
    except Exception as e:
        return f"Error: {str(e)}", ""

# Main
if __name__ == '__main__':
    app.run_server(debug=True, port=8060)

