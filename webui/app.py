"""Hermes WebUI - FastAPI + HTMX Interface for AIOS Agents"""

import asyncio
import os
import json
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import uvicorn

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.hermes import get_registry, AgentConfig, Orchestrator
from agents.hermes.concrete_agents import ResearchAgent, CodingAgent
from services.llm import LLMClient


# Initialize FastAPI app
app = FastAPI(
    title="Hermes WebUI",
    description="Web interface for AIOS Agent Orchestration",
    version="0.1.0"
)

# Setup Jinja2 templates
templates_dir = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(templates_dir))

# Setup static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Global state
registry = get_registry()
orchestrator = Orchestrator()
active_sessions: Dict[str, Dict] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup."""
    registry.clear()
    
    # Create agents
    research_config = AgentConfig(
        name="ResearchAgent",
        description="Specialized in research and analysis",
        capabilities=["research", "analysis", "planning"]
    )
    research_agent = ResearchAgent(research_config, llm_client=None)
    registry.register_agent("research_agent", research_agent)
    
    coding_config = AgentConfig(
        name="CodingAgent",
        description="Specialized in software development",
        capabilities=["coding", "architecture", "implementation"]
    )
    coding_agent = CodingAgent(coding_config, llm_client=None)
    registry.register_agent("coding_agent", coding_agent)
    
    print("✓ Agents initialized at startup")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main page."""
    template = env.get_template("index.html")
    return template.render(app_name="Hermes AIOS", version="0.1.0")


@app.get("/api/agents", response_class=HTMLResponse)
async def list_agents():
    """List all registered agents."""
    agents = registry.list_agents()
    agent_data = []
    
    for agent_id in agents:
        agent = registry.get_agent(agent_id)
        if agent:
            stats = agent.get_stats()
            agent_data.append({
                "id": agent_id,
                "name": stats.get("name"),
                "description": stats.get("description"),
                "capabilities": agent.capabilities,
                "tasks_completed": stats.get("tasks_completed", 0),
                "memory_items": stats.get("memory_items", 0),
            })
    
    template = env.get_template("agents.html")
    return template.render(agents=agent_data)


@app.get("/api/providers", response_class=HTMLResponse)
async def list_providers():
    """List available providers and their status."""
    try:
        config_path = Path(__file__).parent.parent / "configs" / "providers.json"
        with open(config_path) as f:
            config = json.load(f)
        
        providers = []
        for name, settings in config.get("providers", {}).items():
            providers.append({
                "name": name,
                "type": settings.get("type"),
                "enabled": settings.get("enabled"),
                "models": settings.get("models", []),
            })
        
        template = env.get_template("providers.html")
        return template.render(providers=providers)
    
    except Exception as e:
        return f"<div class='error'>Error loading providers: {e}</div>"


@app.post("/api/chat", response_class=HTMLResponse)
async def chat(request: Request):
    """Process chat request."""
    form = await request.form()
    user_message = form.get("message", "")
    agent_id = form.get("agent", "research_agent")
    
    if not user_message:
        return "<div class='error'>Message cannot be empty</div>"
    
    agent = registry.get_agent(agent_id)
    if not agent:
        return f"<div class='error'>Agent {agent_id} not found</div>"
    
    # Create chat response
    timestamp = datetime.now().strftime("%H:%M:%S")
    response = f"""
    <div class='message user-message'>
        <span class='timestamp'>{timestamp}</span>
        <p>{user_message}</p>
    </div>
    """
    
    # For demo, return simple response (would call agent in real implementation)
    demo_response = f"[{agent.name}] I received your message about: {user_message}"
    response += f"""
    <div class='message agent-message'>
        <span class='timestamp'>{timestamp}</span>
        <p><strong>{agent.name}:</strong> {demo_response}</p>
    </div>
    """
    
    return response


@app.get("/api/status", response_class=HTMLResponse)
async def status():
    """Get system status."""
    agent_count = len(registry.list_agents())
    
    stats = orchestrator.get_stats()
    
    status_html = f"""
    <div class='status-panel'>
        <h3>System Status</h3>
        <ul>
            <li>Registered Agents: {agent_count}</li>
            <li>Workflows: {stats.get('registered_workflows', 0)}</li>
            <li>Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
        </ul>
    </div>
    """
    
    return status_html


@app.websocket("/ws/chat/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    active_sessions[client_id] = {
        "connected_at": datetime.now(),
        "messages": []
    }
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Echo back with timestamp
            timestamp = datetime.now().isoformat()
            response = {
                "timestamp": timestamp,
                "message": data,
                "client_id": client_id
            }
            
            active_sessions[client_id]["messages"].append(response)
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        del active_sessions[client_id]
        print(f"Client {client_id} disconnected")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agents": len(registry.list_agents()),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Get config from environment
    host = os.getenv("WEBUI_HOST", "0.0.0.0")
    port = int(os.getenv("WEBUI_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"\n🚀 Starting Hermes WebUI")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print(f"   Open: http://localhost:{port}\n")
    
    uvicorn.run(
        "webui.app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

