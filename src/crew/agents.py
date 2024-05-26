import os
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.get_thread import GmailGetThread
from langchain_community.tools.tavily_search import TavilySearchResults
from textwrap import dedent
from crewai import Agent
from .tools import CreateDraftTool

os.environ["OPENAI_MODEL_NAME"]="gpt-4o"


class EmailFilterAgents():
    def __init__(self):
        self.gmail = GmailToolkit()

    def email_filter_agent(self):
        return Agent(
            role='Senior Email Analyst',
            goal='Filter out non-essential emails like newsletters and promotional content',
            backstory=dedent("""\
				As a Senior Email Analyst, you have extensive experience in email content analysis.
				You are adept at distinguishing important emails from spam, newsletters, and other
				irrelevant content. Your expertise lies in identifying key patterns and markers that
				signify the importance of an email."""),
            verbose=True,
            allow_delegation=False
        )

    def email_action_agent(self):
        return Agent(
            role='Email Action Specialist',
            goal='Identify action-required emails and compile a list of their IDs',
            backstory=dedent("""\
				With a keen eye for detail and a knack for understanding context, you specialize
				in identifying emails that require immediate action. Your skill set includes interpreting
				the urgency and importance of an email based on its content and context."""),
            tools=[
                GmailGetThread(api_resource=self.gmail.api_resource),
                TavilySearchResults()
            ],
            verbose=True,
            allow_delegation=False,
        )

    def email_response_writer(self):
        return Agent(
            role='Email Response Writer',
            goal='Draft responses to action-required emails',
            backstory=dedent("""\
				You are a skilled writer, adept at crafting clear, concise, and effective email responses.
				Your strength lies in your ability to communicate effectively, ensuring that each response is
				tailored to address the specific needs and context of the email."""),
            tools=[
                TavilySearchResults(),
                GmailGetThread(api_resource=self.gmail.api_resource),
                CreateDraftTool.create_draft
            ],
            verbose=True,
            allow_delegation=False,
        )

    def complaint_categorizer_agent(self):
        return Agent(
            role='Complaint Categorizer',
            goal='Categorize emails that contain customer complaints',
            backstory=dedent("""\
	            As a Complaint Categorizer, you have the ability to detect and categorize emails containing customer complaints.
	            Your role is crucial in ensuring that all complaints are identified and processed appropriately."""),
            verbose=True,
            allow_delegation=False
        )

    def complaint_summarizer_agent(self):
        return Agent(
            role='Complaint Summarizer',
            goal='Summarize the contents of complaint emails',
            backstory=dedent("""\
	            As a Complaint Summarizer, your expertise lies in extracting the essence of customer complaints
	            and summarizing them concisely."""),
            verbose=True,
            allow_delegation=False
        )

    def complaint_comparison_agent(self):
        return Agent(
            role='Complaint Comparison Specialist',
            goal='Compare new complaints against existing ones and count similar complaints',
            backstory=dedent("""\
	                As a Complaint Comparison Specialist, you ensure that recurring complaints are tracked and documented.
	                Your role involves comparing new complaints with existing ones and updating the count of similar complaints."""),
            verbose=True,
            allow_delegation=False
        )
