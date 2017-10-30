# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import SimpleBudgetLoader
from decimal import *
import csv
import os
import re

class ElPratBudgetLoader(SimpleBudgetLoader):

    def parse_item(self, filename, line):
        # Since the application expects a code-programme mapping to be constant over time, we are forced
        # to amend budget data when programme codes change:

        # There are some programmes in the 2012 budget that get splited afterwards reusing the same code
        programme_mapping_2012 = {
        # original programme: placeholer programme
            '3424':'342X',  # CEM Julio Méndez y CEM Fondo de En Peixo
        }

        # Programme codes change in 2015 due to new laws
        # See https://github.com/dcabo/presupuestos-aragon/wiki/La-clasificaci%C3%B3n-funcional-en-las-Entidades-Locales
        programme_mapping_pre_2015 = {
        # old programme: new programme
            '1340':'1350',  # Protección civil -> Protección civil
            '1550':'1530',  # Vías públicas -> Vías públicas
            '1551':'1530',  # Parque móvil urbanismo-brigada -> Vías públicas
            '2311':'2312',  # Residencia de ancianos -> Residencia de ancianos
            '3130':'3110',  # Acciones públicas relativas a la salud -> Protección de la salubridad pública
            '3131':'3111',  # Promoción de la salud -> Promoción de la salud
            '3132':'3112',  # Protección de la salud -> Protección de la salud
            '3133':'3120',  # Servicios asistencia sanitaria -> Hospitales, servicios asistenciales y centros de salud
            '3201':'3200',  # Dirección educación -> Administración general de educación
            '3203':'3201',  # Planificación y seguimiento otras enseñanzas -> Planificación y seguimiento otras enseñanzas
            '3210':'3230',  # Educación preescolar y primaria -> Funcionamiento de centros docentes de enseñanza preescolar y primaria y educación especial
            '3211':'3231',  # Guarderías -> Guarderías
            '3212':'3232',  # Conservación, mantenimiento y vigilancia escuelas -> Conservación, mantenimiento y vigilancia escuelas
            '3230':'3240',  # Promoción educativa -> Funcionamiento de centros docentes de enseñanza secundaria
            '3240':'3260',  # Servicios complementarios de educación -> Servicios complementarios de educación
        }

        # There are some programmes in the 2015 budget that change in 2016 and afterwars, as part of the 2015 new laws
        programme_mapping_2015 = {
        # original programme: placeholer programme
            '2314':'2315',  # Plan Actuación San Cosme -> Plan actuación San Cosme
            '2315':'2317',  # Ciudadanía e Inmigración -> Igualdad y solidaridad
            '2317':'2314',  # Colectivos con necesidades especiales -> Colectivos con necesidades especiales
            '3111':'3112',  # Promoción de la salud -> Promoción de la salud
            '3112':'3113',  # Protección de la salud -> Protección de la salud
            '3400':'3401',  # Administración general de deportes -> Administración general de deportes
            '9201':'9205',  # Contratación y Patrimonio -> Contratación y Patrimonio
            '9202':'9206',  # Recursos Humanos -> Recursos Humanos
            '9203':'9208',  # Organización -> Organización
            '9204':'9207',  # Sistemas y Tecnologías de la Información y la Comunicación -> Sistemas y Tecnologías de la Información y la Comunicación
        }

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

            # For years previous to 2016 we check whether we need to amend the programme code
            year = re.search('municipio/(\d+)/', filename).group(1)

            if int(year) == 2012:
                fc_code = programme_mapping_2012.get(fc_code, fc_code)

            if int(year) < 2015:
                fc_code = programme_mapping_pre_2015.get(fc_code, fc_code)

            if int(year) == 2015:
                fc_code = programme_mapping_2015.get(fc_code, fc_code)

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
