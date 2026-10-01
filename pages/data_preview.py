import streamlit as st
from backend.data_engine import profile

def render_data_preview():
    st.title("Data Preview")
    datasets=st.session_state.get("datasets",{})
    if datasets:
        choice=st.selectbox("Choose uploaded file",["Combined analysis"]+list(datasets.keys()))
        df=st.session_state.data if choice=="Combined analysis" else datasets[choice]
    else: df=st.session_state.data; choice=st.session_state.dataset_name
    p=profile(df); a,b,c=st.columns(3); a.metric("Rows",f"{p['rows']:,}"); b.metric("Columns",f"{p['columns']:,}"); c.metric("Numeric fields",f"{len(p['numeric']):,}")
    st.caption(f"Preview: {choice}"); st.dataframe(df.head(200),use_container_width=True,height=500)
    st.download_button("Download processed CSV",df.to_csv(index=False).encode("utf-8"),"hath_hackers_processed.csv","text/csv")
