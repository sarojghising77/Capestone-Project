
from pathlib import Path
import re
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent

FW_FILE = BASE / "four-wheeler.csv"
TW_FILE = BASE / "two-wheeler.csv"


def load_data():
    if not FW_FILE.exists():
        raise FileNotFoundError(f"Missing file: {FW_FILE}")
    if not TW_FILE.exists():
        raise FileNotFoundError(f"Missing file: {TW_FILE}")
    fw = pd.read_csv(FW_FILE)
    tw = pd.read_csv(TW_FILE)
    return fw, tw


def percentages(series):
    if series is None or len(series) == 0:
        return pd.Series(dtype=float)
    s = series.dropna().astype(str).str.strip()
    s = s[(s != "") & (~s.str.lower().isin(["nan", "none", "na", "n/a"]))]
    if len(s) == 0:
        return pd.Series(dtype=float)
    return s.value_counts(normalize=True).mul(100).round(1)


def parse_rank(series):
    # Handles both numeric cells (e.g. 1.0) and text such as "Rank 1".
    if series is None:
        return pd.Series(dtype=float)
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    return pd.to_numeric(
        series.astype(str).str.extract(r"(\d+(?:\.\d+)?)")[0],
        errors="coerce"
    )


def ranked_columns(df, columns, labels):
    values = {}
    for col, label in zip(columns, labels):
        if col not in df.columns:
            continue
        s = parse_rank(df[col]).dropna()
        if len(s):
            values[label] = float(s.mean())
    return pd.Series(values, dtype=float).sort_values()


def priority_index(avg_rank, rank_max):
    # Higher is better/easier to read than raw average rank.
    if avg_rank is None or len(avg_rank) == 0:
        return pd.Series(dtype=float)
    denom = max(rank_max - 1, 1)
    return ((rank_max - avg_rank) / denom * 100).round(1)


def top_n(series, n=6):
    if series is None or len(series) == 0:
        return pd.Series(dtype=float)
    return series.sort_values().head(n)


def category_metrics(df, column):
    return percentages(df[column]) if column in df.columns else pd.Series(dtype=float)


