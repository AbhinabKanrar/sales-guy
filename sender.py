import os
import glob
import json
import time
from mail_engine import MailEngine

INPUT_DIR = "emails"
    
def generate_subject(industry, job_title, company):
    industry_lower = str(industry).lower()
    title_lower = str(job_title).lower()

    # 1. Security & Compliance Roles (CISO, VP Security, Risk)
    # They care about leaks, air-gaps, and regulations.
    if 'security' in title_lower or 'ciso' in title_lower or 'risk' in title_lower:
        if 'health' in industry_lower or 'medical' in industry_lower:
            return f"HIPAA-compliant AI architecture for {company}"
        elif 'financ' in industry_lower or 'bank' in industry_lower:
            return f"Zero-data-leakage inference for {company}"
        else:
            return f"Air-gapped LLM architecture for {company}"

    # 2. Engineering & Architecture Roles (VP Engineering, CTO)
    # They care about systems, monoliths, and pipelines.
    elif 'engineering' in title_lower or 'architecture' in title_lower or 'cto' in title_lower:
        if 'health' in industry_lower:
            return f"EHR monolith deconstruction at {company}"
        elif 'financ' in industry_lower or 'bank' in industry_lower:
            return f"Core system LLM inference at {company}"
        else:
            return f"Inference architecture review: {company}"

    # 3. Data & Analytics Roles (Director of Data, Analytics)
    # They care about data gravity, pipelines, and sovereignty.
    elif 'data' in title_lower or 'analytics' in title_lower:
        return f"Data sovereignty and AI inference at {company}"

    # 4. Fallback Logic (If the title doesn't match the keywords above)
    else:
        if 'health' in industry_lower:
            return f"Healthcare AI infrastructure for {company}"
        elif 'financ' in industry_lower or 'bank' in industry_lower:
            return f"Financial AI infrastructure for {company}"
        else:
            return f"Architecture review: {company}"

def process_directory(mailer : MailEngine):
    print(f"Scanning for chunked JSONs in {INPUT_DIR}/...")
    json_files = glob.glob(os.path.join(INPUT_DIR, "*.json"))

    if not json_files:
        print(f"No json files found in {INPUT_DIR}/. Run the adapter script first")

    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as file:
            print(f'Starting processing: {file_path}')
            drafts = json.load(file)
            for draft in drafts:
                if not draft.get('generated_draft'):
                    print(f"Skipping {draft.get('email_address')} - No draft generated in {file_path}")
                    continue

                company = draft.get('company_name', '')
                recipient = draft['email_address']
                body = draft['generated_draft']
                industry = draft.get('industry', '')
                job_title = draft.get('job_title', '')
                subject_line = generate_subject(industry, job_title, company)

                try:
                    mailer.send_email(recipient, body, subject_line)
                except Exception as e:
                    print(f'Unable to send mail to {recipient} from {file_path}')
                finally:
                    time.sleep(75)

            print(f'Completed processing: {file_path}')

if __name__ == "__main__":
    mailer = MailEngine(default_from="abhinab.kanrar@mabsisa.com")
    try:
        process_directory(mailer)
    except Exception as e:
        print(f"An error occurred: {e}")        
    finally:
        mailer.close_connection()

