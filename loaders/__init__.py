import six

if six.PY2:
    from el_prat_budget_loader import ElPratBudgetLoader
else:
    from .el_prat_budget_loader import ElPratBudgetLoader
