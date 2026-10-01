import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from backend.auth import login_screen, user_metrics
from backend.data_engine import load_multiple_files
from frontend.styles import apply_theme
from pages.dashboard import render_dashboard
from pages.data_preview import render_data_preview
from pages.data_quality import render_data_quality
from pages.statistics import render_statistics
from pages.insights import render_insights
from pages.ask_ai import render_ask_ai
from pages.reports import render_reports
from pages.charts import render_charts
from pages.forecast import render_forecast

st.set_page_config(page_title="HATH HACKERS | AI Data Analyst",page_icon="📊",layout="wide",initial_sidebar_state="expanded")
apply_theme()
if "user" not in st.session_state:
    login_screen(); st.stop()

with st.sidebar:
    st.markdown("<div class='side-brand'>HATH <span>HACKERS</span><small>AI DATA INTELLIGENCE</small></div>",unsafe_allow_html=True)
    st.caption(f"Signed in: {st.session_state.user['email']}")
    if st.button("Sign out",use_container_width=True):
        st.session_state.pop("user",None); st.rerun()
    st.divider()
    uploaded=st.file_uploader("Upload multiple datasets",type=["csv","xlsx","xls"],accept_multiple_files=True,help="Select several related or complementary CSV/Excel files.")
    if uploaded:
        signature=tuple((f.name,len(f.getvalue())) for f in uploaded)
        if st.session_state.get("upload_signature")!=signature:
            try:
                datasets,combined,errors=load_multiple_files(uploaded)
                st.session_state.datasets=datasets; st.session_state.data=combined; st.session_state.dataset_names=list(datasets); st.session_state.dataset_name=", ".join(datasets); st.session_state.upload_errors=errors; st.session_state.upload_signature=signature; st.session_state.custom_charts=[]; st.session_state.ai_history=[]
            except Exception as exc: st.error(str(exc))
        if st.session_state.get("upload_errors"):
            for name,err in st.session_state.upload_errors.items(): st.warning(f"{name}: {err}")
        st.success(f"Loaded {len(st.session_state.get('datasets',{}))} file(s)")
    elif "data" not in st.session_state:
        st.info("Upload CSV or Excel files to begin.")
    st.divider()
    pages={"Dashboard":render_dashboard,"Data Preview":render_data_preview,"Data Quality":render_data_quality,"Statistics":render_statistics,"Charts Studio":render_charts,"Forecast Lab":render_forecast,"AI Insights":render_insights,"Ask AI":render_ask_ai,"Reports":render_reports}
    selection=st.radio("WORKSPACE",list(pages.keys()),label_visibility="visible")
    st.divider()
    total,logins,recent=user_metrics()
    st.caption(f"Registered users: {total} · Login events: {logins}")
if "data" not in st.session_state:
    st.title("HATH HACKERS")
    st.subheader("AI-powered data analysis workspace")
    st.markdown("Upload multiple related CSV or Excel files to explore combined records, quality checks, statistics, colourful charts, AI insights and downloadable reports.")
    st.stop()
pages[selection]()
