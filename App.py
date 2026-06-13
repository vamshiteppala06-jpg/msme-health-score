    import streamlit as st
import pandas as pd

# ============================================
# MSME FINANCIAL HEALTH SCORE - STREAMLIT APP
# IDBI Innovate Hackathon 2026
# Version 2 - With Manual Input Form
# ============================================

st.set_page_config(
    page_title="MSME Financial Health Score",
    page_icon="🏦",
    layout="wide"
)

# ---- SCORING FUNCTIONS ----

def calculate_gst_score(data):
    score = 0
    filing_rate = data["gst_filings_on_time"] / data["gst_total_months"]
    score += filing_rate * 10
    sales = data["gst_monthly_sales"]
    first_half_avg = sum(sales[:6]) / 6
    second_half_avg = sum(sales[6:]) / 6
    if second_half_avg > first_half_avg:
        growth = (second_half_avg - first_half_avg) / first_half_avg
        trend_score = min(15, growth * 100)
    else:
        trend_score = 0
    score += trend_score
    return round(score, 2)

def calculate_upi_score(data):
    score = 0
    avg_transactions = sum(data["upi_monthly_transactions"]) / 12
    if avg_transactions >= 400:
        score += 10
    elif avg_transactions >= 300:
        score += 7
    elif avg_transactions >= 200:
        score += 5
    else:
        score += 2
    payment_rate = data["upi_payments_on_time"] / 12
    score += payment_rate * 15
    return round(score, 2)

def calculate_epfo_score(data):
    score = 0
    contributions = data["epfo_monthly_contributions"]
    paid_months = sum(1 for c in contributions if c == True)
    regularity_rate = paid_months / 12
    score += regularity_rate * 15
    start = data["epfo_employee_count_start"]
    end = data["epfo_employee_count_end"]
    if end > start:
        growth = (end - start) / start
        growth_score = min(10, growth * 50)
    elif end == start:
        growth_score = 5
    else:
        growth_score = 0
    score += growth_score
    return round(score, 2)

def calculate_aa_score(data):
    score = 0
    total_income = sum(data["aa_monthly_income"])
    total_expense = sum(data["aa_monthly_expense"])
    ratio = total_income / total_expense
    if ratio >= 1.5:
        score += 15
    elif ratio >= 1.3:
        score += 12
    elif ratio >= 1.1:
        score += 8
    else:
        score += 3
    repayment_rate = data["aa_existing_loan_repayments_on_time"] / 12
    score += repayment_rate * 10
    return round(score, 2)

def calculate_final_score(gst, upi, epfo, aa):
    return round(gst + upi + epfo + aa, 2)

def get_risk_rating(score):
    if score >= 85:
        return "LOW RISK", "Excellent candidate for credit", "green"
    elif score >= 70:
        return "MEDIUM-LOW RISK", "Good candidate, minor concerns", "blue"
    elif score >= 55:
        return "MEDIUM RISK", "Eligible but needs monitoring", "orange"
    elif score >= 40:
        return "HIGH RISK", "Borderline, needs collateral", "red"
    else:
        return "VERY HIGH RISK", "Not recommended for credit", "red"

def get_pillar_status(score, max_score=25):
    percentage = (score / max_score) * 100
    if percentage >= 80:
        return "STRONG", "green"
    elif percentage >= 60:
        return "MODERATE", "orange"
    else:
        return "WEAK", "red"

def show_report(data, gst, upi, epfo, aa, final, risk, description):
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Business Name", data["business_name"])
    with col2:
        st.metric("Business Type", data["business_type"])
    with col3:
        st.metric("Location", data["location"])

    st.markdown("---")
    col4, col5 = st.columns(2)
    with col4:
        st.metric("Financial Health Score", f"{final} / 100")
        st.progress(final / 100)
    with col5:
        st.metric("Risk Rating", risk)
        st.info(description)

    st.markdown("---")
    st.subheader("📊 Pillar Breakdown")
    col6, col7, col8, col9 = st.columns(4)

    gst_status, _ = get_pillar_status(gst)
    upi_status, _ = get_pillar_status(upi)
    epfo_status, _ = get_pillar_status(epfo)
    aa_status, _ = get_pillar_status(aa)

    with col6:
        st.metric("Revenue Health (GST)", f"{gst} / 25")
        st.progress(gst / 25)
        st.caption(gst_status)
    with col7:
        st.metric("Payment Behavior (UPI)", f"{upi} / 25")
        st.progress(upi / 25)
        st.caption(upi_status)
    with col8:
        st.metric("Workforce Stability (EPFO)", f"{epfo} / 25")
        st.progress(epfo / 25)
        st.caption(epfo_status)
    with col9:
        st.metric("Cash Flow (AA)", f"{aa} / 25")
        st.progress(aa / 25)
        st.caption(aa_status)

    st.markdown("---")
    st.subheader("💡 Recommendations")

    if gst_status == "WEAK":
        st.error("GST: Irregular filings detected. Verify revenue consistency.")
    elif gst_status == "MODERATE":
        st.warning("GST: Revenue stable but growth could be stronger.")
    else:
        st.success("GST: Strong revenue trend. Positive indicator.")

    if upi_status == "WEAK":
        st.error("UPI: Low transaction activity. Risk of informal dealings.")
    elif upi_status == "MODERATE":
        st.warning("UPI: Moderate transaction volume. Monitor for consistency.")
    else:
        st.success("UPI: High transaction volume. Business actively operating.")

    if epfo_status == "WEAK":
        st.error("EPFO: Missed contributions. Employee stability at risk.")
    elif epfo_status == "MODERATE":
        st.warning("EPFO: Workforce stable but contribution gaps exist.")
    else:
        st.success("EPFO: Regular contributions. Workforce stable and growing.")

    if aa_status == "WEAK":
        st.error("AA: Expenses close to income. Cash flow concerning.")
    elif aa_status == "MODERATE":
        st.warning("AA: Acceptable cash flow but repayment needs monitoring.")
    else:
        st.success("AA: Strong cash flow and timely loan repayments.")

    st.markdown("---")
    st.subheader("🏛️ Credit Decision")
    if final >= 70:
        st.success("✅ RECOMMENDED FOR LOAN APPROVAL")
    elif final >= 55:
        st.warning("⚠️ CONDITIONAL APPROVAL WITH MONITORING")
    else:
        st.error("❌ NOT RECOMMENDED AT THIS TIME")


