import random
from collections import defaultdict
from functools import lru_cache
from itertools import chain

from config import ConfigManager
from data.chapter_weights import chapter_probs, chapter_weights
from data.distributions import age_groups_diagnoses, male_diagnoses, maternity_diagnoses, female_diagnoses, age_ranges
from data.icd_groups import icd_groups
from domain.Gender import Gender
from data.atc_data import atc_details
from data.distributions import medical_history_probabilities
from data.icd_codes import icd_codes
from data.icd_atc import icd_atc
from data.icd_diagnoses_antecedents import icd_diagnoses_antecedents
from domain.AdministrationRoute import AdministrationRoute


def get_antecedent_diagnose(rules):
    alpha = 0.4
    beta = 0.6
    threshold = 0.2

    if len(rules) == 1:
        normalizedLift = 1
        score = alpha * rules[0]['support'] + beta * normalizedLift
        if score > threshold:
            return rules[0]
    else:
        all_lifts = [rule['lift'] for rule in rules]

        min_lift, max_lift = min(all_lifts), max(all_lifts)

        for rule in rules:
            rule['normalized_lift'] = (rule['lift'] - min_lift) / (max_lift - min_lift)

        valid_rules = []
        for rule in rules:
            score = alpha * rule['support'] + beta * rule['normalized_lift']
            if score > threshold:
                valid_rules.append(rule)

        if valid_rules:
            return random.choice(valid_rules)['antecedents']
        else:
            return None


@lru_cache(maxsize=128)
def get_filtered_diagnoses(chapter, gender, age_group, maternity):
    relevant_code_groups = [code for code in icd_groups if code.startswith(chapter)]
    relevant_codes = list(chain(*[icd_groups[group] for group in relevant_code_groups]))
    config_filter_icd_groups = ConfigManager.config_filter_icd_groups()

    config_filter_diagnoses = list(code for code in config_filter_icd_groups if code in relevant_codes)
    if age_group == 'newborn':
        filtered_diagnoses = [diag for diag in age_groups_diagnoses['newborn'] if
                              diag[:3] not in config_filter_icd_groups]
    else:
        gender_filtered = {Gender.FEMALE.value: male_diagnoses,
                           Gender.MALE.value: female_diagnoses}
        age_group_filter = set([diagnosis for group in age_groups_diagnoses if group != age_group
                                for diagnosis in age_groups_diagnoses[group]])
        maternity_filtered = set(maternity_diagnoses) if not maternity else {}
        filtered_diagnoses = {diag for diag in relevant_codes if
                              diag not in gender_filtered[gender]
                              and diag not in age_group_filter
                              and diag not in maternity_filtered
                              and diag not in config_filter_diagnoses}

    return tuple(filtered_diagnoses)


def get_diagnosis(gender, age_group, maternity):
    validate_inputs(gender, age_group)

    chapter_choice = choose_chapter(maternity)
    filtered_diagnoses = get_filtered_diagnoses(chapter_choice, gender, age_group, maternity)

    grouped_diagnoses = group_diagnoses_by_prefix(filtered_diagnoses, chapter_choice)
    selected_prefix = choose_prefix(grouped_diagnoses, chapter_choice)

    selected_diagnosis = select_diagnosis_from_group(grouped_diagnoses[selected_prefix], filtered_diagnoses)
    return format_diagnosis(selected_diagnosis)


def validate_inputs(gender, age_group):
    if gender not in [Gender.FEMALE.value, Gender.MALE.value]:
        raise ValueError(f"Invalid gender: {gender}")
    if age_group not in age_ranges:
        raise ValueError(f"Invalid age group: {age_group}")


def choose_chapter(maternity):
    excluded_choices = ["O"] if not maternity else []
    filtered_keys = [key for key in chapter_probs.keys() if key not in excluded_choices]
    filtered_weights = [chapter_probs[key] for key in filtered_keys]

    return random.choices(list(filtered_keys), weights=list(filtered_weights), k=1)[0]


def group_diagnoses_by_prefix(diagnoses, chapter):
    grouped = defaultdict(list)
    for diagnosis in diagnoses:
        for length in [5, 4, 3]:
            prefix = diagnosis[:length]
            if prefix in chapter_weights[chapter]:
                break
        if prefix in grouped:
            grouped[prefix].append(diagnosis)
        else:
            grouped[prefix] = [diagnosis]
    return grouped


def choose_prefix(grouped_diagnoses, chapter_choice):
    weights = chapter_weights[chapter_choice]
    prefix_weights = [weights.get(prefix, 0.1) for prefix in grouped_diagnoses.keys()]
    return random.choices(list(grouped_diagnoses.keys()), weights=prefix_weights, k=1)[0]


def select_diagnosis_from_group(diagnoses, filtered_diagnoses):
    return random.choice([d for d in diagnoses if d in filtered_diagnoses])


def format_diagnosis(diagnosis):
    return (
        diagnosis,
        icd_codes[diagnosis]['name'],
        icd_codes[diagnosis]['description']
    )


def get_medication_atc(diagnosis):
    result = []
    while '.' in diagnosis:
        if diagnosis in icd_atc.keys():
            result = icd_atc[diagnosis]
            break
        diagnosis = diagnosis[:-1]

    if not result and diagnosis in icd_atc.keys():
        result = icd_atc[diagnosis]

    medication = random.choice(result) if result else None
    return medication


def get_atc_data(atc_code):
    atc_data_list = atc_details.get(atc_code, None)

    if atc_data_list:
        atc_data = random.choice(atc_data_list)
        medication_details = {'ATC': atc_code}
        dosage = atc_data.get('DDD', None)
        unit = atc_data.get('unit', None)
        if dosage and unit:
            medication_details['dosage'] = f"{dosage} {unit} per day"

        route = atc_data.get('route', None)
        if route:
            try:
                route_name = AdministrationRoute.get_name(route)
                route_description = AdministrationRoute.get_description(route)
                medication_details['route'] = {
                    'name': route_name,
                    'description': route_description
                }
            except KeyError:
                medication_details['route'] = {'name': route, 'description': "Description not available"}

        name = atc_data.get('name', None)
        if name:
            medication_details['name'] = name

        return medication_details
    return None


def get_medical_history(diagnosis, age_group):
    probability = medical_history_probabilities.get(age_group, 0)
    if not random.random() < probability:
        return None
    diagnosis = diagnosis[:3]
    if diagnosis in icd_diagnoses_antecedents.keys():
        diagnosis_antecedents = get_antecedent_diagnose(icd_diagnoses_antecedents[diagnosis])
    else:
        diagnosis_antecedents = None

    if diagnosis_antecedents:
        diagnoses = []
        for code in diagnosis_antecedents:
            matching_keys = {k: v for k, v in icd_codes.items() if k.startswith(code)}
            if matching_keys:
                key = random.choice(list(matching_keys.keys()))
                diagnosis = {"ICD": key,
                             "name": icd_codes[key]['name'],
                             'description': icd_codes[key]['description']}
                diagnoses.append(diagnosis)
        return diagnoses
