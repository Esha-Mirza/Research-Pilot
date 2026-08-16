
<div align="center">

<h1>Research-Pilot</h1>
Multi-Agent AI Research Assistant

Research smarter with a team of specialized AI agents.

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?logo=ollama)](https://ollama.com/)
[![LLaMA](https://img.shields.io/badge/LLaMA-Local%20Inference-0467DF)](https://www.llama.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Interface-FF4B4B?logo=streamlit\&logoColor=white)](https://streamlit.io/)

A locally powered multi-agent research system that searches, summarizes, fact-checks, and transforms information into structured research reports.

</div>



---

## Overview

ResearchForge AI is a multi-agent research system designed to automate the research workflow using a team of specialized AI agents.

Instead of relying on a single AI model to perform every stage of research, the system divides the workflow into focused roles. Each agent handles a specific responsibility before passing its output to the next stage.

The result is a structured research pipeline that moves from information collection to concise insights, quality review, and final report generation.

### Research Pipeline

**Research Topic → Search Agent → Summarizer Agent → Fact-Checker Agent → Report Generator → Final Research Report**

The application runs locally using Ollama, allowing AI inference to take place on the user's machine without requiring external LLM APIs.

---

## Why ResearchForge AI?

Traditional AI research assistants often depend on a single model to search, reason, summarize, verify, and write a final response.

ResearchForge AI takes a different approach.

By assigning different responsibilities to specialized agents, the system creates a modular research workflow where each stage has a clearly defined purpose.

This architecture makes the system easier to understand, extend, and experiment with while demonstrating the fundamentals of multi-agent AI orchestration.

---

## Key Features

* **Multi-Agent Architecture** — Multiple specialized AI agents collaborate through a structured workflow.
* **Research Agent** — Collects and organizes research information for the requested topic.
* **Summarization Agent** — Converts raw findings into concise and useful insights.
* **Fact-Checking Agent** — Reviews findings for potential inaccuracies, gaps, bias, and unsupported claims.
* **Report Generation Agent** — Produces a polished, structured research report.
* **Local AI Inference** — Runs LLM inference locally through Ollama.
* **Privacy-Focused** — Research processing can remain entirely on the user's machine.
* **No External LLM API Required** — Uses locally hosted models instead of paid cloud inference.
* **Modular Design** — Individual agents can be modified or replaced independently.
* **Interactive Interface** — Provides a simple Streamlit interface for submitting research topics and viewing results.
* **Export-Friendly Results** — Research outputs can be collected and reused as structured research material.

---

## Agent Architecture

ResearchForge AI uses four specialized agents:

| Agent                  | Role                  | Responsibility                                    |
| ---------------------- | --------------------- | ------------------------------------------------- |
|  Search Agent          | Information Collector | Gathers research information and initial findings |
|  Summarizer Agent      | Insight Extractor     | Condenses raw findings into concise insights      |
|  Fact-Checker Agent    | Quality Reviewer      | Reviews findings for accuracy, bias, and gaps     |
|  Report Generator      | Research Writer       | Produces the final structured research report     |

### How the Agents Work

```text
                    ┌─────────────────────┐
                    │   Research Topic    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Search Agent     │
                    │  Information Gather │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Summarizer Agent   │
                    │  Extract Key Facts  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Fact-Checker Agent │
                    │ Review & Validate   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Report Generator    │
                    │ Generate Final      │
                    │ Research Report     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Final Report       │
                    └─────────────────────┘
```

---

## Technology Stack

| Technology    | Purpose                                   |
| ------------- | ----------------------------------------- |
| **Python**    | Core application and agent implementation |
| **Ollama**    | Local LLM runtime and inference           |
| **LLaMA**     | Language model powering the agents        |
| **Streamlit** | Interactive web interface                 |
| **Requests**  | HTTP communication with local services    |

---

## Project Structure

```text
researchforge-ai/
│
├── agents/
│   ├── __init__.py
│   ├── search_agent.py
│   ├── summarize_agent.py
│   ├── checker_agent.py
│   └── report_agent.py
│
├── orchestrator.py
├── frontend.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Core Components

**`agents/`**
Contains the specialized AI agents responsible for different stages of the research workflow.

**`orchestrator.py`**
Coordinates the agents and manages the overall research pipeline.

**`frontend.py`**
Provides the Streamlit-based user interface.

**`requirements.txt`**
Contains the Python dependencies required to run the project.

---

## Getting Started

### Prerequisites

Make sure you have the following installed:

* Python 3.8+
* Ollama
* A compatible local LLM
* 8 GB+ RAM recommended
* Sufficient storage for the selected model

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Esha-Mirza/researchforge-ai.git
cd researchforge-ai
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install a Local Model

For example, using LLaMA 2:

```bash
ollama pull llama2
```

You can also use a smaller model depending on your available hardware:

```bash
ollama pull phi3
```

```bash
ollama pull gemma:2b
```

---

## Running the Application

### 1. Start Ollama

```bash
ollama serve
```

### 2. Launch ResearchForge AI

Open another terminal and run:

```bash
streamlit run frontend.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## Usage

### Step 1 — Enter a Research Topic

Provide a topic you want the system to investigate.

Example:

```text
AI trends in healthcare
```

### Step 2 — Start the Research Pipeline

Run the research workflow from the Streamlit interface.

### Step 3 — Let the Agents Collaborate

The system processes the topic through the following stages:

```text
Topic
  ↓
Search
  ↓
Summarization
  ↓
Fact Checking
  ↓
Report Generation
```

### Step 4 — Review the Final Report

The Report Generator produces a structured research document containing key findings, insights, and recommendations.

---

## Example Research Topics

ResearchForge AI can be used to explore topics such as:

* Artificial Intelligence in Healthcare
* Renewable Energy Technologies
* Quantum Computing
* Electric Vehicle Industry Trends
* Blockchain Applications
* Cybersecurity Developments
* AI Startups and Market Trends
* Future of Robotics
* Generative AI Applications
* Emerging Technology Trends

---

## Example Workflow

### Input

```text
AI trends in healthcare
```

### Search Agent

Collects relevant information and research findings.

### Summarizer Agent

Transforms the collected information into concise insights.

### Fact-Checker Agent

Reviews the findings and identifies:

* Potential inaccuracies
* Missing information
* Possible bias
* Unsupported claims
* Areas requiring additional research

### Report Generator

Combines the processed information into a structured research report containing:

* Executive Summary
* Key Findings
* Important Insights
* Research Considerations
* Recommendations

---

## Configuration

### Change the LLM

The model used by the agents can be changed according to your hardware and performance requirements.

For example:

```python
MODEL = "llama2"
```

You can replace it with another model available through Ollama:

```python
MODEL = "phi3"
```

or:

```python
MODEL = "gemma:2b"
```

### Change the Streamlit Port

```bash
streamlit run frontend.py --server.port 8502
```

---

## Design Principles

ResearchForge AI is built around several core principles:

### Specialized Agents

Each agent has one clearly defined responsibility rather than forcing one model to handle the entire workflow.

### Sequential Processing

The output of one stage becomes the input for the next stage, creating a predictable research pipeline.

### Local-First AI

The project uses locally hosted models through Ollama, reducing dependence on external inference APIs.

### Modular Architecture

Agents are separated into individual modules, making it easier to modify, replace, or extend the system.

### Human-Readable Output

The final stage focuses on transforming intermediate agent outputs into a structured research report.

---

## Future Roadmap

* [ ] Integrate real-time web search
* [ ] Add source citations and references
* [ ] Introduce parallel agent execution
* [ ] Add configurable agent roles
* [ ] Support multiple local LLMs
* [ ] Add research history and session management
* [ ] Add PDF and Markdown report export
* [ ] Add source credibility scoring
* [ ] Introduce persistent research memory
* [ ] Add research comparison across multiple topics
* [ ] Improve report formatting and visualization
* [ ] Add configurable research depth

---

## Use Cases

ResearchForge AI can serve as a foundation for:

*  Automated research workflows
*  Academic research assistance
*  Market and industry research
*  Knowledge discovery
*  Research summarization
*  Business intelligence prototypes
*  Multi-agent AI experimentation
*  Agentic AI research and development

---

## Learning Objectives

This project demonstrates practical concepts in:

* Multi-agent AI systems
* LLM-powered applications
* Agent specialization
* AI workflow orchestration
* Local LLM inference
* Prompt-driven task delegation
* Automated summarization
* AI-assisted fact checking
* Structured report generation
* Streamlit application development

---

## Privacy

ResearchForge AI is designed around local AI inference through Ollama.

When configured to use only local models, the core LLM processing does not require sending prompts to a third-party cloud LLM provider.

> Always review the tools and integrations you add to the project before assuming complete offline operation.

---

## Contributing

Contributions are welcome.

If you would like to improve ResearchForge AI:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Test the workflow
5. Submit a pull request

For larger changes, consider opening an issue first to discuss the proposed improvement.

---

## License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.

---

## Acknowledgments

Built with:

* Python
* Ollama
* LLaMA
* Streamlit

Special thanks to the open-source AI ecosystem for making local LLM experimentation and multi-agent development accessible.

---

## Author

**Esha Mirza**

**GitHub:** [Esha-Mirza](https://github.com/Esha-Mirza)

---

<p align="center">
  <strong>ResearchForge AI</strong>
  <br>
  Turning complex research workflows into coordinated AI intelligence.
</p>
