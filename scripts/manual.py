# %%
import streamlit as st
import json
import pandas as pd
from itertools import groupby
from pathlib import Path
from tools.dashboard import setup_colors, COLOR_DICT

setup_colors()


def colorise(s):
    for k, v in COLOR_DICT.items():
        s = s.replace(k, f'<span class="{v}">{k}</span>')
        s = s.replace("story", "recovery")
    return s


# %%
manual_answers_file = Path(
    "./data/new/manual.json"
)

if manual_answers_file.exists():
    with open(manual_answers_file, "r") as f:
        st.session_state["manual_answer"] = json.loads(f.read())
else:
    st.session_state["manual_answer"] = {}

if "plan_data" not in st.session_state:
    st.session_state["plan_data"] = pd.read_parquet("./data/new/translations/translations.parquet")
    st.session_state["plan_idx"] = len(st.session_state["manual_answer"].keys())


active_plan = st.session_state["plan_data"].iloc[st.session_state["plan_idx"]]

st.title(
    body=f"{st.session_state['plan_idx']} / {len(st.session_state['plan_data'])} -> {active_plan.get('IMRO')}"
)
Information, Questions = st.columns([2, 1])
# %%
with Information:
    st.markdown("#### Information")
    with st.container(height=700):
        st.markdown(body=colorise(active_plan.get("en")), unsafe_allow_html=True)
# %%

MANUAL_QUESTIONS = {
    "DCP": "Development Contributions Plans (DCP)",
    "DA": "Development Agreements (DA)",
    "PLD": "Public Land Development (PLD)",
    "PDP": "Partly DA, and partly PLD",
    "DUO": "Both DA and PLD",
    "INI": "Initiator/private party",
    "MUN": "Municipality covers the costs",
    "HS": "Housing association",
    "CO": "Conservative Plans",
    "LES": "Land Exploitation Scheme",
    "INV": "Invalid"
}

with Questions:
    st.markdown("#### Answers:")
    with st.container(height=750):
        existing_answers = st.session_state["manual_answer"].get(
            active_plan.get("IMRO", None),
            dict(zip(MANUAL_QUESTIONS.keys(), [False] * len(MANUAL_QUESTIONS.keys()))),
        )

        for k, name in MANUAL_QUESTIONS.items():
            if existing_answers.get(str(k), None):
                default_index = existing_answers[str(k)]
            else:
                default_index = False
                existing_answers[k] = False
            existing_answers[k] = st.checkbox(label=MANUAL_QUESTIONS[k], value=default_index)

        submit, prev, next_ = st.columns([1, 1, 1])

        with submit:
            if st.button("submit"):
                st.session_state["manual_answer"][active_plan.get("IMRO")] = (
                    existing_answers
                )
                with open(manual_answers_file, "w") as f:
                    f.write(json.dumps(st.session_state["manual_answer"], indent=4))
                st.session_state["plan_idx"] += 1
                st.rerun()

        with prev:
            if st.button("previous"):
                st.session_state["plan_idx"] -= 1
                st.rerun()

        with next_:
            if st.button("next"):
                st.session_state["plan_idx"] += 1
                st.rerun()

