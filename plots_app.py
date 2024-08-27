import asyncio
from fasthtml.common import *
from fh_plotly import plotly2fasthtml, plotly_headers


import plotly.express as px
from sse_starlette.sse import EventSourceResponse
import pandas as pd

sselink = Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")

app, rt = fast_app(hdrs=(plotly_headers, sselink), ws_hdr=True)

data = pd.DataFrame({"x": [], "y": []})


def generate_line_chart():
    fig = px.line(data, x="x", y="y", range_y=[0, 100])
    fig.update_layout(xaxis_title="Time", yaxis_title="Value")
    return plotly2fasthtml(fig)


@app.get("/")
def home():
    return Div(
        generate_line_chart(),
        id="chart-container",
        hx_ext="sse",
        sse_connect="/data-notifier",
        sse_swap="PlotUpdateEvent",
    )


@app.ws("/ws")
async def ws(msg: str, send):
    global data
    print("Received:", msg)
    value = float(msg)
    new_row = pd.DataFrame({"x": [pd.Timestamp.now()], "y": [value]})
    data = pd.concat([data, new_row], ignore_index=True)
    if len(data) > 100:
        data = data.iloc[1:]


async def data_notifier():
    while True:
        yield dict(data=to_xml(Div(generate_line_chart())), event="PlotUpdateEvent")
        await asyncio.sleep(1)


@rt("/data-notifier")
async def get():
    return EventSourceResponse(data_notifier())


serve()
