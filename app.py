import streamlit as st
import datetime
# Assuming agent.py is in the same directory and run_agent returns a string
from agent import run_agent, MODELS

# --- Page Configuration ---
st.set_page_config(
    page_title="First Mate", 
    page_icon="🏴‍☠️", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- Enhanced Custom CSS ---
st.markdown("""
<style>
    /* Reduce default top padding */
    .block-container { padding-top: 2rem; }

    /* Make markdown tables look better */
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

    /* Missing Badge Styles */
    .github-badge {
        background-color: #24292e; color: white; padding: 4px 8px; 
        border-radius: 12px; font-size: 12px; font-weight: 600; 
        vertical-align: middle; margin-left: 8px;
    }
    .sentry-badge {
        background-color: #362d59; color: white; padding: 4px 8px; 
        border-radius: 12px; font-size: 12px; font-weight: 600; 
        vertical-align: middle; margin-left: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🏴‍☠️ First Mate")
    st.caption("GitHub + Sentry, powered by Coral SQL")
    st.divider()

    nav_selection = st.radio(
        "Navigation",
        ["🛠️ Triage issues", "📝 Release notes", "🔴 Error intelligence"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    selected_model = st.selectbox(
        "🧠 Agent Model",
        options=list(MODELS.keys()),
        help="Select the underlying LLM model for the agent"
    )

@st.cache_data(ttl=300, show_spinner=False)
def cached_agent(prompt_text: str, model: str) -> str:
    return run_agent(prompt_text, model=model)

# --- Helper Function for Execution ---
def execute_agent(prompt_text, status_msg, success_msg):
    with st.status(status_msg, expanded=True) as status:
        st.write("Executing tool...")
        try:
            response = cached_agent(prompt_text, selected_model)
            # response = run_agent(prompt_text, model=selected_model)
            status.update(label=success_msg, state="complete", expanded=False)
            st.toast("✅ " + success_msg)
            return response
        except Exception as e:
            status.update(label="Failed to run agent", state="error")
            st.error(f"Error running agent: {e}")
            return None

# --- Main Content Routing ---
if nav_selection == "🛠️ Triage issues":
    st.markdown("### Issue triage <span class='github-badge'>GitHub</span>", unsafe_allow_html=True)
    st.caption("Identify duplicates and suggest priority labels for open issues.")
    
    # Input Row in a styled container
    with st.container(border=True):
        col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
        with col1:
            repo_input = st.text_input("Target Repository", placeholder="e.g., facebook/react", label_visibility="visible")
        with col2:
            run_btn = st.button("▶ Triage", use_container_width=True, type="primary")

    # Execution & Results
    if run_btn:
        if "/" not in repo_input:
            st.error("❌ Invalid format. Please use 'owner/repo'.")
        else:
            owner, repo = repo_input.split("/", 1)
            prompt = f"Triage open issues for {owner}/{repo}. Find duplicates and suggest priority labels."
            
            response = execute_agent(
                prompt_text=prompt, 
                status_msg="⚓ **Querying Coral SQL & analyzing...**", 
                success_msg="Triage Complete!"
            )
            
            if response:
                with st.container(border=True):
                    st.markdown(response)
    else:
        st.info("👆 Enter a repository above to start triaging issues.")

elif nav_selection == "📝 Release notes":
    st.markdown("### Release notes <span class='github-badge'>GitHub</span>", unsafe_allow_html=True)
    st.caption("Draft release notes based on merged pull requests.")

    # Input Row
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 2, 1], vertical_alignment="bottom")
        with col1:
            repo_input = st.text_input("Target Repository", placeholder="e.g., facebook/react", key="repo_rn")
        with col2:
            since_date = st.date_input("Since Date", value=datetime.date.today() - datetime.timedelta(days=7))
        with col3:
            run_btn = st.button("▶ Draft Notes", use_container_width=True, type="primary")

    # Execution & Results
    if run_btn:
        if "/" not in repo_input:
            st.error("❌ Invalid format. Please use 'owner/repo'.")
        else:
            owner, repo = repo_input.split("/", 1)
            date_str = since_date.strftime("%Y-%m-%d")
            prompt = f"Draft release notes for {owner}/{repo} for all PRs merged since {date_str}."
            
            response = execute_agent(
                prompt_text=prompt, 
                status_msg=f"⚓ **Fetching PRs since {date_str}...**", 
                success_msg="Release Notes Generated!"
            )

            if response:
                with st.container(border=True):
                    st.markdown(response)
    else:
        st.info("👆 Select a repository and date to draft your release notes.")

elif nav_selection == "🔴 Error intelligence":
    st.markdown("### Error intelligence <span class='github-badge'>GitHub</span> <span class='sentry-badge'>Sentry</span>", unsafe_allow_html=True)
    st.caption("Find which recent GitHub pull requests are linked to current Sentry errors.")

    # Input Row
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 2, 1], vertical_alignment="bottom")
        with col1:
            repo_input = st.text_input("Target Repository", placeholder="e.g., facebook/react", key="repo_ei")
        with col2:
            sentry_project = st.text_input("Sentry Project", value="python", placeholder="your-project-name", key="sentry_proj")
        with col3:
            run_btn = st.button("▶ Analyse", use_container_width=True, type="primary")

    # Execution & Results
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

            response = execute_agent(
                prompt_text=prompt, 
                status_msg="🔴 **Querying GitHub + Sentry via Coral SQL...**", 
                success_msg="Error Analysis Complete!"
            )

            if response:
                with st.container(border=True):
                    st.markdown(response)
    else:
        st.info("👆 Enter your repository and Sentry project details to correlate errors.")