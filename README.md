# Google-Form-PDF-to-Email-Automation

This project automates the generation and delivery of structured PDF reports based on Google Form submissions. It is designed to simplify documentation workflows like OPL (One Point Lessons) where engineers submit operational details and images.

Features:
1. Google Forms Integration – Collects structured responses and uploaded images
2. Google Apps Script – Triggers on form submission, processes links, and sends data to backend
3. Python Flask API – Receives and processes form data on a hosted backend (PythonAnywhere)
4. Image Conversion – Automatically converts PNG/WebP images to JPEG using Pillow
5. PDF Generation – Formats all responses into a clean, structured PDF using FPDF
6. Email Automation – Sends the generated report to a recipient via Gmail SMTP

Tech Stack
Python 3.13, Flask, FPDF, Pillow, Requests
Google Apps Script (JavaScript-based)
PythonAnywhere for backend hosting
Google Drive & Gmail SMTP for file access and email delivery

How It Works
Engineer submits a Google Form with form fields and image uploads.
Apps Script is triggered → formats links → makes images public → sends payload to Flask API.
Flask backend downloads images, converts formats, embeds data into a PDF.
PDF is sent to the recipient’s email address (field in form) automatically.

Form Link: https://docs.google.com/forms/d/e/1FAIpQLSeaZaiusgW0Hj3IPJKOJYyNe6B-mS-RxwC18hP11nBNv9sT3A/viewform?usp=dialog
