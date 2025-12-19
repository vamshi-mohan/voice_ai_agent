def check_eligibility(profile: dict, scheme: dict) -> (bool, list):
    reasons = []
    rules = scheme.get("eligibility", {})

    # age
    min_age = rules.get("min_age")
    if min_age is not None:
        if profile.get("age", 0) < min_age:
            reasons.append(f"min_age:{min_age}")

    max_income = rules.get("max_income")
    if max_income is not None:
        if profile.get("income", 99999999) > max_income:
            reasons.append(f"max_income:{max_income}")

    req_farmer = rules.get("is_farmer")
    if req_farmer is True:
        if not profile.get("is_farmer", False):
            reasons.append("requires_farmer")

    req_gender = rules.get("gender")
    if req_gender is not None:
        if profile.get("gender") != req_gender:
            reasons.append(f"gender:{req_gender}")

    ok = len(reasons) == 0
    return ok, reasons
