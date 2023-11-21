import sys

from typing import Any
from EmailReader import (
    set_connection,
    get_unread_emails,
    get_email_data,
    mark_as_read_and_archive,
)
from Summarizer import summarize


def main(max_result: int):
    try:
        service = set_connection()
    except Exception as e:
        print("error in connection...")
        print(e)
        exit()

    unread_emails: list[Any] = get_unread_emails(service, max_result)
    all_emails: list[str] = []

    # print the body of the email messages
    for email in unread_emails:
        email_data = get_email_data(service, email["id"])

        if "text" in email_data and len(email_data["text"]):
            all_emails.append(
                f"""
                ------------------------------------
                From: {email_data['from']}
                Subject: {email_data['subject']}
                Date: {email_data['date']}
                Text: {email_data['text'].strip()}
                ------------------------------------    
                """
            )
            mark_as_read_and_archive(service, email["id"])

    for email in all_emails:
        print(email)
        print("\n")


if __name__ == "__main__":
    max_result = sys.argv[1] if len(sys.argv) > 1 else 5
    main(max_result)
