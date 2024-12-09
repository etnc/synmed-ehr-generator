import xml.etree.ElementTree as ET
import json
from collections import defaultdict

import pandas as pd

import csv


def parse_drugbank_xml(file_path):
    namespaces = {'db': 'http://www.drugbank.ca'}

    drugs_data = {}

    for event, elem in ET.iterparse(file_path, events=('start', 'end')):
        if event == 'end' and elem.tag == '{http://www.drugbank.ca}drug':
            drug_info = {}

            drug_name_elem = elem.find('db:name', namespaces=namespaces)
            if drug_name_elem is None or not drug_name_elem.text:
                continue

            drug_info['name'] = drug_name_elem.text

            dosages = []
            forms_set = set()
            for dosage in elem.findall('./db:dosages/db:dosage', namespaces=namespaces):
                form_elem = dosage.find('db:form', namespaces=namespaces)
                form = form_elem.text if form_elem is not None and form_elem.text else None  # None if missing

                if form is not None and form not in forms_set:
                    strength_elem = dosage.find('db:strength', namespaces=namespaces)
                    if strength_elem is not None and strength_elem.text:
                        dosage_info = {
                            'form': form,
                            'strength': strength_elem.text
                        }
                        dosages.append(dosage_info)
                        forms_set.add(form)

                if len(dosages) >= 3:
                    break

            if dosages:
                drug_info['dosages'] = dosages

            indication_elem = elem.find('db:indication', namespaces=namespaces)
            if indication_elem is not None and indication_elem.text:
                drug_info['indication'] = indication_elem.text

            drugs_data[drug_info['name']] = drug_info

            elem.clear()

    with open('../previous_data/drug_data.py', 'w') as file:
        file.write("drug_data = ")
        json.dump(drugs_data, file, indent=4)

def icd_atc_codes():
    input_file = 'atc_icd_pairs.csv'
    output_file = '../icd_atc.py'

    icd_to_atc = {}

    with open(input_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            icd_code = row.get('code_x')  # ICD code
            atc_code = row.get('code_y')  # ATC code

            if icd_code:
                if icd_code in icd_to_atc:
                    if atc_code and atc_code not in icd_to_atc[icd_code]:
                        icd_to_atc[icd_code].append(atc_code)
                else:
                    icd_to_atc[icd_code] = [atc_code] if atc_code else []

    with open(output_file, 'w', encoding='utf-8') as output:
        output.write("icd_to_atc = {\n")

        for icd_code, atc_codes in icd_to_atc.items():
            output.write(f'    "{icd_code}": {json.dumps(atc_codes)},\n')

        output.write("}\n")


def atc_medication_data():
    file_path = '../raw_data/atc_l5.csv'
    try:
        data = pd.read_csv(file_path)
    except Exception as e:
        raise RuntimeError(f"Error reading csv file: {e}")

    atc_data = defaultdict(list)
    rows = data.dropna(subset=['ATC code']).to_dict('records')
    for row in rows:
        atc_code = row.get('ATC code')
        atc_details = {k: v for k, v in {
            'name': row.get('Name'),
            'DDD': row.get('DDD'),
            'unit': row.get('U'),
            'route': row.get('Adm.R', '').upper().replace('.', '_') if pd.notna(row.get('Adm.R')) else None,
            'note': row.get('Note'),
        }.items() if pd.notna(v)}
        if 'name' not in atc_details:
            existing_entry = atc_data[atc_code][0] if atc_data[atc_code] else {}
            atc_details['name'] = existing_entry.get('name')
        atc_data[atc_code].append(atc_details)

    output_file = '../atc_data.py'
    try:
        with open(output_file, 'w') as py_file:
            py_file.write("atc_details = {\n")
            for atc_code, details_list in atc_data.items():
                py_file.write(f"    \"{atc_code}\": {details_list},\n")
            py_file.write("}\n")
        print(f"Data successfully saved to {output_file}")
    except Exception as e:
        raise RuntimeError(f"Error writing to Python file: {e}")


# atc_medication_data()
