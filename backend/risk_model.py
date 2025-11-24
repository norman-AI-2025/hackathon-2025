# backend/risk_model.py
from transformers import pipeline
from .rules import detect_red_flags

# Load sentiment analysis pipeline
sentiment_model = pipeline("sentiment-analysis")

# ---------------- TEXT SCORE ----------------
def score_text_reason(reason):
    """Compute text-based risk from reason text."""
    sentiment = sentiment_model(reason[:1000])[0]  # limit text for speed
    label = sentiment["label"]  # POSITIVE / NEGATIVE
    score_conf = sentiment["score"]

    # Map sentiment to numeric risk
    if label == "POSITIVE":
        sentiment_risk = (1 - score_conf) * 40
    else:
        sentiment_risk = 40 + (score_conf * 30)

    # Red flags
    flag_risk, flags = detect_red_flags(reason)

    total_text_risk = sentiment_risk + flag_risk
    if total_text_risk > 100:
        total_text_risk = 100

    return total_text_risk, label, flags

# ---------------- NUMERIC SCORE ----------------
def score_numeric_data(salary, loan_amount, repayment_history, savings, existing_debt):
    """Compute numeric risk score based on structured data."""
    if salary == 0:
        salary = 1  # avoid divide by zero

    # Loan-to-income ratio
    lti_ratio = loan_amount / (salary * 12)
    lti_score = min(lti_ratio * 50, 50)

    # Repayment history
    repayment_score = (10 - repayment_history) * 3  # 0-30

    # Savings buffer
    savings_score = 0 if savings > loan_amount else 10

    # Existing debt
    debt_ratio = existing_debt / (salary * 12)
    debt_score = min(debt_ratio * 20, 20)

    numeric_score = lti_score + repayment_score + savings_score + debt_score
    numeric_score = min(numeric_score, 100)
    return numeric_score

# ---------------- FINAL SCORE ----------------
def fuse_scores(numeric_score, text_score):
    final = 0.5 * numeric_score + 0.5 * text_score
    final = round(final, 2)

    # Decision
    if final < 50:
        decision = "ACCEPT"
    else:
        decision = "REJECT"

    return final, decision

# ---------------- EXPLANATION ----------------
def explain_numeric(salary, loan_amount, repayment_history, savings, existing_debt):
    explanations = []

    # Loan-to-income
    lti_ratio = loan_amount / (salary*12)
    if lti_ratio > 0.5:
        explanations.append(f"High loan-to-income ratio ({lti_ratio:.2f})")
    else:
        explanations.append(f"Loan-to-income ratio ({lti_ratio:.2f}) is acceptable")

    # Repayment
    if repayment_history < 5:
        explanations.append(f"Poor repayment history ({repayment_history}/10)")
    else:
        explanations.append(f"Repayment history ({repayment_history}/10) is good")

    # Savings
    if savings < loan_amount:
        explanations.append(f"Low savings ({savings} < loan amount {loan_amount})")
    else:
        explanations.append(f"Savings are sufficient ({savings})")

    # Existing debt
    debt_ratio = existing_debt / (salary*12)
    if debt_ratio > 0.5:
        explanations.append(f"High existing debt ({existing_debt})")
    else:
        explanations.append(f"Existing debt ({existing_debt}) is acceptable")

    return explanations

def explain_text(reason):
    text_score, sentiment_label, flags = score_text_reason(reason)
    explanations = []
    explanations.append(f"Sentiment: {sentiment_label}")
    if flags:
        explanations.append(f"Red-flag keywords: {', '.join(flags)}")
    else:
        explanations.append("No red-flag keywords detected")
    return explanations
