import random

import pandas as pd
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import time
from data.icd_groups import icd_groups
from data.previous_data.drug_data import drug_data
from data.icd_codes import icd_codes
from icd_counts import icd_counts


def extract_icd_codes(input_file, output_file):
    icd_codes = {}
    supplemental_codes_prefixes = ['V', 'Z', 'X', 'W', 'Y']

    with open(input_file, "r") as file:
        for line in file:
            order_number = line[0:5].strip()
            code = line[6:13].strip()
            valid_for_hipaa = line[14].strip()
            short_description = line[16:76].strip()
            long_description = line[77:].strip()

            if any(code.startswith(prefix) for prefix in
                   supplemental_codes_prefixes) or 'other' in short_description.lower():
                continue

            if valid_for_hipaa == "1":
                if len(code) > 3:
                    formatted_code = f"{code[:3]}.{code[3:]}"
                else:
                    formatted_code = code

                icd_codes[formatted_code] = {
                    "name": short_description,
                    "description": long_description
                }

    with open(output_file, "w") as file:
        file.write("icd_codes = {\n")
        for code, descriptions in icd_codes.items():
            file.write(f'    "{code}": {descriptions},\n')
        file.write("}\n")


# input_file_path = 'icd10cm-order-2025.txt'
# output_file_path = 'icd_codes.py'
# extract_icd_codes(input_file_path, output_file_path)


def icd_10_distribution():
    occurrences = [
        149249, 95993, 84824, 55549, 54780, 49343, 26136, 24994, 24714, 19818, 19172, 15438, 15375, 14930, 14751,
        14304, 13998, 13966, 13913, 13240, 12739, 12602, 12344, 10674, 10640, 10471, 10309, 9960, 9782, 9628
    ]

    codes = [
        'I10', 'I63', 'E11', 'I25', 'C34', 'C50', 'J18', 'K29', 'I20', 'N18', 'C16', 'I50', 'I67', 'C78', 'B18', 'C20',
        'J98', 'C22', 'C79', 'K76', 'I48', 'K74', 'C18', 'J44', 'K80', 'C15', 'M32', 'C56', 'I49', 'C92'
    ]

    additional_codes = set(key[:3] for key in icd_codes.keys() if key[:3] not in codes)

    for code in additional_codes:
        # Initialize the occurrence based on a random fraction of the minimum occurrence
        occurrence = min(occurrences) * random.uniform(0.05, 0.1)

        # Find similar codes based on the first 2 or 1 characters
        similar_codes_2 = [existing_code for existing_code in codes if existing_code[:2] == code[:2]]
        similar_codes_1 = [existing_code for existing_code in codes if existing_code[:1] == code[:1]]

        # Apply different percentages based on the similarity
        if similar_codes_2:
            similar_code = similar_codes_2[0]
            additional = random.uniform(0.01, 0.05)  # Small random fraction (1-5%)
        elif similar_codes_1:
            similar_code = similar_codes_1[0]
            additional = random.uniform(0.005, 0.01)  # Even smaller fraction (0.5-1%)
        else:
            similar_code = None
            additional = 0  # No additional percentage if no match

        if similar_code:
            similar_occurrence = occurrences[
                codes.index(similar_code)]  # Corrected: use `similar_code`, not `additional`
            occurrence += similar_occurrence * additional

        occurrences.append(occurrence)
        codes.append(code)

    # Calculate total occurrences and the distribution
    total_occurrences = sum(occurrences)
    icd_10_distribution = {
        icd: round((occurrences[i] / total_occurrences) * 100, 3)
        for i, icd in enumerate(codes)
    }

    # Write to file
    with open("../distributions.py", "a") as file:
        file.write(f"icd_10_distribution = {icd_10_distribution}\n")

    # For debugging
    print(len(occurrences), total_occurrences, icd_10_distribution)


def age_distribution():
    patient_counts = [12222, 2735, 8323, 10040, 22168, 29956, 32506, 20575, 5425, 256, 1]
    age_ranges = ["(0,10]", "(10,20]", "(20,30]", "(30,40]", "(40,50]", "(50,60]",
                  "(60,70]", "(70,80]", "(80,90]", "(90,100]", "(100,110]"]
    total_patients = sum(patient_counts)
    age_distribution = {age_range: round((count / total_patients) * 100, 3) for age_range, count in
                        zip(age_ranges, patient_counts)}

    with open("../distributions.py", "a") as file:
        file.write(f"age_distribution = {age_distribution}\n")


def get_diagnoses(url, num_pages, group):
    diagnoses = []

    for page in tqdm(range(1, num_pages), desc="Scraping pages", unit="page"):
        if page == 1:
            current_url = url
        else:
            current_url = url + f'/{page}'

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        }

        response = requests.get(current_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page} Status code {response.status_code}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        div = soup.find('div', class_="body-content")
        li_elements = div.find_next('ul').find_all('li')
        codes = [li.find('a', class_='identifier') for li in li_elements if li.find('a', class_='identifier')]

        for code in codes:
            diagnoses.append(code.get_text().strip())

        time.sleep(1)

    with open("../distributions.py", "a") as file:
        file.write(f"{group}_diagnoses = " + str(diagnoses))

    print(f"Written {len(diagnoses)} {group} diagnoses to file.")


def get_icd_groups():
    prefix_to_diagnoses = {}
    for diag in icd_codes.keys():
        prefix = diag[:3]
        if prefix not in prefix_to_diagnoses:
            prefix_to_diagnoses[prefix] = []
        prefix_to_diagnoses[prefix].append(diag)

    with open("../icd_groups.py", "w", encoding="utf-8") as py_file:
        py_file.write("icd_groups = {\n")
        for i, (code, codes) in enumerate(prefix_to_diagnoses.items()):
            if i == len(prefix_to_diagnoses) - 1:
                py_file.write(f"    \"{code}\": {codes}\n")
            else:
                py_file.write(f"    \"{code}\": {codes},\n")
        py_file.write("}\n")


