import streamlit as st
from backend.chart_engine import auto_charts, build_custom_chart

def render_charts():
    st.title("Charts Studio")
    st.caption("Explore auto-generated visuals, customize them, or build a new chart from your fields.")
    df=st.session_state.data
    if "custom_charts" not in st.session_state: st.session_state.custom_charts=[]
    auto=auto_charts(df)
    st.subheader("Automatically generated charts")
    for i,(name,fig) in enumerate(auto):
        with st.container(border=True):
            st.plotly_chart(fig,use_container_width=True,key=f"auto_chart_{i}")
            with st.expander(f"Customize {name}"):
                c1,c2,c3=st.columns(3)
                typ=c1.selectbox("Chart type",["Bar","Line","Area","Pie","Donut","Scatter","Histogram","Box plot","Treemap","Heatmap"],key=f"auto_type_{i}")
                x=c2.selectbox("X / category",df.columns.tolist(),index=min(i,len(df.columns)-1),key=f"auto_x_{i}")
                y=c3.selectbox("Y / measure",["(none)"]+df.select_dtypes(include="number").columns.tolist(),key=f"auto_y_{i}")
                if st.button("Apply customization",key=f"auto_apply_{i}"):
                    try:
                        new=build_custom_chart(df,typ,x,None if y=="(none)" else y,title=f"{name} — customized")
                        st.session_state.custom_charts.append((f"Customized: {name}",new)); st.success("Customized chart added below."); st.rerun()
                    except Exception as e: st.error(str(e))
    st.divider(); st.subheader("＋ Create a new chart")
    nums=df.select_dtypes(include="number").columns.tolist(); fields=df.columns.tolist()
    with st.form("new_chart_form"):
        a,b=st.columns(2); typ=a.selectbox("Chart type",["Bar","Line","Area","Pie","Donut","Scatter","Histogram","Box plot","Treemap","Heatmap"]); x=b.selectbox("X-axis / category",fields)
        c,d=st.columns(2); y=c.selectbox("Y-axis / measure",["(none)"]+nums); color=d.selectbox("Color by",["(automatic)"]+fields)
        e,f=st.columns(2); agg=e.selectbox("Aggregation",["Sum","Average","Count","Minimum","Maximum"]); title=f.text_input("Chart title",value="My custom analysis")
        make=st.form_submit_button("Create chart",type="primary",use_container_width=True)
    if make:
        try:
            fig=build_custom_chart(df,typ,x,None if y=="(none)" else y,None if color=="(automatic)" else color,agg,title)
            st.session_state.custom_charts.append((title,fig)); st.success("Chart created.")
        except Exception as e: st.error(str(e))
    for i,(name,fig) in enumerate(st.session_state.custom_charts):
        with st.container(border=True): st.markdown(f"**{name}**"); st.plotly_chart(fig,use_container_width=True,key=f"custom_chart_{i}")
