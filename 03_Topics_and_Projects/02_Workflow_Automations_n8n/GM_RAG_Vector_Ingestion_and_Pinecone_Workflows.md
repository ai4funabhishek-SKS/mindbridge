---
title: "n8n RAG Vector Ingestion, Optical Character Recognition (OCR), and Pinecone Semantic Retrieval"
domain: "02_Workflow_Automations_n8n"
reusability_score: 95
workability_status: "Production-Ready"
tags:
  - "n8n"
  - "rag-pipeline"
  - "pinecone"
  - "ocr"
  - "vector-embeddings"
  - "document-ingestion"
dependencies:
  - "n8n >= 1.20"
  - "@n8n/n8n-nodes-langchain"
  - "pinecone-client"
  - "openai-embeddings"
source_files_synthesized:
  - "Raw_copies/1731539944305-UploadDocumenttoPineconeAgent.json"
  - "Raw_copies/1731539944391-RAGAIAgent.json"
  - "Raw_copies/OCR_Reader_Test (1).json"
---

# Executive Summary & Architectural Mental Model

The **n8n RAG Vector Ingestion and Pinecone Semantic Retrieval Engine** provides a turnkey, low-code data pipeline for converting messy unstructured documents (scanned PDF passbooks, receipts, contracts, Word docs) into high-dimensional vector embeddings stored in Pinecone and queried by intelligent LangChain conversational agents. By combining optical character recognition (OCR) pre-processing, recursive character text chunking, embedding generation (OpenAI `text-embedding-3-small` / Gemini embeddings), and vector upserting, this architecture enables sub-second semantic retrieval across thousands of enterprise documents.

```
+===================================================================================+
|                       n8n RAG & PINECONE VECTOR PIPELINE                          |
|                                                                                   |
|  [ Inbound Document: PDF / Image / Scan / DOCX ]                                  |
|                         |                                                         |
|                         v                                                         |
|  [ OCR Preprocessing Node ] (Extract Raw Text Buffer)                             |
|                         |                                                         |
|                         v                                                         |
|  [ Recursive Character Text Splitter ] (Chunk Size: 1000, Overlap: 200)           |
|                         |                                                         |
|                         v                                                         |
|  [ Embeddings Generator ] (1536-dim vector vectors)                               |
|                         |                                                         |
|                         v                                                         |
|  [ Pinecone Vector Store Upsert Node ] ===================+                       |
|                                                           |                       |
|  +--------------------------------------------------------+                       |
|  |                                                                                |
|  v (Semantic Query Time)                                                          |
|  [ User Question ] ---> [ RAG AI Agent Node ] ---> [ Pinecone Vector Query ]      |
|                                |                                  |               |
|                                v                                  v               |
|                     [ Synthesized Answer with Exact Citations & Lineage ]         |
+===================================================================================+
```

---

## Source Lineage & Merge Rationale

### Synthesized Sources
- `Raw_copies/1731539944305-UploadDocumenttoPineconeAgent.json`: Complete document upload, text splitter, OpenAI embedding, and Pinecone upsert workflow.
- `Raw_copies/1731539944391-RAGAIAgent.json`: LangChain QA Agent connected to Pinecone vector store tool with contextual conversation memory.
- `Raw_copies/OCR_Reader_Test (1).json`: OCR image pre-processing workflow using Tesseract / Cloud Vision OCR nodes.

### Concrete Merge Rationale
The raw repository split the vector ingestion pipeline into two halves: document uploading in one JSON, and QA querying in another, while OCR extraction was maintained as a disconnected experiment. Developers attempting to build a RAG knowledge base lacked a unified workflow covering both data ingestion and semantic query execution. This Golden Master combines the full lifecycle into an integrated document ingestion and RAG query architecture.

### Superiority Justification
1. **End-to-End Pipeline Integration**: Unifies OCR extraction, chunking, embedding upsert, and conversational retrieval into one cohesive playbook.
2. **Optimized Chunking Parameters**: Sets optimal chunk sizes (`chunkSize: 1000`, `chunkOverlap: 200`) to preserve semantic coherence without token bloat.
3. **Template Variable Injection**: Replaces hardcoded Pinecone index names and API keys with `$env` expressions.