# def icd_medication():
#     df = pd.read_csv('../raw_data/icd_diagnoses.csv')
#
#     icd_medications = {}
#
#     def preprocess_medication(medication):
#         if 'Pneumococcal Polysaccharide' in medication:
#             return 'Pneumococcal Polysaccharide Vaccine'
#         return medication.strip()
#
#     df['Active ingredient'] = df['Active ingredient'].apply(lambda x: preprocess_medication(x))
#
#     for index, row in df.iterrows():
#         icds = row['ICD Code'].split(',')
#         medications = row['Active ingredient'].split(',')
#
#         for icd in icds:
#             icd = icd.strip()
#             if icd not in icd_medications:
#                 icd_medications[icd] = []
#
#             for med in medications:
#                 med = med.strip().capitalize()
#                 if med not in icd_medications[icd] and med in drug_data.keys():
#                     icd_medications[icd].append(med)
#
#     with open('../previous_data/icd10_medications.py', 'w', encoding='utf-8') as f:
#         f.write("icd10_medications = {\n")
#         for icd, meds in icd_medications.items():
#             f.write(f"    '{icd}': {meds},\n")
#         f.write("}\n")


# get_diagnoses('https://www.icd10data.com/ICD10CM/Codes/Rules/Male_Diagnosis_Codes', 7,
#               'male')

# get_diagnoses('https://www.icd10data.com/ICD10CM/Codes/Rules/Female_Diagnosis_Codes', 36,
#               'female')
# get_diagnoses('https://www.icd10data.com/ICD10CM/Codes/Rules/Newborn_Codes', 2,
#               'newborn')
# get_diagnoses('https://www.icd10data.com/ICD10CM/Codes/Rules/Pediatric_Codes', 3,
#               'pediatric')
# get_diagnoses('https://www.icd10data.com/ICD10CM/Codes/Rules/Adult_Codes', 10,
#               'adult')

# get_diagnoses("https://www.icd10data.com/ICD10CM/Codes/Rules/Maternity_Codes", 27, "maternity")

# age_distribution()

# icd_medication()

# icd_10_distribution()
#
# get_icd_groups()
# icd_10_distribution()


def icd_distribution():
    frequencies = {
        'I': 443737, 'C': 312425, 'E': 142717, 'K': 118712, 'J': 102677,
        'N': 84206, 'M': 74935, 'D': 47637, 'G': 44870, 'O': 36555,
        'B': 30539, 'R': 27542, 'H': 26172, 'S': 19789, 'Q': 9500,
        'T': 8222, 'F': 8028, 'A': 5975, 'L': 5670, 'P': 1814, 'U': 10
    }
    total_frequency = sum(frequencies.values())
    chapter_probs = {chapter: round(freq / total_frequency, 4) for chapter, freq in frequencies.items()}

    chapter_weights = {}

    for chapter, total_frequency in (frequencies.items()):
        chapter_codes = [code for code in icd_groups if code.startswith(chapter)]
        chapter_codes_occurrences = [code for code in icd_counts.keys() if code.startswith(chapter)]
        print(f"chapter {chapter}, codes: {chapter_codes_occurrences}")

        chapter_weights[chapter] = {}
        chapter_total_occurrences = sum(icd_counts.get(key, 0) for key in chapter_codes)
        print(f"total for chapter from 30: {chapter_total_occurrences}")

        for code in chapter_codes_occurrences:
            code_frequency = icd_counts[code]
            weight = (code_frequency / total_frequency) * 100
            print(f"code {code}, wight: {weight}")
            chapter_weights[chapter][code] = weight

        remaining_codes = [code for code in chapter_codes if code not in chapter_codes_occurrences]
        print(sum(chapter_weights[chapter].values()))
        remaining_weight = 100 - sum(chapter_weights[chapter].values())
        print(remaining_weight)
        if remaining_codes:
            equal_weight = remaining_weight / len(remaining_codes)
            for code in remaining_codes:
                chapter_weights[chapter][code] = equal_weight
        weight_sum = sum(chapter_weights[chapter].values())
        # if weight_sum != 100:
        #     diff = 100 - weight_sum
        #     chapter_weights[chapter][list(chapter_weights[chapter].keys())[0]] += diff

    for chapter, weights in chapter_weights.items():
        chapter_weights[chapter] = {code: round(weight, 3) for code, weight in weights.items()}
    for chapter, weights in chapter_weights.items():
        print(f"Chapter {chapter}: {weights}")
        print(f"Total after rounding (2 decimals): {sum(chapter_weights[chapter].values())}")

    output_file = '../chapter_weights1.py'
    try:
        with open(output_file, 'w') as py_file:
            py_file.write("chapter_weights = {\n")
            for chapter, weights in chapter_weights.items():
                weight_items = ', '.join([f"\"{code}\": {weight}" for code, weight in weights.items()])
                py_file.write(f"    \"{chapter}\": {{ {weight_items} }},\n")

            py_file.write("}\n\n")  # End the chapter_weights dictionary

            py_file.write("chapter_probs = {\n")
            for chapter, prob in chapter_probs.items():
                py_file.write(f"    \"{chapter}\": {prob},\n")
            py_file.write("}\n")

        print(f"Data successfully saved to {output_file}")
    except Exception as e:
        raise RuntimeError(f"Error writing to Python file: {e}")


icd_distribution()
