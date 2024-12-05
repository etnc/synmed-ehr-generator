import cProfile
import json
import sys
import xml
import time
import random
from concurrent.futures import ProcessPoolExecutor

from dicttoxml import dicttoxml
from faker import Faker
from config import config_faker_locales, config_result_format
from domain.Gender import Gender
from service.format_service import generate_rdf
from service.medical_service import get_diagnosis, get_medication_atc, get_atc_data, get_medical_history
from service.patient_service import get_country_from_locale, assign_age, determine_maternity, assign_gender, \
    get_phone_number


def create_ehr_record(_):
    locale = random.choice(config_faker_locales)
    fake = Faker(locale=locale)

    gender = assign_gender()
    if gender == Gender.FEMALE:
        name = f"{fake.first_name_female()} {fake.last_name_female()}"
    else:
        name = f"{fake.first_name_male()} {fake.last_name_male()}"
    age, age_group = assign_age()
    dob = fake.date_of_birth(minimum_age=age, maximum_age=age)
    maternity_status = determine_maternity(gender, age_group)
    diagnosis_code, diagnosis_name, diagnose_description = get_diagnosis(gender, age_group, maternity_status)
    country = get_country_from_locale(locale)

    medication_atc = get_medication_atc(diagnosis_code)
    if medication_atc:
        atc_data = get_atc_data(medication_atc)
    else:
        atc_data = None
    medical_history = get_medical_history(diagnosis_code, age_group)
    ehr_record = {
        "personal_information":
            {
                "patient_id": fake.uuid4()[:10],
                "full_name": name,
                "gender": gender,
                "address": f" {fake.building_number()} {fake.street_name()}, {fake.city()}, {country if country is not None else fake.country()}",
                "phone": get_phone_number(fake.phone_number()),
                "age": age,
                "date_of_birth": dob.strftime("%Y-%m-%d")
            },
        "medical_information":
            {
                "diagnosis": {"ICD": diagnosis_code, "name": diagnosis_name, "description": diagnose_description},
            }
    }

    if atc_data:
        ehr_record['medical_information']['medication'] = atc_data
    elif medication_atc:
        ehr_record['medical_information']['ATC'] = medication_atc
    if medical_history:
        ehr_record['medical_information']['medical_history'] = medical_history

    return ehr_record


def format_and_save_record(record, filename):
    result_format = config_result_format

    extension_map = {
        'JSON': ('json', lambda r: json.dumps(r, indent=4)),
        'XML': ('xml', lambda r: xml.dom.minidom.parseString(
            dicttoxml(r, custom_root='PatientRecord', attr_type=False)
        ).toprettyxml()),
        'turtle': ('ttl', lambda r: generate_rdf(r, result_format)),
        'json-ld': ('jsonld', lambda r: generate_rdf(r, result_format)),
        'rdf/xml': ('rdf', lambda r: generate_rdf(r, 'xml')),
    }

    if result_format in extension_map:
        extension, generate_data = extension_map[result_format]
        data = generate_data(record)
        with open(f"{filename}.{extension}", 'w', encoding='utf-8') as f:
            f.write(data)
        return extension
    else:
        raise ValueError(f"Unsupported result format: {result_format}")



# sample_records = []
# print("here")
# for i in range(145):
#     record = create_ehr_record(None)
#     sample_records.append(record)
#     print(record)
# format_and_save_record(sample_records, 'test-test')
#
def main():
    start_time = time.time()
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(create_ehr_record, range(num_records)))
    file_format = format_and_save_record(results, 'generated_data')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Records have been written to generated_data.{file_format}...")
    print(f"Time taken: {elapsed_time:.2f} seconds.")

#
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <number_of_records>")
        sys.exit(1)
    try:
        num_records = int(sys.argv[1])
        print(f"Generating {num_records} records...")

        # profiler = cProfile.Profile()
        # profiler.enable()
        main()
        # profiler.disable()
        # profiler.print_stats()

    except ValueError:
        print("Please provide a valid integer for the number of records.")
