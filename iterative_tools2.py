from rich import print
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,add_messages,START,END
from langgraph.prebuilt import ToolNode
from typing import TypedDict,Annotated,Literal
from langchain_tavily import TavilySearch

from dotenv import load_dotenv

load_dotenv()
#tools
search=TavilySearch(max_results=3,search_depth="basic")
tools=[search]
llm_writer=ChatGroq(model="openai/gpt-oss-120b", temperature=0.8,max_tokens=512,streaming=True)

llm_writer_with_tool=llm_writer.bind_tools(tools)

#
llm_reviewer=ChatGroq(model="openai/gpt-oss-120b", temperature=0.2,streaming=True)

class State(TypedDict):
    topic:str
    messages:Annotated[list,add_messages]
    draft:str
    review_feedback:str
    is_approved:str
    attempts:int


WRITER_SYSTEM_PROMPT = (
    "You are an expert LinkedIn content writer. Your job is to write "
    "engaging, professional LinkedIn posts about the given topic. "
    "If the topic requires up-to-date information, statistics, or "
    "current trends, use the web search tool to gather fresh context "
    "before writing. If you have already received feedback on a "
    "previous draft, carefully address every point in the new draft. "
    "Rules for good LinkedIn posts: strong hook in the first line, "
    "1 clear takeaway, easy to skim (short paragraphs), around "
    "150-200 words, ends with a question or call-to-action to invi_ "
    "engagement. Do not use hashtags."
)

def writer_node(state : State) -> dict:
    """Writes (or rewrites) the LinkedIn post. Can call Tavily to search first."""

    attempts=state.get("attempts",0)+1
    topic=state["topic"]
    previous_feedback=state.get("review_feedback","NULL")


    if attempts == 1:
        user_message = f"""Write a LinkedIn post on this topic {topic}
    if you need current info search the web first """
    else:
        user_message = f"""your previous draft on '{topic}' was rejected
        Here is the reviewer's feedback \n\n {previous_feedback}\n\n
        write a new ,improved draft that fixes every mentioned issue.
        Do not repeat same mistake"""

    messages=[("system",WRITER_SYSTEM_PROMPT),("user",user_message)]

    response=llm_writer_with_tool.invoke(messages)

    return{
        "messages":[("human",user_message),response],
        "attempts":attempts,

    }

tool_node=ToolNode(tools)

def extract_draft_node(state:State)->dict:
    """After the writer finishes tool calls, pulls the final text out as the draft."""
    last_message=state["messages"][-1]
    draft=last_message.content
    print(f"=========GENERATED POST==========\n\n{draft}")
    return{"draft":draft}


REVIEWER_SYSTEM_PROMPT = (
    "You are a strict LinkedIn content reviewer. You judge whether a "
    "post is publish-ready. Evaluate against these criteria:\n"
    "1. Strong hook in the first line\n"
    "2. One clear, valuable takeaway\n"
    "3. Easy to skim - uses short paragraphs\n"
    "4. Roughly 150-200 words\n"
    "5. Ends with an engaging question or CTA\n"
    "6. Professional but human tone (not corporate-robotic)\n"
    "7. No hashtags\n\n"
    "Respond in exactly this format:\n"
    "VERDICT: APPROVED or REJECTED\n"
    "FEEDBACK: <one short paragraph explaining why>\n\n"
    "Be strict but fair. Approve only if the post genuinely meets all "
    "criteria. Reject if even one criterion is clearly missing."
)

def reviewer_node(state:State)->dict:
    """Review draft and decides: to approve or reject the post based on feedback."""
    draft=state["draft"]
    print("=====================REVIEWER++++++++++++++++++++++")

    prompt = (
    f"review this LinkedIn post draft : \n"
    f"{draft}\n"
    f"give your reviews"
    )
    response = llm_reviewer.invoke(
    [("system", REVIEWER_SYSTEM_PROMPT),("human",prompt)]
    )

    review_txt=response.content.strip()

    is_approved = "APPROVED" in review_txt.upper().split("FEEDBACK") [0]

    if "FEEDBACK:" in review_txt:
        feedback = review_txt.split("FEEDBACK:", 1) [1].strip()
    else:
        feedback = review_txt
        verdict = "APPROVED" if is_approved else "REJECTED"
        print(f" [Verdict: {verdict}]")
        print(f" [Feedback: {feedback}]")
        return {
        "review_feedback": feedback,
        "is_approved": is_approved,
        
        }

#router function
def should_use_tool(state:State):
    last_message = state ['messages'] [-1]
    if getattr(last_message, 'tool_calls', None):
        return "tools"
    return "extract_draft"
    I    

def should_stop_looping(state: State):
    if state['is_approved']:
        print("post haas been approved \n")
        return END
    if state['attempts'] >= 3:
        print("reached max attempts")
        return END
    return "writer"

#build the graph
graph = StateGraph (State)
graph.add_node("writer", writer_node)
graph.add_node("tools", tool_node)
graph.add_node("extract_draft", extract_draft_node)
graph.add_node("reviewer", reviewer_node)


graph.add_edge(START, "writer")
graph.add_conditional_edges (
    "writer", should_use_tool,
)
graph.add_edge("tools","reviewer")
graph.add_edge("extract_draft", "reviewer")

graph.add_conditional_edges (
"reviewer", should_stop_looping
)

app=graph.compile()

def main():

    print("\n")
    print(
        "[bold magenta]====================================[/bold magenta]"
    )
    print(
        "[bold magenta]      LINKEDIN POST GENERATOR       [/bold magenta]"
    )
    print(
        "[bold magenta]====================================[/bold magenta]"
    )

    print(
        "\nType a topic to generate a LinkedIn post."
    )

    print(
        "Type [bold red]exit[/bold red] to quit.\n"
    )

    while True:

        topic = input(
            "\n[You] Topic: "
        ).strip()

        if topic.lower() in ["exit", "quit"]:

            print(
                "\n[bold green]Goodbye! 👋[/bold green]"
            )

            break

        if not topic:

            print(
                "[red]Please enter a topic.[/red]"
            )

            continue

        # Initial state
        initial_state = {
            "topic": topic,
            "messages": [],
            "draft": "",
            "review_feedback": "",
            "is_approved": False,
            "attempts": 0
        }

        print(
            "\n[bold cyan]Generating your LinkedIn post...[/bold cyan]"
        )

        # try:

        final_state = app.invoke(
                initial_state
            )

        print("\n")

        print(
                "[bold green]========== FINAL POST ==========[/bold green]"
            )

        print(
                final_state.get(
                    "draft",
                    "No post generated."
                )
            )

        print(
                "\n[bold]Attempts:[/bold]",
                final_state.get("attempts", 0)
            )

        # except Exception as e:

        #     print(
        #         f"\n[bold red]Error:[/bold red] {e}"
        #     )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()