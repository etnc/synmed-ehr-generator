import pandas as pd


def simplify_icd_code(icd):
    icd = icd.strip()
    if icd.endswith('.'):
        return icd[:-1]
    if '.' in icd:
        parts = icd.split('.')
        if len(parts) > 1:
            if parts[1].lstrip('0') == '':
                return parts[0] + '.0'  #
            return parts[0] + '.' + parts[1].lstrip('0')[0]
    return icd


def get_dataset():
    icd_counts_total = pd.Series(dtype=int)

    chunk_size = 50000

    for chunk in pd.read_csv('../raw_data/Dataset (1).csv', chunksize=chunk_size, usecols=['ICD_10']):
        chunk_filtered = chunk[chunk['ICD_10'].apply(lambda x: '+' not in str(x) and str(x).isascii())].copy()

        chunk_filtered['ICD_10'] = chunk_filtered['ICD_10'].apply(
            lambda x: simplify_icd_code(x.split('x')[0] if 'x' in x else x)
        )

        icd_counts_chunk = chunk_filtered['ICD_10'].value_counts()

        icd_counts_total = icd_counts_total.add(icd_counts_chunk, fill_value=0)

    icd_counts_df = icd_counts_total.reset_index()
    icd_counts_df.columns = ['ICD_10', 'Count']

    icd_counts_df = icd_counts_df.sort_values(by='Count', ascending=False)

    icd_counts_dict = icd_counts_total.to_dict()
    with open('icd_counts.py', 'w') as f:
        f.write(f"icd_counts = {icd_counts_dict}")
