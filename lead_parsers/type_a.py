import os
import pandas as pd
import uuid
import re

# --- CONFIGURATION ---
INPUT_FILE = "input/IT_Related_Leads.xlsx"
SOURCE_NAME = os.path.splitext(os.path.basename(INPUT_FILE))[0]
OUTPUT_FILE = f"leads/{SOURCE_NAME}.csv"

def extract_domain(email):
    """Extracts domain from email, ignoring common freemail providers if necessary."""
    if pd.isna(email) or '@' not in email:
        return None
    domain = email.split('@')[1].strip().lower()
    return domain

def normalize_it_leads(input_path, output_path):
    print(f"Loading raw data from {input_path}...")
    df = pd.read_excel(input_path)
    
    # Initialize the standardized dataframe
    norm_df = pd.DataFrame()
    
    # 1. Generate unique IDs
    norm_df['lead_id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    
    # 2. Split Full Name into First and Last
    # Handles simple splits; more complex names might need a library like nameparser
    def split_name(name):
        parts = str(name).strip().split(' ', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return parts[0], ""
        
    names = df['Full Name'].apply(split_name)
    norm_df['first_name'] = names.apply(lambda x: x[0])
    norm_df['last_name'] = names.apply(lambda x: x[1])
    
    # 3. Map direct columns
    norm_df['email_address'] = df['Email Address'].str.strip()
    norm_df['company_name'] = df['Company Name'].str.strip()
    norm_df['job_title'] = df['Job Title'].str.strip()
    norm_df['industry'] = df['Company Industry (Not mandatory)'].fillna('Unknown').str.strip()
    norm_df['linkedin_url'] = df['LinkedIn URL'].str.strip()
    
    # 4. Derive Company Domain
    norm_df['company_domain'] = norm_df['email_address'].apply(extract_domain)
    
    # 5. Tag source
    norm_df['source_file'] = SOURCE_NAME
    
    # 6. Clean and filter out invalid rows (e.g., missing emails)
    norm_df = norm_df.dropna(subset=['email_address'])
    
    # Save to the universal schema
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    norm_df.to_csv(output_path, index=False)
    print(f"Successfully normalized {len(norm_df)} leads into {output_path}.")
    print("Schema preview:")
    print(norm_df.head(2).to_string())

if __name__ == "__main__":
    normalize_it_leads(INPUT_FILE, OUTPUT_FILE)

