from flask import Flask, request
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import os
import re
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = Flask(__name__)

# --- Validate Email ---
def is_valid_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email)

# --- Convert Google Drive link to direct download ---
def convert_to_direct_link(drive_url):
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", drive_url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return None

# --- Download image from Google Drive ---
def download_image(drive_url, filename):
    if not drive_url:
        print(f"[ERROR] No URL provided for {filename}")
        return None

    direct_url = convert_to_direct_link(drive_url)
    print(f"[DEBUG] Final direct download URL for {filename}: {direct_url}")

    if not direct_url:
        print(f"[ERROR] Invalid Drive URL: {drive_url}")
        return None

    try:
        r = requests.get(direct_url)
        print(f"[INFO] HTTP status for {filename}: {r.status_code}")
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            print(f"[INFO] Downloaded and saved {filename}")
            return filename
        else:
            print(f"[ERROR] Failed to download {filename}. Status: {r.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception downloading {filename}: {e}")
    return None

# --- Main endpoint ---
@app.route('/submit', methods=['POST'])
def receive_data():
    data = request.json
    email = data.get('email', '').strip()

    print(f"[INFO] Received form submission for: {email}")
    print(f"[INFO] Before URL: {data.get('before_image_url')}")
    print(f"[INFO] After URL: {data.get('after_image_url')}")

    if not is_valid_email(email):
        print("[ERROR] Invalid email format.")
        return {'status': 'error', 'message': 'Invalid email address'}, 400

    pdf_file = generate_pdf(data)
    send_email(email, pdf_file)

    # Cleanup
    for img in ["before.jpg", "after.jpg"]:
        if os.path.exists(img):
            os.remove(img)

    return {'status': 'success'}

# --- Generate PDF from form data ---
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "One Point Lesson (OPL) Report", ln=True, align='C')
    pdf.ln(10)

    # Text Fields
    def write_field(label, value):
        if value:
            pdf.set_font("Arial", 'B', 12)
            pdf.multi_cell(0, 10, f"{label}:", border=0)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, f"{value}\n", border=0)
            pdf.ln(2)

    write_field("Department", data.get("department"))
    write_field("Site", data.get("site"))
    write_field("Shift Engineer", data.get("shift_engineer"))
    write_field("Equipment", data.get("equipment"))
    write_field("Area", data.get("area"))
    write_field("Objective", data.get("objective"))
    write_field("Issue Description", data.get("issue_description"))
    write_field("Reason for Issue", data.get("reason"))
    write_field("Remedial Action", data.get("remedial_action"))
    write_field("Troubleshooting Action", data.get("troubleshooting_action"))

    # Images
    before_path = download_image(data.get("before_image_url"), "before.jpg")
    after_path = download_image(data.get("after_image_url"), "after.jpg")

    if before_path:
        print("[INFO] Embedding before.jpg in PDF")
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Before:", ln=True)
        pdf.image(before_path, w=80)
        pdf.ln(10)

    if after_path:
        print("[INFO] Embedding after.jpg in PDF")
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "After:", ln=True)
        pdf.image(after_path, w=80)

    filename = "opl_report.pdf"
    pdf.output(filename)
    print(f"[INFO] PDF generated: {filename}")
    return filename

# --- Send Email with PDF attachment ---
def send_email(to_email, file_path):
    sender = os.getenv("EMAIL_FROM")
    password = os.getenv("EMAIL_PASSWORD")

    print(f"[INFO] Sending email to {to_email} from {sender}")

    msg = EmailMessage()
    msg["Subject"] = "Your OPL Report"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content("Attached is your One Point Lesson (OPL) report.")

    try:
        with open(file_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=file_path)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
            print("[INFO] Email sent successfully ✅")

    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
