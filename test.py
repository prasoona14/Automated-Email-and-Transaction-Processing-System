import imaplib

email_user = "projectstest288@gmail.com"
email_password = "cdjo rvua bvkf mzim"

try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_user, email_password)
    print("Login successful!")
    mail.logout()
except Exception as e:
    print(f"Error: {e}")
