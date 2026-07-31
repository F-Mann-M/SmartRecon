# SmartRecon

# Next-Gen RAG & Agentic AI Knowledge System

This repository is an active, hands-on development project that I am building alongside my participation in the [IBM RAG and Agentic AI Professional Certificate on Coursera](https://www.coursera.org/professional-certificates/ibm-rag-and-agentic-ai).

## Project Purpose
The goal of this project is to directly apply, test, and deepen the advanced conceptual knowledge and practical frameworks acquired throughout the 10-module IBM curriculum. By moving directly from theoretical modules to live code, this system serves as a production-oriented implementation of modern generative AI architectures.

## Models
Currently this project is using a local model via OLLama. https://docs.langchain.com/oss/python/integrations/chat/ollama


# When starting locally
run colima or DockerDesktop if you prefer

```bash
start colima
```

start database from smartrecon/infra

```bash
docker-compose up -d
```

check it the postgres server in the container is running:

```bash
docker exec -it smartrecon_db psql -U postgres -d smartrecon -c "\dx"
```
