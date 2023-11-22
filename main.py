import sys

from typing import Any
from EmailReader import (
    set_connection,
    get_unread_emails,
    get_email_data,
    mark_as_read_and_archive,
)
from Summarizer import summarize, text_to_speech


def main(max_result: int, tts: int, read_and_archive):
    try:
        service = set_connection()
    except Exception as e:
        print("error in connection...")
        print(e)
        exit()

    unread_emails: list[Any] = get_unread_emails(service, max_result)
    all_emails: list[str] = []

    print("Getting emails data...")
    for email in unread_emails:
        email_data = get_email_data(service, email["id"])

        if read_and_archive:
            mark_as_read_and_archive(service, email["id"])

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

    summaries: list[str] = []
    for email in all_emails:
        summary = summarize(email)
        if tts:
            text_to_speech(summary)
        summaries.append(summary)

    print(summaries)
    for i, summary in enumerate(summaries):
        print(f"{i+1} Summary:\n {summary} ")


if __name__ == "__main__":
    max_result: int = sys.argv[1] if len(sys.argv) > 1 else 5
    tts: bool = sys.argv[2] if len(sys.argv) > 2 else 0
    read_and_archive: bool = sys.argv[3] if len(sys.argv) > 3 else 0

    main(max_result, tts, read_and_archive)
