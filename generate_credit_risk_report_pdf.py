from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parent
OUTPUT_MD = ROOT / "ThanhPham_CreditRisk_Report.md"
OUTPUT_PDF = ROOT / "ThanhPham_CreditRisk_Report.pdf"
PROJECT_DIR = ROOT / "credit_risk_project"
OUTPUTS_DIR = PROJECT_DIR / "outputs"
DATA_DIR = PROJECT_DIR / "data"

NAVY = "#17324D"
SLATE = "#5B6B7A"
LIGHT = "#F5F7FA"
MID = "#E3E9F0"
ACCENT = "#B84A3A"
TOP5_FILL = "#FCEDEA"
ESCALATE_FILL = "#FDE8E4"

TOP5_RISKS = {"Monte dei Paschi", "Turkey", "Greece", "Italy", "Brazil"}


def wrap_cell(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(str(text), width=width, break_long_words=False))


def add_footer(fig: plt.Figure, page_number: int) -> None:
    fig.text(0.06, 0.025, "Thanh Pham | Credit Risk Monitoring Report", fontsize=8, color=SLATE)
    fig.text(0.94, 0.025, f"Page {page_number}", fontsize=8, color=SLATE, ha="right")


def add_box(ax, xy, width, height, title=None, facecolor="white", edgecolor=MID, linewidth=1.0):
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.01",
        linewidth=linewidth,
        edgecolor=edgecolor,
        facecolor=facecolor,
        transform=ax.transAxes,
    )
    ax.add_patch(box)
    if title:
        ax.text(
            xy[0] + 0.02,
            xy[1] + height - 0.035,
            title,
            transform=ax.transAxes,
            fontsize=12,
            fontweight="bold",
            color=NAVY,
            va="top",
        )


def add_wrapped_block(ax, x, y, text, width, fontsize=10, color="#1B1F23", line_gap=0.035, bullet=False):
    prefix = "- " if bullet else ""
    wrapped = textwrap.wrap(text, width=width, break_long_words=False)
    if not wrapped:
        wrapped = [""]
    current_y = y
    for i, line in enumerate(wrapped):
        line_text = f"{prefix}{line}" if i == 0 else ("  " + line if bullet else line)
        ax.text(x, current_y, line_text, transform=ax.transAxes, fontsize=fontsize, color=color, va="top")
        current_y -= line_gap
    return current_y


def load_data():
    ratings = pd.read_csv(OUTPUTS_DIR / "internal_rating_table.csv")
    watch = pd.read_csv(OUTPUTS_DIR / "watchlist.csv")
    market_summary = pd.read_csv(OUTPUTS_DIR / "market_monitoring_summary.csv", parse_dates=["date"])
    banks = pd.read_csv(DATA_DIR / "banks_sample.csv")
    sovereigns = pd.read_csv(DATA_DIR / "sovereigns_sample.csv")
    market = pd.read_csv(DATA_DIR / "market_data_sample.csv", parse_dates=["date"])
    return ratings, watch, market_summary, banks, sovereigns, market


