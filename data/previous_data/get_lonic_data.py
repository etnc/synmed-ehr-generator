from itertools import chain

import pandas as pd

from data.previous_data.icd_lonic import icd10_to_loinc


def get_loinc_data(loinc_codes):
    """
    Create a dictionary mapping LOINC codes to their descriptions from the LOINC dataset.

    Parameters:
        loinc_codes (list): List of LOINC codes to search for.
        loinc_file (str): Path to the LOINC dataset CSV file.
        description_column (str): Column name in the dataset containing the descriptions.

    Returns:
        dict: A dictionary mapping LOINC codes to their descriptions.
    """
    loinc_df = pd.read_csv("Loinc.csv")

    # Filter the dataset for the provided LOINC codes
    filtered_loinc = loinc_df[loinc_df["LOINC_NUM"].isin(loinc_codes)]
    loinc_details = {}
    for _, row in filtered_loinc.iterrows():
        loinc_details[row['LOINC_NUM']] = {
            "description": row["LONG_COMMON_NAME"],
            "component": row["COMPONENT"],
            "property": row["PROPERTY"],
            "system": row["SYSTEM"],
            "scale_type": row["SCALE_TYP"],
            "method_type": row["METHOD_TYP"],
        }

    return loinc_details


flattened_list = list(chain(*icd10_to_loinc.values()))

print(len(flattened_list))

loinc = get_loinc_data(flattened_list)

for key in flattened_list:
    if key not in loinc.keys():
        print(key)
