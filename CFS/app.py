import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import warnings

warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION VARIABLES
# =============================================================================
# Update this path to your actual file location
FILE_PATH = "https://raw.githubusercontent.com/Navneet831/CFSDashboard/main/Base%20data/OPL%20CFS.xlsx"
CCC_SHEET = "CCC"
CRORE_CONVERSION = 10000000
BANK_LIMITS = {
    'SBI': 69000000, 'ICICI': 100000000, 'HDFC': 100000000,
    'Federal': 150000000, 'Axis': 5000000, 'Yes': 50000000
}
POSITIVE_BALANCE_BANKS = ['SBI', 'ICICI', 'HDFC', 'Yes']

# --- Professional Dark Theme Color Palette ---
BG_PRIMARY = '#0f172a'
BG_SECONDARY = '#1e293b'
TEXT_PRIMARY = '#f1f5f9'
TEXT_SECONDARY = '#cbd5e1'
TEXT_MUTED = '#94a3b8'
ACCENT_PRIMARY = '#3b82f6'
ACCENT_SUCCESS = '#10b981'
ACCENT_DANGER = '#ef4444'
ACCENT_WARNING = '#f59e0b'
ACCENT_INFO = '#06b6d4'
BORDER_COLOR = '#334155'

# --- Custom Metric Card Background Colors (As per image) ---
# Light Blue for Actual/Current Metrics
ACTUAL_CARD_BG = '#1f3d64' 
# Light Green for Forecasted Metrics
FORECAST_CARD_BG = '#254e42' 

# --- Gradient Colors for Dynamic Header ---
GRADIENT_DEFAULT_START, GRADIENT_DEFAULT_END = '#1e3a8a', '#7c3aed'
GRADIENT_RED_START, GRADIENT_RED_END = '#991b1b', '#ef4444'
GRADIENT_ORANGE_START, GRADIENT_ORANGE_END = '#b45309', '#f59e0b'

