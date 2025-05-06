import os
import boto3
import zipfile
from botocore.exceptions import ClientError
from datetime import datetime

# === CONFIGURATION ===
REPORTS_FOLDER = "daily_reports"
ZIP_FILE_NAME = "daily_reports.zip"
BUCKET_NAME = "company-daily-reports-automation"  # Change if needed

# === STEP 1: Connect to S3 ===
s3 = boto3.client('s3')

# === STEP 2: Create Bucket if it doesn't exist ===
def ensure_bucket_exists(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' already exists.")
    except ClientError:
        print(f"🪣 Creating bucket '{bucket_name}'...")
        try:
            s3.create_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' created successfully.")
        except Exception as e:
            print(f"❌ Failed to create bucket: {e}")
            exit(1)

# === STEP 3: Ensure report folder exists and populate dummy files ===
def ensure_reports_exist(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"📁 Created folder: {folder}")

    if not os.listdir(folder):
        print("📝 Adding dummy reports...")
        for i in range(1, 4):
            filename = f"report_{i}.txt"
            with open(os.path.join(folder, filename), 'w') as f:
                f.write(f"This is dummy report #{i} for {datetime.today().date()}")
        print("✅ Dummy reports created.")
    else:
        print("📄 Reports already present.")

# === STEP 4: Create ZIP archive ===
def zip_reports(source_folder, zip_filename):
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
        print("♻️ Removed existing ZIP file.")

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk(source_folder):
            for file in files:
                path = os.path.join(root, file)
                arcname = os.path.relpath(path, start=source_folder)
                zipf.write(path, arcname)
    print(f"✅ Reports zipped into: {zip_filename}")

# === STEP 5: Upload ZIP to S3 ===
def upload_zip_to_s3(zip_file, bucket_name):
    try:
        s3.upload_file(zip_file, bucket_name, zip_file)
        print(f"🚀 Uploaded '{zip_file}' to S3 bucket '{bucket_name}' successfully.")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        exit(1)

# === MAIN SCRIPT ===
if __name__ == "__main__":
    ensure_bucket_exists(BUCKET_NAME)
    ensure_reports_exist(REPORTS_FOLDER)
    zip_reports(REPORTS_FOLDER, ZIP_FILE_NAME)
    upload_zip_to_s3(ZIP_FILE_NAME, BUCKET_NAME)
