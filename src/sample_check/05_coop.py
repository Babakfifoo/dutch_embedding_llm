# %%
import streamlit as st
import json
from tools import COLOR_DICT, setup_colors
import random

random.seed(2025)
# %%


def colorise(s):
    for k, v in COLOR_DICT.items():
        s = s.replace(k, f'<span class="{v}">{k}</span>')
        s = s.replace("story", "recovery")
    return s


def bool_cleaner(s: str) -> bool:
    # validating the answer
    if not isinstance(s, str):
        return False
    if "true" in s.lower():
        return True
    return False


setup_colors()


manual_answers_file = (
    "./data/plan_documents/results/manual_inspection/inspection_coop.json"
)
LLM_answer_file = "./data/plan_documents/answered/cooperation agreement.json"
FACTOR = "Cooperation Agreement"

if "original" not in st.session_state:
    with open(LLM_answer_file, "r") as f:
        st.session_state["original"] = json.loads(f.read())

try:
    with open(manual_answers_file, "r") as f:
        st.session_state["manual_answer"] = json.loads(f.read())

except Exception as e:
    print(f"{e}\nresult file not found. Creating one ...")
    st.session_state["manual_answer"] = {}

if "LLM_anterior" not in st.session_state:
    data = [  # Getting the plans with True value ...
        p for p in st.session_state["original"] if json.loads(p.get("answer")).get("answer")
    ]
    if len(data) < 400:
        st.session_state["LLM_anterior"] = data
    else:
        numbers = set(
            random.choices(
                population=range(len(data)),
                k=int(400)  # This is the sample size, set to 10%
            )
        )
        numbers = list(numbers)
        st.session_state["sample"] = len(numbers)
        st.session_state["LLM_anterior"] = [p for i, p in enumerate(data) if i in numbers]
    st.session_state["plan_idx"] = 0


active_plan = st.session_state["LLM_anterior"][st.session_state["plan_idx"]]
active_plan["answer"] = bool_cleaner(active_plan.get("answer"))


st.title(
    body=f"{st.session_state['plan_idx']} / {st.session_state['sample']} -> {active_plan.get('IMRO')}"
)

Information, Questions = st.columns([2, 1])
with Information:
    st.markdown("#### Information")
    with st.container(height=400):
        listOfThings = colorise(s=active_plan.get("context"))
        st.markdown(body=listOfThings, unsafe_allow_html=True)


with Questions:
    st.markdown("#### Answers:")
    with st.container(height=400):
        existing_answers = st.checkbox(label=FACTOR)
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
