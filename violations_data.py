# This is our local "Traffic Law Database" — a dictionary of known violations.
# Each violation has: the fine amount, the legal section, and extra penalty if any.
# This matches your hackathon slide's "Traffic Laws Database -> State-Specific Rules" flow.

VIOLATIONS_DB = {
    "no helmet": {
        "violation": "Riding without a helmet",
        "fine": "₹1,000",
        "section": "Section 194D, Motor Vehicles Act, 1988",
        "extra_penalty": "License disqualification for 3 months"
    },
    "no seatbelt": {
        "violation": "Driving without seatbelt",
        "fine": "₹1,000",
        "section": "Section 194B, Motor Vehicles Act, 1988",
        "extra_penalty": "None"
    },
    "triple riding": {
        "violation": "Triple riding on a two-wheeler",
        "fine": "₹1,000 (first offence), ₹2,000 (subsequent)",
        "section": "Section 128 read with Section 194C, Motor Vehicles Act, 1988",
        "extra_penalty": "License disqualification possible"
    },
    "red light jump": {
        "violation": "Jumping a red light / signal violation",
        "fine": "₹1,000 to ₹5,000",
        "section": "Section 184, Motor Vehicles Act, 1988",
        "extra_penalty": "License disqualification possible for repeat offences"
    },
    "drunk driving": {
        "violation": "Driving under the influence of alcohol",
        "fine": "₹10,000 and/or imprisonment up to 6 months (first offence)",
        "section": "Section 185, Motor Vehicles Act, 1988",
        "extra_penalty": "Imprisonment up to 2 years for repeat offence within 3 years"
    },
    "overspeeding": {
        "violation": "Overspeeding",
        "fine": "₹1,000 to ₹2,000 (light motor vehicle)",
        "section": "Section 183, Motor Vehicles Act, 1988",
        "extra_penalty": "License disqualification possible"
    },
    "no license": {
        "violation": "Driving without a valid license",
        "fine": "₹5,000",
        "section": "Section 181, Motor Vehicles Act, 1988",
        "extra_penalty": "Imprisonment possible"
    },
    "using phone while driving": {
        "violation": "Using a mobile phone while driving",
        "fine": "₹1,000 to ₹5,000",
        "section": "Section 184, Motor Vehicles Act, 1988",
        "extra_penalty": "License disqualification possible"
    },
    "no insurance": {
        "violation": "Driving without valid insurance",
        "fine": "₹2,000 (first offence), ₹4,000 (subsequent)",
        "section": "Section 196, Motor Vehicles Act, 1988",
        "extra_penalty": "Imprisonment up to 3 months possible"
    },
    "wrong side driving": {
        "violation": "Driving on the wrong side of the road",
        "fine": "₹1,000 to ₹5,000",
        "section": "Section 177/184, Motor Vehicles Act, 1988",
        "extra_penalty": "None"
    },
}


def find_violation(user_text: str):
    """
    Searches our local database for a violation matching the user's text.
    Returns the matching entry if found, otherwise None.
    """
    user_text_lower = user_text.lower()
    for keyword, details in VIOLATIONS_DB.items():
        if keyword in user_text_lower:
            return details
    return None