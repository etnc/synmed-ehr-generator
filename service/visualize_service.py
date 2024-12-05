import numpy as np
import plotly.graph_objects as go
import networkx as nx
from matplotlib import pyplot as plt
from rdflib import Graph

import json
import pandas as pd

with open("../generated_data.json") as f:
    data = json.load(f)

records = []
for record in data:
    personal = record["personal_information"]
    medical = record["medical_information"]

    # Current diagnosis
    diagnosis = medical["diagnosis"]
    records.append({
        "patient_id": personal["patient_id"],
        "full_name": personal["full_name"],
        "gender": personal["gender"],
        "age": personal["age"],
        "current_diagnosis": diagnosis["ICD"],
    })

df = pd.DataFrame(records)
frequencies = {
    'I': 443737, 'C': 312425, 'E': 142717, 'K': 118712, 'J': 102677,
    'N': 84206, 'M': 74935, 'D': 47637, 'G': 44870, 'O': 36555,
    'B': 30539, 'R': 27542, 'H': 26172, 'S': 19789, 'Q': 9500,
    'T': 8222, 'F': 8028, 'A': 5975, 'L': 5670, 'P': 1814, 'U': 10
}
icd_counts = pd.DataFrame(list(frequencies.items()), columns=["ICD Prefix", "Frequency"])

icd_counts = icd_counts.sort_values(by="Frequency", ascending=False)
icd_prefixes = icd_counts['ICD Prefix'].tolist()

matrix = np.full((len(icd_prefixes), len(icd_prefixes)), "", dtype=object)

for i, icd_prefix in enumerate(icd_prefixes):
    matrix[i, i] = icd_counts[icd_counts['ICD Prefix'] == icd_prefix]['Frequency'].values[0]

matrix_df = pd.DataFrame(matrix, columns=icd_prefixes, index=icd_prefixes)

matrix_df.to_csv("icd_prefix_diagonal_distribution.csv")

print(matrix_df)
