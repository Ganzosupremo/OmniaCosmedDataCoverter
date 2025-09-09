"""Email notification service for job completion."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
    
    def send_job_completion_email(
        self, 
        to_email: str, 
        user_name: str, 
        job_id: str, 
        status: str,
        download_url: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Send job completion notification email."""
        
        if not self.smtp_username or not self.smtp_password:
            print("SMTP credentials not configured, skipping email notification")
            return
        
        subject = f"COSMED Analysis Job {status.title()} - {job_id[:8]}"
        
        # Create email content
        if status == "completed":
            body = f"""
            Dear {user_name},

            Your COSMED phase analysis job has been completed successfully!

            Job ID: {job_id}
            Status: {status.title()}

            You can download your results using the link below:
            {download_url}

            This download link will be valid for 7 days.

            Thank you for using COSMED Phase Analyzer!

            Best regards,
            The COSMED Phase Analyzer Team
            """
        else:
            body = f"""
            Dear {user_name},

            Your COSMED phase analysis job has failed to complete.

            Job ID: {job_id}
            Status: {status.title()}
            Error: {error_message or 'Unknown error occurred'}

            Please check your input files and try again. If the problem persists,
            please contact our support team.

            Best regards,
            The COSMED Phase Analyzer Team
            """
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable TLS encryption
            server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            print(f"Email notification sent to {to_email} for job {job_id}")
            
        except Exception as e:
            print(f"Failed to send email notification: {e}")


# Global email service instance
email_service = EmailService()


class TestEmailService:
    """Test email service that logs emails instead of sending them."""
    
    def __init__(self):
        self.sent_emails = []
    
    def send_job_completion_email(
        self, 
        to_email: str, 
        user_name: str, 
        job_id: str, 
        status: str,
        download_url: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Mock email sending for testing."""
        email_data = {
            "to_email": to_email,
            "user_name": user_name,
            "job_id": job_id,
            "status": status,
            "download_url": download_url,
            "error_message": error_message,
            "sent_at": str(os.getenv("TEST_TIMESTAMP", "2024-01-01T12:00:00"))
        }
        
        self.sent_emails.append(email_data)
        print(f"TEST MODE: Email logged for {to_email} - Job {job_id} - Status: {status}")
        
        return email_data
    
    def get_sent_emails(self):
        """Get all logged emails for testing."""
        return self.sent_emails
    
    def clear_emails(self):
        """Clear the email log for testing."""
        self.sent_emails = []
    
    def test_smtp_connection(self) -> dict:
        """Test SMTP connection (mock for testing)."""
        return {
            "status": "connected",
            "smtp_server": "test.smtp.example.com",
            "smtp_port": 587,
            "tls_enabled": True,
            "authentication": "successful",
            "test_mode": True
        }


# Test email service instance
test_email_service = TestEmailService()


def get_email_service(test_mode: bool = False):
    """Get email service instance (real or test)."""
    if test_mode or os.getenv("EMAIL_TEST_MODE", "false").lower() == "true":
        return test_email_service
    return email_service
