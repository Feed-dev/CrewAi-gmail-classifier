from src.graph import WorkFlow

if __name__ == "__main__":
    app = WorkFlow().app
    initial_state = {
        "checked_emails_ids": [],
        "emails": [],
        "action_required_emails": {},
        "complaint_emails": [],
        "summaries": []
    }
    app.invoke(initial_state)
