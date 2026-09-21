import os
from typing import TypedDict
from rich import print
import rich

#state first

class pipelineState(TypedDict):
    raw_input:str
    editor_txt:str
    script_txt:str
    final_output:str

from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq( model="openai/gpt-oss-120b", temperature=0.5,max_tokens=512)

def editor_node(state: pipelineState) -> dict:
    """Stage 1: Clean grammar, spelling, and clarity while preserving meaning."""

    print("\n--- [Stage 1] Executing Editor Node ---")

    prompt = (
        "You are an expert copyeditor. "
        "Edit the following raw text to make it grammatically correct, clear, "
        "natural, and easy to understand. Fix grammar, spelling, punctuation, "
        "sentence structure, and awkward phrasing. Improve the flow between ideas "
        "and remove unnecessary repetition. Preserve the original meaning, facts, "
        "intent, and important technical terms. Do not add new information or "
        "change the author's message. Return only the edited text.\n\n"
        f"Raw Text:\n{state['raw_input']}"
    )

    response = llm.invoke(prompt)

    return {"editor_txt": response.content.strip()}


def scriptwriter_node(state: pipelineState) -> dict:
    """Stage 2: Transform the edited text into an engaging video script."""

    print("\n--- [Stage 2] Executing Scriptwriter Node ---")

    prompt = (
        "You are a professional YouTube scriptwriter and storyteller. "
        "Transform the following edited text into an engaging, natural, and "
        "conversational video script. Start with a strong hook that creates curiosity "
        "and keeps the audience interested. Use short, punchy, easy-to-speak sentences "
        "and smooth transitions. Make the script sound like a real person speaking "
        "naturally and confidently, not like an article being read aloud. "
        "Preserve the original meaning, facts, and important technical terms. "
        "Do not invent facts, examples, statistics, or information. "
        "Do not add explanations outside the script. Return only the final script.\n\n"
        f"Edited Text:\n{state['editor_txt']}"
    )

    response = llm.invoke(prompt)

    return {"script_txt": response.content.strip()}


def translator_node(state: pipelineState) -> dict:
    """Stage 3: Convert the script into natural flowing Hinglish."""

    print("\n--- [Stage 3] Executing Hinglish Translator Node ---")

    prompt = (
        "You are an expert Indian content localizer and Hinglish scriptwriter. "
        "Convert the following English video script into natural, fluent, and "
        "conversational Hinglish suitable for an Indian audience. "
        "Do not translate word-for-word or sentence-by-sentence. "
        "Preserve the original meaning, facts, structure, tone, and technical terms. "
        "Use Hindi and English naturally, the way a knowledgeable Indian tech educator "
        "would speak during a live stream or YouTube video. Keep technical terms in "
        "English when they sound more natural. Use simple Hindi where appropriate. "
        "Make the result smooth, engaging, and easy to speak aloud. "
        "Do not add new information, examples, opinions, or explanations. "
        "Return only the final Hinglish script.\n\n"
        f"Script:\n{state['script_txt']}"
    )

    response = llm.invoke(prompt)

    return {"final_output": response.content.strip()}

#now we have to connect the node by edges and create a graph and then we will run the graph and get the final output.

from langgraph.graph import StateGraph,START,END

graph = StateGraph(pipelineState)
#add nodes to the graph
graph.add_node("editor", editor_node)
graph.add_node("scriptwriter", scriptwriter_node)
graph.add_node("translator", translator_node)

#add edges to the graph

graph.add_edge(START, "editor")
graph.add_edge("editor", "scriptwriter")
graph.add_edge("scriptwriter", "translator")
graph.add_edge("translator", END)

#compile the graph

app=graph.compile()
results=app.invoke({"raw_input":"The quick brown fox jumps over the lazy dog. This sentence is a pangram, meaning it contains every letter of the English alphabet at least once. Pangrams are often used to test fonts, keyboards, and other text-related applications. The quick brown fox is a classic example of a pangram that has been used for centuries."})

#output
print("\n--- Final Output ---")
rich.print(results["final_output"])


