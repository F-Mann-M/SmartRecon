# SmartRecon

# RAG & Agentic AI Bank Account Manager

This repository is an active, hands-on development project that I am building alongside my participation in the [IBM RAG and Agentic AI Professional Certificate on Coursera](https://www.coursera.org/professional-certificates/ibm-rag-and-agentic-ai).

## Project Purpose
The goal of this project is to directly apply, test, and deepen the advanced conceptual knowledge and practical frameworks acquired throughout the 10-module IBM curriculum. By moving directly from theoretical modules to live code, this system serves as a production-oriented implementation of modern generative AI architectures.

## Models
Currently this project is using a local model via OLLama. https://docs.langchain.com/oss/python/integrations/chat/ollama


# Start Postgres locally
run colima 

```bash
start colima
```

start database from smartrecon/infra to run the docker-compose.yml
it builds an image and runs the container

```bash
docker-compose up -d
```

check if pg server is running:

```bash
docker exec -it smartrecon_db psql -U postgres -d smartrecon -c "\dx"
```
