# %%
import streamlit as st
import json
from pathlib import Path


# %%
# settings:
st.set_page_config(layout="wide")


# files:
Extraction_QA = Path("data/plan_documents/Dashboard_outputsvalidated_extraction.json")
EXTRACTED = Path("data/plan_documents/extracted.json")

if Extraction_QA.exists():
    with open(Extraction_QA, "r") as f:
        st.session_state["manual_answer"] = json.loads(f.read())
else:
    st.session_state["manual_answer"] = {}


if "plan_data" not in st.session_state:
    with open(EXTRACTED, "r") as f:
        st.session_state["plan_data"] = [
            {"IMRO": k, "text": v} for k, v in json.loads(f.read()).items()
        ]

    st.session_state["plan_idx"] = 1372

active_plan = st.session_state["plan_data"][st.session_state["plan_idx"]]


# %%

# Layout:

Extracted, plan_text, user_input = st.columns(spec=[3, 3, 2])

plan_info = dict()

with plan_text:
    st.markdown(
        f"### {st.session_state['plan_idx']} / {len(st.session_state['plan_data'])} -> {active_plan.get('IMRO')}"
    )
    with st.container(height=850):
        with open(
            f"data/plan_documents/md/{active_plan.get('IMRO')}.md",
            "r",
            encoding="utf-8",
        ) as f:
            plan_text_nl = f.read()
        st.markdown(plan_text_nl, unsafe_allow_html=True)

with Extracted:
    st.markdown("### Extracted")
    with st.container(height=850):
        st.markdown("\n\n".join(active_plan.get("text")))


with user_input:
    st.markdown("### Verdict")
    col1, col2 = st.columns(spec=[1, 1])
    with col1:
        plan_info["Valid Extraction"] = st.radio(
            label="Correct Extraction?",
            options=[True, False],
            format_func=lambda option: "yes" if option else "no",
            horizontal=True,
        )
    with col2:
        plan_info["Valid Document"] = st.radio(
            label="Valid document?", options=["yes", "no"], horizontal=True
        )

    with st.container():
        plan_info["feasability text"] = st.text_area(
            label="input",
            value="\n\n".join(active_plan.get("text")),
            height=700,
            disabled=plan_info["Valid Extraction"],
        )

    submit, prev, next_ = st.columns([1, 1, 1])

    with submit:
        if st.button("submit", use_container_width=70):
            st.session_state["manual_answer"][active_plan.get("IMRO")] = plan_info
            with open(Extraction_QA, "w") as f:
                f.write(json.dumps(st.session_state["manual_answer"], indent=4))
            st.session_state["plan_idx"] += 1
            del plan_info
            st.rerun()

    with prev:
        if st.button("previous", use_container_width=70):
            st.session_state["plan_idx"] -= 1
            st.rerun()

    with next_:
        if st.button("next", use_container_width=70):
            st.session_state["plan_idx"] += 1
            st.rerun()
