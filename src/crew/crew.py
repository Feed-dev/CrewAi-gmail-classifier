from crewai import Crew
from .agents import EmailFilterAgents
from .tasks import EmailFilterTasks


class EmailFilterCrew():
    def __init__(self):
        agents = EmailFilterAgents()
        self.filter_agent = agents.email_filter_agent()
        self.action_agent = agents.email_action_agent()
        self.writer_agent = agents.email_response_writer()
        self.complaint_categorizer = agents.complaint_categorizer_agent()
        self.complaint_summarizer = agents.complaint_summarizer_agent()
        self.complaint_comparison = agents.complaint_comparison_agent()

    def kickoff(self, state):
        print("### Filtering emails")
        tasks = EmailFilterTasks()
        crew = Crew(
            agents=[
                self.filter_agent,
                self.action_agent,
                self.writer_agent,
                self.complaint_categorizer,
                self.complaint_summarizer,
                self.complaint_comparison
            ],
            tasks=[
                tasks.filter_emails_task(self.filter_agent, self._format_emails(state['emails'])),
                tasks.action_required_emails_task(self.action_agent),
                tasks.draft_responses_task(self.writer_agent),
                tasks.categorize_complaints_task(self.complaint_categorizer, self._format_emails(state['emails'])),
                tasks.summarize_complaints_task(self.complaint_summarizer, state['complaint_emails']),
                # added way to load existing complaints from a file for comparison
                tasks.compare_complaints_task(self.complaint_comparison, state['complaint_emails'],
                                              self.load_existing_complaints())
            ],
            verbose=2,
            memory=True
        )
        result = crew.kickoff()
        return {**state, "action_required_emails": result}

    def _format_emails(self, emails):
        emails_string = []
        for email in emails:
            print(email)
            arr = [
                f"ID: {email['id']}",
                f"- Thread ID: {email['threadId']}",
                f"- Snippet: {email['snippet']}",
                f"- From: {email['sender']}",
                f"--------"
            ]
            emails_string.append("\n".join(arr))
        return "\n".join(emails_string)

    def load_existing_complaints(self):
        existing_complaints = []
        try:
            with open('complaints_summaries.txt', 'r') as file:
                for line in file:
                    existing_complaints.append(line.strip())
        except FileNotFoundError:
            pass
        return existing_complaints
