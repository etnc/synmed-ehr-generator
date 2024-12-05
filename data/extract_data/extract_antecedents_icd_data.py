import csv
from collections import defaultdict
from operator import contains

from data.icd_diagnoses_antecedents import icd_diagnoses_antecedents


def extract_antecedents_icd_data():
    with open("../raw_data/diagnoses_relation.csv", "r", encoding="utf-8", errors='replace') as file:
        antecedents_data = extract_icd_codes(file)

    with open("../icd_diagnoses_antecedents.py", "w", encoding="utf-8") as py_file:
        py_file.write("icd_diagnoses_antecedents = {\n")
        for code, codes in antecedents_data.items():
            py_file.write(f"    \"{code}\": {codes},\n")
        py_file.write("}\n")


def filter_antecedents_data():
    all_lifts = []
    all_supports = []
    for diagnoses in icd_diagnoses_antecedents.values():
        for rule in diagnoses:
            all_lifts.append(rule['lift'])
            all_supports.append(rule['support'])

    min_lift = min(all_lifts)
    max_lift = max(all_lifts)

    def normalize_lift(lift):
        return (lift - min_lift) / (max_lift - min_lift)

    alpha = 0.4  # Weight for support
    beta = 0.6  # Weight for normalized lift
    threshold = 0.2

    filtered_rules = []

    def filter_rules(rules):
        for r in rules:
            normalized_lift = normalize_lift(r['lift'])
            score = (alpha * r['support']) + (beta * normalized_lift)
            if score > threshold:
                filtered_rules.append(r)
        return filtered_rules

    for icd_code, antecedents_list in icd_diagnoses_antecedents.items():
        icd_diagnoses_antecedents[icd_code] = filter_rules(antecedents_list)

    with open("../previous_data/icd_diagnoses_antecedents_filtered.py", "w", encoding="utf-8") as py_file:
        py_file.write("icd_diagnoses_antecedents_filtered = {\n")
        for code, codes in icd_diagnoses_antecedents.items():
            py_file.write(f"    \"{code}\": {codes},\n")
        py_file.write("}\n")


def extract_icd_codes(file):
    icd_antecedents = defaultdict(list)
    reader = csv.DictReader(file)

    for row in reader:
        data = {}
        association_rules = row.get('Association rules (ICD-10 codes)')
        if not association_rules:
            continue
        consequent, antecedents = parse_association_rule(association_rules)
        if not consequent:
            continue

        if not isinstance(antecedents, list):
            antecedents = [antecedents]
        data = {
            'antecedents': antecedents,
            'support': round(float(row.get('Support').replace('%', '')) / 100, 3) if row.get('Support') else None,
            'lift': float(row.get('Lift')) if row.get('Lift') else None,
            'confidence': round(float(row.get('Confidence').replace('%', '')) / 100, 2) if row.get(
                'Confidence') else None,
        }

        icd_antecedents[consequent].append(data)

    return icd_antecedents


def parse_association_rule(association_rule):
    if contains(association_rule, '->'):
        antecedents = association_rule.split("->")[0]
        consequents = association_rule.split("->")[1]
    elif contains(association_rule, '- >'):
        antecedents = association_rule.split("- >")[0]
        consequents = association_rule.split("- >")[1]
    else:
        return None, None
    if contains(antecedents, ','):
        codes = [code.strip() for code in antecedents.split(",")]
    else:
        codes = [antecedents.strip()]

    return consequents.strip(), codes


# filter_antecedents_data()
