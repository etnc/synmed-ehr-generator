from urllib.parse import urljoin, quote
from rdflib import RDF, Literal, RDFS, Namespace, Graph, URIRef

def generate_rdf(records, rdf_format):
    valid_formats = ('ttl', 'json-ld', 'xml',)
    if rdf_format not in valid_formats:
        raise ValueError(f"Invalid format '{rdf_format}'. Supported formats are: {','.join(valid_formats)}")
    BASE = Namespace("https://synmed.org/")
    SCHEMA = Namespace("https://schema.org/")
    g = Graph()

    g.bind("schema", SCHEMA)
    g.bind("base", BASE)

    hasHistoricalDiagnosis = BASE.hasHistoricalDiagnosis
    g.add((hasHistoricalDiagnosis, RDFS.domain, SCHEMA.Patient))
    g.add((hasHistoricalDiagnosis, RDFS.range, SCHEMA.MedicalCondition))

    hasAdministrationRoute = BASE.hasAdministrationRoute
    g.add((hasAdministrationRoute, RDFS.domain, SCHEMA.Medication))
    g.add((hasAdministrationRoute, RDFS.range, SCHEMA.AdministrationRoute))

    def get_entity_url(entity_type, entity_id):
        encoded_entity_id = quote(entity_id, safe=":/")
        return URIRef(urljoin(str(BASE), f"{entity_type}/{encoded_entity_id}"))

    def get_or_add_route(route_name, route_description=None):
        route_uri = get_entity_url("route", route_name)
        if (route_uri, RDF.type, BASE.AdminostrationRoute) not in g:
            g.add((route_uri, RDF.type, BASE.AdministrationRoute))
            g.add((route_uri, BASE.name, Literal(route_name)))
            if route_description:
                g.add((route_uri, BASE.description, Literal(route_description)))
        return route_uri

    def add_patient():
        g.add((patient_uri, RDF.type, SCHEMA.Patient))
        g.add((patient_uri, SCHEMA.name, Literal(patient_data["full_name"])))
        g.add((patient_uri, SCHEMA.gender, Literal(patient_data["gender"])))
        g.add((patient_uri, SCHEMA.age, Literal(patient_data["age"])))
        g.add((patient_uri, SCHEMA.address, Literal(patient_data["address"])))
        g.add((patient_uri, SCHEMA.birthDate, Literal(patient_data["date_of_birth"])))
        g.add((patient_uri, SCHEMA.telephone, Literal(patient_data["phone"])))

    def add_diagnosis(diagnosis_to_add, diagnosis_uri_to_add):
        diagnosis_code = diagnosis_to_add.get("ICD")
        diagnosis_name = diagnosis_to_add.get("name")
        diagnosis_description = diagnosis_to_add.get("description")
        g.add((diagnosis_uri_to_add, RDF.type, SCHEMA.MedicalCondition))
        g.add((diagnosis_uri_to_add, SCHEMA.identifier, Literal(diagnosis_code)))
        g.add((diagnosis_uri_to_add, SCHEMA.name, Literal(diagnosis_name)))
        g.add((diagnosis_uri_to_add, SCHEMA.description, Literal(diagnosis_description)))

    def add_medication():
        medication_name = medication_data["name"]
        atc_code = medication_data["ATC"]
        if "dosage" in medication_data:
            dosage = medication_data["dosage"]
        else:
            dosage = None

        g.add((medication_uri, RDF.type, SCHEMA.Drug))
        g.add((medication_uri, SCHEMA.name, Literal(medication_name)))
        g.add((medication_uri, SCHEMA.identifier, Literal(atc_code)))
        if dosage:
            g.add((medication_uri, SCHEMA.description, Literal(f"Dosage: {dosage}")))
        route_name = medication_data.get("route", {}).get("name")
        if route_name:
            route_description = medication_data.get("route", {}).get("description")
            route_node = get_or_add_route(route_name, route_description)
            g.add((medication_uri, SCHEMA.administrationRoute, Literal(route_name)))
            g.add((medication_uri, BASE.hasAdministrationRoute, route_node))

    for ehr in records:
        patient_uri = get_entity_url("patient", ehr['personal_information']['patient_id'])
        patient_data = ehr["personal_information"]
        medical_data = ehr['medical_information']
        add_patient()

        diagnosis_data = medical_data.get("diagnosis", {})
        diagnosis_uri = get_entity_url("diagnosis", diagnosis_data.get("ICD"))
        if (diagnosis_uri, RDF.type, SCHEMA.MedicalCondition) not in g:
            add_diagnosis(diagnosis_data, diagnosis_uri)
        g.add((patient_uri, SCHEMA.diagnosis, diagnosis_uri))

        if "medication" in medical_data:
            medication_data = medical_data["medication"]
            medication_uri = get_entity_url("medication", medication_data["ATC"])
            if (medication_uri, RDF.type, SCHEMA.Drug) not in g:
                add_medication()
            g.add((patient_uri, SCHEMA.usesDrug, medication_uri))
        elif "ATC" in ehr:
            g.add((patient_uri, SCHEMA.usesDrug, Literal(medical_data['ATC'])))

        if 'medical_history' in medical_data:
            medical_history = medical_data['medical_history']
            for diagnosis in medical_history:
                diagnosis_uri = get_entity_url("diagnosis", diagnosis.get("ICD"))
                if (diagnosis_uri, RDF.type, SCHEMA.MedicalCondition) not in g:
                    add_diagnosis(diagnosis, diagnosis_uri)
                g.add((patient_uri, BASE.hasHistoricalDiagnosis, diagnosis_uri))

    return g.serialize(format=rdf_format)
