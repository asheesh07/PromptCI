from langgraph.graph import StateGraph,END
from langgraph.constants import Send
from langgraph.constants import Send

from agent.state import PromptCIState
from agent.nodes.fetch_context import fetch_context
from agent.nodes.diff_analyst import diff_analyst
from agent.nodes.test_generator import test_generator
from agent.nodes.regression_runner import regression_runner
from agent.nodes.safety_checker import safety_checker
from agent.nodes.judge import judge
from agent.nodes.report_writer import report_writer

def fan_out(state: PromptCIState):
        return [
            Send("regression_runner", state),
            Send("safety_checker", state)
        ]

def build_graph():
    graph = StateGraph(PromptCIState)
    
    #register nodes
    graph.add_node("fetch_context",fetch_context)
    graph.add_node("diff_analyst",diff_analyst)
    graph.add_node("test_generator",test_generator)
    graph.add_node("regression_runner",regression_runner)
    graph.add_node("safety_checker",safety_checker)
    graph.add_node("judge",judge)
    graph.add_node("report_writer",report_writer)
    
    #set entry point
    graph.set_entry_point("fetch_context")
    
    #sequence of nodes 
    graph.add_edge("fetch_context","diff_analyst")
    graph.add_edge("diff_analyst","test_generator")
    

    graph.add_conditional_edges("test_generator", fan_out, ["regression_runner", "safety_checker"])
    graph.add_edge("regression_runner", "judge")
    graph.add_edge("safety_checker", "judge")
    
    #final report generation
    graph.add_edge("judge","report_writer")
    graph.add_edge("report_writer",END)
    
    return graph.compile()

#compiled graph imported into the fastapi
promptci_graph = build_graph()
    
