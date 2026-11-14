import os
import pandas as pd
import requests
import json
import time
import glob

# --- CONFIGURATION ---
INPUT_DIR = "leads"
OUTPUT_JSON_DIR = "emails"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "your_openrouter_api_key_here")

def generate_email(first_name, company, industry, job_title):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are Abhinab Kanrar, the Founder and Systems Architect at Mabsisa Inc. (Toronto, Canada). "
        "You engineer mission-critical, air-gapped AI enterprise platforms for highly regulated sectors. "
        "Your objective is to write a ruthlessly concise, hyper-technical cold email to an IT executive. "
        "STRICT CONSTRAINTS: "
        "1. Maximum 4-5 sentences. "
        "2. ZERO marketing fluff. Do NOT use words like 'cutting-edge', 'revolutionary', 'unlock', or 'synergy'. "
        "3. Tone: Direct, intellectually heavy, peer-to-peer CTO level. No fake enthusiasm. "
        "4. DO NOT start with 'I hope this finds you well' or 'My name is...'. "
        "STRUCTURE: "
        "Sentence 1: State a blunt, technical observation about the difficulty of integrating AI into legacy monoliths within their specific [Industry] without violating compliance. "
        "Sentence 2: Explain how you solve this using Mabsisa's 'Zero-Data-Leakage Sovereign Enclaves'—deconstructing their monolith into serverless, asynchronous neural pipelines. "
        "Sentence 3: Emphasize the security constraint (e.g., 100% proprietary IP ownership, hardware-level encryption, zero external data egress). "
        "Sentence 4: A low-friction, high-value Call to Action (e.g., offering to spin up a bespoke, functional UI prototype connected to a dummy dataset within 24 hours to prove the architecture). "
        "Sign off simply as 'Abhinab Kanrar | Founder, Mabsisa Inc.'."
    )

    
    prompt = f"Prospect Name: {first_name}\nJob Title: {job_title}\nCompany: {company}\nIndustry: {industry}"
    
    payload = {
        "model": "nvidia/nemotron-3.5-super-vl:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            print(f"OpenRouter Error ({response.status_code}): {response.text}")
            return None

        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error generating email for {first_name} at {company}: {e}")
        return None

def process_directory():
    print(f"Scanning for chunked CSVs in {INPUT_DIR}/...")
    csv_files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {INPUT_DIR}/. Run the adapter script first.")
        return
        
    os.makedirs(OUTPUT_JSON_DIR, exist_ok=True)
    
    for file_path in csv_files:
        # Extract base name (e.g., '1' from 'output_chunks/1.csv')
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        json_output_path = os.path.join(OUTPUT_JSON_DIR, f"{base_name}.json")
        
        # Skip if already processed
        if os.path.exists(json_output_path):
            print(f"Skipping {file_path} - JSON already exists.")
            continue
            
        print(f"Processing {file_path}...")
        df = pd.read_csv(file_path)
        results = []
        
        for _, row in df.iterrows():
            draft = generate_email(row['first_name'], row['company_name'], row['industry'], row['job_title'])

            print(f"OpenRouter response: {draft}")
            
            lead_data = {
                "lead_id": row['lead_id'],
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email_address": row['email_address'],
                "company_name": row['company_name'],
                "job_title": row['job_title'],
                "industry": row['industry'],
                "generated_draft": draft
            }
            results.append(lead_data)
            
            # API rate limit delay
            time.sleep(1)
            
        # Save JSON
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
            
        print(f"Saved {len(results)} drafts to {json_output_path}")

if __name__ == "__main__":
    process_directory()
