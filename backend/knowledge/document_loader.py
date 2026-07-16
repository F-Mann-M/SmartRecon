from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentLoader:
    """A class to load and split documents from various sources."""

    def __init__(self, source_type, source):
        self.source_type = source_type
        self.source = source

    def load(self):
        """Load the document based on the source type."""
        if self.source_type == "pdf":
            documents = self.load_pdf(self.source)
        elif self.source_type == "web":
            documents = self.load_web(self.source)
        else:
            raise ValueError(f"Unsupported source type: {self.source_type}")
        return documents


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


    def split_document(documents, chunk_size=1000, chunk_overlap=200):
        """Takes in a document, split its content into chunks, and return the chunks."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        chunks = text_splitter.split_documents(documents)
        return chunks
