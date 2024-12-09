import openai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_KEY')
openai.api_key = api_key


response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system",
         "content": "You are a helpful assistant that generates realistic Electronic Health Records (EHR) with patient information, diagnoses, and medications. You must ensure that the diagnoses and medications follow common distributions, with appropriate ICD codes and ATC codes. The data should be realistic, considering age, gender, and health conditions."},
        {"role": "user",
         "content": "Please generate 50 EHR records with the following details: Each record should include a patient's name, age, gender, diagnosis with ICD-10 codes, and corresponding medication with ATC codes. Ensure that the diagnoses are age-appropriate and the medications correspond to the diagnoses. Distribute the diagnoses realistically by frequency (e.g., common diseases should appear more often)."},
    ]
)

print(response['choices'][0]['message']['content'])


def generate_batch(batch_number):
    response = openai.ChatCompletion.create(
        model="gpt-4",

        messages=[
            {
                "role": "system",
                "content": "You are a medical data expert proficient in generating realistic and medically "
                           "consistent electronic health records (EHRs) in Turtle (TTL) format. "
                           "You should structure the data using RDF triples, ensuring that all relationships 4"
                           "between patients, diagnoses, medications, and other relevant details are clearly represented."
            },
            {
                "role": "user",
                "content": f"""
Generate 10 fictional electronic health records (EHRs) in Turtle (TTL) format. Each record should include the following details: 1. **Demographics**: 
   - Gender (Male/Female)
   - Age (appropriate for the diagnosis)
   - Address (fictional address in a shortened format)
   - Telephone number (formatted as (xxx) xxx-xxxx)
2. **Diagnosis**: 
   - A diagnosis with its corresponding ICD code. Ensure diagnoses are realistic and represent common medical conditions.
3. **Medications**: 
   - A related medication with its ATC code, dosage, and administration route. Some diagnoses may not have an associated medication. 
4. **Medical History**: 
   - Include relevant medical history when appropriate to make the cases realistic."""}]
    )

    return response['choices'][0]['message']['content']


def generate_batch_completion(batch):
    response = openai.Completion.create(
        model="babbage-002",
        prompt=(
            "You are a medical data expert proficient in generating realistic and medically "
            "consistent electronic health records (EHRs) in Turtle (TTL) format. "
            "Generate 5 fictional electronic health records (EHRs) in TTL format with the following details: "
            "- Patient information: Name, gender, age, address, and phone number. "
            "- Diagnosis: ICD code and description. "
            "- Medications: ATC code, dosage, and route of administration. "
            "- Medical History: Diagnosis that is highly related to the current diagnosis of patient"
            "- Ensure the data is consistent, realistic, and clearly represented as RDF triples. "
            "Provide the output in Turtle format."
        ),
        max_tokens=1000

    )
    return response['choices'][0]['text']


def generate_all_batches(total_batches):
    all_records = []

    for batch_number in range(1, total_batches + 1):
        print(f"Generating batch {batch_number}...")
        batch_data = generate_batch(batch_number)
        all_records.append(batch_data)

        with open(f"ehr_batch_{batch_number}.ttl", "w") as file:
            file.write(batch_data)

    return all_records


