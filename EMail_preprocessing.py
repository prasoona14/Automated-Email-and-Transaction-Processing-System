import imaplib
import email
from email.header import decode_header
import os

# Email Preprocessing Agent
class EmailPreprocessingAgent:
    def __init__(self, email_server, email_user, email_password, output_directory):
        """
        Initialize the email preprocessing agent.

        Args:
            email_server (str): The IMAP server (e.g., imap.gmail.com).
            email_user (str): The email account username.
            email_password (str): The email account password.
            output_directory (str): Directory to save extracted images.
        """
        self.email_server = email_server
        self.email_user = email_user
        self.email_password = email_password
        self.output_directory = output_directory
        self.mail = None

    def connect_to_email_server(self):
        """Connect to the IMAP email server and log in."""
        try:
            self.mail = imaplib.IMAP4_SSL(self.email_server)
            self.mail.login(self.email_user, self.email_password)
            self.mail.select("inbox")  # Select the inbox folder
            print("Connected to email server successfully.")
        except Exception as e:
            print(f"Error connecting to email server: {e}")

    def fetch_emails(self):
        """Fetch unread emails."""
        try:
            _, messages = self.mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            print(f"Found {len(email_ids)} unread emails.")
            return email_ids
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def process_email(self, email_id):
        """Process a single email."""
        try:
            _, msg_data = self.mail.fetch(email_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parse email content
                    msg = email.message_from_bytes(response_part[1])

                    # Get email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    print(f"Processing email with subject: {subject}")

                    # Get email sender
                    from_ = msg.get("From")
                    print(f"From: {from_}")

                    # Extract email text and attachments
                    email_text = ""
                    images = []
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                # Extract plain text
                                email_text = part.get_payload(decode=True).decode()
                            elif part.get_content_disposition() in ("inline", "attachment"):
                                # Save inline or attached images
                                filename = part.get_filename()
                                if filename:
                                    filepath = os.path.join(self.output_directory, filename)
                                    with open(filepath, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                    images.append(filepath)
                    else:
                        # If the email is not multipart
                        email_text = msg.get_payload(decode=True).decode()

                    print(f"Extracted text: {email_text}")
                    print(f"Extracted images: {images}")

        except Exception as e:
            print(f"Error processing email: {e}")

    def run(self):
        """Run the agent to process emails."""
        self.connect_to_email_server()
        email_ids = self.fetch_emails()
        for email_id in email_ids:
            self.process_email(email_id)


# Example Usage
if __name__ == "__main__":
    email_server = "imap.gmail.com"
    email_user = "projectstest288@gmail.com"
    email_password = "cdjo rvua bvkf mzim"  # Replace with your actual App Password
    output_directory = "./attachments"

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Initialize and run the agent
    agent = EmailPreprocessingAgent(email_server, email_user, email_password, output_directory)
    agent.run()
