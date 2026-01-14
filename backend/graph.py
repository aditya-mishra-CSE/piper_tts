import sqlite3
from typing import Annotated, TypedDict, List

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

from backend.rag import retrieve_context


load_dotenv()
# ---------- LLM ----------
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# ---------- TOOL ----------
@tool
def rag_tool(query: str, thread_id: str) -> dict:
    """
    Retrieve context from uploaded PDF.
    """
    return {
        "context": retrieve_context(query, thread_id)
    }

tools = [rag_tool]
llm_with_tools = llm.bind_tools(tools)

# ---------- STATE ----------
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# ---------- NODE ----------
def chat_node(state: ChatState, config):
    thread_id = config["configurable"]["thread_id"]

    system = SystemMessage(
        content=(
            "You are a helpful assistant.\n\n"
            "ALWAYS respond as a conversation between TWO speakers:\n"
            "Speaker A and Speaker B.\n\n"
            "RULES:\n"
            "- Use strict format\n"
            "- Speaker A explains\n"
            "- Speaker B asks or responds\n"
            "- End with Speaker B satisfied\n\n"
            "FORMAT:\n"
            "Speaker A: sentence\n"
            "Speaker B: sentence\n"
            "Speaker A: sentence\n"
            "Speaker B: sentence\n\n"
            "If PDF context is required, use rag_tool with thread_id."
        )
    )

    response = llm_with_tools.invoke(
        [system, *state["messages"]],
        config=config
    )

    return {"messages": [response]}

# ---------- GRAPH ----------
conn = sqlite3.connect("chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", tools_condition)
graph.add_edge("tools", "chat")

chatbot = graph.compile(checkpointer=checkpointer)

# ---------- HELPERS ----------
def retrieve_all_threads():
    return list({
        c.config["configurable"]["thread_id"]
        for c in checkpointer.list(None)
    })
