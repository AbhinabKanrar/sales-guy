import os
import pandas as pd
import uuid
import glob

# --- CONFIGURATION ---
INPUT_DIR = "input"
OUTPUT_DIR = "leads"
CHUNK_SIZE = 50
SOURCE_NAME = "Combined_Leads"

def extract_domain(email):
    if pd.isna(email) or '@' not in email:
        return None
    return str(email).split('@')[1].strip().lower()

def split_name(name):
    parts = str(name).strip().split(' ', 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ""

def process_and_chunk():
    print(f"Scanning for Excel files in {INPUT_DIR}/...")
    
    # Gather all Excel files in the directory
    all_files = glob.glob(os.path.join(INPUT_DIR, "*.xlsx")) + glob.glob(os.path.join(INPUT_DIR, "*.csv"))
    
    if not all_files:
        print("No files found in the input directory.")
        return
        
    all_data = pd.DataFrame()
    
    for file in all_files:
        print(f"Reading {file}...")
        if file.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        # Normalize to standard schema
        norm_df = pd.DataFrame()
        norm_df['lead_id'] = [str(uuid.uuid4()) for _ in range(len(df))]
        
        names = df['Full Name'].apply(split_name) if 'Full Name' in df.columns else pd.Series([("", "")] * len(df))
        norm_df['first_name'] = names.apply(lambda x: x[0])
        norm_df['last_name'] = names.apply(lambda x: x[1])
        
        norm_df['email_address'] = df.get('Email Address', pd.Series()).str.strip()
        norm_df['company_name'] = df.get('Company Name', pd.Series()).str.strip()
        norm_df['job_title'] = df.get('Job Title', pd.Series()).str.strip()
        norm_df['industry'] = df.get('Company Industry (Not mandatory)', pd.Series()).fillna('Unknown').str.strip()
        norm_df['linkedin_url'] = df.get('LinkedIn URL', pd.Series()).str.strip()
        norm_df['company_domain'] = norm_df['email_address'].apply(extract_domain)
        norm_df['source_file'] = os.path.basename(file)
        
        all_data = pd.concat([all_data, norm_df], ignore_index=True)
        
    # Clean up and remove duplicates across all files
    all_data = all_data.dropna(subset=['email_address'])
    all_data = all_data.drop_duplicates(subset=['email_address'], keep='first')
    print(f"Total unique leads after deduplication: {len(all_data)}")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Chunking logic
    total_chunks = (len(all_data) // CHUNK_SIZE) + (1 if len(all_data) % CHUNK_SIZE != 0 else 0)
    
    for i in range(total_chunks):
        start_idx = i * CHUNK_SIZE
        end_idx = start_idx + CHUNK_SIZE
        chunk_df = all_data.iloc[start_idx:end_idx]
        
        output_file = os.path.join(OUTPUT_DIR, f"{i + 1}.csv")
        chunk_df.to_csv(output_file, index=False)
        
    print(f"Successfully generated {total_chunks} chunked CSV files in '{OUTPUT_DIR}/'.")

if __name__ == "__main__":
    process_and_chunk()
