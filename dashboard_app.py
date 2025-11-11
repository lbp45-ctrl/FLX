# Run with: streamlit run dashboard_app.py

from __future__ import annotations

from typing import Callable, Dict, List, Sequence, Tuple

import pandas as pd
import streamlit as st

import local_impact_calculator as lic

RetailerInputs = getattr(lic, "RetailerInputs", None)
if RetailerInputs is None:
    raise AttributeError("RetailerInputs class was not found in local_impact_calculator.py")

# TODO: Add or adjust names in this tuple if your calculator function uses a different
# TODO: function name or signature for local impact.
candidate_calculator_names: List[str] = [
    "calculate_local_impact",
    "calculate_retailer_impact",
    "compute_local_impact",
    "summarize_retailer",
    "local_impact_dollars",
]

calculator_fn: Callable[..., object] | None = None
calculator_fn_name: str | None = None
for name in candidate_calculator_names:
    maybe_fn = getattr(lic, name, None)
    if callable(maybe_fn):
        calculator_fn = maybe_fn
        calculator_fn_name = name
        break

if calculator_fn is None:
    raise AttributeError(
        "No local impact calculator function found. Update candidate_calculator_names "
        "so the dashboard can call the correct function from local_impact_calculator.py."
    )


def get_retailer_inputs(
    retailer_name: str,
    *,
    default_total_sales: float = 50_000.0,
    default_taxes: float = 4_000.0,
    default_shipping: float = 2_500.0,
    default_local_rate: float = 0.6,
    local_rate_help: str | None = None,
) -> object:
    st.sidebar.subheader(f"{retailer_name} inputs")
    total_sales = st.sidebar.number_input(
        f"{retailer_name} total sales (NY State $)",
        min_value=0.0,
        value=default_total_sales,
        step=1000.0,
        help="Use New York State sales estimates for consistency across retailers.",
    )
    taxes = st.sidebar.number_input(
        f"{retailer_name} taxes ($)", min_value=0.0, value=default_taxes, step=500.0
    )
    shipping = st.sidebar.number_input(
        f"{retailer_name} shipping ($)", min_value=0.0, value=default_shipping, step=250.0
    )
    local_rate = st.sidebar.slider(
        f"{retailer_name} local rate",
        min_value=0.0,
        max_value=1.0,
        value=default_local_rate,
        step=0.05,
        help=local_rate_help,
    )
    multiplier = st.sidebar.slider(
        f"{retailer_name} multiplier",
        min_value=1.3,
        max_value=2.0,
        value=1.6,
        step=0.05,
        help="Economic multiplier (Cornell guidance: 1.3–2.0 range).",
    )
    return RetailerInputs(
        name=retailer_name,
        total_sales=total_sales,
        taxes=taxes,
        shipping=shipping,
        local_rate=local_rate,
        multiplier=multiplier,
    )


def _compute_local_impact(retailer_inputs: object) -> Tuple[float, float]:
    total_sales = getattr(retailer_inputs, "total_sales", 0.0) or 0.0

    if calculator_fn_name == "summarize_retailer":
        summary = calculator_fn(retailer_inputs)
        local_impact = float(summary.get("local_impact_dollars", 0.0))
        share = float(summary.get("local_impact_share", 0.0))
        if not share and total_sales:
            share = local_impact / total_sales
        return local_impact, share

    if calculator_fn_name == "local_impact_dollars":
        local_impact = float(
            calculator_fn(
                getattr(retailer_inputs, "total_sales", 0.0),
                getattr(retailer_inputs, "taxes", 0.0),
                getattr(retailer_inputs, "shipping", 0.0),
                getattr(retailer_inputs, "local_rate", 0.0),
                getattr(retailer_inputs, "multiplier", 1.0),
            )
        )
        share = (local_impact / total_sales) if total_sales else 0.0
        return local_impact, share

    # Default assumption: the calculator accepts a RetailerInputs instance and returns dollars.
    # TODO: adjust this call if your calculator signature differs from the assumptions above.
    local_impact = float(calculator_fn(retailer_inputs))
    share = (local_impact / total_sales) if total_sales else 0.0
    return local_impact, share


