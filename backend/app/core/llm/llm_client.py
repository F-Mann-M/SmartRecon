from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from core.config import settings

def _get_azure_token_provider():
    credential = DefaultAzureCredential(
        managed_identity_client_id=settings.AZURE_CLIENT_ID
    )
    return get_bearer_token_provider(
        credential, "https://cognitiveservices.azure.com/.default"
    )


def get_chat_model(reasoning_effort: str = "low") -> BaseChatModel:
    """Returns the chat/reasoning LLM based on the active environment."""
    if settings.ENVIRONMENT == "cloud":
        token_provider = _get_azure_token_provider()
        return AzureChatOpenAI(
            azure_deployment=settings.AZURE_DEPLOYMENT_CHAT,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            model_kwargs={"reasoning_effort": reasoning_effort},
        )
    if settings.ENVIRONMENT == "local":
        return ChatOllama(
            model=settings.LOCAL_CHAT_MODEL,
            temperature=0.5,
            streaming=True,
        )
    raise ValueError(f"Unsupported ENVIRONMENT: {settings.ENVIRONMENT}")


def get_structured_model() -> BaseChatModel:
    """Returns the model used for structured extraction/parsing tasks."""
    if settings.ENVIRONMENT == "cloud":
        token_provider = _get_azure_token_provider()
        return AzureChatOpenAI(
            azure_deployment=settings.AZURE_DEPLOYMENT_CHAT,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=0,
        )
    if settings.ENVIRONMENT == "local":
        return ChatOllama(
            model=settings.LOCAL_STRUCTURED_MODEL,
            temperature=0,
            streaming=False,
        )
    raise ValueError(f"Unsupported ENVIRONMENT: {settings.ENVIRONMENT}")


def get_embedding_model() -> Embeddings:
    """Returns the embedding model based on the active environment."""
    if settings.ENVIRONMENT == "cloud":
        token_provider = _get_azure_token_provider()
        return AzureOpenAIEmbeddings(
            azure_deployment=settings.AZURE_DEPLOYMENT_EMBEDDING,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version=settings.AZURE_EMBEDDING_API_VERSION,
        )

    # Local development
    if settings.ENVIRONMENT == "local":
        return OllamaEmbeddings(
            model=settings.LOCAL_EMBEDDING_MODEL,
            base_url="http://localhost:11434",
        )
    raise ValueError(f"Unsupported ENVIRONMENT: {settings.ENVIRONMENT}")

structured_llm = get_structured_model()
chat_llm = get_chat_model()
embedding_model = get_embedding_model()