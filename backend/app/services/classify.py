import re

KEYWORDS = {
    "earnings": [
        r"beats", r"misses", r"EPS", r"revenue", r"guidance", r"raises guidance", r"lowers guidance"
    ],
    "mna": [
        r"acquires", r"to acquire", r"merger", r"to be acquired", r"buyout"
    ],
    "ratings": [
        r"upgraded to", r"downgraded to", r"initiates coverage", r"price target"
    ],
    "fda": [
        r"FDA", r"PDUFA", r"approval", r"Complete Response Letter", r"CRL"
    ],
    "filing": [
        r"8-K", r"S-1", r"13D", r"13G", r"Form 4", r"registration statement"
    ],
}

PLAYBOOK_HINTS = {
    "earnings": "Watch VWAP reclaim + higher lows; pullback to VWAP for entries.",
    "mna": "Range break of pre-market high; look for break-retest continuation.",
    "ratings": "Bias follows rating change if under/over VWAP; look for trend alignment.",
    "fda": "Be cautious on halts; first higher-low after unhalt can be high R/R.",
    "filing": "Context-dependent; 8-K contract wins can trend; avoid thin names.",
    "other": "Tape-read; avoid chasing; confirm with volume & VWAP.",
}

def classify_event(headline: str, body: str | None) -> str:
    text = f"{headline} {body or ''}"
    for label, pats in KEYWORDS.items():
        for p in pats:
            if re.search(p, text, flags=re.IGNORECASE):
                return label
    return "other"

def playbook_for(label: str) -> str:
    return PLAYBOOK_HINTS.get(label, PLAYBOOK_HINTS["other"])
