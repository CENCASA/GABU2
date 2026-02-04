import random
from typing import List
from models import Company, DecisionsMarketing, DecisionsOperations, DecisionsFinanceHR, CompanyState

TOTAL_DEMAND = 100000
W_PRICE = 0.35
W_QUALITY = 0.30
W_MARKETING = 0.20
W_REPUTATION = 0.15

COST_VAR_BASE = 20
FATIGUE = 0.03
VAR_MOT = 0.10

def create_companies(n: int) -> List[Company]:
    return [Company(state=CompanyState(name=f"Empresa {i}")) for i in range(1, n+1)]

def set_decisions(company: Company, price: float, budget: float,
                  quality: float, production: float, mot_actions: int):
    company.dec_mkt = DecisionsMarketing(price=price, budget=budget)
    company.dec_ops = DecisionsOperations(quality_level=quality, planned_production=production)
    company.dec_fin = DecisionsFinanceHR(motivation_actions=mot_actions)

def attractiveness(c: Company) -> float:
    d = c.dec_mkt
    q = c.dec_ops.quality_level
    rep = c.state.reputation
    return (
        W_PRICE * (1.0 / max(d.price, 0.01)) +
        W_QUALITY * q +
        W_MARKETING * d.budget +
        W_REPUTATION * rep
    )

def allocate_demand(companies: List[Company]):
    scores = [attractiveness(c) for c in companies]
    total_score = sum(scores) or 1.0
    for c, s in zip(companies, scores):
        c.demand_share = TOTAL_DEMAND * (s / total_score)

def update_motivation(c: Company):
    s = c.state
    impact_actions = 0.05 * c.dec_fin.motivation_actions
    noise = (random.random() - 0.5) * VAR_MOT
    s.motivation = max(0.0, min(1.0, s.motivation + impact_actions - FATIGUE + noise))

def simulate_period(companies: List[Company]):
    allocate_demand(companies)

    for c in companies:
        update_motivation(c)
        productivity = 1.0 + 0.01 * (c.state.motivation * 100)

        planned = c.dec_ops.planned_production
        c.effective_production = planned * productivity

        c.sales_units = min(c.demand_share, c.effective_production)
        c.revenue = c.sales_units * c.dec_mkt.price

        quality_cost = 1000 * c.dec_ops.quality_level
        unit_cost = COST_VAR_BASE + (quality_cost / max(c.effective_production, 1))
        prod_cost = unit_cost * c.effective_production
        mkt_cost = c.dec_mkt.budget
        personnel_cost = 50000
        amort = 0.1 * c.state.fixed_assets

        c.op_result = c.revenue - (prod_cost + mkt_cost + personnel_cost + quality_cost + amort)

        interest = c.state.long_debt * 0.05 + c.state.short_debt * 0.12
        c.net_result = c.op_result - interest

        c.state.cash += c.net_result
        c.state.equity += c.net_result

        total_assets = c.state.fixed_assets + c.state.current_assets
        total_debt = c.state.long_debt + c.state.short_debt
        liquidity = c.state.current_assets / max(total_debt, 1)
        solvency = c.state.equity / max(total_assets, 1)

        c.kpis = {
            "liquidity": liquidity,
            "solvency": solvency,
            "margin_net": c.net_result / max(c.revenue, 1),
            "motivation": c.state.motivation,
        }

def normalize(values):
    mn, mx = min(values), max(values)
    if mx == mn:
        return [0.5 for _ in values]
    return [(v - mn) / (mx - mn) for v in values]

def compute_ranking(companies: List[Company]):
    rent = [c.net_result for c in companies]
    solv = [c.kpis["solvency"] for c in companies]
    mot = [c.kpis["motivation"] for c in companies]
    rep = [c.state.reputation for c in companies]
    innov = [c.state.technology_level for c in companies]

    rent_n = normalize(rent)
    solv_n = normalize(solv)
    mot_n = normalize(mot)
    rep_n = normalize(rep)
    innov_n = normalize(innov)

    scores = []
    for i, c in enumerate(companies):
        score = (
            0.3 * rent_n[i] +
            0.25 * solv_n[i] +
            0.2 * innov_n[i] +
            0.15 * mot_n[i] +
            0.1 * rep_n[i]
        )
        scores.append((c.state.name, score, c.net_result))

    scores_sorted = sorted(scores, key=lambda x: x[1], reverse=True)
    return scores_sorted
