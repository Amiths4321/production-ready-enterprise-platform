Enterprise Agentic Workflow Orchestrator (Backend Core)

A production-ready platform for building, compiling, and deploying stateful, graph-based agentic workflows. This system transforms raw visual nodes and edges (e.g., from a React Flow canvas UI) into executable LangGraph state machines, using LiteLLM to natively support over 100+ cloud and local LLM providers.

🏗️ Architecture System Topology
The platform separates the orchestration runtime from the inference compute layer, allowing a lightweight local application server to securely leverage remote GPU acceleration:

[ Visual React Flow Frontend ]
             │ (Dispatches JSON Layout Array)
             ▼
 ┌───────────────────────┐
 │  FastAPI Router App   │ ◄─── Runs locally (localhost:8000)
 └───────────┬───────────┘
             │ (Validates Nodes & Compiles State Graph)
             ▼
 ┌───────────────────────┐
 │   LangGraph Engine    │ ◄─── Manages state loops and evaluate cycles
 └───────────┬───────────┘
             │ (Dispatches Unified Completion Body)
             ▼
 ┌───────────────────────┐
 │    LiteLLM Gateway    │ ◄─── Translates to 100+ API Provider Formats
 └───────────┬───────────┘
             │ (Routes traffic through secure SSH Local Loopback)
             ▼
  ========= [ SECURE SSH TUNNEL (Port 11434:11434) ] =========
             │
             ▼
 ┌───────────────────────┐
 │ Remote Ollama Server  │ ◄─── Runs on Remote GPU Cluster Subnet
 └───────────────────────┘
🛠️ Prerequisites & Installation
Ensure you have Python 3.10+ installed on your local control plane workstation.

Bash
# Clone the repository and navigate to your project space
cd "Visual Workflow Orchestrator Code Blueprint"

# Install enterprise orchestration and translation dependencies
pip install fastapi uvicorn pydantic litellm langgraph watchfiles
🚀 Step-by-Step Deployment Strategy
1. Initialize the Secure Compute Pipeline (SSH Tunnel)
If your model inference server is hosted on an external GPU subnet (10.22.X.X) and protected by an enterprise firewall, establish a local loopback tunnel.

Open a dedicated terminal window on your machine and run:

Bash
ssh -L 11434:localhost:11434 username@10.22.X.X
Keep this terminal window running in the background.

2. Verify Available Remote Base Models
Open a separate terminal window and ping your local loop interface to identify what model weights are downloaded and accessible on the remote server:

Bash
curl http://localhost:11434/api/tags
(Take note of the correct model name string, e.g., "mistral", "llama3.2:latest", or "qwen2.5").

3. Launch the API Gateway
Run the live-reloading FastAPI application on your local machine:

Bash
python -m uvicorn production_server:app --reload --host 0.0.0.0 --port 8000
🎯 Verification and Payload Testing
Open your web browser and navigate to the built-in Interactive API documentation: http://localhost:8000/docs

Expand the POST /platform/deploy-and-run endpoint block and click Try it out.

Clear the text field and paste the following structural layout payload.

⚠️ CRITICAL: Update the provider_model property below to match a model name verified from your Step 2 diagnostic checklist.

JSON
{
  "nodes": [
    {
      "id": "input_block_1",
      "type": "user_input",
      "properties": {}
    },
    {
      "id": "llm_worker_block_2",
      "type": "llm_worker",
      "properties": {
        "provider_model": "ollama/mistral",
        "api_base_url": "http://localhost:11434"
      }
    }
  ],
  "edges": [
    {
      "source": "input_block_1",
      "target": "llm_worker_block_2"
    }
  ],
  "user_prompt": "Hello server! Verify your LangGraph compilation state machine works."
}
Click Execute. The backend will compile the diagram nodes, pass them through a structural validation parser, spin up the LangGraph loop, and deliver a successful 200 OK JSON response containing your response text.

🔒 Enterprise Production Configuration
The orchestration platform uses LiteLLM, meaning hot-swapping from a local development workspace to commercial cloud providers requires zero backend code alterations. Simply modify the JSON data payload sent by your front-end layout builder:

Routing to Anthropic Claude (Cloud)
JSON
"properties": {
  "provider_model": "anthropic/claude-3-5-sonnet",
  "api_key": "sk-ant-your-production-key-here"
}
Routing to OpenAI GPT-4o (Cloud)
JSON
"properties": {
  "provider_model": "openai/gpt-4o",
  "api_key": "sk-your-production-openai-key-here"
}
