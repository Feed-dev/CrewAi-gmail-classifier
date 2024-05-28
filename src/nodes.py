import os
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class Nodes():
    def __init__(self):
        self.creds = None
        self.authenticate_gmail_api()

    def authenticate_gmail_api(self):
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    def check_email(self, state):
        print("# Checking for new emails")
        try:
            service = build("gmail", "v1", credentials=self.creds)
            query = "newer_than:1d"
            results = service.users().messages().list(userId="me", q=query).execute()
            messages = results.get('messages', [])
            print(f"Retrieved {len(messages)} messages")  # Debug statement

            checked_emails = state.get('checked_emails_ids', [])
            print(f"Previously checked emails: {checked_emails}")  # Debug statement
            thread = []
            new_emails = []
            for msg in messages:
                msg_id = msg['id']
                msg_detail = service.users().messages().get(userId="me", id=msg_id).execute()
                thread_id = msg_detail['threadId']
                snippet = msg_detail['snippet']
                sender = None
                for header in msg_detail['payload']['headers']:
                    if header['name'] == 'From':
                        sender = header['value']
                        break
                print(f"Processing email from {sender} with snippet: {snippet}")  # Debug statement
                if (msg_id not in checked_emails) and (thread_id not in thread) and ('feeddev75@gmail.com' not in sender):
                    thread.append(thread_id)
                    new_emails.append(
                        {
                            "id": msg_id,
                            "threadId": thread_id,
                            "snippet": snippet,
                            "sender": sender
                        }
                    )
            checked_emails.extend([msg['id'] for msg in messages])
            print(f"New emails: {new_emails}")  # Debug statement
            return {
                **state,
                "emails": new_emails,
                "checked_emails_ids": checked_emails
            }
        except HttpError as error:
            print(f"An error occurred: {error}")
            return state

    def wait_next_run(self, state):
        print("## Waiting for 180 seconds")
        time.sleep(180)
        return state

    def new_emails(self, state):
        if len(state['emails']) == 0:
            print("## No new emails")
            return "end"
        else:
            print("## New emails")
            return "continue"

    def categorize_complaints(self, state):
        print("# Categorizing complaint emails")
        complaint_emails = [email for email in state['emails'] if 'complaint' in email['snippet'].lower()]
        print(f"Categorized complaints: {complaint_emails}")  # Debug statement
        return {**state, "complaint_emails": complaint_emails}

    def summarize_complaints(self, state):
        print("# Summarizing complaint emails")
        summaries = []
        for email in state['complaint_emails']:
            summary = f"Summary of complaint: {email['snippet'][:100]}"
            summaries.append(summary)
        print(f"Summaries: {summaries}")  # Debug statement
        return {**state, "summaries": summaries}

    def save_summaries(self, state):
        print("# Saving summaries to file")
        with open('complaints_summaries.txt', 'a') as file:
            for summary in state['summaries']:
                file.write(f"{summary}\n")
        print("Summaries saved to file")  # Debug statement
        return state
