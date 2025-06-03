import imaplib
import email
from email.header import decode_header
import os

def clean(text):
    # Clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def fetch_emails(user_email, app_password):
    imap_server = "imap.gmail.com"
    
    # Connect to the server
    mail = imaplib.IMAP4_SSL(imap_server)

    # Login
    mail.login(user_email, app_password)

    # Select inbox
    mail.select("inbox")

    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()
    
    fetched_emails = []
    
    for num in email_ids[-10:]:  # Fetch last 10 emails for now
        _, data = mail.fetch(num, "(RFC822)")
        
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                from_ = msg.get("From")

                # If the email message is multipart
                if msg.is_multipart():
                    body = ""
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        try:
                            # Get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass

                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            break
                else:
                    # Extract content type of email
                    body = msg.get_payload(decode=True).decode()

                email_data = {
                    "from": from_,
                    "subject": subject,
                    "body": body
                }
                fetched_emails.append(email_data)
    
    mail.logout()
    return fetched_emails
