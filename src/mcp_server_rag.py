import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Any
from langchain_ollama import OllamaEmbeddings

# Load environment variables from .env file (contains API keys)
load_dotenv(override=True)

NOW_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(NOW_DIR, os.pardir)
DATA_DIR = os.path.join(ROOT_DIR, "data")

def create_retriever() -> Any:
    """
    Creates and returns a document retriever based on FAISS vector store.

    This function performs the following steps:
    1. Loads a PDF document(place your PDF file in the data folder)
    2. Splits the document into manageable chunks
    3. Creates embeddings for each chunk
    4. Builds a FAISS vector store from the embeddings
    5. Returns a retriever interface to the vector store

    Returns:
        Any: A retriever object that can be used to query the document database
    """
    # Step 1: Load Documents
    # PyMuPDFLoader is used to extract text from PDF files
    loader = PyMuPDFLoader(os.path.join(DATA_DIR, "SPRI_AI_Brief_2023년12월호_F.pdf"))
    docs = loader.load()

    # Step 2: Split Documents
    # Recursive splitter divides documents into chunks with some overlap to maintain context
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    split_documents = text_splitter.split_documents(docs)

    # Step 3: Create Embeddings
    embeddings = OllamaEmbeddings(model="bge-m3:latest",
                                  base_url="work.soundmind.life:11434")
    
    # Step 4: Create Vector Database
    # FAISS is an efficient similarity search library that stores vector embeddings
    # and allows for fast retrieval of similar vectors
    vectorstore = Chroma.from_documents(documents=split_documents, embedding=embeddings)

    # Step 5: Create Retriever
    # The retriever provides an interface to search the vector database
    # and retrieve documents relevant to a query
    retriever = vectorstore.as_retriever()
    return retriever


# Initialize FastMCP server with configuration
mcp = FastMCP(
    "Retriever",
    # instructions="You are an assistant who searches documents and helps answer questions.",
    instructions="You are an assistant who searches documents and helps answer questions.",
    host="0.0.0.0",
    port=8005,
)


@mcp.tool()
async def retrieve(query:str) -> str:
    """
    Retrieves information from the document database based on the query.

    This function creates a retriever, queries it with the provided input,
    and returns the concatenated content of all retrieved documents.

    Args:
        query (str): The search query to find relevant information

    Returns:
        str: Concatenated text content from all retrieved documents
    """

    # Create a new retriever instance for each query
    # Note: In production, consider caching the retriever for better performance
    retriever = create_retriever()
    
    # Use the invoke() method to get relevant documents based on the query
    retrieved_docs = retriever.invoke(query)

    # Join all document contents with newlines and return as a single string
    return "\n".join([doc.page_content for doc in retrieved_docs])


if __name__ == "__main__":
    # Run the MCP server with stdio transport for integration with MCP clients
    mcp.run(transport="stdio")
