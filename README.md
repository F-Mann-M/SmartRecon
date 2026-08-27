# SmartRecon

# RAG & Agentic AI Bank Account Manager
This is an active hands-on project that ingests invoices and bank statements, matches transactions, and powers a RAG-based financial analysis agent, with Azure infrastructure already in place.

## Project Goal:
SmartRecon — Intelligent Financial Matching & Analytics Agent

SmartRecon is an automated financial reconciliation and analytics system currently in development, built on a hybrid RAG (Retrieval-Augmented Generation) and multi-tool agent architecture.

The core goal of the project is to bridge unstructured document processing (invoices) with structured relational bank data (bank statements) to streamline end-to-end accounting workflows:

### Automated Reconciliation & Matching: 
Designed to leverage PGVector similarity search alongside relational SQL logic to automatically match incoming invoice documents with bank transactions based on vendor details, line items, amounts, and payment dates.

### Autonomous Financial Multi-Tool Agent: 
Aiming to integrate a LangGraph orchestration layer that enables an AI agent to execute database queries, analyze spending trends, highlight cost anomalies, and handle manual transaction overrides through natural language commands.

### Hybrid Data Infrastructure: 
Combining traditional PostgreSQL tables for precise relational record-keeping with vector embeddings to enable semantic search across unstructured invoices, suppliers, and bank transaction metadata.


## Models
Currently this project is using a local model via OLLama. https://docs.langchain.com/oss/python/integrations/chat/ollama



# Start Postgres locally
run colima 
```bash
colima start
```

in case there is an issue with the current colima stop it and start again
```bash
colima stop --force
```

start database from smartrecon/infra to run the docker-compose.yml
it builds an image and runs the container
```bash
docker-compose up -d
```

check if pg server is running
```bash
docker exec -it smartrecon_db psql -U postgres -d smartrecon -c "\dx"
```

To stop the container run
```bash
docker stop smartrecon_db
```

Reset Database:
```bash
docker exec -it smartrecon_db psql -U postgres -c "DROP DATABASE smartrecon;" -c "CREATE DATABASE smartrecon;"
```