from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

def get_company_cost_shares(trucks, total_cost):
    total_load = sum(t.assigned_load for t in trucks)
    company_loads = defaultdict(int)

    for truck in trucks:
        company_loads[truck.company.name] += truck.assigned_load

    company_costs = {}
    for company, load in company_loads.items():
        if total_load > 0:
            share = (Decimal(load) / Decimal(total_load)) * Decimal(total_cost)
            company_costs[company] = {
                "assigned_load": load,
                "cost_share": str(share.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            }
        else:
            company_costs[company] = {
                "assigned_load": load,
                "cost_share": "0.00"
            }
    return company_costs
