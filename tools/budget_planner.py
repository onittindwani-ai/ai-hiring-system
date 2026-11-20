"""Budget planner: what a hire really costs and which way of hiring fits your budget.

Usage:
    python3 tools/budget_planner.py --base-pay 60000 --hires 2
    python3 tools/budget_planner.py --base-pay 60000 --hires 2 --budget 4000 --currency EUR
    python3 tools/budget_planner.py --base-pay 60000 --hires 1 --recruiter-fee-pct 18 --board-spend 300
        --tool-spend 100 --hours-per-hire 30 --hourly-value 40 --employer-cost-pct 20 --json

What it does:
    Works out the fully loaded yearly cost of one employee (base pay plus employer cost), then the
    cost of FINDING and HIRING per hire for five paths: do it yourself with this system, job boards
    plus this system, a recruiter, a contractor, and AI plus a part time person. It says whether your
    hiring budget covers each path and gives a plain recommendation by budget tier (none, small,
    medium, large) using a ratio to one month of base pay. Every assumption is printed. The default
    numbers are STARTING ASSUMPTIONS for planning, not market facts: use your own quotes and rates.
    --budget means money you can spend on FINDING people (boards, tools, a recruiter fee), not salaries.
"""
import argparse
import json
import sys

# STARTING ASSUMPTIONS: planning numbers only, replace with your own data.
DEFAULTS = {
    "employer_cost_pct": 25.0,
    "recruiter_fee_pct": 20.0,
    "hours_per_hire": 25.0,
    "contractor_premium_pct": 30.0,
    "contractor_hours_per_year": 1800.0,
    "own_time_share_recruiter": 0.25,
    "own_time_share_contractor": 0.40,
    "own_time_share_ai_parttimer": 0.60,
    "ai_tool_cost_pct_of_base": 3.0,
    "parttimer_share_of_hours": 0.5,
}
# Tier thresholds: budget per hire compared with one month of base pay (planning ratios).
TIER_RATIOS = [("none", 0.05), ("small", 0.25), ("medium", 1.0)]

TIER_ADVICE = {
    "none": "Do it yourself with this system. Use referrals, free postings (check what each board charges), "
            "communities and public web search. It costs your time, not cash.",
    "small": "Do it yourself with this system and pay for one thing that saves the most time: one paid posting "
             "on the board where your role's people look, or one tool.",
    "medium": "Boards plus this system, and consider paying a part time person for admin (scheduling, "
              "first replies). A recruiter fee is likely still above your budget.",
    "large": "You can afford a recruiter for the hard to fill hire. Compare the recruiter quote with the "
             "boards plus system path, and keep this system for screening and the pipeline either way.",
}


def money(value, currency):
    return "%s %s" % (currency, format(round(value), ","))


def tier_for_budget(budget_per_hire, base_pay):
    month = base_pay / 12.0
    ratio = budget_per_hire / month if month else 0.0
    for name, limit in TIER_RATIOS:
        if ratio < limit:
            return name, ratio
    return "large", ratio


def path_costs(base_pay, hires, cfg):
    """Cost to find and hire ONE person on each path (not salary)."""
    own_hour = cfg["hourly_value"]
    own = cfg["hours_per_hire"] * own_hour
    tools = cfg["tool_spend"] / hires
    boards = cfg["board_spend"] / hires
    hourly_equivalent = base_pay * (1 + cfg["contractor_premium_pct"] / 100.0) / cfg["contractor_hours_per_year"]
    return {
        "self_with_system": {"cost": own + tools,
                             "what": "your own time (%g hours) plus tools" % cfg["hours_per_hire"]},
        "boards_plus_system": {"cost": own + tools + boards,
                               "what": "your own time, tools and paid job board spend"},
        "recruiter": {"cost": base_pay * cfg["recruiter_fee_pct"] / 100.0 + own * cfg["own_time_share_recruiter"],
                      "what": "fee of %g%% of first year base pay plus a quarter of your time" % cfg["recruiter_fee_pct"]},
        "contractor": {"cost": own * cfg["own_time_share_contractor"] + tools,
                       "what": "less hiring effort, but about %.2f per hour equivalent instead of employee pay"
                               % hourly_equivalent,
                       "hourly_equivalent": round(hourly_equivalent, 2)},
        "ai_plus_part_timer": {"cost": own * cfg["own_time_share_ai_parttimer"] + tools
                               + base_pay * cfg["ai_tool_cost_pct_of_base"] / 100.0,
                               "what": "AI does the drafting and sorting, a part timer covers %g%% of the hours"
                                       % (100 * cfg["parttimer_share_of_hours"])},
    }


