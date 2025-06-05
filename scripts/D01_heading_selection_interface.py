# %%

import streamlit as st
import json
from pathlib import Path
import pandas as pd
import re

st.set_page_config(layout="wide")


def remove_span(s):
    pattern = r'<span\s+id=".+?">.*?</span>'
    output_string = re.sub(pattern, "", s, flags=re.DOTALL | re.IGNORECASE)
    return output_string


# files:
HEADING_SELECTION = Path(
    "data/plan_documents/Dashboard_outputs/D01_selected_headings.json"
)

if HEADING_SELECTION.exists():
    with open(HEADING_SELECTION, "r") as f:
        st.session_state["selection"] = json.loads(f.read())
else:
    st.session_state["selection"] = {}

if "FILES" not in st.session_state:
    st.session_state["FILES"] = list(Path("./data/plan_documents/md/").iterdir())
    st.session_state["INDEX"] = 0


active_file = st.session_state["FILES"][st.session_state["INDEX"]]

with open(file=active_file, mode="r", encoding="utf-8") as f:
    data = list(dict.fromkeys([remove_span(x) for x in f.read().split("\n")]))

heading_selection = {}

st.markdown(
    f"### {st.session_state['INDEX']} / {len(st.session_state['FILES'])} -> {active_file.stem}",
    unsafe_allow_html=True,
)
with st.container(height=700):
    for heading in data:
        heading_selection[heading] = st.checkbox(label=heading, value=False)
# %%
prev, submit, next_ = st.columns([1, 1, 1])
with submit:
    if st.button("submit", use_container_width=70):
        st.session_state["selection"][active_file.stem] = [
            h for h, v in heading_selection.items() if v
        ]
        with open(HEADING_SELECTION, "w") as f:
            f.write(json.dumps(st.session_state["selection"], indent=4))
        st.session_state["INDEX"] += 1
        del heading_selection
        st.rerun()
with prev:
    if st.button("previous"):
        st.session_state["INDEX"] -= 1
        st.rerun()

with next_:
    if st.button("next"):
        st.session_state["INDEX"] += 1
        st.rerun()
