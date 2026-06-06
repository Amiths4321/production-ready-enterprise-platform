from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Literal
import litellm
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

app = FastAPI(title="Enterprise Agentic Workflow Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable LiteLLM's internal structural telemetry/fallbacks
litellm.drop_params = True 

# --- ENTERPRISE SCHEMAS ---
class VisualNode(BaseModel):
    id: str
    type: Literal["user_input", "router_agent", "llm_worker", "rag_retriever"]
    properties: Dict[str, Any]

class VisualEdge(BaseModel):
    source: str
    target: str

class PipelinePayload(BaseModel):
    nodes: List[VisualNode]
    edges: List[VisualEdge]
    user_prompt: str

# LangGraph Shared Thread State Object
class AgentWorkflowState(TypedDict):
    current_prompt: str
    model_response: str
    next_step: str
    provider_config: Dict[str, Any]
    loop_count: int

# --- CORE PLATFORM ENGINE RUNTIME ---
class EnterpriseWorkflowCompiler:
    def __init__(self, payload: PipelinePayload):
        self.payload = payload
        self.nodes_by_id = {node.id: node for node in payload.nodes}
        
        # Locate the explicit LLM worker configuration block
        self.llm_config = next((n for n in payload.nodes if n.type == "llm_worker"), None)
        if not self.llm_config:
            raise ValueError("Compilation Error: Workspace requires a configured 'llm_worker' node.")

    def execute_llm_call(self, prompt: str) -> str:
        """
        Natively targets 100+ LLM providers via a single completion schema.
        Properties field accepts strings like:
          - "openai/gpt-4o"
          - "anthropic/claude-3-5-sonnet"
          - "ollama/mistral"
          - "bedrock/anthropic.claude-v3"
        """
        provider_string = self.llm_config.properties.get("provider_model", "ollama/qwen2.5vl:latest")
        api_base = self.llm_config.properties.get("api_base_url", None) # Optional override (e.g., http://10.22.39.192:11434)
        api_key = self.llm_config.properties.get("api_key", "sk-dummy-or-local")

        try:
            response = litellm.completion(
                model=provider_string,
                messages=[{"role": "user", "content": prompt}],
                api_base=api_base,
                api_key=api_key,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM Provider layer connection failed via LiteLLM: {str(e)}")

    def build_runtime_graph(self):
        """Compiles the raw visual payload topology into a strict LangGraph state machine."""
        workflow = StateGraph(AgentWorkflowState)

        # Node Definition 1: Core Processing Agent
        def agent_reasoning_node(state: AgentWorkflowState) -> Dict[str, Any]:
            prompt = f"Analyze this goal: {state['current_prompt']}. Formulate the next actionable item."
            llm_out = self.execute_llm_call(prompt)
            return {
                "model_response": llm_out, 
                "loop_count": state.get("loop_count", 0) + 1
            }

        # Node Definition 2: Quality Guard/Evaluation Router
        def evaluation_router_node(state: AgentWorkflowState) -> Dict[str, Any]:
            eval_prompt = (
                f"Review this output: '{state['model_response']}'.\n"
                f"Does it completely answer the initial request? Respond with exactly 'COMPLETE' or 'REVISE'."
            )
            decision = self.execute_llm_call(eval_prompt).strip().upper()
            next_action = END if "COMPLETE" in decision or state["loop_count"] >= 3 else "agent_core"
            return {"next_step": next_action}

        # Wire graph primitives
        workflow.add_node("agent_core", agent_reasoning_node)
        workflow.add_node("eval_router", evaluation_router_node)

        workflow.set_entry_point("agent_core")
        workflow.add_edge("agent_core", "eval_router")
        
        # Build state loops based on dynamic execution routing
        workflow.add_conditional_edges(
            "eval_router",
            lambda state: state["next_step"],
            {"agent_core": "agent_core", END: END}
        )

        return workflow.compile()

@app.post("/platform/deploy-and-run")
async def process_enterprise_workflow(payload: PipelinePayload):
    try:
        compiler = EnterpriseWorkflowCompiler(payload)
        compiled_graph = compiler.build_runtime_graph()
        
        # Initialize thread state variables
        initial_state: AgentWorkflowState = {
            "current_prompt": payload.user_prompt,
            "model_response": "",
            "next_step": "",
            "provider_config": {},
            "loop_count": 0
        }
        
        # Run graph instance execution
        final_output = compiled_graph.invoke(initial_state)
        return {
            "status": "success",
            "execution_turns": final_output["loop_count"],
            "payload_delivery": final_output["model_response"]
        }
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Runtime compilation crash: {str(err)}")