def build(base_pay, hires, cfg):
    loaded = base_pay * (1 + cfg["employer_cost_pct"] / 100.0)
    paths = path_costs(base_pay, hires, cfg)
    for name, info in paths.items():
        info["total_for_all_hires"] = info["cost"] * hires
        info["covered_by_budget"] = (None if cfg["budget"] is None else info["total_for_all_hires"] <= cfg["budget"])
    result = {"base_pay": base_pay, "hires": hires, "loaded_yearly_cost_per_employee": loaded,
              "loaded_yearly_cost_all_hires": loaded * hires, "paths": paths, "assumptions": cfg}
    if cfg["budget"] is not None:
        tier, ratio = tier_for_budget(cfg["budget"] / hires, base_pay)
        result.update({"tier": tier, "budget_per_hire": cfg["budget"] / hires, "ratio_to_one_month_pay": ratio,
                       "recommendation": TIER_ADVICE[tier]})
    return result


def format_text(result, currency):
    cfg = result["assumptions"]
    lines = ["HIRING BUDGET PLAN (%d hire%s)" % (result["hires"], "" if result["hires"] == 1 else "s"), "",
             "Fully loaded yearly cost of one employee: %s" % money(result["loaded_yearly_cost_per_employee"], currency),
             "  = base pay %s plus %g%% employer cost (taxes, benefits, equipment; varies by country)."
             % (money(result["base_pay"], currency), cfg["employer_cost_pct"]),
             "Fully loaded yearly cost for all hires: %s" % money(result["loaded_yearly_cost_all_hires"], currency),
             "", "Cost to FIND and HIRE one person, by path (this is not salary):"]
    for name, info in result["paths"].items():
        covered = ""
        if info["covered_by_budget"] is not None:
            covered = "  [covered by your budget]" if info["covered_by_budget"] else "  [over your budget]"
        lines.append("  %-20s %-14s %s%s" % (name, money(info["cost"], currency), info["what"], covered))
    comparable = [n for n in result["paths"] if n != "contractor"]
    cheapest = min(comparable, key=lambda n: result["paths"][n]["cost"])
    lines.append("Cheapest way to find an employee: %s. Cheapest is not always best: a hard role may need a recruiter. "
                 "The contractor path hides its cost in the hourly rate, so compare it by that rate, not by this number." % cheapest)
    if "tier" in result:
        lines += ["", "Your hiring budget: %s in total, %s per hire, which is %.2f of one month of base pay."
                  % (money(cfg["budget"], currency), money(result["budget_per_hire"], currency),
                     result["ratio_to_one_month_pay"]),
                  "Budget tier: %s" % result["tier"].upper(), "Recommendation: " + result["recommendation"]]
    else:
        lines += ["", "No --budget given, so no tier. Add --budget <money you can spend on finding people>."]
    lines += ["", "ASSUMPTIONS (starting assumptions, replace with your own quotes and rates):"]
    for key, value in cfg.items():
        if value is not None:
            lines.append("  %-28s %g" % (key, value))
    lines += ["  tier ratios (budget per hire / one month base pay): under 0.05 none, under 0.25 small, under 1.0 medium, else large",
              "", "Not financial advice. Costs of employing people differ a lot by country: check with an accountant."]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Hiring budget planner")
    parser.add_argument("--base-pay", type=float, required=True, help="yearly base pay of one hire")
    parser.add_argument("--hires", type=int, required=True)
    parser.add_argument("--currency", default="USD")
    parser.add_argument("--budget", type=float, help="total money you can spend on finding people")
    parser.add_argument("--board-spend", type=float, default=0.0, help="total spend on paid job boards")
    parser.add_argument("--tool-spend", type=float, default=0.0, help="total spend on tools")
    parser.add_argument("--hourly-value", type=float, help="what one hour of your time is worth (default: base pay / 2000)")
    for key, value in DEFAULTS.items():
        if key in ("employer_cost_pct", "recruiter_fee_pct", "hours_per_hire"):
            parser.add_argument("--" + key.replace("_", "-"), type=float, default=value)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.base_pay <= 0 or args.hires < 1:
        print("--base-pay must be above 0 and --hires must be 1 or more.")
        return 1
    if min(args.board_spend, args.tool_spend, args.employer_cost_pct, args.recruiter_fee_pct, args.hours_per_hire) < 0:
        print("Money, percent and hour values cannot be negative.")
        return 1
    cfg = dict(DEFAULTS)
    cfg.update({"employer_cost_pct": args.employer_cost_pct, "recruiter_fee_pct": args.recruiter_fee_pct,
                "hours_per_hire": args.hours_per_hire, "board_spend": args.board_spend,
                "tool_spend": args.tool_spend, "budget": args.budget,
                "hourly_value": args.hourly_value if args.hourly_value is not None else round(args.base_pay / 2000.0, 2)})
    result = build(args.base_pay, args.hires, cfg)
    print(json.dumps(result, indent=2) if args.json else format_text(result, args.currency.upper()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
