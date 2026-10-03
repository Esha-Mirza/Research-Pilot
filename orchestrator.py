from agents import search_agent, summarize_agent, checker_agent, report_agent

def run_research(topic: str) -> dict:
    print(f"🔍 Starting research on: {topic}")
    
    # Step 1: Search (real web sources, numbered [S1], [S2], ...)
    print("📡 Agent 1: Searching...")
    sources = search_agent.collect(topic)
    search_results = search_agent.format_results(topic, sources)
    
    # Step 2: Summarize (every bullet is verified against its cited source)
    print("📝 Agent 2: Summarizing...")
    summarized = summarize_agent.summarize(topic, sources)
    summary = summarized["text"]
    
    # Step 3: Fact Check (automated grounding check + AI review)
    print("✅ Agent 3: Fact-checking...")
    feedback = checker_agent.run(
        summary, sources, topic=topic,
        removed=summarized["removed"], fallback=summarized["fallback"],
    )
    
    # Step 4: Report
    print("📄 Agent 4: Generating report...")
    report = report_agent.run(summary, feedback, sources, topic=topic)
    
    print("🎯 Research complete!")
    
    return {
        "search": search_results,
        "summary": summary,
        "feedback": feedback,
        "report": report
    }