def calculate_metrics(retailer_inputs: object) -> dict[str, float | str]:
    local_impact, share = _compute_local_impact(retailer_inputs)
    return {
        "name": getattr(retailer_inputs, "name", ""),
        "local_impact": local_impact,
        "share": share,
    }


def render_kpis(metrics: List[dict[str, float | str]]) -> None:
    st.subheader("Local impact KPIs")
    columns = st.columns(len(metrics))
    for column, metric in zip(columns, metrics):
        column.metric(
            label=f"{metric['name']} local impact",
            value=f"{metric['share']:.1%} of sales",
            delta=f"${metric['local_impact']:,.0f} local impact",
        )


def render_chart(metrics: List[dict[str, float | str]]) -> None:
    chart_df = pd.DataFrame(
        {
            "Retailer": [metric["name"] for metric in metrics],
            "Local impact ($)": [metric["local_impact"] for metric in metrics],
        }
    ).set_index("Retailer")
    st.bar_chart(chart_df)


def main() -> None:
    st.set_page_config(page_title="Local Impact Dashboard", layout="wide")
    st.title("Retailer local economic impact")
    st.caption("Compare FLX Goods vs Amazon based on your calculator inputs.")

    st.sidebar.title("Input assumptions")
    st.sidebar.info("Adjust the sliders and numbers to test different scenarios.")

    base_configs: Sequence[Dict[str, object]] = (
        {
            "name": "FLX Goods",
            "defaults": {
                "default_total_sales": 60_000.0,
                "default_taxes": 4_500.0,
                "default_shipping": 2_000.0,
                "default_local_rate": 0.90,
                "local_rate_help": "Recommended Cornell estimate for FLX Goods (90% local).",
            },
        },
        {
            "name": "Amazon",
            "defaults": {
                "default_total_sales": 150_000.0,
                "default_taxes": 12_000.0,
                "default_shipping": 8_000.0,
                "default_local_rate": 0.10,
                "local_rate_help": "Assumed Amazon local spending rate (10%).",
            },
        },
        {
            "name": "Walmart",
            "defaults": {
                "default_total_sales": 120_000.0,
                "default_taxes": 9_500.0,
                "default_shipping": 7_000.0,
                "default_local_rate": 0.25,
                "local_rate_help": "Example Walmart local rate assumption (25%).",
            },
        },
        {
            "name": "Wegmans",
            "defaults": {
                "default_total_sales": 90_000.0,
                "default_taxes": 7_200.0,
                "default_shipping": 5_500.0,
                "default_local_rate": 0.35,
                "local_rate_help": "Example Wegmans local rate assumption (35%).",
            },
        },
    )

    retailer_inputs = [
        get_retailer_inputs(config["name"], **config["defaults"]) for config in base_configs
    ]

    st.sidebar.subheader("Custom competitors")
    custom_names_raw = st.sidebar.text_input(
        "Add competitor names (comma separated)",
        value="",
        help="Enter any other competitors you want to compare; leave blank to skip.",
    )
    custom_names = [name.strip() for name in custom_names_raw.split(",") if name.strip()]
    for custom_name in custom_names:
        retailer_inputs.append(
            get_retailer_inputs(
                custom_name,
                default_total_sales=80_000.0,
                default_taxes=6_000.0,
                default_shipping=4_000.0,
                default_local_rate=0.20,
                local_rate_help="Adjust this estimate based on how local the competitor is.",
            )
        )

    metrics = [calculate_metrics(retailer) for retailer in retailer_inputs]

    render_kpis(metrics)
    st.divider()
    st.subheader("Local impact comparison")
    render_chart(metrics)


if __name__ == "__main__":
    main()
