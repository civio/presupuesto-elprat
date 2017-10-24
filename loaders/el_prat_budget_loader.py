# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import SimpleBudgetLoader
from decimal import *
import csv
import os
import re

class ElPratBudgetLoader(SimpleBudgetLoader):

    def parse_item(self, filename, line):
        # Institutional code (all income go to the root node, and all expenses come from the root node too)
        ic_code = '000'

        # Type of data
        is_expense = (filename.find('gastos.csv')!=-1)
        is_actual = (filename.find('/ejecucion_')!=-1)

        # Expenses
        if is_expense:
            # Functional code
            # We got 3- or 4- digit functional codes as input, sso we normalize them at 4- and add trailing zeroes when required
            fc_code = line[2].strip().ljust(4, '0')[:4]

            # Economic code
            # We got 3-, 4-, 5- or 6- digit economic codes as input, so we normalize them at 5- and add trailing zeroes when required
            full_ec_code = line[3].strip().ljust(5, '0')[:5]

            ec_code = full_ec_code[:3]

            # Item numbers are the last two digits from the economic codes (fourth and fifth digit)
            item_number = full_ec_code[-2:]

            # Description
            description = line[4].strip()

            # Parse amount
            amount = line[11 if is_actual else 8].strip()
            amount = self._parse_amount(amount)

            return {
                'is_expense': True,
                'is_actual': is_actual,
                'fc_code': fc_code,
                'ec_code': ec_code,
                'ic_code': ic_code,
                'item_number': item_number,
                'description': description,
                'amount': amount
            }

        # Income
        else:
            # Economic code
            # We got 3-, 4-, 5- or 6- digit economic codes as input, so we normalize them at 5- and add trailing zeroes when required
            full_ec_code = line[2].strip().ljust(5, '0')[:5]

            # On economic codes we get the first three digits
            ec_code = full_ec_code[:3]

            # Item numbers are the last two digits from the economic codes (fourth and fifth digit)
            item_number = full_ec_code[-2:]

            # Description
            description = line[3].strip()

            # Parse amount
            amount = line[7 if is_actual else 4].strip()
            amount = self._parse_amount(amount)

            return {
                'is_expense': False,
                'is_actual': is_actual,
                'ec_code': ec_code,
                'ic_code': ic_code,
                'item_number': item_number,
                'description': description,
                'amount': amount
            }
