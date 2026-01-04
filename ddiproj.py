import pandas as pd
import zipfile
import os

# --- 1. List of your FAERS ZIP files ---
zip_files = [
    "faers_ascii_2024Q1.zip",
    "faers_ascii_2024Q2.zip",
    "faers_ascii_2024Q3.zip",
    "faers_ascii_2024Q4.zip",
    "faers_ascii_2025q1 (1).zip",
    "faers_ascii_2025q2 (2).zip",
    "faers_ascii_2025q3 (2).zip",
]

# --- 2. Columns to drop ---
unwanted_cols = [
    'val_vbm', 'dose_vbm', 'cum_dose_chr', 'cum_dose_unit',
    'dechal', 'rechal', 'lot_num', 'exp_dt', 'nda_num'
]

# --- 3. Drug names to keep ---
drug_list = [
    "Lamotrigine", "Levetiracetam", "Topiramate", "Gabapentin", "Pregabalin",
    "Oxcarbazepine", "Zonisamide", "Lacosamide", "Clobazam", "Phenytoin",
    "Carbamazepine", "Phenobarbital", "Valproic acid", "Sodium valproate",
    "Ethosuximide", "Levodopa + Carbidopa", "Bromocriptine", "Pramipexole",
    "Ropinirole", "Rotigotine", "Apomorphine", "Selegiline", "Rasagiline",
    "Safinamide", "Entacapone", "Tolcapone", "Trihexyphenidyl", "Benzhexol",
    "Benztropine", "Amantadine", "Donepezil", "Rivastigmine", "Galantamine",
    "Memantine", "Interferon beta-1a", "Interferon beta-1b", "Glatiramer acetate",
    "Fingolimod", "Teriflunomide", "Dimethyl fumarate", "Natalizumab",
    "Ocrelizumab", "Alemtuzumab", "Baclofen", "Tizanidine", "Modafinil",
    "Sumatriptan", "Rizatriptan", "Zolmitriptan", "Ibuprofen", "Naproxen",
    "Ergotamine", "Dihydroergotamine", "Metoclopramide", "Domperidone",
    "Propranolol", "Amitriptyline", "Candesartan", "Botulinum toxin A",
    "Nortriptyline", "Duloxetine", "Tetrabenazine", "Deutetrabenazine",
    "Haloperidol", "Risperidone", "Diazepam", "Pyridostigmine", "Neostigmine",
    "Prednisolone", "Azathioprine", "Mycophenolate mofetil", "Cyclosporine",
    "Eculizumab", "Rituximab", "Plasmapheresis", "IV immunoglobulin",
    "Zolpidem", "Zopiclone", "Melatonin", "Sodium oxybate", "Methylphenidate",
    "Ceftriaxone", "Vancomycin", "Acyclovir", "Amphotericin B", "Citicoline",
    "Piracetam", "Cerebrolysin", "Edaravone"
]

# Lowercase version for case-insensitive comparison
drug_list_lower = [d.strip().lower() for d in drug_list]

# --- Master DataFrame ---
master_drug_df = pd.DataFrame()   # <- initialize here

# --- Loop through ZIP files ---
for zip_path in zip_files:
    if not os.path.exists(zip_path):
        print(f"File not found: {zip_path}")
        continue
    
    with zipfile.ZipFile(zip_path, "r") as z:
        # Find DRUG tables
        drug_files = [f for f in z.namelist() if "DRUG" in f.upper() and f.endswith(".txt")]
        
        for file_name in drug_files:
            with z.open(file_name) as f:
                df = pd.read_csv(f, sep="$", encoding="latin-1", low_memory=False)
                
                # Drop unwanted columns if they exist
                df = df.drop(columns=[c for c in unwanted_cols if c in df.columns])
                
                # Filter only if required columns exist
                if {'drugname', 'role_cod'}.issubset(df.columns):
                    df = df[
                        (df['drugname'].str.strip().str.lower().isin(drug_list_lower)) &
                        (df['role_cod'].isin(['PS', 'SS']))
                    ]
                    
                    # Append filtered rows
                    master_drug_df = pd.concat([master_drug_df, df], ignore_index=True)
# --- REMOVE DUPLICATES ---
master_drug_df = master_drug_df.drop_duplicates(
    subset=['primaryid', 'caseid', 'drugname']
)
import pandas as pd
import numpy as np

# Convert 'Unknown' values to NaN
master_drug_df = master_drug_df.replace('Unknown', np.nan)

# Check percentage of missing values per column
missing_percent = master_drug_df.isna().mean() * 100
print("Missing value percentages per column:\n", missing_percent)

# Drop columns where more than 60% of values are missing
cols_to_drop = missing_percent[missing_percent > 60].index
print(f"Columns to drop (more than 60% missing): {list(cols_to_drop)}")

master_drug_df_clean = master_drug_df.drop(columns=cols_to_drop)

# Optional: Check the updated DataFrame
print("Remaining columns:", master_drug_df_clean.columns)
print(f"Total rows after filtering: {len(master_drug_df)}")
master_drug_df_clean.head(100)
import pandas as pd
import zipfile