# ---- BUSINESS DATA ----

businesses = {
    "Ravi Traders": {
        "business_name": "Ravi Traders",
        "business_type": "Small Manufacturing Unit",
        "location": "Visakhapatnam",
        "gst_monthly_sales": [180000,195000,210000,190000,220000,235000,
                               215000,240000,255000,230000,260000,275000],
        "gst_filings_on_time": 10,
        "gst_total_months": 12,
        "upi_monthly_transactions": [320,340,355,330,370,390,
                                      360,400,415,395,420,440],
        "upi_payments_on_time": 11,
        "epfo_monthly_contributions": [True,True,True,True,False,True,
                                        True,True,True,False,True,True],
        "epfo_employee_count_start": 8,
        "epfo_employee_count_end": 11,
        "aa_monthly_income": [200000,215000,225000,205000,235000,250000,
                               230000,255000,270000,245000,275000,290000],
        "aa_monthly_expense": [150000,155000,160000,152000,165000,170000,
                                162000,175000,180000,168000,182000,190000],
        "aa_existing_loan_repayments_on_time": 10
    },
    "Priya Stores": {
        "business_name": "Priya Stores",
        "business_type": "Retail Shop",
        "location": "Hyderabad",
        "gst_monthly_sales": [120000,115000,130000,110000,125000,118000,
                               122000,119000,128000,115000,121000,124000],
        "gst_filings_on_time": 8,
        "gst_total_months": 12,
        "upi_monthly_transactions": [180,175,190,170,185,178,
                                      182,176,188,172,183,179],
        "upi_payments_on_time": 9,
        "epfo_monthly_contributions": [True,True,False,True,False,True,
                                        True,False,True,True,False,True],
        "epfo_employee_count_start": 5,
        "epfo_employee_count_end": 5,
        "aa_monthly_income": [135000,128000,142000,125000,138000,130000,
                               136000,129000,140000,127000,137000,132000],
        "aa_monthly_expense": [118000,115000,125000,112000,122000,118000,
                                120000,116000,124000,114000,121000,119000],
        "aa_existing_loan_repayments_on_time": 8
    },
    "Kumar Enterprises": {
        "business_name": "Kumar Enterprises",
        "business_type": "Small Trading Company",
        "location": "Vijayawada",
        "gst_monthly_sales": [90000,85000,80000,75000,70000,65000,
                               60000,55000,50000,48000,45000,42000],
        "gst_filings_on_time": 5,
        "gst_total_months": 12,
        "upi_monthly_transactions": [90,85,80,75,70,65,
                                      60,55,50,48,45,42],
        "upi_payments_on_time": 6,
        "epfo_monthly_contributions": [True,False,False,True,False,False,
                                        True,False,False,True,False,False],
        "epfo_employee_count_start": 6,
        "epfo_employee_count_end": 3,
        "aa_monthly_income": [95000,90000,85000,80000,75000,70000,
                               65000,60000,55000,52000,49000,46000],
        "aa_monthly_expense": [88000,85000,82000,78000,74000,69000,
                                64000,59000,54000,51000,48000,45000],
        "aa_existing_loan_repayments_on_time": 4
    }
}

# ---- MAIN UI ----

st.title("🏦 MSME Financial Health Score")
st.subheader("AI-Powered Credit Assessment for Small Businesses")
st.markdown("---")

# Two tabs
tab1, tab2, tab3 = st.tabs([
    "📋 Sample Businesses",
    "✏️ Evaluate New Business",
    "📊 Compare All"
])

