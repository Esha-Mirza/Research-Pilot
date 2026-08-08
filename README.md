# Multi-Agent Research Assistant

An AI-powered multi-agent research assistant that uses specialized agents to search, summarize, fact-check, and generate research reports for Horizon Insights.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Ollama](https://img.shields.io/badge/LLM-Ollama-black)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Agent Team](#agent-team)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Sample Research Topics](#sample-research-topics)
- [Sample Input](#sample-input)
- [Sample Output](#sample-output)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Contact](#contact)

---

## Overview

This application implements a team of specialized AI agents that collaborate like human analysts. Instead of a single monolithic LLM, it uses multiple agents — Search, Summarizer, Fact-Checker, and Report Generator — each with a specific role in the research process.

The application runs entirely locally, ensuring data privacy and eliminating API costs. It uses Ollama to host the LLaMA 2 model, a manual multi-agent orchestration system, and Streamlit for the user interface.

---

## Features

- **Multi-Agent Collaboration** — Specialized agents work together like a research team
- **Search Agent** — Collects raw information (simulated or via API)
- **Summarizer Agent** — Condenses findings into concise insights
- **Fact-Checker Agent** — Reviews for hallucinations, bias, and gaps
- **Report Generator Agent** — Produces polished executive-style reports
- **Export Ready** — Download all research components
- **Privacy-Focused** — All processing happens locally, no data is sent to external servers
- **No API Costs** — Free to use with no usage limits

---

## Agent Team

| Agent | Role | Responsibility |
|---|---|---|
| **Search Agent** | Information Collector | Gathers raw data and findings |
| **Summarizer Agent** | Insight Extractor | Condenses information into bullet points |
| **Fact-Checker Agent** | Quality Assurance | Reviews for accuracy, bias, and gaps |
| **Report Generator Agent** | Report Writer | Produces polished executive reports |

---

## Technology Stack

| Technology | Purpose |
|---|---|
| **LLaMA 2** | Large Language Model for agent reasoning |
| **Ollama** | Local LLM hosting and inference |
| **Streamlit** | Frontend user interface |
| **Requests** | HTTP client for API communication |
| **Uvicorn** | ASGI server for FastAPI |

---

## Prerequisites

| Requirement | Details |
|---|---|
| **Python** | Version 3.8 or higher |
| **Ollama** | Installed and running |
| **LLaMA 2 Model** | Downloaded via Ollama |
| **RAM** | 8GB+ recommended |
| **Storage** | 4GB+ free space for model |

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Esha-Mirza/School_Of_AI_Internship.git
cd School_Of_AI_Internship/"Project-11 Multi_Agent Research Assistant"
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Pull LLaMA 2 Model via Ollama

```bash
ollama pull llama2
```

This downloads the LLaMA 2 model (~3.8 GB). Alternatively, you can use a smaller model:

```bash
ollama pull phi3        # 2.2 GB, faster inference
ollama pull gemma:2b    # 1.4 GB, lightest option
```

---

## Running the Application

**Terminal 1: Start Ollama Service**

```bash
ollama serve
```

**Terminal 2: Start Streamlit Frontend**

```bash
streamlit run frontend.py
```

The frontend will open at: `http://localhost:8501`

---

## Usage

1. Open your browser and navigate to `http://localhost:8501`
2. Enter a research topic (e.g., "AI trends in healthcare")
3. Click the **Run Research** button
4. Watch the agents collaborate in sequence:
   - **Search Agent** collects information
   - **Summarizer Agent** condenses findings
   - **Fact-Checker Agent** reviews for accuracy
   - **Report Generator Agent** produces final report

---

## Sample Research Topics

- "AI trends in healthcare"
- "Electric vehicle market growth 2024"
- "Blockchain in financial services"
- "Renewable energy startups"
- "Quantum computing commercial applications"

---

## Sample Input

```text
AI trends in healthcare
```

---

## Sample Output

**Search Results:**

```text
SEARCH RESULTS FOR: AI trends in healthcare
==========================================
1. AI enables diagnostic automation with 95% accuracy.
2. Regulatory compliance remains a major challenge.
3. Startups raised over $500M in healthcare AI funding in 2024.
4. Key players: Google Health, Microsoft, Pfizer.
5. AI reduces drug discovery time by 40%.
```

**Summary:**

```text
• AI diagnostics achieving 95% accuracy
• $500M+ funding in healthcare AI
• Regulatory compliance is top challenge
• Drug discovery accelerated by 40%
```

**Fact-Checker Feedback:**

```text
• Accuracy claims appear reliable
• Consider mentioning data privacy concerns
• Add more diversity in cited examples
```

**Final Report:**

```text
EXECUTIVE RESEARCH REPORT
Topic: AI trends in healthcare 2024

Executive Summary:
AI is transforming healthcare through improved diagnostics, accelerated drug discovery, and significant investment. While regulatory compliance remains a challenge, the sector shows strong growth potential.

Key Findings:
1. AI diagnostics achieving 95% accuracy
2. $500M+ funding in healthcare AI
3. Regulatory compliance is top challenge
4. Drug discovery accelerated by 40%

Recommendations:
- Continue monitoring regulatory developments
- Focus on data privacy and security
- Invest in AI diagnostic tools
```

---

## Project Structure

```
Project-11 Multi_Agent Research Assistant/
├── agents/
│   ├── __init__.py
│   ├── search_agent.py
│   ├── summarize_agent.py
│   ├── checker_agent.py
│   └── report_agent.py
├── orchestrator.py
├── frontend.py
├── requirements.txt
└── README.md
```

---

## Configuration

### Changing the Model

To use a different model, modify each agent file:

```python
MODEL = "phi3"        # Change from "llama2" to your preferred model
```

### Changing the Port

```bash
streamlit run frontend.py --server.port 8502
```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Model not found | Run `ollama pull llama2` to download the model |
| Connection refused | Ensure Ollama is running (`ollama serve`) |
| Port already in use | Use `--server.port` flag to specify a different port |
| Module not found | Run `pip install -r requirements.txt` |
| Slow inference | Switch to a smaller model like `phi3` or `gemma:2b` |

---

## Roadmap

- [ ] Connect the Search Agent to a real web search API (currently simulated)
- [ ] Add a "show agent reasoning" toggle for transparency into each step
- [ ] Add exportable PDF research report generation

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Acknowledgments

- [Ollama](https://ollama.com/) - Local LLM runtime
- Meta - LLaMA 2 model
- Streamlit - UI framework

---

## Contact

- **GitHub:** [Esha-Mirza](https://github.com/Esha-Mirza)
- **Email:** esha101374@gmail.com
