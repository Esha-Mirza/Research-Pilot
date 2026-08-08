import streamlit as st
from orchestrator import run_research

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Multi-Agent Research Assistant")
st.markdown("*AI agents collaborate to research any topic*")

with st.sidebar:
    st.header("🤖 Agents")
    st.write("""
    1. 🔍 **Search Agent** - Collects information
    2. 📝 **Summarizer Agent** - Condenses findings
    3. ✅ **Fact-Checker Agent** - Reviews for accuracy
    4. 📄 **Report Agent** - Generates final report
    """)
    
    st.header("💡 Example Topics")
    st.write("""
    - AI trends in healthcare
    - Electric vehicle market 2024
    - Blockchain in finance
    - Renewable energy startups
    - Quantum computing applications
    """)

topic = st.text_input("📝 Enter a research topic:", placeholder="e.g., AI trends in healthcare")

if st.button("🚀 Run Research", type="primary"):
    if topic:
        with st.spinner("🧠 Agents working..."):
            try:
                results = run_research(topic)
                
                tabs = st.tabs(["🔍 Search", "📝 Summary", "✅ Feedback", "📄 Report"])
                
                with tabs[0]:
                    st.subheader("Search Results")
                    st.text(results.get("search", "N/A"))
                
                with tabs[1]:
                    st.subheader("Summary")
                    st.write(results.get("summary", "N/A"))
                
                with tabs[2]:
                    st.subheader("Fact-Checker Feedback")
                    st.write(results.get("feedback", "N/A"))
                
                with tabs[3]:
                    st.subheader("Final Report")
                    st.write(results.get("report", "N/A"))
                
                # Download all results
                export = f"""=== MULTI-AGENT RESEARCH ===
Topic: {topic}

🔍 SEARCH:
{results.get('search', 'N/A')}

📝 SUMMARY:
{results.get('summary', 'N/A')}

✅ FEEDBACK:
{results.get('feedback', 'N/A')}

📄 REPORT:
{results.get('report', 'N/A')}
"""
                st.download_button(
                    label="📥 Download Research Package",
                    data=export,
                    file_name=f"research_{topic.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("⚠️ Please enter a research topic")

st.caption("🧠 Multi-Agent Research Assistant | Powered by TinyLlama via Ollama")