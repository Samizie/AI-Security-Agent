import streamlit as st
from typing import Dict, Any, List
import json

from llm.provider_factory import LLMProviderFactory

def provider_settings_page():
    """Page for managing LLM provider settings"""
    st.title("🧠 LLM Provider Settings")
    
    # Get available providers
    available_providers = LLMProviderFactory.get_available_providers()
    
    # Display registered providers
    if 'llm_registry' in st.session_state:
        st.markdown("### Registered Providers")
        
        # Get registered providers
        providers = st.session_state.llm_registry.providers
        instances = st.session_state.llm_registry.instances
        default_provider = st.session_state.llm_registry.default_provider
        
        if not instances:
            st.info("No providers registered yet. Add a provider below.")
        else:
            # Create a table of registered providers
            provider_data = []
            for name, instance in instances.items():
                provider_data.append({
                    "Name": name,
                    "Provider": instance.__class__.provider_name,
                    "Default": "✓" if name.startswith(default_provider) else "",
                    "Model": getattr(instance, "default_model", "Unknown")
                })
            
            st.table(provider_data)
    
    # Add new provider
    st.markdown("### Add New Provider")
    
    # Provider selection
    provider_options = list(available_providers.keys())
    selected_provider = st.selectbox(
        "Select Provider",
        provider_options,
        key="add_provider_select"
    )
    
    # Get the selected provider info
    provider_info = available_providers[selected_provider]
    
    # Model selection
    model_options = provider_info.get("models", [])
    selected_model = st.selectbox(
        "Select Model",
        model_options,
        key="add_provider_model"
    )
    
    # API key input
    api_key = st.text_input(
        f"{provider_info['name']} API Key",
        type="password",
        key="add_provider_api_key"
    )
    
    # Set as default
    set_default = st.checkbox("Set as Default Provider", value=True)
    
    # Add provider button
    if st.button("Add Provider"):
        if not api_key:
            st.error("Please enter an API key")
        else:
            try:
                # Create the provider
                provider = LLMProviderFactory.create_provider(
                    provider_name=selected_provider,
                    api_key=api_key,
                    default_model=selected_model
                )
                
                # Register with the registry
                if 'llm_registry' in st.session_state:
                    st.session_state.llm_registry.register_provider(provider.__class__)
                    provider_instance = st.session_state.llm_registry.create_provider_instance(
                        selected_provider,
                        api_key=api_key,
                        default_model=selected_model
                    )
                    
                    # Set as default if requested
                    if set_default:
                        st.session_state.llm_registry.set_default_provider(selected_provider)
                    
                    st.success(f"Successfully added {provider_info['name']} provider")
                    st.experimental_rerun()
                else:
                    st.error("LLM registry not initialized")
            except Exception as e:
                st.error(f"Failed to add provider: {str(e)}")
    
    # Export/Import settings
    st.markdown("### Export/Import Settings")
    
    # Export settings
    if 'llm_registry' in st.session_state and st.session_state.llm_registry.providers:
        if st.button("Export Provider Settings"):
            # Create a JSON representation of the settings
            # Note: We don't include API keys for security reasons
            settings = {
                "providers": {},
                "default_provider": st.session_state.llm_registry.default_provider
            }
            
            for name, instance in st.session_state.llm_registry.instances.items():
                settings["providers"][name] = {
                    "provider_name": instance.__class__.provider_name,
                    "default_model": getattr(instance, "default_model", None),
                    "temperature": getattr(instance, "default_temperature", 0.7)
                }
            
            # Create a download button
            st.download_button(
                label="Download Settings",
                data=json.dumps(settings, indent=2),
                file_name="codiskout_provider_settings.json",
                mime="application/json"
            )
    
    # Import settings
    st.markdown("### Import Settings")
    
    uploaded_file = st.file_uploader("Upload Settings File", type=["json"])
    
    if uploaded_file is not None:
        try:
            settings = json.load(uploaded_file)
            
            if "providers" in settings and "default_provider" in settings:
                st.info("Settings file loaded. Please enter API keys for each provider.")
                
                # Display form for entering API keys
                for name, provider_info in settings["providers"].items():
                    st.text_input(
                        f"API Key for {provider_info['provider_name']} ({name})",
                        type="password",
                        key=f"import_api_key_{name}"
                    )
                
                if st.button("Import Settings"):
                    # Check if we have all API keys
                    missing_keys = False
                    for name in settings["providers"]:
                        if not st.session_state.get(f"import_api_key_{name}"):
                            missing_keys = True
                    
                    if missing_keys:
                        st.error("Please enter all API keys")
                    else:
                        # Import the settings
                        if 'llm_registry' in st.session_state:
                            for name, provider_info in settings["providers"].items():
                                try:
                                    # Create the provider
                                    provider = LLMProviderFactory.create_provider(
                                        provider_name=provider_info["provider_name"],
                                        api_key=st.session_state[f"import_api_key_{name}"],
                                        default_model=provider_info.get("default_model"),
                                        temperature=provider_info.get("temperature", 0.7)
                                    )
                                    
                                    # Register with the registry
                                    st.session_state.llm_registry.register_provider(provider.__class__)
                                    st.session_state.llm_registry.create_provider_instance(
                                        provider_info["provider_name"],
                                        api_key=st.session_state[f"import_api_key_{name}"],
                                        default_model=provider_info.get("default_model"),
                                        temperature=provider_info.get("temperature", 0.7)
                                    )
                                except Exception as e:
                                    st.error(f"Failed to import provider {name}: {str(e)}")
                            
                            # Set default provider
                            if settings["default_provider"] in st.session_state.llm_registry.providers:
                                st.session_state.llm_registry.set_default_provider(settings["default_provider"])
                            
                            st.success("Successfully imported provider settings")
                            st.experimental_rerun()
                        else:
                            st.error("LLM registry not initialized")
            else:
                st.error("Invalid settings file format")
        except Exception as e:
            st.error(f"Failed to load settings file: {str(e)}")

# Add this page to Streamlit's pages
if __name__ == "__main__":
    provider_settings_page()