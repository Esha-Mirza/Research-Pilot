from agents import search_agent, summarize_agent, checker_agent, report_agent

def run_research(topic: str) -> dict:
    print(f"🔍 Starting research on: {topic}")
    
    # Step 1: Search
    print("📡 Agent 1: Searching...")
    search_results = search_agent.run(topic)
    
    # Step 2: Summarize
    print("📝 Agent 2: Summarizing...")
    summary = summarize_agent.run(search_results)
    
    # Step 3: Fact Check
    print("✅ Agent 3: Fact-checking...")
    feedback = checker_agent.run(summary)
    
    # Step 4: Report
    print("📄 Agent 4: Generating report...")
    report = report_agent.run(summary, feedback)
    
    print("🎯 Research complete!")
    
    return {
        "search": search_results,
        "summary": summary,
        "feedback": feedback,
        "report": report
    }