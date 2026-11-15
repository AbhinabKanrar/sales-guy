import os
import glob
import json
from mail_engine import MailEngine

INPUT_DIR = "emails"
    

def process_directory(mailer : MailEngine):
    print(f"Scanning for chunked JSONs in {INPUT_DIR}/...")
    json_files = glob.glob(os.path.join(INPUT_DIR, "*.json"))

    if not json_files:
        print(f"No json files found in {INPUT_DIR}/. Run the adapter script first")

    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as file:
            drafts = json.load(file)
            for draft in drafts:
                print(draft)

if __name__ == "__main__":
    mailer = MailEngine(default_from="abhinab.kanrar@mabsisa.com")
    try:
        process_directory(mailer)
    except Exception as e:
        print(f"An error occurred: {e}")        
    finally:
        mailer.close_connection()

