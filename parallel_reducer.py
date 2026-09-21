import os
from typing import TypedDict,Annotated
from rich import print
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,START,END

llm=ChatGroq(model="openai/gpt-oss-120b", temperature=0.2,max_tokens=512,streaming=True)
#create a merge dictionary
def merge_score_dicts(existing: dict, newupdate: dict) -> dict:
    """Merge two dictionaries containing safety scores."""

    existing = existing or {}
    newupdate = newupdate or {}

    return {**existing, **newupdate}
#create a state
class AnalyzerState(TypedDict):
    raw_text:str
    safety_score:Annotated[dict[str:int],merge_score_dicts]

#nodes

def toxicity_node(state: AnalyzerState) -> dict:
    print("\n [Branch 1] Analyzing Toxicity and Hate Speech...")

    prompt = (
        "You are an expert content safety analyzer. "
        "Analyze the following text for profanity, aggression, harassment, "
        "hate speech, threats, insults, or other forms of toxic language. "
        "Provide a toxicity score from 0 to 100, where 0 means completely "
        "clean and non-toxic, and 100 means extremely toxic, hateful, "
        "or abusive content. "
        "Consider the overall context and intent of the text when assigning "
        "the score. Do not judge the topic itself; only evaluate the level "
        "of toxic or abusive language. "
        "Return ONLY the plain integer number between 0 and 100. "
        "Do not include a percentage sign, explanation, label, or any other text.\n\n"
        f"Text:\n{state['raw_text']}"
    )

    response = llm.invoke(prompt)

    try:
        score = int(response.content.strip())
    except ValueError:
        score = 0

    return {"safety_score": {"toxicity_level": score}}


def copyright_node(state: AnalyzerState) -> dict:
    print("\n [Branch 2] Analyzing Copyright & Originality Risks...")

    prompt = (
        "You are an expert content originality and copyright risk analyzer. "
        "Analyze the following text for signs of heavy similarity to commonly "
        "used or potentially copied content, lack of originality, excessive "
        "use of distinctive phrases, or potential corporate trademark risks. "
        "Evaluate the overall risk rather than assuming that a topic or common "
        "phrase is copyrighted. "
        "Provide a score from 0 to 100, where 0 means very low originality or "
        "copyright risk and 100 means very high risk. "
        "Return ONLY the plain integer number between 0 and 100. "
        "Do not include a percentage sign, explanation, label, or any other text.\n\n"
        f"Text:\n{state['raw_text']}"
    )

    response = llm.invoke(prompt)

    try:
        score = int(response.content.strip())
    except ValueError:
        score = 0

    return {"safety_score": {"copyright_risk": score}}

def culture_node(state: AnalyzerState) -> dict:
    print("\n [Branch 3] Analyzing Regional & Cultural Sensitivity...")

    prompt = (
        "You are an expert cultural sensitivity and global content analyst. "
        "Analyze the following text for regional sensitivities, political "
        "sensitivities, cultural stereotypes, discriminatory language, or "
        "culturally insensitive statements that could reasonably offend a "
        "global audience. Consider the context and intent of the text. "
        "Do not treat ordinary mentions of countries, cultures, religions, "
        "or political topics as inherently offensive. "
        "Provide a score from 0 to 100, where 0 means completely safe and "
        "culturally respectful, and 100 means highly offensive or culturally "
        "insensitive. "
        "Return ONLY the plain integer number between 0 and 100, nothing else. "
        "Do not include explanations, labels, symbols, or a percentage sign.\n\n"
        f"Text:\n{state['raw_text']}"
    )

    response = llm.invoke(prompt)

    try:
        score = int(response.content.strip())
    except ValueError:
        score = 0

    return {"safety_score": {"culture_score": score}}

builder=StateGraph(AnalyzerState)

builder.add_node("toxicity",toxicity_node)
builder.add_node("copyright",copyright_node)
builder.add_node("culture",culture_node)


builder.add_edge(START,"toxicity")
builder.add_edge(START,"copyright")
builder.add_edge(START,"culture")

builder.add_edge("toxicity",END)
builder.add_edge("copyright",END)
builder.add_edge("culture",END)

app=builder.compile()


sample_script ="""
Yo guys! Welcome back to the stream. Today I am going to show you how to hack into your friend's system using a script I copied directly from an online forum.
Honestly, traditional security protocols are absolute garbage and anyone still using them is an absolute idiot. Let's dive into the code!
"""

initial_state={
    "raw_text":sample_script,
    "safety_score":{}
}

result=app.invoke(initial_state)
print(result["safety_score"])