def build_stats(ratings, watch, market_summary, market):
    last_date = market_summary["date"].max()
    first_date = market["date"].min()
    last_market_date = market["date"].max()
    watchlist_names = set(ratings.loc[ratings["final_watchlist_flag"], "entity_name"])
    last_snapshot = market.loc[market["date"] == last_market_date].copy()
    last_snapshot["watchlist"] = last_snapshot["entity_name"].isin(watchlist_names)

    stats = {
        "total_entities": len(ratings),
        "watchlist_count": int(ratings["final_watchlist_flag"].sum()),
        "watchlist_banks": int(ratings.loc[(ratings["entity_type"] == "Bank") & ratings["final_watchlist_flag"]].shape[0]),
        "watchlist_sovereigns": int(ratings.loc[(ratings["entity_type"] == "Sovereign") & ratings["final_watchlist_flag"]].shape[0]),
        "last_cds_alerts": int(market_summary.loc[market_summary["date"] == last_date, "entities_with_cds_alert"].iloc[0]),
        "last_spread_alerts": int(market_summary.loc[market_summary["date"] == last_date, "entities_with_spread_alert"].iloc[0]),
        "last_equity_alerts": int(market_summary.loc[market_summary["date"] == last_date, "entities_with_equity_alert"].iloc[0]),
        "first_avg_cds": float(market.loc[market["date"] == first_date, "cds_5y_bps"].mean()),
        "last_avg_cds": float(market.loc[market["date"] == last_market_date, "cds_5y_bps"].mean()),
        "first_avg_spread": float(market.loc[market["date"] == first_date, "bond_spread_bps"].mean()),
        "last_avg_spread": float(market.loc[market["date"] == last_market_date, "bond_spread_bps"].mean()),
        "watch_avg_cds": float(last_snapshot.loc[last_snapshot["watchlist"], "cds_5y_bps"].mean()),
        "watch_avg_spread": float(last_snapshot.loc[last_snapshot["watchlist"], "bond_spread_bps"].mean()),
        "nonwatch_avg_cds": float(last_snapshot.loc[~last_snapshot["watchlist"], "cds_5y_bps"].mean()),
        "nonwatch_avg_spread": float(last_snapshot.loc[~last_snapshot["watchlist"], "bond_spread_bps"].mean()),
        "correlation_cds_spread": float(market[["cds_5y_bps", "bond_spread_bps"]].corr().iloc[0, 1]),
        "correlation_cds_vol": float(market[["cds_5y_bps", "equity_vol_30d"]].corr().iloc[0, 1]),
        "correlation_spread_vol": float(market[["bond_spread_bps", "equity_vol_30d"]].corr().iloc[0, 1]),
        "last_date_str": last_market_date.strftime("%d %B %Y"),
        "first_date_str": first_date.strftime("%d %B %Y"),
    }
    return stats


def prepare_portfolio_table(ratings: pd.DataFrame) -> pd.DataFrame:
    table = (
        ratings[["entity_name", "entity_type", "internal_score", "implied_internal_rating", "market_alert_count", "final_watchlist_flag"]]
        .sort_values(["internal_score", "market_alert_count"], ascending=[True, False])
        .copy()
    )
    table["internal_score"] = table["internal_score"].map(lambda x: f"{x:.2f}")
    table["market_alert_count"] = table["market_alert_count"].astype(int).astype(str)
    table["final_watchlist_flag"] = table["final_watchlist_flag"].map({True: "Yes", False: "No"})
    table.columns = [
        "Entity Name",
        "Entity Type",
        "Internal Score",
        "Implied Rating",
        "Alerts",
        "Watchlist",
    ]
    return table


def prepare_watchlist_table(watch: pd.DataFrame) -> pd.DataFrame:
    reasons = {
        "Monte dei Paschi": "Weakest bank score; high NPLs, negative earnings, and non-investment-grade profile.",
        "Turkey": "Inflation shock and external imbalance keep sovereign risk elevated.",
        "Brazil": "Weak fiscal balance and non-investment-grade profile; market spreads remain wide.",
        "Greece": "High debt burden and latest spread widening keep refinancing risk live.",
        "Italy": "High debt stock and weak internal score leave limited headroom.",
        "Societe Generale": "Weak profitability, efficiency, and liquidity metrics.",
        "Deutsche Bank": "Cost efficiency and leverage remain the key constraints.",
        "Commerzbank": "Weak efficiency and an active volatility alert warrant closer monitoring.",
        "Spain": "External-balance and reserve metrics keep the score below threshold.",
        "Santander": "Internal score remains weak despite a short-term equity rebound.",
        "Barclays": "Leverage and liquidity metrics lag stronger peer banks.",
        "BNP Paribas": "Liquidity and leverage metrics constrain the score.",
        "ABN AMRO": "Marginal breach of the score threshold; liquidity and leverage remain weak.",
        "HSBC": "Score remains below threshold and recent deterioration reduces headroom.",
        "France": "Fiscal slippage and weaker external metrics depress the sovereign score.",
        "United Kingdom": "Fiscal and external deficits continue to constrain sovereign headroom.",
        "United States": "High debt and external deficits drive a conservative model score.",
        "Japan": "Very high debt/GDP dominates an otherwise stable sovereign profile.",
    }
    table = watch.copy()
    table["Reason"] = table["entity_name"].map(reasons)
    table["Latest Market Signal"] = table.apply(
        lambda r: f"CDS {r['latest_cds_5y_bps']:.0f}bp | Spread {r['latest_bond_spread_bps']:.0f}bp\nEquity 5d {r['latest_equity_return_5d'] * 100:+.1f}%",
        axis=1,
    )
    table["Priority Rank"] = table["analyst_priority"].map({"Escalate": 0, "Review": 1, "Monitor": 2})
    table = table.sort_values(["Priority Rank", "latest_cds_5y_bps"], ascending=[True, False])
    table = table[["entity_name", "Reason", "Latest Market Signal", "analyst_priority"]].copy()
    table.columns = ["Name", "Reason for Inclusion", "Latest Market Signal", "Recommendation"]
    return table