def build_insights():
    fw, tw = load_data()

    # Exact survey columns from the supplied CSV files.
    stage_fw = category_metrics(fw, "Q1. Current Situation")
    stage_tw = category_metrics(tw, "current_situation")

    purpose_fw = category_metrics(fw, "Q2. Primary Purpose")
    purpose_tw = category_metrics(tw, "purchase_purpose")

    vehicle_fw = category_metrics(fw, "Q3. Preferred Vehicle Type")
    vehicle_tw = category_metrics(tw, "vehicle_type_preference")

    brand_fw = category_metrics(fw, "Q6. Most Likely Automobile Brand")
    brand_tw = category_metrics(tw, "q15_preferred_brand")

    brand_importance_fw = category_metrics(fw, "Q10. Brand Importance")
    brand_importance_tw = category_metrics(tw, "q16_brand_influence")

    brand_approach_fw = category_metrics(fw, "Q12. Approach when choosing brand")
    brand_approach_tw = category_metrics(tw, "q18_brand_selection_approach")

    ev_fw = category_metrics(fw, "# Consider purchasing an Electric Vehicle (EV)")
    ev_tw = category_metrics(tw, "q12_considering_ev")

    # Ranked questions.
    fw_factor_cols = [c for c in fw.columns if c.startswith("Q4. Factor")]
    fw_factor_labels = [c.split(" - ", 1)[1] for c in fw_factor_cols]
    tw_factor_cols = [
        "q8_rank_price", "q8_rank_fuel_eff_range", "q8_rank_quality_reliability",
        "q8_rank_brand_reputation", "q8_rank_maintenance_cost", "q8_rank_after_sales",
        "q8_rank_resale_value", "q8_rank_safety"
    ]
    tw_factor_labels = [
        "Price / initial cost", "Fuel efficiency / battery range",
        "Quality & reliability", "Brand reputation", "Maintenance cost",
        "After-sales service", "Resale value", "Safety"
    ]

    fw_source_cols = [c for c in fw.columns if c.startswith("Q5. Source")]
    fw_source_labels = [c.split(" - ", 1)[1] for c in fw_source_cols]
    tw_source_cols = [
        "q9_rank_friends_relatives", "q9_rank_online_reviews",
        "q9_rank_social_media", "q9_rank_youtube_reviews",
        "q9_rank_dealerships", "q9_rank_auto_shows"
    ]
    tw_source_labels = [
        "Friends & relatives", "Online reviews & tech blogs",
        "Social media", "YouTube & vehicle reviews",
        "Dealer showroom & test rides", "Auto exhibitions / NADA"
    ]

    fw_challenge_cols = [c for c in fw.columns if c.startswith("Q7. Challenge")]
    fw_challenge_labels = [c.split(" - ", 1)[1] for c in fw_challenge_cols]
    tw_challenge_cols = [
        "q10_rank_high_purchase_price", "q10_rank_import_taxes",
        "q10_rank_rising_fuel_costs", "q10_rank_high_maintenance",
        "q10_rank_limited_charging_infra", "q10_rank_unreliable_after_sales",
        "q10_rank_finding_spare_parts"
    ]
    tw_challenge_labels = [
        "High purchase price", "Taxes / import duties", "Rising fuel costs",
        "High maintenance", "Limited charging infrastructure",
        "Unreliable after-sales service", "Finding spare parts"
    ]

    fw_ev_cols = [c for c in fw.columns if c.startswith("Q8. EV Factor")]
    fw_ev_labels = [c.split(" - ", 1)[1] for c in fw_ev_cols]
    tw_ev_cols = [
        "q14_rank_lower_running_costs", "q14_rank_environmental_benefits",
        "q14_rank_lower_purchase_price", "q14_rank_longer_driving_range",
        "q14_rank_faster_charging_times", "q14_rank_better_public_charging_infra",
        "q14_rank_govt_subsidies"
    ]
    tw_ev_labels = [
        "Lower running / electricity costs", "Environmental benefits",
        "Lower initial purchase price", "Longer driving range",
        "Faster charging", "Better public charging infrastructure",
        "Government subsidies"
    ]

    fw_attr_cols = [c for c in fw.columns if c.startswith("Q11. Brand Attribute")]
    fw_attr_labels = [c.split(" - ", 1)[1] for c in fw_attr_cols]
    tw_attr_cols = [
        "q17_rank_quality_durability", "q17_rank_fuel_energy_efficiency",
        "q17_rank_smart_tech", "q17_rank_value_for_money",
        "q17_rank_after_sales_support", "q17_rank_eco_friendly",
        "q17_rank_safety_braking", "q17_rank_design_styling"
    ]
    tw_attr_labels = [
        "Quality & durability", "Fuel / energy efficiency", "Smart technology",
        "Value for money", "After-sales support", "Eco-friendly",
        "Safety & braking", "Design & styling"
    ]

    factors_fw = ranked_columns(fw, fw_factor_cols, fw_factor_labels)
    factors_tw = ranked_columns(tw, tw_factor_cols, tw_factor_labels)
    sources_fw = ranked_columns(fw, fw_source_cols, fw_source_labels)
    sources_tw = ranked_columns(tw, tw_source_cols, tw_source_labels)
    challenges_fw = ranked_columns(fw, fw_challenge_cols, fw_challenge_labels)
    challenges_tw = ranked_columns(tw, tw_challenge_cols, tw_challenge_labels)
    ev_drivers_fw = ranked_columns(fw, fw_ev_cols, fw_ev_labels)
    ev_drivers_tw = ranked_columns(tw, tw_ev_cols, tw_ev_labels)
    attributes_fw = ranked_columns(fw, fw_attr_cols, fw_attr_labels)
    attributes_tw = ranked_columns(tw, tw_attr_cols, tw_attr_labels)

    # Demographics.
    demo_fw = {
        "Age": category_metrics(fw, "Age"),
        "Gender": category_metrics(fw, "Gender"),
        "Income": category_metrics(fw, "Monthly Household Income"),
        "Occupation": category_metrics(fw, "Occupation"),
    }
    demo_tw = {
        "Age": category_metrics(tw, "age_group"),
        "Gender": category_metrics(tw, "gender"),
        "Income": category_metrics(tw, "monthly_income"),
        "Occupation": category_metrics(tw, "occupation"),
    }

    def top(series):
        if series is None or len(series) == 0:
            return "Data unavailable", 0.0
        return str(series.index[0]), float(series.iloc[0])

    # Business insights are generated from the actual survey results.
    soon_fw = stage_fw.get("I plan to purchase a four-wheeler within the next 12 months.", 0)
    soon_tw = stage_tw.get("I plan to purchase a two-wheeler within the next 12 months.", 0)

    ev_yes_fw = ev_fw.get("Yes", 0)
    ev_yes_tw = ev_tw.get("Yes", 0)

    brand_fw_top, brand_fw_pct = top(brand_fw)
    brand_tw_top, brand_tw_pct = top(brand_tw)
    factor_fw_top, factor_fw_rank = top(factors_fw)
    factor_tw_top, factor_tw_rank = top(factors_tw)
    source_fw_top, source_fw_rank = top(sources_fw)
    source_tw_top, source_tw_rank = top(sources_tw)
    challenge_fw_top, challenge_fw_rank = top(challenges_fw)
    challenge_tw_top, challenge_tw_rank = top(challenges_tw)
    attr_fw_top, attr_fw_rank = top(attributes_fw)
    attr_tw_top, attr_tw_rank = top(attributes_tw)
    evdriver_fw_top, _ = top(ev_drivers_fw)
    evdriver_tw_top, _ = top(ev_drivers_tw)

    # Cross-category business messages.
    journey_message = (
        f"{soon_tw:.0f}% of two-wheeler respondents and {soon_fw:.0f}% of four-wheeler respondents "
        "plan to purchase within 12 months. Prioritize near-term conversion tactics such as "
        "test rides, dealer follow-up, financing and time-limited offers."
    )

    ev_message = (
        f"EV consideration is {ev_yes_tw:.0f}% among two-wheeler respondents and {ev_yes_fw:.0f}% "
        "among four-wheeler respondents. The strongest EV purchase trigger is "
        f"{evdriver_tw_top} for two-wheelers and {evdriver_fw_top} for four-wheelers. "
        "Marketing should lead with practical ownership benefits and remove charging/affordability concerns."
    )

    discovery_message = (
        f"{source_tw_top} ranks first for two-wheelers, while {source_fw_top} ranks first for four-wheelers. "
        "Allocate research-stage marketing to the channels customers actually use, with different content mixes "
        "for the two segments rather than one generic media plan."
    )

    barrier_message = (
        f"The leading barrier is {challenge_tw_top} for two-wheelers and {challenge_fw_top} for four-wheelers. "
        "Use financing, total-cost-of-ownership messaging and targeted dealer support to address the highest "
        "purchase friction before asking customers to convert."
    )

    attribute_message = (
        f"Two-wheeler buyers rank {attr_tw_top} highest, while four-wheeler buyers rank {attr_fw_top} highest. "
        "Position the brand around the attributes customers value most, and make those benefits visible in "
        "advertising, showroom demonstrations and sales conversations."
    )

    factor_message = (
        f"{factor_tw_top} is the top two-wheeler decision factor, while {factor_fw_top} leads four-wheelers. "
        "Product positioning and sales scripts should be segment-specific: emphasize running/ownership economics "
        "for two-wheelers and the leading value drivers for four-wheelers."
    )

    return {
        "fw": fw,
        "tw": tw,
        "total_n": len(fw) + len(tw),
        "fw_n": len(fw),
        "tw_n": len(tw),

        "stage": {"fw": stage_fw, "tw": stage_tw},
        "purpose": {"fw": purpose_fw, "tw": purpose_tw},
        "vehicle_type": {"fw": vehicle_fw, "tw": vehicle_tw},
        "brand": {"fw": brand_fw, "tw": brand_tw},
        "brand_importance": {"fw": brand_importance_fw, "tw": brand_importance_tw},
        "brand_approach": {"fw": brand_approach_fw, "tw": brand_approach_tw},
        "ev_rate": {"fw": ev_fw, "tw": ev_tw},

        "factors": {"fw": factors_fw, "tw": factors_tw},
        "sources": {"fw": sources_fw, "tw": sources_tw},
        "challenges": {"fw": challenges_fw, "tw": challenges_tw},
        "ev_drivers": {"fw": ev_drivers_fw, "tw": ev_drivers_tw},
        "attributes": {"fw": attributes_fw, "tw": attributes_tw},

        "demographics": {"fw": demo_fw, "tw": demo_tw},

        "business_insights": {
            "journey": journey_message,
            "ev": ev_message,
            "discovery": discovery_message,
            "barriers": barrier_message,
            "attributes": attribute_message,
            "factors": factor_message,
            "brands": (
                f"{brand_fw_top} leads four-wheelers at {brand_fw_pct:.1f}% and {brand_tw_top} leads "
                f"two-wheelers at {brand_tw_pct:.1f}%. Use the leading brands as competitive benchmarks, "
                "but also identify the attributes and channels that explain why customers prefer them."
            ),
        }
    }
