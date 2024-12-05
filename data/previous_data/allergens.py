allergen_weights = {
    "penicillin": 5,  # High severity and common
    "cephalosporin": 4,  # Common cross-reactivity with penicillin
    "carbapenem": 4,  # Moderate to severe reactions, related to penicillin
    "monobactam": 3,  # Less severe but can cause reactions in some
    "sulfonamide": 4,  # Can cause severe reactions, common in some populations
    "trimethoprim-sulfamethoxazole": 4,  # Common sulfonamide drug with potential for severe reactions
    "aspirin": 3,  # Common, can cause asthma-like reactions
    "ibuprofen": 3,  # Common NSAID, mild reactions in some
    "naproxen": 3,  # Common NSAID, similar to ibuprofen
    "phenytoin": 4,  # Can cause severe rashes and allergic reactions
    "carbamazepine": 4,  # Severe skin reactions, including SJS
    "valproate": 3,  # Less common, mild reactions
    "insulin": 3,  # Rare but can cause anaphylaxis in some individuals
    "codeine": 2,  # Opioid, mild reactions (e.g., itching)
    "morphine": 3,  # Opioid, mild to moderate reactions
    "oxycodone": 3,  # Opioid, similar reactions to morphine
    "paclitaxel": 5,  # Severe infusion reactions
    "rituximab": 4,  # Severe infusion-related reactions
    "adalimumab": 4,  # Monoclonal antibody, potential severe reactions
    "trastuzumab": 4,  # Similar to other monoclonal antibodies
    "iodine contrast": 5,  # Common and severe reactions like anaphylaxis
    "levothyroxine": 2,  # Rare allergic reactions
    "hydroxyzine": 2,  # Mild allergic reactions
    "cetirizine": 1
}
# 5: Severe reactions, common, or well-known to cause anaphylaxis or other serious reactions.
# 4: Common or significant reactions that may require medical attention but are less severe than 5.
# 3: Moderate likelihood of reaction, less severe in most cases.
# 2: Uncommon or mild reactions, with low incidence.
# 1: Rare and mild, with minimal reactions.
# The weights provided here are meant to represe
