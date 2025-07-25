import streamlit as st
from typing import Dict, Any, List, Optional

def render_provider_selection(available_providers: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Render the LLM provider selection UI"""
    st.markdown("### 🧠 LLM Provider")
    
    # Provider selection
    provider_options = list(available_providers.keys())
    selected_provider = st.selectbox(
        "Select LLM Provider",
        provider_options,
        index=provider_options.index("groq") if "groq" in provider_options else 0,
        help="Choose which LLM provider to use for analysis"
    )
    
    # Get the selected provider info
    provider_info = available_providers[selected_provider]
    
    # Model selection
    model_options = provider_info.get("models", [])
    selected_model = st.selectbox(
        "Select Model",
        model_options,
        index=0,
        help="Choose which model to use for analysis"
    )
    
    # API key input
    api_key = st.text_input(
        f"{provider_info['name']} API Key",
        type="password",
        help=f"Enter your {provider_info['name']} API key"
    )
    
    # Advanced options
    with st.expander("Advanced Options"):
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="Higher values make output more random, lower values more deterministic"
        )
        
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=8000,
            value=1000,
            step=100,
            help="Maximum number of tokens to generate"
        )
    
    return {
        "provider": selected_provider,
        "model": selected_model,
        "api_key": api_key,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

def render_agent_status(agents: List[Dict[str, Any]]) -> None:
    """Render the agent status dashboard"""
    st.markdown("### 🎯 Agent Status")
    
    # Create columns for each agent
    cols = st.columns(len(agents))
    
    for i, agent in enumerate(agents):
        with cols[i]:
            status_color = {
                "ready": "green",
                "working": "orange",
                "error": "red",
                "standby": "gray"
            }.get(agent.get("status", "standby"), "gray")
            
            st.markdown(f"""
            <div class="agent-card">
                <h4>{agent['name']}</h4>
                <p>{agent['description']}</p>
                <span style="color: {status_color};">●</span> {agent['status'].capitalize()}
            </div>
            """, unsafe_allow_html=True)

def render_analysis_options() -> Dict[str, bool]:
    """Render the analysis options"""
    st.markdown("#### Analysis Options")
    
    deep_analysis = st.checkbox(
        "Deep Analysis",
        value=True,
        help="Perform comprehensive analysis"
    )
    
    include_deps = st.checkbox(
        "Include Dependencies",
        value=True,
        help="Analyze dependency vulnerabilities"
    )
    
    parallel_execution = st.checkbox(
        "Parallel Execution",
        value=True,
        help="Run analysis tasks in parallel when possible"
    )
    
    return {
        "deep_analysis": deep_analysis,
        "include_deps": include_deps,
        "parallel_execution": parallel_execution
    }

def render_progress_tracking(stages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Render the progress tracking UI"""
    st.markdown("### 🔄 Analysis Progress")
    
    progress_bars = {}
    status_elements = {}
    
    for stage in stages:
        progress_bars[stage["id"]] = st.progress(0)
        status_elements[stage["id"]] = st.empty()
        status_elements[stage["id"]].text(f"⏳ {stage['name']}: Waiting...")
    
    return {
        "progress_bars": progress_bars,
        "status_elements": status_elements
    }

def update_progress(progress_ui: Dict[str, Any], stage_id: str, 
                   progress: float, status: str, message: str) -> None:
    """Update the progress for a specific stage"""
    progress_bars = progress_ui["progress_bars"]
    status_elements = progress_ui["status_elements"]
    
    # Update progress bar
    progress_bars[stage_id].progress(progress)
    
    # Update status message
    status_icon = {
        "waiting": "⏳",
        "in_progress": "🔄",
        "completed": "✅",
        "failed": "❌"
    }.get(status, "⏳")
    
    status_elements[stage_id].text(f"{status_icon} {message}")