st.set_page_config(
    page_title="Cash Flow Metrics",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# STYLING & HELPER FUNCTIONS
# =============================================================================

def get_dynamic_styles(header_color_profile='default'):
    """Generates CSS with dynamic header colors and uniform metric cards, optimizing breakdown readability."""
    if header_color_profile == 'red':
        start_color, end_color = GRADIENT_RED_START, GRADIENT_RED_END
    elif header_color_profile == 'orange':
        start_color, end_color = GRADIENT_ORANGE_START, GRADIENT_ORANGE_END
    else:
        start_color, end_color = GRADIENT_DEFAULT_START, GRADIENT_DEFAULT_END
    
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        .stApp {{ background-color: {BG_PRIMARY}; color: {TEXT_PRIMARY}; }}
        * {{ font-family: 'Inter', sans-serif; }}
        
        /* --- HEADER STYLES --- */
        .main-header {{ 
            background: linear-gradient(135deg, {start_color} 0%, {end_color} 100%); 
            padding: 1.5rem; 
            border-radius: 16px; 
            box-shadow: 0 10px 20px rgba(0,0,0,0.3); 
            animation: slideDown 0.6s ease-out; 
            border: 1px solid rgba(255,255,255,0.1); 
            margin-bottom: 1.5rem; 
        }}
        .header-content {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }}
        .header-title-group {{ text-align: left; }}
        .funding-alert {{ 
            color: {TEXT_PRIMARY}; 
            font-size: 1.1rem; 
            font-weight: 600; 
            background-color: rgba(0,0,0,0.2); 
            padding: 0.5rem 1rem; 
            border-radius: 10px; 
            border: 1px solid {BORDER_COLOR}; 
        }}
        @keyframes slideDown {{ from {{ opacity: 0; transform: translateY(-30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .main-header h1 {{ color: {TEXT_PRIMARY}; font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .main-header p {{ color: {TEXT_SECONDARY}; font-size: 0.95rem; opacity: 0.95; margin: 0; }}
        
        /* Streamlit Date Input Container Fix */
        .stDateInput > label {{ padding-bottom: 0.5rem; }}
        
        /* --- METRIC CARD BASE STYLES --- */
        .metric-card {{ 
            padding: 1rem; 
            border-radius: 12px; 
            box-shadow: 0 6px 16px rgba(0,0,0,0.2); 
            border: 1px solid {BORDER_COLOR}; 
            transition: all 0.3s ease; 
            animation: fadeInUp 0.6s ease-out; 
            height: 100%; 
            min-height: 120px; 
            display: flex; 
            flex-direction: column; 
            justify-content: space-between; 
            position: relative; 
        }}
        .metric-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }}
        
        /* Card Colors */
        .actual-card {{ background: {ACTUAL_CARD_BG}; border-color: #3b82f6; }}
        .actual-card:hover {{ border-color: #7c3aed; }}
        .forecast-card {{ background: {FORECAST_CARD_BG}; border-color: #10b981; }}
        .forecast-card:hover {{ border-color: #06b6d4; }}
        
        @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}

        .metric-label {{ color: {TEXT_MUTED}; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem; }}
        .metric-delta {{ font-size: 1.2rem; position: absolute; top: 0.75rem; right: 0.75rem; }}

        .value-group {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: flex-end; 
            margin-top: 0.5rem;
        }}
        .metric-value {{ 
            font-size: 1.6rem; 
            font-weight: 700; 
            line-height: 1.2; 
            text-align: left;
            flex-grow: 1;
        }}
        .metric-value.positive {{ color: {ACCENT_SUCCESS}; }} .metric-value.negative {{ color: {ACCENT_DANGER}; }} .metric-value.neutral {{ color: {TEXT_PRIMARY}; }}
        
        /* IMPROVEMENT: Increased font size for breakdown for better visibility */
        .metric-breakdown {{ 
            display: flex; 
            flex-direction: column; 
            font-size: 0.9rem; 
            font-weight: 500; 
            line-height: 1.3; 
            text-align: right; 
            margin-left: 1rem; 
            border-left: 1px solid {BORDER_COLOR};
            padding-left: 0.75rem;
            flex-shrink: 0;
        }}
        .breakdown-line {{ color: {TEXT_SECONDARY}; font-size: 0.85rem; font-weight: 500; }}
        .fixed-text {{ color: {ACCENT_INFO}; }} 
        .contingency-text {{ color: {ACCENT_WARNING}; }}
        
        .copyright {{ text-align: center; color: {TEXT_MUTED}; font-size: 0.75rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid {BORDER_COLOR}; }}
    </style>
    """

def create_metric_card(label, value, value_format="₹{:.2f}", value_color="neutral", breakdown_html="", delta="", card_type="actual"):
    """
    Creates a flexible metric card HTML structure with different background colors.
    card_type can be 'actual' or 'forecast'.
    """
    card_class = "actual-card" if card_type == "actual" else "forecast-card"
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ""
    
    # Check if the value is a string (e.g., Cash Runway) and needs no formatting
    if isinstance(value, str):
         main_value_html = f'<div class="metric-value {value_color}">{value}</div>'
    else:
         main_value_html = f'<div class="metric-value {value_color}">{value_format.format(value)}</div>'

    if breakdown_html:
        # Side-by-side layout (Value on Left, Breakdown on Right)
        content_html = f"""
        <div class="value-group">
            {main_value_html}
            <div class="metric-breakdown">{breakdown_html}</div>
        </div>
        """
    else:
        # Original simple layout
        content_html = main_value_html

    return f"""<div class="metric-card {card_class}">{delta_html}<div class="metric-label">{label}</div>{content_html}</div>"""


# =============================================================================
# DATA LOADING & PROCESSING FUNCTIONS 
# =============================================================================
@st.cache_data(ttl=300)
def load_excel_data():
    try:
        xls = pd.ExcelFile(FILE_PATH)
        bank_data, forecast_data, inflow_forecast_data, inflow_sheet = {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        bank_name_mapping = {'sbi': 'SBI', 'icici': 'ICICI', 'hdfc': 'HDFC', 'federal': 'Federal', 'axis': 'Axis', 'yes': 'Yes'}
        
        for sheet in xls.sheet_names:
            df, sheet_lower = pd.read_excel(xls, sheet_name=sheet), sheet.lower()
            
            if sheet_lower == 'inflow':
                inflow_sheet = df
                continue
            
            if 'forecast' in sheet_lower and 'inflow' not in sheet_lower:
                forecast_data = df
            elif 'inflow' in sheet_lower and 'forecast' in sheet_lower:
                inflow_forecast_data = df
            else:
                bank_name = next((val for key, val in bank_name_mapping.items() if key in sheet_lower), None)
                if bank_name:
                    try:
                        bank_data[bank_name] = pd.DataFrame({
                            'Value_Date': pd.to_datetime(df.iloc[:, 2], errors='coerce'),
                            'Net_Flow': pd.to_numeric(df.iloc[:, 8], errors='coerce'),
                            'Running_Balance': pd.to_numeric(df.iloc[:, 9], errors='coerce'),
                            'Nature': df.iloc[:, 13] if len(df.columns) > 13 else None
                        }).dropna(subset=['Value_Date', 'Net_Flow'])
                    except Exception:
                        pass
        
        if not forecast_data.empty:
            forecast_data = pd.DataFrame({
                'Forecast_Date': pd.to_datetime(forecast_data.iloc[:, 2], errors='coerce'),
                'Net_Payable': pd.to_numeric(forecast_data.iloc[:, 6], errors='coerce'),
                'Certainty': forecast_data.iloc[:, 15].fillna('Unknown')
            }).dropna(subset=['Forecast_Date'])
        
        if not inflow_forecast_data.empty:
            inflow_forecast_data = pd.DataFrame({
                'Forecast_Date': pd.to_datetime(inflow_forecast_data.iloc[:, 24], errors='coerce'),
                'Amount_Received': pd.to_numeric(inflow_forecast_data.iloc[:, 26], errors='coerce')
            }).dropna(subset=['Forecast_Date'])
        
        return bank_data, forecast_data, inflow_forecast_data, inflow_sheet
    except Exception as e:
        st.error(f"Fatal error loading Excel file: {e}")
        return {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=300)
def load_ccc_data():
    """Load and calculate CCC metrics from CCC sheet."""
    try:
        df_ccc = pd.read_excel(FILE_PATH, sheet_name=CCC_SHEET, header=None)
        
        date_cell = pd.to_datetime(df_ccc.iloc[0, 0])
        C1, E1 = df_ccc.iloc[0, 2], df_ccc.iloc[0, 4]
        J1, L1 = df_ccc.iloc[0, 9], df_ccc.iloc[0, 11]
        S1, V1 = df_ccc.iloc[0, 18], df_ccc.iloc[0, 21]
        NetSales = df_ccc.iloc[0, 14]
        COGS = df_ccc.iloc[0, 22] + df_ccc.iloc[0, 23]
        
        no_of_days = (date_cell - datetime(date_cell.year - (date_cell.month < 4), 4, 1)).days + 1
        avg_payables = (C1 + E1) / 2
        avg_receivables = (J1 + L1) / 2
        avg_inventory = (V1 + S1) / 2
        
        DSO = (avg_receivables / NetSales) * no_of_days if NetSales != 0 else 0
        DPO = (avg_payables / COGS) * no_of_days if COGS != 0 else 0
        DIO = (avg_inventory / COGS) * no_of_days if COGS != 0 else 0
        CCC = DSO + DIO - DPO
        
        return {'CCC': CCC, 'DSO': DSO, 'DPO': DPO, 'DIO': DIO}
    except Exception as e:
        st.warning(f"Could not load CCC data: {e}")
        return None

def extract_cash_flows(bank_data, start_date, end_date):
    """Extract Operating, Investing, and Financing cash flows from bank data."""
    op, inv, fin = 0, 0, 0
    for name, df in bank_data.items():
        if 'Nature' not in df.columns or df['Nature'].isna().all():
            continue
        filtered = df[(df['Value_Date'] >= start_date) & (df['Value_Date'] <= end_date)]
        op += filtered[filtered['Nature'].str.contains("Operating", case=False, na=False)]['Net_Flow'].sum()
        inv += filtered[filtered['Nature'].str.contains("Investing", case=False, na=False)]['Net_Flow'].sum()
        fin += filtered[filtered['Nature'].str.contains("Financing", case=False, na=False)]['Net_Flow'].sum()
    return op / CRORE_CONVERSION, inv / CRORE_CONVERSION, fin / CRORE_CONVERSION

def extract_revenue(inflow_sheet, start_date, end_date):
    """Extract revenue from Inflow sheet based on billing date."""
    if inflow_sheet.empty:
        return 0
    try:
        inflow_sheet['Billing_Date'] = pd.to_datetime(inflow_sheet.iloc[:, 15], errors='coerce')
        inflow_sheet['Amount'] = pd.to_numeric(inflow_sheet.iloc[:, 17], errors='coerce')
        return inflow_sheet[(inflow_sheet['Billing_Date'] >= start_date) & (inflow_sheet['Billing_Date'] <= end_date)]['Amount'].sum() / CRORE_CONVERSION
    except Exception:
        return 0

def get_bank_balances(bank_data, as_of_date):
    total_balance_available = 0
    for bank, limit in BANK_LIMITS.items():
        balance_on_date = 0
        if bank in bank_data and not bank_data[bank].empty:
            df_filtered = bank_data[bank][bank_data[bank]['Value_Date'] <= as_of_date]
            if not df_filtered.empty:
                balance_on_date = df_filtered.sort_values('Value_Date')['Running_Balance'].iloc[-1]
        
        balance_available = (limit + balance_on_date) if bank in POSITIVE_BALANCE_BANKS else (limit - balance_on_date)
        total_balance_available += balance_available
    return total_balance_available

def consolidate_bank_data(bank_data, start_date, end_date):
    if not bank_data:
        return pd.DataFrame()
    df = pd.concat(list(bank_data.values())).query("@start_date <= Value_Date <= @end_date").copy()
    if df.empty:
        return pd.DataFrame()
    df['Withdrawal'] = df['Net_Flow'].apply(lambda x: abs(x) if x < 0 else 0)
    df['Deposit'] = df['Net_Flow'].apply(lambda x: x if x > 0 else 0)
    return df

def calculate_cash_metrics(consolidated_data):
    if consolidated_data.empty:
        return {'total_inflow': 0, 'total_outflow': 0, 'net_flow': 0}
    return {
        'total_inflow': consolidated_data['Deposit'].sum() / CRORE_CONVERSION,
        'total_outflow': consolidated_data['Withdrawal'].sum() / CRORE_CONVERSION,
        'net_flow': consolidated_data['Net_Flow'].sum() / CRORE_CONVERSION
    }

def get_forecast_metrics(data, start_date, end_date, forecast_type='outflow'):
    if data.empty:
        return {'fixed': 0, 'contingency': 0, 'total': 0} if forecast_type == 'outflow' else {'total': 0}
    filtered = data.query("@start_date <= Forecast_Date <= @end_date")
    if forecast_type == 'inflow':
        return {'total': filtered['Amount_Received'].sum() / CRORE_CONVERSION}
    return {
        'fixed': filtered.query("Certainty.str.lower() == 'fixed'")['Net_Payable'].sum() / CRORE_CONVERSION,
        'contingency': filtered.query("Certainty.str.lower() == 'contingency'")['Net_Payable'].sum() / CRORE_CONVERSION,
        'total': filtered['Net_Payable'].sum() / CRORE_CONVERSION
    }

def calculate_cash_runway(total_balance_available, forecast_data, as_of_date, certainty_levels):
    """
    Calculates how many days until available limit reaches zero based on future forecasted outflows.
    """
    total_balance_base = total_balance_available 
    
    query_str = " or ".join([f"Certainty.str.lower() == '{level}'" for level in certainty_levels])
    
    future_outflows = forecast_data.query(f"({query_str}) and Forecast_Date > @as_of_date", engine='python').copy()
    
    if total_balance_base <= 0 or future_outflows.empty:
        return 0
    
    daily_outflows = future_outflows.groupby('Forecast_Date')['Net_Payable'].sum().sort_index().to_frame(name='Daily_Outflow')
    daily_outflows['Cumulative_Spend'] = daily_outflows['Daily_Outflow'].cumsum()
    
    breach_df = daily_outflows[daily_outflows['Cumulative_Spend'] > total_balance_base]
    
    if breach_df.empty:
        return 999 
    
    breach_date = breach_df.index[0]
    
    return max(0, (breach_date.date() - as_of_date.date()).days)

def perform_predictive_analysis(consolidated_data):
    if consolidated_data.empty or len(consolidated_data) < 7:
        return None
    daily_flow = consolidated_data.groupby(consolidated_data['Value_Date'].dt.date)['Net_Flow'].sum()
    ma_7 = daily_flow.rolling(window=7, min_periods=1).mean()
    current_trend = ma_7.iloc[-1] - ma_7.iloc[-7] if len(ma_7) >= 7 else 0
    return {
        'trend': 'Increasing' if current_trend > 0 else 'Decreasing',
        'trend_value': current_trend / CRORE_CONVERSION,
        'avg_inflow': consolidated_data[consolidated_data['Net_Flow'] > 0]['Net_Flow'].mean() / CRORE_CONVERSION,
        'avg_outflow': abs(consolidated_data[consolidated_data['Net_Flow'] < 0]['Net_Flow'].mean()) / CRORE_CONVERSION,
        'volatility': daily_flow.std() / CRORE_CONVERSION if len(daily_flow) > 1 else 0
    }
    
# =============================================================================
# MAIN APPLICATION
# =============================================================================
def app():
    with st.spinner('🔄 Loading financial data...'):
        bank_data, forecast_data, inflow_forecast_data, inflow_sheet = load_excel_data()
        ccc_data = load_ccc_data()

    if not bank_data:
        st.error("❌ No bank data found. Please check Excel file path and format.")
        return
    
    all_dates = [d for df in bank_data.values() for d in df['Value_Date'].dropna()]
    if not all_dates:
        st.error("❌ No valid dates found in the data.")
        return

    min_date, max_date = min(all_dates).date(), max(all_dates).date()
    
    # --- Consolidated Header Section for minimal scrolling ---
    # Use columns to align the dates, title, and alert on one line if possible, 
    # but Streamlit forces date pickers to take full lines unless inside a container/form.
    
    st.markdown(get_dynamic_styles('default'), unsafe_allow_html=True)
    
    # --- Date Pickers (Moved to the side of the main title area for a compact look) ---
    c_date1, c_date2, c_gap, c_alert = st.columns([1, 1, 3, 1])
    
    with c_date1:
        start_date = pd.Timestamp(st.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date, label_visibility="collapsed"))
    with c_date2:
        end_date = pd.Timestamp(st.date_input("To Date", value=max_date, min_value=start_date.date(), max_value=max_date, label_visibility="collapsed"))

    # Re-calculate dynamic header elements based on the selected dates
    total_balance_available_base = get_bank_balances(bank_data, end_date)
    runway_fixed = calculate_cash_runway(total_balance_available_base, forecast_data, end_date, certainty_levels=['fixed'])
    runway_total = calculate_cash_runway(total_balance_available_base, forecast_data, end_date, certainty_levels=['fixed', 'contingency'])
    
    header_profile, funding_alert_text = 'default', "✅ Sufficient Funds Available"
    if runway_fixed < 30:
        header_profile, funding_alert_text = 'red', f"🚨 Funding Required within {runway_fixed} Days (Fixed Outflows)"
    elif runway_total < 30:
        header_profile, funding_alert_text = 'orange', f"⚠️ Contingency Funding within {runway_total} Days (Total Outflows)"

    # Apply CSS styling dynamically based on alert status
    st.markdown(get_dynamic_styles(header_profile), unsafe_allow_html=True)

    # Use a container for the main header content to look like the image
    st.markdown(f"""
        <div class="main-header">
            <div class="header-content">
                <div class="header-title-group">
                    <h1>💰 Cash Flow Metrics</h1>
                    <p>Key Performance Indicators & Forecasts</p>
                </div>
                <div class="funding-alert">{funding_alert_text}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    consolidated_data = consolidate_bank_data(bank_data, start_date, end_date)
    cash_metrics = calculate_cash_metrics(consolidated_data)
    predictive_insights = perform_predictive_analysis(consolidated_data)
    
    # Extract cash flow activities and revenue
    op_flow, inv_flow, fin_flow = extract_cash_flows(bank_data, start_date, end_date)
    revenue = extract_revenue(inflow_sheet, start_date, end_date)
    ocf_sales_ratio = (op_flow / revenue) if revenue != 0 else 0
    
    # ========================================================================
    # ROW 1: KEY FINANCIAL METRICS (4 Cards)
    # ========================================================================
    st.markdown("### 📊 Key Financial Metrics")
    kfm1, kfm2, kfm3, kfm4 = st.columns(4) 
    
    # Card 1: Available Limit
    with kfm1:
        balance_trend = "📈" if total_balance_available_base > 0 else "📉"
        st.markdown(create_metric_card("Available Limit", total_balance_available_base / CRORE_CONVERSION, value_color="positive", delta=balance_trend, card_type="actual"), unsafe_allow_html=True)
        
    # Card 2: Cash Runway
    with kfm2:
        runway_color = "positive" if runway_fixed >= 90 else ("negative" if runway_fixed < 30 else "warning")
        runway_days_text = f"{runway_fixed} days" if runway_fixed < 999 else "> 999 days"
        runway_breakdown = f"""
            <div class="breakdown-line">Total: {runway_total} days</div>
            <div class="breakdown-line">As of: {end_date.strftime("%d %b")}</div>
        """
        st.markdown(create_metric_card("Cash Runway (Fixed Outflow)", runway_days_text, value_format="{}", value_color=runway_color, breakdown_html=runway_breakdown, card_type="actual"), unsafe_allow_html=True)
        
    # Card 3: Revenue
    with kfm3:
        st.markdown(create_metric_card("Revenue", revenue, value_color="positive", card_type="actual"), unsafe_allow_html=True)
        
    # Card 4: Cash Conversion Cycle
    with kfm4:
        if ccc_data:
            ccc_breakdown = f"""
                <div class="breakdown-line">DSO: {ccc_data['DSO']:.1f}</div>
                <div class="breakdown-line">DPO: {ccc_data['DPO']:.1f}</div>
                <div class="breakdown-line">DIO: {ccc_data['DIO']:.1f}</div>
            """
            st.markdown(create_metric_card("Cash Conversion Cycle", ccc_data['CCC'], value_format="{:.1f} days", value_color="positive" if ccc_data['CCC'] < 60 else "negative", breakdown_html=ccc_breakdown, card_type="actual"), unsafe_allow_html=True)
        else:
            st.markdown(create_metric_card("Cash Conversion Cycle", 0, value_format="{:.1f} days", value_color="neutral", card_type="actual"), unsafe_allow_html=True)

    # ========================================================================
    # ROW 2: CASH FLOW ACTIVITIES (4 Cards)
    # ========================================================================
    st.markdown("### 💼 Cash Flow Activities")
    cfa1, cfa2, cfa3, cfa4 = st.columns(4) 
    
    # Card 1: Operating Activity
    with cfa1:
        st.markdown(create_metric_card("Operating Activity", op_flow, value_color="positive" if op_flow >= 0 else "negative", card_type="actual"), unsafe_allow_html=True)
    
    # Card 2: Investing Activity
    with cfa2:
        st.markdown(create_metric_card("Investing Activity", inv_flow, value_color="positive" if inv_flow >= 0 else "negative", card_type="actual"), unsafe_allow_html=True)
    
    # Card 3: Financing Activity
    with cfa3:
        st.markdown(create_metric_card("Financing Activity", fin_flow, value_color="positive" if fin_flow >= 0 else "negative", card_type="actual"), unsafe_allow_html=True)
        
    # Card 4: Net Flow
    with cfa4:
        net_flow_bifurcation = f"""
            <div class="breakdown-line">In: ₹{cash_metrics['total_inflow']:.2f}</div>
            <div class="breakdown-line">Out: ₹{cash_metrics['total_outflow']:.2f}</div>
        """
        st.markdown(create_metric_card("Net Flow (Period)", cash_metrics['net_flow'], value_color="positive" if cash_metrics['net_flow'] >= 0 else "negative", breakdown_html=net_flow_bifurcation, card_type="actual"), unsafe_allow_html=True)


    # ========================================================================
    # ROW 3: FORECAST BREAKDOWN (4 Cards)
    # ========================================================================
    st.markdown("### 🔮 Forecast Breakdown")
    
    # Forecast period selector 
    forecast_period = st.selectbox("Select Forward-Looking Period", ["Next 7 Days", "Next 30 Days", "Next 60 Days"])
    
    # Define columns for the four forecast cards
    f_today, f1, f2, f3 = st.columns(4)
    
    # Card 1: Amount Needed Today
    with f_today:
        today_forecast = get_forecast_metrics(forecast_data, end_date, end_date)
        today_bifurcation = f"""
            <div class="breakdown-line fixed-text">Fixed: ₹{today_forecast['fixed']:.2f}</div>
            <div class="breakdown-line contingency-text">Contingency: ₹{today_forecast['contingency']:.2f}</div>
        """
        st.markdown(create_metric_card("Amount Needed Today", today_forecast['total'], value_color="negative" if today_forecast['total'] > 0 else "neutral", breakdown_html=today_bifurcation, card_type="forecast"), unsafe_allow_html=True)

    # Future Forecasts Calculations
    days_map = {"Next 7 Days": 7, "Next 30 Days": 30, "Next 60 Days": 60}
    forecast_start = end_date + timedelta(days=1)
    forecast_end = end_date + timedelta(days=days_map[forecast_period])

    outflow_metrics = get_forecast_metrics(forecast_data, forecast_start, forecast_end)
    inflow_metrics = get_forecast_metrics(inflow_forecast_data, forecast_start, forecast_end, forecast_type='inflow')
    net_forecast = inflow_metrics['total'] - outflow_metrics['total']
    
    outflow_breakdown_html = f"""
        <div class="breakdown-line fixed-text">Fixed: ₹{outflow_metrics['fixed']:.2f}</div>
        <div class="breakdown-line contingency-text">Contingency: ₹{outflow_metrics['contingency']:.2f}</div>
    """

    # Card 2, 3, 4: Forecast Inflow, Outflow, Net Flow
    with f1:
        st.markdown(create_metric_card("Forecasted Inflow", inflow_metrics['total'], value_color="positive", card_type="forecast"), unsafe_allow_html=True)
    with f2:
        st.markdown(create_metric_card("Forecasted Outflow", outflow_metrics['total'], value_color="negative", breakdown_html=outflow_breakdown_html, card_type="forecast"), unsafe_allow_html=True)
    with f3:
        st.markdown(create_metric_card("Net Forecasted Flow", net_forecast, value_color="positive" if net_forecast >= 0 else "negative", card_type="forecast"), unsafe_allow_html=True)

    # ========================================================================
    # ROW 4: PREDICTIVE INSIGHTS (4 Cards)
    # ========================================================================
    st.markdown("### 🔍 Predictive Insights & Trend Analysis")
    
    # Forecast Efficiency calculation uses the global start_date and end_date
    efficiency_start_date = start_date
    efficiency_end_date = end_date
    efficiency_actual_net_flow = cash_metrics['net_flow']
    efficiency_outflow_metrics = get_forecast_metrics(forecast_data, efficiency_start_date, efficiency_end_date)
    efficiency_inflow_metrics = get_forecast_metrics(inflow_forecast_data, efficiency_start_date, efficiency_end_date, forecast_type='inflow')
    efficiency_forecast_net_flow = efficiency_inflow_metrics['total'] - efficiency_outflow_metrics['total']
    
    variance = efficiency_actual_net_flow - efficiency_forecast_net_flow
    if efficiency_actual_net_flow != 0:
        forecast_efficiency = (variance / abs(efficiency_actual_net_flow)) * 100
    else:
        forecast_efficiency = 999.0 if abs(variance) > 0.01 else 0.0 

    eff_color = "positive" if abs(forecast_efficiency) < 15.0 else "negative"
    date_format = "%b %d"
    period_label = f"{start_date.strftime(date_format)} - {end_date.strftime(date_format)}"

    eff_breakdown = f"""
        <div class="breakdown-line">Actual Net: ₹{efficiency_actual_net_flow:.2f}</div>
        <div class="breakdown-line">Forecast Net: ₹{efficiency_forecast_net_flow:.2f}</div>
        <div class="breakdown-line">Variance: ₹{variance:.2f}</div>
    """

    # --- Display Metrics (4 Columns: Trend, Efficiency, OCF, Volatility) ---
    if predictive_insights:
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            # ACTUAL/INSIGHTS CARD: Cash Flow Trend
            trend_symbol = "📈" if predictive_insights['trend'] == 'Increasing' else "📉"
            trend_bifurcation = f"""
                <div class="breakdown-line">Avg In: ₹{predictive_insights['avg_inflow']:.2f}</div>
                <div class="breakdown-line">Avg Out: ₹{predictive_insights['avg_outflow']:.2f}</div>
            """
            st.markdown(create_metric_card("Cash Flow Trend", abs(predictive_insights['trend_value']), value_color="positive" if predictive_insights['trend'] == 'Increasing' else "negative", breakdown_html=trend_bifurcation, delta=trend_symbol, card_type="actual"), unsafe_allow_html=True)
        
        with p2:
            # ACTUAL/INSIGHTS CARD: Forecast Efficiency
            st.markdown(create_metric_card("Forecast Efficiency", forecast_efficiency, value_format="{:.1f}%", value_color=eff_color, breakdown_html=eff_breakdown, card_type="actual"), unsafe_allow_html=True)

        with p3:
            # ACTUAL/INSIGHTS CARD: OCF to Sales Ratio
            st.markdown(create_metric_card("OCF to Sales Ratio", ocf_sales_ratio, value_format="{:.2%}", value_color="positive" if ocf_sales_ratio >= 0 else "negative", card_type="actual"), unsafe_allow_html=True)
        with p4:
            # ACTUAL/INSIGHTS CARD: Flow Volatility
            st.markdown(create_metric_card("Flow Volatility", predictive_insights['volatility'], value_color="neutral", card_type="actual"), unsafe_allow_html=True)
    
    else:
        # Fallback view
        st.warning("Insufficient data to show full predictive insights. Showing available metrics.")
        p1, p2 = st.columns(2)
        
        with p1:
            st.markdown(create_metric_card("Forecast Efficiency", forecast_efficiency, value_format="{:.1f}%", value_color=eff_color, breakdown_html=eff_breakdown, delta=f"Period: {period_label}", card_type="actual"), unsafe_allow_html=True)

        with p2:
            st.markdown(create_metric_card("OCF to Sales Ratio", ocf_sales_ratio, value_format="{:.2%}", value_color="positive" if ocf_sales_ratio >= 0 else "negative", card_type="actual"), unsafe_allow_html=True)


    st.markdown("""
        ---
        <a href="https://github.com/streamlit/streamlit/issues/new?title=Feature+Request+for+Cash+Flow+Dashboard" target="_blank" style="text-decoration: none;">
            <div style="text-align: center; color: #3b82f6; font-size: 0.85rem; padding: 1rem 0;">
                💡 Suggest a Feature (GitHub Issue)
            </div>
        </a>
        """, unsafe_allow_html=True)
    st.markdown(f"""<div class="copyright">© {datetime.now().year} Cash Flow Analytics Dashboard | Created by Navneet Chaudhary</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    app()
