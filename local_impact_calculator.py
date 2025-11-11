"""
local_impact_calculator.py

Core calculator for FLX Goods local impact vs competitors.

Formulae (per project brief):
- Retail Impact Base = Total Sales - 0.5 * Taxes - Shipping
- Local Impact ($) = Retail Impact Base * Local Rate * Multiplier
- Local Impact Share of Sales = Local Impact ($) / Total Sales

Where:
- Total Sales: total revenue ($)
- Taxes: total taxes associated with those sales ($)
- Shipping: total shipping costs ($)
- Local Rate: share of relevant spending that is local (0–1), e.g. 0.65
- Multiplier: economic multiplier (use 1.3–2.0; this will be a slider on the website)
"""

from dataclasses import dataclass
from typing import Dict, Union


Number = Union[int, float]

@dataclass
class RetailerInputs:
    name: str
    total_sales: float       # $
    taxes: float             # $
    shipping: float          # $
    local_rate: float        # 0–1, fraction of spending that is local
    multiplier: float        # 1.3–2.0 (tunable / slider)

    def __post_init__(self) -> None:
        """Lightweight validation so bad inputs fail fast."""
        for field_name in ("total_sales", "taxes", "shipping", "local_rate", "multiplier"):
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)):
                raise TypeError(f"{field_name} must be numeric, got {type(value)!r}")

        if self.total_sales < 0:
            raise ValueError("total_sales cannot be negative")
        if self.taxes < 0:
            raise ValueError("taxes cannot be negative")
        if self.shipping < 0:
            raise ValueError("shipping cannot be negative")
        if not 0 <= self.local_rate <= 1:
            raise ValueError("local_rate must be between 0 and 1")
        if self.multiplier <= 0:
            raise ValueError("multiplier must be > 0")

def retail_impact_base(total_sales: Number, taxes: Number, shipping: Number) -> float:
    """Compute Retail Impact Base."""
    total_sales_f = float(total_sales)
    taxes_f = float(taxes)
    shipping_f = float(shipping)
    return total_sales_f - 0.5 * taxes_f - shipping_f

def local_impact_dollars(total_sales: Number,
                         taxes: Number,
                         shipping: Number,
                         local_rate: Number,
                         multiplier: Number) -> float:
    """
    Local impact in dollars:
    (Total Sales - 0.5 * Taxes - Shipping) * Local Rate * Multiplier
    """
    base = retail_impact_base(total_sales, taxes, shipping)
    local_rate_f = float(local_rate)
    multiplier_f = float(multiplier)
    return max(0.0, base) * local_rate_f * multiplier_f

def local_impact_share(total_sales: Number,
                       taxes: Number,
                       shipping: Number,
                       local_rate: Number,
                       multiplier: Number) -> float:
    """
    Local impact as a fraction of total sales (0–1).
    """
    total_sales_f = float(total_sales)
    if total_sales_f <= 0:
        return 0.0
    return local_impact_dollars(total_sales, taxes, shipping, local_rate, multiplier) / total_sales_f

def summarize_retailer(inputs: RetailerInputs) -> Dict[str, Number]:
    """
    Return a summary dict for easy use in templates / front-end.
    """
    base = retail_impact_base(inputs.total_sales, inputs.taxes, inputs.shipping)
    li_dollars = local_impact_dollars(
        inputs.total_sales,
        inputs.taxes,
        inputs.shipping,
        inputs.local_rate,
        inputs.multiplier,
    )
    li_share = li_dollars / inputs.total_sales if inputs.total_sales > 0 else 0.0

    result: Dict[str, Number] = {
        "name": inputs.name,
        "total_sales": round(inputs.total_sales, 2),
        "taxes": round(inputs.taxes, 2),
        "shipping": round(inputs.shipping, 2),
        "retail_impact_base": round(base, 2),
        "local_rate": inputs.local_rate,
        "multiplier": inputs.multiplier,
        "local_impact_dollars": round(li_dollars, 2),
        "local_impact_share": round(li_share, 4),
    }
    return result

if __name__ == "__main__":
    # Dummy example values
    flx = RetailerInputs(
        name="FLX Goods",
        total_sales=100000.0,
        taxes=8000.0,
        shipping=5000.0,
        local_rate=0.70,     
        multiplier=1.7,      
    )

    amazon = RetailerInputs(
        name="Amazon",
        total_sales=100000.0,
        taxes=8000.0,
        shipping=7000.0,
        local_rate=0.10,
        multiplier=1.4,
    )

    walmart = RetailerInputs(
        name="Walmart",
        total_sales=100000.0,
        taxes=8000.0,
        shipping=6000.0,
        local_rate=0.20,
        multiplier=1.4,
    )

    wegmans = RetailerInputs(
        name="Wegmans",
        total_sales=100000.0,
        taxes=8000.0,
        shipping=6000.0,
        local_rate=0.30,
        multiplier=1.5,
    )

    for r in [flx, amazon, walmart, wegmans]:
        s = summarize_retailer(r)
        print(
            f"{s['name']}: "
            f"Local impact = ${s['local_impact_dollars']:,} "
            f"({s['local_impact_share']*100:.1f}% of each $1)"
        )
