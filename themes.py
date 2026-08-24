
import re
import pandas as pd

THEMES = {
    "Price & affordability": ["price", "cost", "afford", "financ", "interest", "tax"],
    "Reliability & quality": ["reliab", "durab", "quality", "build"],
    "After-sales & service": ["after-sales", "service", "spare parts", "maintenance"],
    "Safety": ["safety", "braking", "secure"],
    "Efficiency & running cost": ["fuel", "efficien", "running cost", "mileage", "electricity"],
    "Brand trust & reputation": ["trust", "reputation", "brand"],
    "Transparency": ["transparent", "hidden", "honest", "markup"],
    "EV & charging": ["electric", "ev", "charging", "battery"],
}


def tag_themes(series):
    counts = pd.Series(0, index=list(THEMES.keys()), dtype=int)
    if series is None:
        return counts
    for value in series.dropna():
        text = str(value).lower()
        for theme, words in THEMES.items():
            if any(w in text for w in words):
                counts[theme] += 1
    return counts.sort_values(ascending=False)


def sample_quotes(series, n=3):
    if series is None:
        return []
    vals = []
    for value in series.dropna().astype(str):
        value = value.strip()
        if value and value.lower() not in {"nan", "none"}:
            vals.append(value)
    return vals[:n]
