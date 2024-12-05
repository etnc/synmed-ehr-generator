# Step 1: Load the dataset into a pandas DataFrame
df = pd.read_csv('your_dataset.csv')  # Replace with your actual file path

# Step 2: Filter out ICD-10 codes containing '+'
df_filtered = df[~df['ICD_10'].str.contains('\+', na=False)]

# Step 3: Group by ICD-10 code and count occurrences
icd_counts = df_filtered['ICD_10'].value_counts().reset_index()

# Step 4: Rename columns for better readability
icd_counts.columns = ['ICD_10', 'Count']

# Step 5: Display the result
print(icd_counts)
