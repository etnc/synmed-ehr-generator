import json
from datetime import datetime
from typing import Optional

from fhir.resources.bundle import BundleEntry, Bundle
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.coding import Coding
from fhir.resources.condition import Condition
from fhir.resources.medication import Medication
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.patient import Patient
from fhir.resources.reference import Reference

from domain.AdministrationRoute import AdministrationRoute
from service.logger_service import logger, setup_logger


def get_patient_resource(personal_information):
    return Patient(
        id=personal_information['patient_id'],
        name=[{
            "given": [name_part.strip() for name_part in
                      personal_information['full_name'].split() if name_part],
            "family": personal_information['full_name'].split()[-1]
        }],
        gender=personal_information['gender'].lower(),
        birthDate=personal_information['date_of_birth'],
        address=[{
            "line": [personal_information['address'].split(',')[0]],  # line should be a list
            "city": personal_information['address'].split(',')[1].strip() if len(
                personal_information['address'].split(',')) > 1 else '',
            "state": personal_information['address'].split(',')[2].strip() if len(
                personal_information['address'].split(',')) > 2 else ''
        }],
        telecom=[{
            "system": "phone",
            "value": personal_information['phone']
        }]
    )


def get_condition(medical_information, patient_id, status):
    return Condition(
        id=medical_information['diagnosis']['ICD'],
        subject={"reference": f"Patient/{patient_id}"},
        code=CodeableConcept(
            coding=[Coding(
                system="http://hl7.org/fhir/sid/icd-10",
                code=medical_information['diagnosis']['ICD'],
                display=medical_information['diagnosis']['name']
            )]
        ),
        clinicalStatus={
            "coding": [
                {"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": status}]}
    )


def get_medical_history(medical_history, patient_id):
    conditions = []
    for condition in medical_history:
        c = get_condition({'diagnosis': condition}, patient_id, 'inactive')
        conditions.append(c)
    return conditions


def get_medication_request(medication_information, patient_id):
    def parse_dosage(dosage: str) -> Optional[tuple]:
        try:
            parts = dosage.split()
            return float(parts[0]), parts[1]
        except (IndexError, ValueError):
            return None

    medication_data = medication_information.get('medication', {})
    if medication_data:
        atc_code = medication_data.get('ATC')
        name = medication_data.get('name')
        dosage = medication_data.get('dosage', None)
        route_name = medication_data.get('route', {}).get('name', None)
    else:
        atc_code = medication_information.get('ATC')
        name = medication_information.get('ATC')
        dosage = None
        route_name = None
    medication = Medication(
        id=atc_code,
        code=CodeableConcept(
            coding=[Coding(
                system="http://www.whocc.no/atc/",
                code=atc_code,
                display=name
            )]
        )
    )
    medication_request = MedicationRequest(
        id=atc_code,
        subject={"reference": f"Patient/{patient_id}"},
        medication=CodeableReference(
            reference=Reference(reference=f"Medication/{atc_code}"),
        ),
        status="active",
        intent="order"  # Medication request intent
    )
    if dosage:
        dose_value, dose_unit = parse_dosage(dosage)
        route_name = route_name or "Oral"
        route_snomed_code = AdministrationRoute.get_snomed_code()[route_name]
        medication_request.dosageInstruction = [{
            "doseAndRate": [  # Include dosage details
                {
                    "doseQuantity": {
                        "value": dose_value,
                        "unit": dose_unit
                    }
                }
            ],
            "route": CodeableConcept(
                coding=[Coding(
                    system="http://snomed.info/sct",
                    code=route_snomed_code,
                    display=route_name
                )]
            )
        }]


def create_fhir_bundle(patient, conditions, medication, bundle_type="collection"):
    entries = [
        BundleEntry(resource=patient),
        *[BundleEntry(resource=condition) for condition in conditions],
        BundleEntry(resource=medication)
    ]
    return Bundle(
        type=bundle_type,
        entry=entries
    )


def ehr_fhir(ehr_record):
    patient = get_patient_resource(ehr_record['personal_information'])
    condition = get_condition(ehr_record['medical_information'], patient.id, "active"),
    medication = get_medication_request(ehr_record['medical_information'], patient.id)
    history = get_medical_history(ehr_record['medical_information'].get('medical_history', []), patient.id)
    return create_fhir_bundle(patient, [condition[0], *history], medication)


def save_fhir(records):
    logger = setup_logger()
    bundles = []
    for r in records:
        bundles.append(ehr_fhir(r))

    bundle_dicts = [json.loads(bundle.json()) for bundle in bundles]
    file_path = "results/fhir_data.json"
    logger.info(f"FHIR data saved in {file_path}")
    with open(file_path, "w") as f:
        json.dump(bundle_dicts, f, indent=4)
