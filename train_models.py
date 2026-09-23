import pandas as pd
import numpy as np
import time
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
import joblib
import os

print("Ensuring models directory exists...")
os.makedirs('models', exist_ok=True)

print("Loading dataset...")
try:
    df = pd.read_csv('data/transactions.csv', encoding='latin1')
except FileNotFoundError:
    print("Dataset not found. Creating a dummy dataset to test the UI.")
    df = pd.DataFrame({
        'InvoiceNo': [1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 5],
        'Description': ['Laptop', 'Mouse', 'Laptop Bag', 'Laptop', 'Keyboard', 'Laptop', 'Mouse', 'Keyboard', 'Mouse', 'Laptop Bag', 'Laptop', 'Mouse']
    })

print("Cleaning data...")
cleaned_df = df.dropna(subset=['InvoiceNo', 'Description'])
cleaned_df = cleaned_df[cleaned_df['Description'].astype(str).str.strip() != '']
cleaned_df = cleaned_df[~cleaned_df['InvoiceNo'].astype(str).str.startswith('C')]

if 'Country' in cleaned_df.columns:
    cleaned_df = cleaned_df[cleaned_df['Country'] == 'United Kingdom']

transactions = cleaned_df.groupby('InvoiceNo')['Description'].apply(lambda x: [str(item).strip() for item in x]).tolist()

print("One-hot encoding...")
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

print(f"Encoded Dataset Shape: {df_encoded.shape}")

print("Running FP-Growth...")
fpgrowth_itemsets = fpgrowth(df_encoded, min_support=0.03, use_colnames=True)

print("Generating Rules...")
rules = association_rules(fpgrowth_itemsets, metric='confidence', min_threshold=0.3)
highly_confident_rules = rules[rules['confidence'] >= 0.50]

print(f"Saving models (Generated {len(highly_confident_rules)} rules)...")
joblib.dump(fpgrowth_itemsets, 'models/frequent_itemsets.pkl')
joblib.dump(highly_confident_rules, 'models/association_rules.pkl')
joblib.dump(list(df_encoded.columns), 'models/product_mapping.pkl')

print("Done! Models saved.")
