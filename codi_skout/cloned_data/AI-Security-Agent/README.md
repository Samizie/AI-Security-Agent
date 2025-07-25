# CodiSkout

## Project Description
CodiSkout is an AI-powered security orchestration tool designed to automate the process of identifying security vulnerabilities in GitHub repositories. It leverages Streamlit for an interactive user interface and Langchain for advanced AI capabilities, allowing users to clone repositories, scan codebases, identify vulnerabilities, and generate detailed security reports.

## Features
- **GitHub Repository Cloning**: Easily clone any public GitHub repository for analysis.
- **Codebase Scanning**: Analyze the structure, views, and exposed URLs within the codebase.
- **Vulnerability Identification**: Utilize AI to detect potential security vulnerabilities.
- **Detailed Reporting**: Generate comprehensive JSON reports of all findings.
- **Interactive UI**: A user-friendly Streamlit interface to interact with the agent and view results.
- **Customizable**: Easily extendable to add new scanning capabilities or reporting formats.

## Installation

To set up the AI-Security-Agent, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/AI-Security-Agent.git
    cd AI-Security-Agent
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment**:
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    (Note: A `requirements.txt` file will be generated or should be created with necessary dependencies like `streamlit`, `langchain`, etc.)

5.  **Set up environment variables**:
    Create a `.env` file in the root directory and add your API keys (e.g., for OpenAI, GitHub, etc.) if required by the agents.
    ```
    OPENAI_API_KEY="your_openai_api_key"
    GITHUB_TOKEN="your_github_token"
    ```

## Usage

To run the Streamlit application:

1.  **Activate your virtual environment** (if not already active):
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

2.  **Run the Streamlit application**:
    ```bash
    streamlit run main.py
    ```

3.  Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

## Project Structure

```
AI-Security-Agent/
├── .dist/                  # Distribution files (if any)
├── .gitignore              # Git ignore file
├── README.md               # Project documentation
├── ai_auditor/             # Main application source code
│   ├── __init__.py
│   ├── agents/             # AI agents for specific tasks (cloning, scanning, reporting)
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── code_reviewer.py
│   │   ├── github_cloner.py
│   │   ├── reporter.py
│   │   └── security_analyst.py
│   ├── app.py              # Streamlit application entry point
│   ├── cloning_data/       # Directory for cloned repository data (ignored by git)
│   ├── config/             # Configuration files (prompts, settings)
│   │   ├── __init__.py
│   │   ├── prompts.py
│   │   └── settings.py
│   ├── core/               # Core logic (orchestration, data structures, message bus)
│   │   ├── __init__.py
│   │   ├── data_structures.py
│   │   ├── message_bus.py
│   │   └── orchestrator.py
│   └── ui/                 # User interface components
│       └── __init__.py
├── data/                   # Directory for generated reports (ignored by git)
└── main.py                 # Main script to run the Streamlit app
```

## Contributing

We welcome contributions to the AI-Security-Agent! Please follow these steps to contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and ensure they are well-tested.
4.  Commit your changes with clear and concise messages.
5.  Push your branch to your forked repository.
6.  Open a pull request to the `main` branch of the original repository.

Please ensure your code adheres to the existing coding style and includes appropriate documentation.