def draw_title_page(pdf: PdfPages, stats) -> None:
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    ax.text(0.06, 0.95, "Credit Risk Monitoring Report", fontsize=24, fontweight="bold", color=NAVY, va="top")
    ax.text(0.06, 0.915, "Prepared by Thanh Pham", fontsize=11, color=SLATE, va="top")
    ax.text(0.94, 0.915, "Reference Date: 31 December 2025", fontsize=11, color=SLATE, va="top", ha="right")

    add_box(ax, (0.06, 0.68), 0.88, 0.17, title="Executive Snapshot", facecolor=LIGHT)
    ax.text(0.09, 0.785, f"{stats['total_entities']}", fontsize=26, fontweight="bold", color=NAVY, va="center")
    ax.text(0.09, 0.75, "Entities Monitored", fontsize=10, color=SLATE)
    ax.text(0.31, 0.785, f"{stats['watchlist_count']}", fontsize=26, fontweight="bold", color=NAVY, va="center")
    ax.text(0.31, 0.75, "Watchlist Names", fontsize=10, color=SLATE)
    ax.text(0.53, 0.785, "Stable", fontsize=26, fontweight="bold", color=NAVY, va="center")
    ax.text(0.53, 0.75, "Overall Outlook", fontsize=10, color=SLATE)
    ax.text(0.75, 0.795, f"{stats['last_cds_alerts']} CDS  |  {stats['last_spread_alerts']} Spread  |  {stats['last_equity_alerts']} Equity", fontsize=12, color=NAVY, va="center")
    ax.text(0.75, 0.75, "Active alerts on 31 Dec 2025", fontsize=10, color=SLATE)

    add_box(ax, (0.06, 0.34), 0.58, 0.29, title="1. Executive Summary")
    y = 0.59
    bullets = [
        f"The monitoring perimeter covers {stats['total_entities']} entities, with {stats['watchlist_count']} names on watchlist; the split is balanced between {stats['watchlist_banks']} banks and {stats['watchlist_sovereigns']} sovereigns.",
        "Tail risk is concentrated in Monte dei Paschi, Turkey, Greece, Italy, and Brazil, where weak internal scores coincide with materially wider CDS and bond spreads.",
        "Monte dei Paschi is the only name on Escalate status, reflecting the weakest internal score in the bank book, a non-investment-grade profile, and persistently stressed market pricing.",
        "Macro and market conditions remain shaped by higher-for-longer rates, wider sovereign spread dispersion, and elevated volatility in weaker credits rather than by a broad-based systemic shock.",
        "Year-end market stress is selective rather than generalized: CDS and equity alerts have faded, while a small number of weaker names still show elevated volatility and one active spread alert.",
        "Overall credit outlook is Stable, but downside risk remains skewed to lower-quality sovereigns and second-tier European banks.",
    ]
    for bullet in bullets:
        y = add_wrapped_block(ax, 0.09, y, bullet, width=74, fontsize=10.5, line_gap=0.028, bullet=True) - 0.011

    add_box(ax, (0.67, 0.34), 0.27, 0.29, title="Key Monitoring Takeaways", facecolor=LIGHT)
    right_y = 0.59
    takeaways = [
        f"Portfolio average CDS widened from {stats['first_avg_cds']:.0f}bp to {stats['last_avg_cds']:.0f}bp across the observation window.",
        f"Average bond spreads widened from {stats['first_avg_spread']:.0f}bp to {stats['last_avg_spread']:.0f}bp.",
        f"Watchlist names trade materially wider than non-watchlist names: {stats['watch_avg_cds']:.0f}bp vs {stats['nonwatch_avg_cds']:.0f}bp CDS and {stats['watch_avg_spread']:.0f}bp vs {stats['nonwatch_avg_spread']:.0f}bp spreads.",
        "Stress remains concentrated in the weaker tail, not across the full portfolio.",
    ]
    for bullet in takeaways:
        right_y = add_wrapped_block(ax, 0.70, right_y, bullet, width=32, fontsize=10, line_gap=0.03, bullet=True) - 0.014

    add_footer(fig, 1)
    pdf.savefig(fig)
    plt.close(fig)


