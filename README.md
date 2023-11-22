# Emails Summarizer with GPT and Gmail API

This project is just for fun, if you want to improve it feel free to make a pull request.

## Setup

First of all, let’s understand our environment. We are using the Gmail API to access emails data (because its simple). To access the api, firstly, you need to make a desktop project in [google's console](https://console.developers.google.com/). Then follow the steps [here](https://support.google.com/googleapi/answer/6158841?hl=en) to enable the API. After enabling it don't forget to download the credentials to a JSON file and the email you want as a test user, it will be important later on. Then make sure you got an API key from OpenAI.

Install the requirements.

```bash
pip install -r requirements.txt
```

## Understand the code

Firstly, the code is separated into three modules. main.py, Summarizer.py, EmailReader.py Each has the code to do what its name says.

To run the file.

```bash
python main.py first-arg second-arg third-arg
```

first arg -> represent the maximum results you want to read.  
second arg -> represent if you want to generate text to speech file.  
third arg -> represent if want to read and archive the emails.

The following is so important for the code to work, it makes the connection with your google account and after reading the `credentials.json` files we saved earlier it makes a `token.json` for easier access, if the token is finished delete the file.

```python
def set_connection() -> Any:
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
```

## Moreover

Read the rest of the code it will be clear. feel free to connect with me for fun projects to work on.
