<div align="center">

#  Research-Pilot

### Multi-Agent AI Research Assistant

**Research smarter with a team of specialized AI agents.**

A locally powered research system where four agents search the live web, write source-grounded summaries, fact-check the findings, and turn everything into a structured research report, all running on your machine with Ollama.

<br>

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?logo=ollama)](https://ollama.com/)
[![TinyLlama](https://img.shields.io/badge/Model-TinyLlama-0467DF)](https://ollama.com/library/tinyllama)
[![DuckDuckGo](https://img.shields.io/badge/Search-DuckDuckGo-DE5833?logo=duckduckgo&logoColor=white)](https://duckduckgo.com/)

</div>

---

##  Demo


<div align="center">

<!-- Main interface -->
<img width="1917" height="861" alt="Image" src="https://github.com/user-attachments/assets/c2b77894-2b63-44e6-93f2-aab788c1176c" />



<br>

<!-- Results -->
<img width="1917" height="873" alt="Image" src="https://github.com/user-attachments/assets/752c1293-a391-4cfd-ac38-17a0db83bd7c" />


</div>


---

##  Overview

Research-Pilot splits the research workflow across **four specialized agents** instead of asking one model to do everything. Each agent has a single job and passes its output to the next stage, so every step is easier to inspect, debug, and improve.

Findings are grounded in **real web sources** retrieved through DuckDuckGo (no API key required). Sources are numbered `[S1]`, `[S2]`, … and every summary bullet is checked against the source it cites. LLM inference runs locally through **Ollama**, so there are no paid LLM APIs involved.

### Research Pipeline

```
Research Topic
      │
      ▼
 Search Agent        →  Collects real web sources, numbered [S1], [S2], ...
      │
      ▼
 Summarizer Agent    →  Writes bullets and verifies each one against its cited source
      │
      ▼
 Fact-Checker Agent  →  Automated grounding check + AI review
      │
      ▼
 Report Agent        →  Produces the final structured research report
```

---

##  Key Features

- **Multi-agent architecture**: four focused agents coordinated by a single orchestrator
- **Real web search**: live sources via DuckDuckGo, no API key needed
- **Source-grounded summaries**: every bullet is verified against its cited source, and unsupported claims are removed
- **Two-layer fact-checking**: an automated grounding check combined with an AI review
- **Structured reports**: clean, readable final output built from verified findings
- **Local LLM inference**: runs on Ollama with a lightweight model, so it works on modest hardware
- **Web interface**: Flask app with a simple UI and a JSON API
- **Modular design**: each agent lives in its own module and can be modified or replaced independently

---

##  Agents

| Agent | Role | Responsibility |
| --- | --- | --- |
| **Search Agent** | Information collector | Searches the web and gathers numbered sources for the topic |
| **Summarizer Agent** | Insight extractor | Condenses sources into concise bullets, each verified against its cited source |
| **Fact-Checker Agent** | Quality reviewer | Runs a grounding check and an AI review for gaps, bias, and unsupported claims |
| **Report Agent** | Research writer | Combines summary, feedback, and sources into the final report |

The **orchestrator** (`orchestrator.py`) runs the agents in sequence and returns a single result containing the search results, summary, fact-check feedback, and final report.

---

##  Tech Stack

| Technology | Purpose |
| --- | --- |
| **Python** | Core application and agent logic |
| **Flask** | Web server and REST API |
| **Ollama** | Local LLM runtime |
| **TinyLlama** | Default lightweight language model |
| **ddgs (DuckDuckGo)** | Real web search for the Search Agent |
| **Requests** | HTTP calls to the local Ollama service |
| **Gunicorn** | Production WSGI server |

---

##  Project Structure

```
Research-Pilot/
│
├── agents/
│   ├── __init__.py
│   ├── search_agent.py       # Web search and source collection
│   ├── summarize_agent.py    # Source-verified summarization
│   ├── checker_agent.py      # Grounding check + AI fact review
│   └── report_agent.py       # Final report generation
│
├── templates/                # HTML templates (Flask)
├── static/                   # CSS, JS, and static assets
├── assets/screenshots/       # README demo screenshots
│
├── app.py                    # Flask app and API endpoint
├── orchestrator.py           # Runs the four-agent pipeline
├── frontend.py               # Alternative Streamlit interface (optional)
├── requirements.txt
└── README.md
```

---

##  Getting Started

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) installed
- An internet connection (the Search Agent queries the live web)
- Enough free disk space and RAM for the selected model

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/Esha-Mirza/Research-Pilot.git
cd Research-Pilot
```

**2. Create a virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Pull the local model**

```bash
ollama pull tinyllama
```

### Run the App

**1. Start Ollama**

```bash
ollama serve
```

**2. Start Research-Pilot** (in a new terminal)

```bash
python app.py
```

**3. Open your browser**

```
http://localhost:5000
```

> **Optional:** a Streamlit interface is also included. Install it with `pip install streamlit`, then run `streamlit run frontend.py`.

---

##  Usage

1. Enter a research topic, for example `AI trends in healthcare`
2. Start the research run
3. Wait while the agents search, summarize, fact-check, and write
4. Review the sources, summary, fact-check feedback, and final report

### API

The Flask backend exposes a single endpoint:

```http
POST /api/research
Content-Type: application/json

{ "topic": "AI trends in healthcare" }
```

**Response**

```json
{
  "search":   "numbered web sources [S1], [S2], ...",
  "summary":  "source-verified summary",
  "feedback": "fact-checker review",
  "report":   "final structured report"
}
```

An empty topic returns `400`, and pipeline failures return `500` with an `error` message.

---

##  Example Topics

- Artificial intelligence in healthcare
- Renewable energy technologies
- Quantum computing applications
- Electric vehicle market trends
- Blockchain in finance
- Cybersecurity developments

---

##  Design Principles

- **Specialized agents**: one responsibility per agent
- **Grounded outputs**: claims are tied to numbered sources and verified before they reach the report
- **Sequential pipeline**: each stage feeds the next, keeping the flow predictable
- **Local-first inference**: the LLM runs on your machine through Ollama
- **Modular architecture**: easy to extend, swap, or test individual agents

---

##  Roadmap

- [x] Real-time web search
- [x] Numbered source citations
- [x] Source-grounded summary verification
- [ ] PDF and Markdown report export
- [ ] Research history and session management
- [ ] Parallel agent execution
- [ ] Model selection from the UI
- [ ] Source credibility scoring

---

##  Privacy

LLM processing runs locally through Ollama, so prompts and generated text are not sent to a cloud LLM provider. The Search Agent does query DuckDuckGo to retrieve web sources, so search queries leave your machine.

---

##  Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push the branch and open a pull request

For larger changes, please open an issue first to discuss what you would like to change.

---

##  License

Distributed under the MIT License. See the `LICENSE` file for details.

---

## Author

**Esha Mirza**

[![GitHub](https://img.shields.io/badge/GitHub-Esha--Mirza-181717?logo=github)](https://github.com/Esha-Mirza)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-esha--mirza1623-0A66C2?logo=linkedin&logoColor=white)](https://linkedin.com/in/esha-mirza1623)

---

<div align="center">

** Research-Pilot**

*Research smarter with a team of specialized AI agents.*

</div>
