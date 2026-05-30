import streamlit as st
import datetime
# Assuming agent.py is in the same directory and run_agent returns a string
from agent import run_agent, MODELS

# --- Page Configuration ---
st.set_page_config(page_title="First Mate", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS ---
st.markdown("""
<style>
    /* make markdown tables look better */
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th { background: rgba(128,128,128,0.1); padding: 8px 12px; text-align: left; font-weight: 600; }
    td { padding: 8px 12px; border-bottom: 1px solid rgba(128,128,128,0.1); }
    tr:last-child td { border-bottom: none; }
    
    /* Fix duplicate blockquote styling */
    [data-testid="stMarkdownContainer"] blockquote {
    border-left: 4px solid #ed6c02 !important;
    background-color: #fff4e5 !important;
    color: #4a2800 !important;
    padding: 12px 16px !important;
    margin: 8px 0 !important;
    border-radius: 0 6px 6px 0 !important;
    display: flex !important;
    align-items: center !important;
}
    [data-testid="stMarkdownContainer"] blockquote p {
    color: #4a2800 !important;
    margin: 0 !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
}
    [data-testid="stMarkdownContainer"] blockquote strong {
    color: #b45309 !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🏴‍☠️ First Mate")
    st.caption("GitHub + Sentry, powered by Coral SQL")

    nav_selection = st.radio(
        "Navigation",
        ["🛠️ Triage issues", "📝 Release notes", "🔴 Error intelligence"],
        label_visibility="collapsed"
    )

    for _ in range(12):
        st.write("")

    selected_model = st.selectbox(
        "Model",
        options=list(MODELS.keys()),
        help="Select the underlying LLM model"
    )

# --- Main Content Routing ---
if nav_selection == "🛠️ Triage issues":
    st.markdown("## Issue triage <span class='github-badge'>GitHub</span>", unsafe_allow_html=True)
    st.divider()

    # Input Row
    col1, col2 = st.columns([5, 1], vertical_alignment="bottom")
    with col1:
        repo_input = st.text_input("Repository", placeholder="owner/repo", label_visibility="collapsed")
    with col2:
        run_btn = st.button("▶ Triage", use_container_width=True, type="primary")

    st.write("") 

    # Execution
    if run_btn:
        if "/" not in repo_input:
            st.error("❌ Invalid format. Please use 'owner/repo'.")
        else:
            owner, repo = repo_input.split("/", 1)
            prompt = f"Triage open issues for {owner}/{repo}. Find duplicates and suggest priority labels."
            
            with st.status("⚓ **Querying Coral SQL & analyzing...**", expanded=True) as status:
                st.write("Executing `triage_issues` tool...")
                
                # Call your agent backend
                try:
                    print(f"Running agent with prompt: {prompt} and model: {selected_model}")
                    response = run_agent(prompt, model=selected_model)
                    print(f"Agent response: {response}")
                    status.update(label="Triage Complete!", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="Failed", state="error")
                    st.error(f"Error running agent: {e}")
                    response = None

            # Render the Markdown output from the agent
            if response:
                with st.container(border=True):
                    # st.markdown(response)
                    st.markdown(response)

elif nav_selection == "📝 Release notes":
    st.markdown("## Release notes <span class='github-badge'>GitHub</span>", unsafe_allow_html=True)
    st.divider()

    # Input Row for Release Notes
    col1, col2, col3 = st.columns([3, 2, 1], vertical_alignment="bottom")
    with col1:
        repo_input = st.text_input("Repository", placeholder="owner/repo", key="repo_rn", label_visibility="collapsed")
    with col2:
        # Streamlit date picker to replace the YYYY-MM-DD CLI argument
        since_date = st.date_input("Since Date", value=datetime.date.today() - datetime.timedelta(days=7))
    with col3:
        run_btn = st.button("▶ Draft Notes", use_container_width=True, type="primary")

    st.write("")

    # Execution
    if run_btn:
        if "/" not in repo_input:
            st.error("❌ Invalid format. Please use 'owner/repo'.")
        else:
            owner, repo = repo_input.split("/", 1)
            date_str = since_date.strftime("%Y-%m-%d")
            prompt = f"Draft release notes for {owner}/{repo} for all PRs merged since {date_str}."
            
            with st.status(f"⚓ **Fetching PRs since {date_str}...**", expanded=True) as status:
                st.write("Executing `draft_release_notes` tool...")
                
                try:
                    response = run_agent(prompt, model=selected_model)
                    status.update(label="Draft Complete!", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="Failed", state="error")
                    st.error(f"Error running agent: {e}")
                    response = None

            if response:
                with st.container(border=True):
                    st.markdown(response)
elif nav_selection == "🔴 Error intelligence":
    st.markdown("## Error intelligence <span class='github-badge'>GitHub</span> <span class='github-badge' style='background:#e74c3c'>Sentry</span>", unsafe_allow_html=True)
    st.caption("Cross-join merged PRs with Sentry errors to find which PRs introduced bugs.")
    st.divider()

    col1, col2, col3 = st.columns([3, 2, 1], vertical_alignment="bottom")
    with col1:
        repo_input = st.text_input(
            "Repository",
            placeholder="owner/repo", key="repo_ei",
            label_visibility="collapsed"
        )
    with col2:
        sentry_project = st.text_input(
        "Sentry project",
        value="python",
        placeholder="your-project-name",
        key="sentry_proj",
        label_visibility="collapsed"
    )
        
    with col3:
        run_btn = st.button("▶ Analyse", use_container_width=True, type="primary")

    st.write("")

    if run_btn:
        if "/" not in repo_input:
            st.error("❌ Invalid format. Please use 'owner/repo'.")
        else:
            owner, repo = repo_input.split("/", 1)
            prompt = (
                f"Run error intelligence for GitHub repo {owner}/{repo} "
                f"and Sentry project {sentry_project}. "
                f"Show unresolved Sentry errors and correlate them with recent merged PRs."
            )

            with st.status("🔴 **Querying GitHub + Sentry via Coral SQL...**", expanded=True) as status:
                st.write("Executing `error_intelligence` tool...")
                try:
                    response = run_agent(prompt, model=selected_model)
                    status.update(label="Analysis Complete!", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="Failed", state="error")
                    st.error(f"Error running agent: {e}")
                    response = None

            if response:
                with st.container(border=True):
                    st.markdown(response)