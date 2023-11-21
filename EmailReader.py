import os
import base64
import re

from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from typing import Any


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


def set_connection() -> Any:
    """
    Set connection to gmail API

    Returns:
        service: gmail API service
    """

    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_unread_emails(service, max_results: int = 5) -> list[Any]:
    """
    Get unread emails from gmail API,

    Args:
        service: gmail API service
        max_results: maximum number of emails to get (default: 5)

    Returns:
        messages: list of unread emails
    """

    query = "is:unread is:inbox"
    response = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    messages = []
    if "messages" in response:
        messages.extend(response["messages"])
    return messages


def remove_hyperlinks(text: str) -> str:
    """
    Remove hyperlinks from text

    Args:
        text: text to remove hyperlinks from

    Returns:
        text: text without hyperlinks
    """

    # Remove URLs starting with http/https
    text = re.sub(r"http\S+", "", text)

    # Remove URLs containing '.com'
    text = re.sub(r"\S+\.com\S*", "", text)
    text = re.sub(r"\S+\.net\S*", "", text)
    text = re.sub(r"\S+\.org\S*", "", text)
    text = re.sub(r"\n+", "", text)
    return text


def process_headers(headers):
    email_data = {}
    for header in headers:
        name = header["name"]
        value = header["value"]
        if name.lower() in ["from", "date", "subject"]:
            email_data[name.lower()] = value
    return email_data


def decode_body(data):
    text = base64.urlsafe_b64decode(data.encode("UTF-8")).decode("UTF-8")
    soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text()
    clean_text = remove_hyperlinks(clean_text)
    return clean_text


def get_parts(parts):
    data = []
    if parts:
        for part in parts:
            mimeType = part.get("mimeType")
            body = part.get("body")
            data_part = body.get("data")
            if part.get("parts"):
                data += get_parts(part.get("parts"))
            if data_part:
                text = decode_body(data_part)
                data.append(text)
    return data


def get_email_data(service, message_id: int) -> dict[str, str]:
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    payload = msg["payload"]
    headers = payload["headers"]

    email_data = process_headers(headers)
    email_data["id"] = message_id

    parts = payload.get("parts")
    data = get_parts(parts)
    email_data["text"] = " ".join(data)

    return email_data


def mark_as_read_and_archive(service, message_id):
    service.users().messages().modify(
        userId="me", id=message_id, body={"removeLabelIds": ["UNREAD", "INBOX"]}
    ).execute()