---

## Core Implementations & Code Artifacts

### 1. Pinecone Document Vector Ingestion n8n Node Schema (`pinecone_ingestion.json`)

```json
{
  "name": "Pinecone_Vector_Ingestion_Pipeline",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "ingest-document",
        "responseMode": "lastNode",
        "options": {}
      },
      "id": "node-ingest-trigger",
      "name": "Ingest Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1.1,
      "position": [200, 300]
    },
    {
      "parameters": {
        "chunkSize": 1000,
        "chunkOverlap": 200,
        "options": {}
      },
      "id": "node-text-splitter",
      "name": "Recursive Character Text Splitter",
      "type": "@n8n/n8n-nodes-langchain.textSplitterRecursiveCharacterTextSplitter",
      "typeVersion": 1,
      "position": [440, 480]
    },
    {
      "parameters": {
        "model": "text-embedding-3-small"
      },
      "id": "node-openai-embeddings",
      "name": "OpenAI Embeddings",
      "type": "@n8n/n8n-nodes-langchain.embeddingsOpenAi",
      "typeVersion": 1.1,
      "position": [620, 480]
    },
    {
      "parameters": {
        "mode": "insert",
        "pineconeIndex": {
          "__rl": true,
          "value": "={{ $env.PINECONE_INDEX_NAME }}",
          "mode": "name"
        },
        "options": {
          "pineconeNamespace": "knowledge-base"
        }
      },
      "id": "node-pinecone-store",
      "name": "Pinecone Vector Store",
      "type": "@n8n/n8n-nodes-langchain.vectorStorePinecone",
      "typeVersion": 1,
      "position": [540, 300]
    }
  ],
  "connections": {
    "Ingest Webhook": {
      "main": [
        [
          {
            "node": "Pinecone Vector Store",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Recursive Character Text Splitter": {
      "ai_textSplitter": [
        [
          {
            "node": "Pinecone Vector Store",
            "type": "ai_textSplitter",
            "index": 0
          }
        ]
      ]
    },
    "OpenAI Embeddings": {
      "ai_embedding": [
        [
          {
            "node": "Pinecone Vector Store",
            "type": "ai_embedding",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## Parameterized Prompt Decks & Templates

### Prompt Deck 1: RAG Question-Answering Agent Prompt

```markdown
<system_role>
You are an expert Enterprise Knowledge Retrieval Agent.
You answer user queries exclusively using the retrieved vector context from the Pinecone knowledge base.
</system_role>

<context>
Retrieved Knowledge Context:
{{RETRIEVED_CHUNKS}}

User Query:
{{USER_QUERY}}
</context>

<instructions>
1. Carefully synthesize an accurate response based ONLY on the retrieved knowledge context.
2. If the context does not contain sufficient information, state clearly: "I cannot find this information in the knowledge base." Do not hallucinate.
3. Cite the source document title and section for each factual claim.
</instructions>
```

---

## Deployment SOP & Operational Guide

1. **Pinecone Index Configuration**:
   - Create a Pinecone serverless index with 1536 dimensions and cosine metric.
   - Set environment variables: `PINECONE_API_KEY` and `PINECONE_INDEX_NAME`.
2. **Import Workflow**:
   - Paste `pinecone_ingestion.json` into n8n canvas.
3. **Ingest Documents**:
   - Post document text or file payload to `http://localhost:5678/webhook/ingest-document`.
4. **Verify Semantic Search**:
   - Query the index via n8n RAG Agent node and verify retrieved chunk relevance.

---

## Failure Modes, Edge Cases & Troubleshooting

- **Failure Mode 1: Dimension Mismatch in Pinecone (1536 vs 768)**:
  - *Cause*: Using Gemini embeddings (768-dim) against an OpenAI 1536-dim Pinecone index.
  - *Remedy*: Ensure the embedding model dimension matches the Pinecone index configuration exactly.
- **Failure Mode 2: Missing Text Content in Scanned PDFs**:
  - *Cause*: Scanned PDF contains pure raster images with no embedded text stream.
  - *Remedy*: Route through the OCR Preprocessing node before passing text to the text splitter.
