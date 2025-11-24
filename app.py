import streamlit as st
from backend.risk_model import score_text_reason, score_numeric_data, fuse_scores, explain_numeric, explain_text

st.set_page_config(page_title="AI Credit Risk System", layout="centered")
st.title("AI Credit Risk Assessment System (Track 2)")

st.header("Structured Data Input")
salary = st.number_input("Monthly Salary (RM)", min_value=0)
loan_amount = st.number_input("Loan Amount (RM)", min_value=0)
repayment_history = st.slider("Repayment History (0-10)", 0, 10)
savings = st.number_input("Total Savings (RM)", min_value=0)
existing_debt = st.number_input("Existing Debt (RM)", min_value=0)

st.header("Unstructured Data Input")
reason = st.text_area("Reason for Loan")

if st.button("Assess Risk"):

    # Compute scores
    numeric_score = score_numeric_data(salary, loan_amount, repayment_history, savings, existing_debt)
    text_score, sentiment, flags = score_text_reason(reason)
    final_score, decision = fuse_scores(numeric_score, text_score)

    # Display
    if decision == "ACCEPT":
        color = "🟢 ACCEPT"
    else:
        color = "🔴 REJECT"

    st.subheader(f"Final Risk Score: {final_score}/100 → {color}")

    st.divider()
    st.subheader("Explanation")
    st.write("### Numeric Factors:")
    for line in explain_numeric(salary, loan_amount, repayment_history, savings, existing_debt):
        st.write("- " + line)
    st.write("### Text / Behavioral Factors:")
    for line in explain_text(reason):
        st.write("- " + line)
