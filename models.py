from dataclasses import dataclass, field

@dataclass
class DecisionsMarketing:
    price: float
    budget: float

@dataclass
class DecisionsOperations:
    quality_level: float
    planned_production: float

@dataclass
class DecisionsFinanceHR:
    motivation_actions: int  # 0–3

@dataclass
class CompanyState:
    name: str
    cash: float = 100000
    equity: float = 150000
    long_debt: float = 50000
    short_debt: float = 20000
    fixed_assets: float = 100000
    current_assets: float = 50000
    reputation: float = 0.5
    motivation: float = 0.6
    technology_level: float = 0.3

@dataclass
class Company:
    state: CompanyState
    dec_mkt: DecisionsMarketing | None = None
    dec_ops: DecisionsOperations | None = None
    dec_fin: DecisionsFinanceHR | None = None

    demand_share: float = 0.0
    effective_production: float = 0.0
    sales_units: float = 0.0
    revenue: float = 0.0
    op_result: float = 0.0
    net_result: float = 0.0
    kpis: dict = field(default_factory=dict)
