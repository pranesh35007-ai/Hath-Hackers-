import numpy as np
import pandas as pd
import plotly.express as px

PALETTE=["#3978F6","#9B59D0","#16B8A6","#F59E0B","#EF648A","#22A6D5","#8BC34A","#F97316"]

def base(fig):
    fig.update_layout(template="plotly_white",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="Inter, Arial",color="#203047"),margin=dict(l=22,r=22,t=65,b=35),legend_title_text="",title_font=dict(size=17))
    return fig

def auto_charts(df):
    charts=[]; nums=df.select_dtypes(include=np.number).columns.tolist(); cats=[c for c in df.select_dtypes(include=["object","category","bool"]).columns if c!="_source_file"]; dates=df.select_dtypes(include=["datetime64[ns]","datetime64[ns, UTC]"]).columns.tolist()
    if dates and nums:
        x,y=dates[0],nums[0]; d=df[[x,y]].dropna().groupby(x,as_index=False)[y].sum().sort_values(x)
        if len(d): charts.append(("Trend",base(px.area(d,x=x,y=y,title=f"{y} over time",color_discrete_sequence=[PALETTE[2]]))))
    if cats and nums:
        c,y=cats[0],nums[0]; d=df[[c,y]].dropna().groupby(c,as_index=False)[y].sum().sort_values(y,ascending=False).head(12)
        if len(d): charts.append(("Category performance",base(px.bar(d,x=c,y=y,color=c,title=f"{y} by {c}",color_discrete_sequence=PALETTE))))
        d2=df[c].value_counts().head(8).rename_axis(c).reset_index(name="Records")
        if len(d2)>1: charts.append(("Category mix",base(px.pie(d2,names=c,values="Records",hole=.48,title=f"Records by {c}",color_discrete_sequence=PALETTE))))
    if len(nums)>=2:
        x,y=nums[:2]; d=df[[x,y]].dropna().head(5000)
        if len(d): charts.append(("Variable relationship",base(px.scatter(d,x=x,y=y,title=f"{y} vs {x}",color_discrete_sequence=[PALETTE[1]]))))
        corr=df[nums[:15]].corr(numeric_only=True)
        if len(corr)>1: charts.append(("Correlation map",base(px.imshow(corr,text_auto=".2f",aspect="auto",title="Numeric correlation heatmap",color_continuous_scale=["#F4F7FB",PALETTE[0],"#15294B"]))))
    if nums:
        y=nums[-1]; charts.append(("Distribution",base(px.histogram(df,x=y,nbins=30,title=f"Distribution of {y}",color_discrete_sequence=[PALETTE[3]]))))
        if cats:
            c=cats[min(1,len(cats)-1)]; d=df[[c,y]].dropna()
            if len(d): charts.append(("Spread by group",base(px.box(d,x=c,y=y,color=c,title=f"{y} spread by {c}",color_discrete_sequence=PALETTE))))
    return charts

def build_custom_chart(df, chart_type, x, y=None, color=None, aggregation="Sum", title=None):
    work=df.copy(); title=title or f"{chart_type.title()} chart"
    if chart_type in ["Histogram","Box plot"]:
        if not y: y=x
        if chart_type=="Histogram": fig=px.histogram(work,x=x,color=color,title=title,color_discrete_sequence=PALETTE)
        else: fig=px.box(work,x=color,y=y if color else None,title=title,color_discrete_sequence=PALETTE)
    elif chart_type=="Heatmap":
        nums=work.select_dtypes(include=np.number).columns.tolist(); fig=px.imshow(work[nums].corr(),text_auto=".2f",title=title,color_continuous_scale=["#F4F7FB",PALETTE[0],"#15294B"])
    else:
        if not y: raise ValueError("Choose a Y-axis field.")
        if aggregation=="Count": d=work.groupby(x,dropna=False).size().reset_index(name="_value"); val="_value"
        else:
            fn={"Sum":"sum","Average":"mean","Minimum":"min","Maximum":"max"}[aggregation]
            d=work.groupby(x,dropna=False)[y].agg(fn).reset_index(); val=y
        if chart_type=="Bar": fig=px.bar(d,x=x,y=val,color=color if color in d.columns else x,title=title,color_discrete_sequence=PALETTE)
        elif chart_type=="Line": fig=px.line(d,x=x,y=val,color=color if color in d.columns else None,markers=True,title=title,color_discrete_sequence=PALETTE)
        elif chart_type=="Area": fig=px.area(d,x=x,y=val,color=color if color in d.columns else None,title=title,color_discrete_sequence=PALETTE)
        elif chart_type in ["Pie","Donut"]: fig=px.pie(d,names=x,values=val,hole=.5 if chart_type=="Donut" else 0,title=title,color_discrete_sequence=PALETTE)
        elif chart_type=="Scatter": fig=px.scatter(work,x=x,y=y,color=color if color in work.columns else None,title=title,color_discrete_sequence=PALETTE)
        elif chart_type=="Treemap": fig=px.treemap(d,path=[x],values=val,title=title,color_discrete_sequence=PALETTE)
        else: raise ValueError("Unsupported chart type")
    return base(fig)
