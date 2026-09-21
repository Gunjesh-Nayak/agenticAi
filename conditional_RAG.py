import os
from typing import TypedDict,Annotated
from rich import print
from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END,add_messages
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


load_dotenv()

embedding=HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")

def build_retriver(pdf_path: str):
    docs=PyPDFLoader(file_path=pdf_path)
    documents=docs.load()

    splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
    chunks=splitter.split_documents(documents)
    # print(chunks)
    vector_store=FAISS.from_documents(chunks, embedding)
    # print(vector_store)
    return vector_store.as_retriever(search_type="mmr",search_kwargs={"k":3})


fee_retriever= build_retriver("./fee_structure.pdf")
academic_retriever= build_retriver("./academics_handbook.pdf")

llm = ChatGroq( model="openai/gpt-oss-120b", temperature=0.5,max_tokens=1024)

class State(TypedDict):
    programe:str
    messages:Annotated[list,add_messages]
    query_type:str
    retriever_context:str


def classifier_node(state:State)->dict:
    """Look at latest user message and decide which path to take. fees/academics/general question"""

    last_message=state["messages"][-1].content

    prompt = (
    "You are a college query classifier. "
    "Classify the student's query into exactly ONE of these categories: "
    "academic, fee, or general.\n\n"

    "Category rules:\n"
    "- academic: attendance, exams, marks, grades, credits, promotion, "
    "courses, curriculum, summer training, internships required for the "
    "degree, or other academic/degree requirements.\n"
    
    "- fee: tuition fees, payments, refunds, fines, late charges, "
    "scholarships, fee concessions, or any question specifically about "
    "college-related money or payments.\n"
    
    "- general: greetings, casual conversation, college information that "
    "does not concern academics or fees, or anything that clearly does "
    "not fit the academic or fee categories.\n\n"

    "Classification rules:\n"
    "1. Choose exactly one category.\n"
    "2. Use the meaning and intent of the query, not just individual keywords.\n"
    "3. If the query is about academic requirements, choose academic.\n"
    "4. If the query is about money or payments, choose fee.\n"
    "5. If neither applies, choose general.\n\n"

    f"Student query: {last_message}\n\n"
    "Output ONLY one lowercase word: academic, fee, or general."
    )

    response=llm.invoke(prompt)
    category=response.content.strip().lower()

    if "academic" in category:
        category="academic"
    elif "fee" in category:
        category="fee"
    else:
        category="general"

    return {"query_type":category}

     
def academic_rag_node(state: State) -> dict:
    """Retrieves relevant chunks from the academics handbook."""
    query = state ["messages"] [-1].content
    docs = academic_retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    return {"retriever_context": context}


def fee_rag_node(state: State) -> dict:
    """Retrieves relevant chunks from the fee structure PDF."""
    query = state ["messages"] [-1].content
    docs = fee_retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    return {"retriever_context": context}


def general_node(state: State) -> dict:
    """Answers directly using the LLM's own knowledge, no retrieval needed."""
    return {"retriever_context": "NO_RETRIEVAL_NEEDED"}


def response_node(state: State) -> dict:
    """Generates the final answer, personalized using the student's programme."""
    query = state["messages"][-1].content
    programme = state.get("programe", "Unknown")
    context = state["retriever_context"]

    if context == "NO_RETRIEVAL_NEEDED":
        prompt = (
            f"You are a friendly college assistant talking to a {programme} student. "
            f"Answer this question using your own general knowledge:\n\n{query}"
        )
    else:
        prompt = (
            f"You are a college assistant helping a {programme} student. "
            f"Use the following context from the official college documents to answer "
            f"the question accurately. If the context mentions specific figures for "
            f"different programmes, highlight the one relevant to {programme} if possible.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Give a clear, friendly, and precise answer."
        )

    response = llm.invoke(prompt)
    return {"messages": [("ai", response.content.strip())]}

#router function

def router_query(state:State):#->Literal['academic_rag','fee_rag','general']
    if state ['query_type'] == 'academic':
        return "academic_rag"
    elif state['query_type'] == "fee":
        return "fee_rag"
    else:
        return "general"


#building graph
graph=StateGraph(State)

graph.add_node("classifier",classifier_node)
graph.add_node("academic_rag",academic_rag_node)
graph.add_node("fee_rag",fee_rag_node)
graph.add_node("general",general_node)
graph.add_node("response",response_node)

graph.add_edge(START,"classifier")
graph.add_conditional_edges(
    "classifier",router_query
)
graph.add_edge("academic_rag","response")
graph.add_edge("fee_rag","response")
graph.add_edge("general","response")

graph.add_edge("response",END)

app=graph.compile()

# print("""
# ===============WELCOME TO COLLEGE ASSISTANT===============
#     CHOOSE YOUR PROGRAMME OR COURSE
#     BBA || BCA || BCOM(H)
# """)

# choice=input("Course??  ").upper()

# while True:
#     user_query=input("YOU:")
#     if user_query == '0': 
#         break
#     result=app.invoke({
#         "programe":choice,
#         "messages":[("human",user_query)]
#     })

#     print(f'Assistant : {result["messages"][-1].content}')