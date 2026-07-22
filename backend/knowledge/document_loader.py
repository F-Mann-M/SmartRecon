from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from knowledge.vector_store import add_chunks_to_chroma


def load_pdf(file_path):
    """Load a PDF file and return its content as a list of documents."""
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents


def load_web(url):
    """Load a web page and return its content as a list of documents."""
    loader = WebBaseLoader(url)
    documents = loader.load()
    return documents


def load_from_directory(dir_path: str = "data/raw"):
    loader = PyPDFDirectoryLoader(
        path=dir_path, 
        recursive=False)
    
    pages = loader.load()

    if not pages:
        print(f"No PDF found in {dir_path}.")
        return []
    
    print(f"Loaded page count {len(pages)}")
    return pages


def split_document(documents, chunk_size=1000, chunk_overlap=200):
    """Takes in a document, split its content into chunks, and return the chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def load_and_process_pdf():
    """loads pdf form directory splits and stores it into chromaDB"""
    documents = load_from_directory()
    chunks = split_document(documents)
    add_chunks_to_chroma(chunks)