# --- Master REAC DataFrame ---
master_reac_df = pd.DataFrame()  # <- fix this line

# --- Read and clean REAC tables ---
for zip_path in zip_files:
    with zipfile.ZipFile(zip_path, "r") as z:
        reac_files = [f for f in z.namelist() if "REAC" in f.upper() and f.endswith(".txt")]

        for file_name in reac_files:
            with z.open(file_name) as f:
                reac_df = pd.read_csv(f, sep="$", encoding="latin-1", low_memory=False)

                # Remove drug_rec_act column if exists
                reac_df = reac_df.drop(columns=['drug_rec_act'], errors='ignore')

                # Keep only join-relevant columns
                reac_df = reac_df[['primaryid', 'pt']]

                master_reac_df = pd.concat([master_reac_df, reac_df], ignore_index=True)

# --- Join DRUG + REAC ---
final_df = master_drug_df_clean.merge(
    master_reac_df,
    on='primaryid',
    how='inner'
)

print("Final dataset shape:", final_df.shape)
final_df.head(10)
import pandas as pd
import zipfile

# Loop through ZIP files and read DEMO table
for zip_path in zip_files:
    with zipfile.ZipFile(zip_path, "r") as z:
        # Find DEMO file
        demo_files = [f for f in z.namelist() if "DEMO" in f.upper() and f.endswith(".txt")]
        
        if demo_files:
            with z.open(demo_files[0]) as f:
                demo_df = pd.read_csv(f, sep="$", encoding="latin-1", low_memory=False)
                
                print(f"\nFirst 10 records from DEMO table in {zip_path}:")  
                break  # stop after first DEMO table
# Columns to drop manually
demo_cols_to_drop = [
    'rept_cod', 'to_mfr', 'caseversion', 'i_f_code', 'event_dt',
    'mfr_dt', 'init_fda_dt', 'fda_dt', 'rept_dt', 'occp_cod'
]

# Drop manually specified columns (if they exist)
demo_df_clean = demo_df.drop(
    columns=[col for col in demo_cols_to_drop if col in demo_df.columns]
)

# Drop columns where >60% values are null
threshold = 0.6  # 60% null
demo_df_clean = demo_df_clean.dropna(axis=1, thresh=int((1 - threshold) * len(demo_df_clean)))

print("Remaining DEMO columns after cleaning:")
print(demo_df_clean.columns)

# --- Join FINAL with DEMO ---
# Use suffixes to avoid automatic _x/_y column names
final_demo_df = final_df.merge(
    demo_df_clean,
    on='primaryid',
    how='inner',
    suffixes=('_drug', '_demo')  # rename overlapping columns clearly
)

# Optional: drop duplicate columns if not needed (example: caseid_demo)
if 'caseid_demo' in final_demo_df.columns:
    final_demo_df = final_demo_df.drop(columns=['caseid_demo'])

# Optional: rename columns for clarity
if 'caseid_drug' in final_demo_df.columns:
    final_demo_df = final_demo_df.rename(columns={'caseid_drug': 'caseid'})

print("Final DRUG + REAC + DEMO dataset shape:", final_demo_df.shape)
final_demo_df.head(10)
# --- Create transaction dataset ---
transactions = (
    final_demo_df[['primaryid', 'drugname']]
    .drop_duplicates()
    .assign(present=1)
    .pivot(index='primaryid', columns='drugname', values='present')
    .fillna(0)
)
#convert to boolian
transactions = transactions.astype(bool)
#Run appriori algorithem
from mlxtend.frequent_patterns import apriori, association_rules
#resadonalbe minimam support
frequent_itemsets = apriori(
    transactions,
    min_support=0.001,   # adjust if needed
    use_colnames=True
)
#keep only drug drrug items(size=2)
frequent_itemsets['itemset_size'] = frequent_itemsets['itemsets'].apply(len)

drug_drug_itemsets = frequent_itemsets[
    frequent_itemsets['itemset_size'] == 2
]
#generating assosiation rules (support, confidence, lift)
rules = association_rules(
    frequent_itemsets,
    metric='confidence',
    min_threshold=0.1
)
# Filter only drug–drug rules and make an explicit copy ---
rules_ddi = rules[
    (rules['antecedents'].apply(len) == 1) &
    (rules['consequents'].apply(len) == 1)
].copy()
#filter only drug drug rules
rules_ddi['drug_1'] = rules_ddi['antecedents'].apply(lambda x: list(x)[0])
rules_ddi['drug_2'] = rules_ddi['consequents'].apply(lambda x: list(x)[0])

rules_ddi_final = rules_ddi[
    ['drug_1', 'drug_2', 'support', 'confidence', 'lift']
].sort_values(by='lift', ascending=False)
#apply validation threshold
validated_ddi = rules_ddi_final[
    (rules_ddi_final['support'] >= 0.001) &
    (rules_ddi_final['confidence'] >= 0.3) &
    (rules_ddi_final['lift'] > 1)
]
validated_ddi.head(10)
print("Number of validated DDI rules:", len(validated_ddi))
