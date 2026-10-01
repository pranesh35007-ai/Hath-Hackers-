import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from backend.chart_engine import base, PALETTE

def render_forecast():
    st.title("Forecast Lab")
    st.caption("A simple trend projection for datasets with a usable date field and numeric measure.")
    df=st.session_state.data
    dates=df.select_dtypes(include=["datetime64[ns]","datetime64[ns, UTC]"]).columns.tolist()
    nums=[c for c in df.select_dtypes(include=np.number).columns if c!="_source_file"]
    if not dates or not nums:
        st.info("A forecast needs at least one detected date column and one numeric measure. Check Data Preview and Data Quality."); return
    a,b,c=st.columns(3)
    date_col=a.selectbox("Date field",dates)
    measure=b.selectbox("Measure",nums)
    horizon=c.selectbox("Future periods",[3,6,12],index=1)
    freq=st.selectbox("Period",["Month","Week","Day"])
    freq_code={"Month":"MS","Week":"W","Day":"D"}[freq]
    d=df[[date_col,measure]].dropna().copy().sort_values(date_col)
    d[date_col]=pd.to_datetime(d[date_col],errors="coerce")
    d=d.dropna().set_index(date_col)[measure].resample(freq_code).sum().reset_index()
    if len(d)<4:
        st.warning("At least four non-empty time periods are recommended for this simple trend projection."); return
    d["_t"]=np.arange(len(d)); slope,intercept=np.polyfit(d["_t"],d[measure],1)
    future_t=np.arange(len(d),len(d)+int(horizon)); future_dates=pd.date_range(d[date_col].max(),periods=int(horizon)+1,freq=freq_code)[1:]
    forecast=pd.DataFrame({date_col:future_dates,measure:intercept+slope*future_t,"Series":"Forecast"})
    actual=d[[date_col,measure]].copy(); actual["Series"]="Actual"
    combined=pd.concat([actual,forecast],ignore_index=True)
    fig=px.line(combined,x=date_col,y=measure,color="Series",markers=True,title=f"{measure}: actual and projected",color_discrete_map={"Actual":PALETTE[0],"Forecast":PALETTE[3]})
    st.plotly_chart(base(fig),use_container_width=True)
    st.dataframe(forecast[[date_col,measure]].rename(columns={date_col:"Period",measure:"Projected value"}),use_container_width=True)
    st.warning("This is an illustrative linear trend projection, not a certainty interval or causal prediction. It does not model seasonality, external drivers, or structural changes.")
    st.session_state.forecast_table=forecast[[date_col,measure]].copy()
