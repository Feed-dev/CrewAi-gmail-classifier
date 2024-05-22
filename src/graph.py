from dotenv import load_dotenv
from langgraph.graph import StateGraph
from .state import EmailsState
from .nodes import Nodes
from .crew.crew import EmailFilterCrew

load_dotenv()


class WorkFlow():
	def __init__(self):
		nodes = Nodes()
		workflow = StateGraph(EmailsState)

		workflow.add_node("check_new_emails", nodes.check_email)
		workflow.add_node("wait_next_run", nodes.wait_next_run)
		workflow.add_node("draft_responses", EmailFilterCrew().kickoff)
		workflow.add_node("categorize_complaints", nodes.categorize_complaints)
		workflow.add_node("summarize_complaints", nodes.summarize_complaints)
		workflow.add_node("save_summaries", nodes.save_summaries)

		workflow.set_entry_point("check_new_emails")
		workflow.add_conditional_edges(
				"check_new_emails",
				nodes.new_emails,
				{
					"continue": 'draft_responses',
					"end": 'wait_next_run'
				}
		)
		workflow.add_edge('draft_responses', 'categorize_complaints')
		workflow.add_edge('categorize_complaints', 'summarize_complaints')
		workflow.add_edge('summarize_complaints', 'save_summaries')
		workflow.add_edge('save_summaries', 'wait_next_run')
		workflow.add_edge('wait_next_run', 'check_new_emails')
		self.app = workflow.compile()
