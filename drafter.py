import os
import pandas as pd
import requests
import json
import time
import random
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURATION ---
INPUT_DIR = "leads"
OUTPUT_JSON_DIR = "emails"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "your_openrouter_api_key_here")

# Setting the model back to your preferred Nvidia model
MODEL = "nvidia/nemotron-3.5-super-vl:free"

# 5 concurrent threads is safe. If you get too many 429s, lower this to 3.
MAX_CONCURRENT_CALLS = 3

MAX_RETRIES = 5

def generate_email(row):
    # JITTER: Random micro-delay so threads don't hit the API at the exact same millisecond
    time.sleep(random.uniform(0.1, 1.5))
    
    first_name = row['first_name']
    company = row['company_name']
    industry = row['industry']
    job_title = row['job_title']
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are Abhinab Kanrar, the Founder and Systems Architect at Mabsisa Inc. (Toronto, Canada). "
        "You engineer mission-critical, air-gapped AI enterprise platforms for highly regulated sectors. "
        "Your objective is to write a ruthlessly concise, hyper-technical cold email to an IT executive. "
        "STRICT CONSTRAINTS: "
        "1. You MUST start the email by addressing the prospect by their first name on the first line (e.g., 'John,'). "
        "2. Maximum 5 sentences following the greeting. "
        "3. ZERO marketing fluff. Do NOT use words like 'quick chat', 'synergy', 'touch base', or 'revolutionary'. "
        "4. Tone: Direct, intellectually heavy, peer-to-peer CTO level. No fake enthusiasm. "
        "5. DO NOT use generic pleasantries like 'I hope this finds you well'. "
        "6. FORMATTING: You MUST use blank lines (paragraph breaks) to separate the sections. Do not write a single wall of text. "
        "STRUCTURE: "
        "Greeting: [First Name],\n\n"
        "Paragraph 1 (Sentence 1): State a blunt, technical observation about the difficulty of integrating AI into legacy monoliths within their specific [Industry] without violating compliance.\n\n"
        "Paragraph 2 (Sentences 2 & 3): Explain how Mabsisa resolves this via 'Zero-Data-Leakage Sovereign Enclaves'—deconstructing their monolith into serverless, asynchronous neural pipelines. Emphasize the security constraints (100% proprietary IP ownership, hardware-level encryption, zero external data egress).\n\n"
        "Paragraph 3 (Sentences 4 & 5): Offer to deploy a bespoke, functional UI prototype connected to a dummy dataset within 24 hours. Propose a brief technical scoping call to review their specific integration constraints.\n\n"
        "Sign-off:\nBest,\nAbhinab Kanrar | Founder, Mabsisa Inc. | mabsisa.com"
    )
    
    prompt = f"Prospect Name: {first_name}\nJob Title: {job_title}\nCompany: {company}\nIndustry: {industry}"
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            
            # Explicitly catch 429 Rate Limits
            if response.status_code == 429:
                # Progressive backoff: 5s, then 10s, then 15s
                wait_time = 5 * (attempt + 1) 
                print(f"Rate limit (429) for {first_name}. Thread pausing for {wait_time}s (Attempt {attempt + 1}/{MAX_RETRIES})...")
                time.sleep(wait_time)
                continue
                
            if response.status_code != 200:
                print(f"OpenRouter Error ({response.status_code}) for {first_name}: {response.text}")
                return None
                
            return response.json()['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            print(f"Request failed for {first_name} at {company}: {e}")
            time.sleep(3) # Wait briefly on a network failure before retrying
            
    print(f"Failed to generate email for {first_name} after {max_retries} attempts.")
    return None

def process_chunk(file_path):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    json_output_path = os.path.join(OUTPUT_JSON_DIR, f"{base_name}.json")
    
    if os.path.exists(json_output_path):
        print(f"Skipping {file_path} - JSON already exists.")
        return
        
    print(f"Processing {file_path} in parallel (Max {MAX_CONCURRENT_CALLS} threads)...")
    df = pd.read_csv(file_path)
    results = []
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_CALLS) as executor:
        future_to_row = {executor.submit(generate_email, row): row for _, row in df.iterrows()}
        
        for future in as_completed(future_to_row):
            row = future_to_row[future]
            draft = future.result()
            
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
            
    # Save JSON
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully drafted and saved {len(results)} emails to {json_output_path}")

def process_directory():
    print(f"Scanning for chunked CSVs in {INPUT_DIR}/...")
    csv_files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {INPUT_DIR}/. Run the adapter script first.")
        return
        
    os.makedirs(OUTPUT_JSON_DIR, exist_ok=True)
    
    for file_path in csv_files:
        process_chunk(file_path)

if __name__ == "__main__":
    process_directory()
