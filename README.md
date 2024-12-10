## EHR Generation System Synmed

### Overview

This project is designed to generate and manage Electronic Health Records (EHRs) using a flexible and customizable data
generation system. The system enables the creation of patient records, including demographics, diagnoses,
medications and patient medical history. It supports multiple formats (JSON, RDF, XML) and adheres to
predefined distributions for gender, age, and diagnosis commonality.

### Data

- *Patient Information*:
    - Includes details such as ID, name, age, gender, date of birth, address, and phone number.
    - Age and Gender Distribution
- *Medical Data*:
    - Diagnoses mapped to ICD-10 codes
    - Medications mapped to ATC codes
    - Medications Details
    - Medications linked to diagnoses
    - Diagnoses distributions
- Export Formats: Supports JSON, RDF, XML and additional FHIR in JSON format

### Usage

#### Prerequisites:

- Python 3.12.5

- Required libraries

##### 1.Clone this repository:

    git clone https://github.com/evamilenkova/synmed-ehr-generator

    cd synmed-ehr-generator

##### 2. Install required libraries 
```bash
pip install -r requirements.txt
```
##### 4.Set up the configuration file (config.yml)

##### 5.Generate EHR data by running:

    python generate_ehr.py
Or (overrides config.yml):

    python generate_ehr.py --records 100 --result_format turtle --generate_fhir 1 

After running the script, the generated EHR data will be saved in the `results/` folder. Each generated record will be
stored in a file corresponding to the specified format. For example:

- `results/generated_data.json`
- `results/generated_data.rdf`
- `results/generated_data.json-ld`
- `results/generated_data.ttl` 