# ---- TAB 1: SAMPLE BUSINESSES ----
with tab1:
    st.markdown("### Select a Sample Business")
    selected = st.selectbox(
        "Choose a business:",
        list(businesses.keys())
    )
    data = businesses[selected]
    gst = calculate_gst_score(data)
    upi = calculate_upi_score(data)
    epfo = calculate_epfo_score(data)
    aa = calculate_aa_score(data)
    final = calculate_final_score(gst, upi, epfo, aa)
    risk, description, color = get_risk_rating(final)
    show_report(data, gst, upi, epfo, aa, final, risk, description)

# ---- TAB 2: MANUAL INPUT FORM ----
with tab2:
    st.markdown("### Enter Business Details")
    st.caption("Fill in the details below to get an instant Financial Health Score")

    col_a, col_b = st.columns(2)
    with col_a:
        biz_name = st.text_input("Business Name", "My Business")
        biz_type = st.text_input("Business Type", "Retail Shop")
        biz_location = st.text_input("Location", "Hyderabad")

    with col_b:
        st.markdown("**GST Details**")
        gst_filings = st.slider("GST Filings On Time (out of 12)", 0, 12, 8)
        avg_monthly_sales = st.number_input(
            "Average Monthly Sales (₹)", 10000, 10000000, 150000, step=10000
        )

    st.markdown("---")
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("**UPI Details**")
        avg_upi = st.number_input(
            "Average Monthly UPI Transactions", 10, 2000, 200, step=10
        )
        upi_ontime = st.slider("UPI Payments On Time (out of 12)", 0, 12, 9)

    with col_d:
        st.markdown("**EPFO Details**")
        epfo_paid = st.slider("EPFO Contributions Made (out of 12)", 0, 12, 8)
        emp_start = st.number_input("Employees at Start of Year", 1, 500, 5)
        emp_end = st.number_input("Employees at End of Year", 1, 500, 5)

    st.markdown("---")
    col_e, col_f = st.columns(2)
    with col_e:
        st.markdown("**Account Aggregator Details**")
        avg_income = st.number_input(
            "Average Monthly Income (₹)", 10000, 10000000, 180000, step=10000
        )
        avg_expense = st.number_input(
            "Average Monthly Expense (₹)", 10000, 10000000, 140000, step=10000
        )
    with col_f:
        st.markdown(" ")
        loan_ontime = st.slider(
            "Loan Repayments On Time (out of 12)", 0, 12, 8
        )

    st.markdown("---")

    if st.button("🔍 Calculate Financial Health Score", type="primary"):
        sales_list = [avg_monthly_sales] * 12
        sales_list[6:] = [avg_monthly_sales * 1.05] * 6
        transactions_list = [avg_upi] * 12
        income_list = [avg_income] * 12
        expense_list = [avg_expense] * 12
        contributions_list = (
            [True] * epfo_paid + [False] * (12 - epfo_paid)
        )

        manual_data = {
            "business_name": biz_name,
            "business_type": biz_type,
            "location": biz_location,
            "gst_monthly_sales": sales_list,
            "gst_filings_on_time": gst_filings,
            "gst_total_months": 12,
            "upi_monthly_transactions": transactions_list,
            "upi_payments_on_time": upi_ontime,
            "epfo_monthly_contributions": contributions_list,
            "epfo_employee_count_start": int(emp_start),
            "epfo_employee_count_end": int(emp_end),
            "aa_monthly_income": income_list,
            "aa_monthly_expense": expense_list,
            "aa_existing_loan_repayments_on_time": loan_ontime
        }

        gst_m = calculate_gst_score(manual_data)
        upi_m = calculate_upi_score(manual_data)
        epfo_m = calculate_epfo_score(manual_data)
        aa_m = calculate_aa_score(manual_data)
        final_m = calculate_final_score(gst_m, upi_m, epfo_m, aa_m)
        risk_m, desc_m, _ = get_risk_rating(final_m)

        st.success(f"Score calculated for {biz_name}")
        show_report(
            manual_data,
            gst_m, upi_m, epfo_m, aa_m,
            final_m, risk_m, desc_m
        )

# ---- TAB 3: COMPARE ALL ----
with tab3:
    st.markdown("### All Businesses Comparison")
    summary = []
    for name, bdata in businesses.items():
        g = calculate_gst_score(bdata)
        u = calculate_upi_score(bdata)
        e = calculate_epfo_score(bdata)
        a = calculate_aa_score(bdata)
        f = calculate_final_score(g, u, e, a)
        r, _, _ = get_risk_rating(f)
        if f >= 70:
            decision = "✅ APPROVED"
        elif f >= 55:
            decision = "⚠️ CONDITIONAL"
        else:
            decision = "❌ REJECTED"
        summary.append({
            "Business": name,
            "GST Score": g,
            "UPI Score": u,
            "EPFO Score": e,
            "AA Score": a,
            "Final Score": f,
            "Risk": r,
            "Decision": decision
        })

    df = pd.DataFrame(summary)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Score Comparison Chart")
    chart_data = df[["Business", "GST Score",
                      "UPI Score", "EPFO Score", "AA Score"]]
    chart_data = chart_data.set_index("Business")
    st.bar_chart(chart_data)

st.markdown("---")
st.caption(
    "MSME Financial Health Score | "
    "IDBI Innovate Hackathon 2026 | "
    "Built by Vamshi Teppala"
)    