def style_table(table, header_color=NAVY, header_text_color="white", body_fontsize=8.5, yscale=1.3):
    table.auto_set_font_size(False)
    table.set_fontsize(body_fontsize)
    table.scale(1, yscale)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(MID)
        cell.set_linewidth(0.6)
        if row == 0:
            cell.set_facecolor(header_color)
            cell.get_text().set_color(header_text_color)
            cell.get_text().set_fontweight("bold")
        else:
            cell.set_facecolor("white" if row % 2 else LIGHT)


def draw_portfolio_page(pdf: PdfPages, portfolio: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(11.69, 8.27), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    ax.text(0.05, 0.95, "2. Portfolio Overview Table", fontsize=20, fontweight="bold", color=NAVY, va="top")
    ax.text(0.05, 0.918, "Bold rows indicate the top 5 riskiest names based on combined internal weakness and current market pricing.", fontsize=10, color=SLATE, va="top")

    table_ax = fig.add_axes([0.04, 0.08, 0.92, 0.80])
    table_ax.axis("off")
    col_widths = [0.28, 0.12, 0.13, 0.12, 0.10, 0.10]
    table = table_ax.table(
        cellText=portfolio.values.tolist(),
        colLabels=portfolio.columns.tolist(),
        cellLoc="left",
        colLoc="left",
        colWidths=col_widths,
        bbox=[0, 0, 1, 1],
    )
    style_table(table, body_fontsize=8.3, yscale=1.25)

    for i, entity in enumerate(portfolio["Entity Name"], start=1):
        if entity in TOP5_RISKS:
            for col in range(len(portfolio.columns)):
                cell = table[(i, col)]
                cell.set_facecolor(TOP5_FILL)
                cell.get_text().set_fontweight("bold")
        if portfolio.iloc[i - 1]["Watchlist"] == "Yes" and entity not in TOP5_RISKS:
            table[(i, 5)].get_text().set_color(ACCENT)
            table[(i, 5)].get_text().set_fontweight("bold")

    add_footer(fig, 2)
    pdf.savefig(fig)
    plt.close(fig)


def draw_watchlist_page(pdf: PdfPages, watchlist: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(11.69, 8.27), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    ax.text(0.05, 0.95, "3. Watchlist Section", fontsize=20, fontweight="bold", color=NAVY, va="top")
    ax.text(0.05, 0.918, "Action status is recommendation-driven: one Escalate case and the remainder on Review pending further market confirmation.", fontsize=10, color=SLATE, va="top")

    wrapped = watchlist.copy()
    wrapped["Reason for Inclusion"] = wrapped["Reason for Inclusion"].map(lambda x: wrap_cell(x, 44))
    wrapped["Latest Market Signal"] = wrapped["Latest Market Signal"].map(lambda x: wrap_cell(x, 24))

    table_ax = fig.add_axes([0.03, 0.07, 0.94, 0.81])
    table_ax.axis("off")
    col_widths = [0.15, 0.46, 0.23, 0.12]
    table = table_ax.table(
        cellText=wrapped.values.tolist(),
        colLabels=wrapped.columns.tolist(),
        cellLoc="left",
        colLoc="left",
        colWidths=col_widths,
        bbox=[0, 0, 1, 1],
    )
    style_table(table, body_fontsize=7.8, yscale=1.85)

    for i, recommendation in enumerate(wrapped["Recommendation"], start=1):
        if recommendation == "Escalate":
            for col in range(len(wrapped.columns)):
                cell = table[(i, col)]
                cell.set_facecolor(ESCALATE_FILL)
                cell.get_text().set_fontweight("bold")
            table[(i, 3)].get_text().set_color(ACCENT)
        else:
            table[(i, 3)].get_text().set_color(NAVY)
            table[(i, 3)].get_text().set_fontweight("bold")

    add_footer(fig, 3)
    pdf.savefig(fig)
    plt.close(fig)


def draw_note_page(pdf: PdfPages, title: str, overview: str, strengths, weaknesses, market_signals, rating_outlook: str, analyst_view: str, page_number: int) -> None:
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    ax.text(0.06, 0.95, title, fontsize=20, fontweight="bold", color=NAVY, va="top")

    add_box(ax, (0.06, 0.79), 0.88, 0.10, title="Overview", facecolor=LIGHT)
    add_wrapped_block(ax, 0.09, 0.84, overview, width=94, fontsize=11, line_gap=0.032)

    add_box(ax, (0.06, 0.55), 0.40, 0.20, title="Strengths")
    y = 0.70
    for item in strengths:
        y = add_wrapped_block(ax, 0.09, y, item, width=40, fontsize=10.5, line_gap=0.03, bullet=True) - 0.012

    add_box(ax, (0.54, 0.55), 0.40, 0.20, title="Weaknesses")
    y = 0.70
    for item in weaknesses:
        y = add_wrapped_block(ax, 0.57, y, item, width=40, fontsize=10.5, line_gap=0.03, bullet=True) - 0.012

    add_box(ax, (0.06, 0.35), 0.40, 0.14, title="Market Signals", facecolor=LIGHT)
    y = 0.455
    for item in market_signals:
        y = add_wrapped_block(ax, 0.09, y, item, width=42, fontsize=10.5, line_gap=0.03, bullet=True) - 0.01

    add_box(ax, (0.54, 0.35), 0.40, 0.14, title="Internal Rating + Outlook", facecolor=LIGHT)
    ax.text(0.57, 0.42, rating_outlook, transform=ax.transAxes, fontsize=18, fontweight="bold", color=NAVY, va="center")

    add_box(ax, (0.06, 0.12), 0.88, 0.17, title="Analyst View")
    add_wrapped_block(ax, 0.09, 0.245, analyst_view, width=96, fontsize=11, line_gap=0.032)

    add_footer(fig, page_number)
    pdf.savefig(fig)
    plt.close(fig)


def draw_final_page(pdf: PdfPages, stats, page_number: int) -> None:
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    ax.text(0.06, 0.95, "4.2 Sovereign Note: Turkey", fontsize=20, fontweight="bold", color=NAVY, va="top")

    add_box(ax, (0.06, 0.69), 0.88, 0.21, title="Detailed Credit Note")
    y = 0.845
    paragraphs = [
        "Overview: Turkey remains the highest-risk sovereign in the perimeter on a market-implied basis, with a 46.92 internal score and a B implied internal rating.",
        "Strengths: Debt/GDP of 31% is low relative to peers, while GDP growth of 2.9% and FX reserves of 4.2 months of imports provide a limited near-term cushion.",
        "Weaknesses: Inflation at 48.0% is the dominant constraint, while a fiscal deficit of -5.2% of GDP, a current account deficit of -3.5% of GDP, and a political risk score of 7.0 leave little tolerance for renewed market dislocation.",
        "Market signals: CDS 473bp, bond spread 402bp, equity +1.5% over 5 days, and 30-day equity volatility of 53.5%.",
        "Internal rating + outlook: B / Deteriorating.",
        "Analyst view: Maintain heightened review. Low public debt is not enough to offset inflation, external imbalance, and political risk; collateral and sovereign exposure assumptions should remain conservative while spreads stay above 400bp.",
    ]
    for paragraph in paragraphs:
        y = add_wrapped_block(ax, 0.09, y, paragraph, width=98, fontsize=10.5, line_gap=0.028) - 0.012

    add_box(ax, (0.06, 0.36), 0.88, 0.27, title="5. Market Monitoring Insights", facecolor=LIGHT)
    y = 0.58
    insights = [
        f"CDS trends: Portfolio average CDS widened from {stats['first_avg_cds']:.0f}bp on {stats['first_date_str']} to {stats['last_avg_cds']:.0f}bp on {stats['last_date_str']}. Turkey and Monte dei Paschi remained persistent top-three daily risk movers, with Brazil joining that cluster on most sessions.",
        f"Bond spread movements: Average spreads widened from {stats['first_avg_spread']:.0f}bp to {stats['last_avg_spread']:.0f}bp, but by year-end the desk showed only {stats['last_spread_alerts']} active spread alert, indicating pressure was concentrated rather than systemic.",
        "Equity volatility: Watchlist names still show visibly higher volatility than non-watchlist names, with active volatility alerts in Turkey, Monte dei Paschi, and Commerzbank.",
        f"Correlation / stress signal: CDS and bond spreads remain tightly linked ({stats['correlation_cds_spread']:.2f}), and both are positively correlated with equity volatility ({stats['correlation_cds_vol']:.2f}-{stats['correlation_spread_vol']:.2f}), indicating that current stress is being expressed primarily through credit markets rather than through equity returns alone.",
        f"Relative market pricing: Watchlist names trade at {stats['watch_avg_cds']:.0f}bp average CDS and {stats['watch_avg_spread']:.0f}bp average bond spread, versus {stats['nonwatch_avg_cds']:.0f}bp and {stats['nonwatch_avg_spread']:.0f}bp for non-watchlist names.",
    ]
    for insight in insights:
        y = add_wrapped_block(ax, 0.09, y, insight, width=96, fontsize=10, line_gap=0.026, bullet=True) - 0.01

    add_box(ax, (0.06, 0.12), 0.88, 0.18, title="6. Methodology")
    y = 0.255
    methodology = [
        "Internal scores combine financial metrics for banks and macro-fiscal indicators for sovereigns into a single 0-100 assessment, then map the result to an implied rating from AA to CCC.",
        "Bank scoring emphasizes capital, asset quality, profitability, leverage, funding, efficiency, and liquidity.",
        "Sovereign scoring emphasizes debt burden, fiscal balance, inflation, reserves, growth, political risk, and external balance.",
        "Market alerts are triggered by sharp 5-day CDS widening, bond spread widening, negative equity moves, or elevated equity volatility.",
        "Watchlist recommendations reconcile the internal model with current market pricing and focus attention on names where both signals point in the same adverse direction.",
    ]
    for item in methodology:
        y = add_wrapped_block(ax, 0.09, y, item, width=96, fontsize=10, line_gap=0.026, bullet=True) - 0.008

    add_footer(fig, page_number)
    pdf.savefig(fig)
    plt.close(fig)


def main():
    ratings, watch, market_summary, banks, sovereigns, market = load_data()
    _ = banks, sovereigns
    stats = build_stats(ratings, watch, market_summary, market)
    portfolio = prepare_portfolio_table(ratings)
    watchlist = prepare_watchlist_table(watch)

    with PdfPages(OUTPUT_PDF) as pdf:
        draw_title_page(pdf, stats)
        draw_portfolio_page(pdf, portfolio)
        draw_watchlist_page(pdf, watchlist)
        draw_note_page(
            pdf,
            title="4.1 Bank Note: Monte dei Paschi",
            overview="Monte dei Paschi is the weakest bank in the monitored book on the current snapshot, with a 36.84 internal score and a CCC implied internal rating.",
            strengths=[
                "CET1 ratio of 18.3% provides a meaningful capital buffer relative to peers.",
                "A loan/deposit ratio of 0.95x indicates funding is not the primary near-term pressure point.",
            ],
            weaknesses=[
                "NPL ratio of 12.4% remains the key structural credit weakness and is materially above peer levels.",
                "ROE of -2.5% and a cost/income ratio of 88.4% point to weak earnings resilience and poor operating efficiency.",
                "The liquidity ratio of 112% is the weakest in the bank sample and leaves limited room for renewed market stress.",
            ],
            market_signals=[
                "CDS 5Y: 306bp",
                "Bond spread: 342bp",
                "Equity: +0.6% over 5 days",
                "30-day equity volatility: 46.1%",
            ],
            rating_outlook="CCC / Deteriorating",
            analyst_view="Escalate. Capital strength is not sufficient to offset weak asset quality, negative earnings, and stressed funding spreads; this name warrants tighter risk appetite and more frequent review.",
            page_number=4,
        )
        draw_final_page(pdf, stats, page_number=5)

    print(f"Generated PDF: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
