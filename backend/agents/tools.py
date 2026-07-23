
from langchain_core.tools import tool
import sys
import os
from knowledge.vector_store import similarity_search


@tool
def calculator(expression: str) -> str:
    """A simple calculator that can add, subtract, multiply, or divide two numbers.
    Input should be a mathematical expression like '2 + 2' or '15 / 3'."""
    
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the internal knowledge base for relevant document chunks and context.
    Use this tool whenever you need to look up information from uploaded invoices, 
    PDFs, or internal documents to answer the user's request.
    
    Args:
        query: The semantic search query string.
    """
    results = similarity_search(query)
 
    return results
    
# Tool List
tools = [calculator, search_knowledge_base]