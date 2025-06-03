from app import db, Email
from utils.spam_detector import predict_spam

def save_emails_to_db(fetched_emails, user_id):
    """
    Saves fetched emails into the database after classifying as Spam or Not Spam.

    Args:
        fetched_emails (list): List of emails with 'from', 'subject', 'body' fields.
        user_id (int): ID of the user who owns these emails.
    """
    for email_data in fetched_emails:
        sender = email_data.get('from', '')
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')

        # Predict if email is Spam or Not Spam
        classification = predict_spam(subject + " " + body)

        # Check if email has an image (basic check using keywords)
        has_image = 'image' in body.lower() or 'attachment' in body.lower()

        # Create Email record
        new_email = Email(
            user_id=user_id,
            sender=sender,
            subject=subject,
            body=body,
            classification=classification,
            has_image=has_image
        )

        # Add to database session
        db.session.add(new_email)

    # Commit all emails at once
    db.session.commit()
