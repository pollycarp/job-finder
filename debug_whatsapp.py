"""Test WhatsApp notification with a single dummy job."""
from whatsapp_notifier import send_jobs_to_whatsapp

test_jobs = [
    {
        "Job Title": "Data Scientist",
        "Company": "Safaricom PLC",
        "Location": "Nairobi",
        "Job URL": "https://brightermonday.co.ke/listings/test-job-123",
    }
]

sent = send_jobs_to_whatsapp(test_jobs)
print(f"Messages sent: {sent}")
