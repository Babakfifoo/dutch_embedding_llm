# %%
import streamlit as st
import json
from tools import COLOR_DICT, setup_colors


def colorise(s):
    for k, v in COLOR_DICT.items():
        s = s.replace(k, f"<span class=\"{v}\">{k}</span>")
        s = s.replace("story", "recovery")
    return s


def bool_cleaner(s: str) -> bool:
    # validating the answer
    if not isinstance(s, str):
        return False
    if "true" in s.lower():
        return True
    return False


def extract_true_ones(lst: list) -> dict:
    imros = [p.get("IMRO") for p in lst]
    answers = [bool_cleaner(p.get("answer")) for p in lst]
    return {k: v for k, v in dict(zip(imros, answers)).items() if v}


setup_colors()


manual_answers_file = "./data/plan_documents/results/inspecting_false/result_purchase.json"
LLM_answer_file = "./data/plan_documents/answered/purchase agreement.json"
FACTOR = "Purchase Agreement"

if "original" not in st.session_state:
    with open(LLM_answer_file, "r") as f:
        st.session_state["original"] = json.loads(f.read())

try:
    with open(manual_answers_file, "r") as f:
        st.session_state["manual_answer"] = json.loads(f.read())
except Exception as e:
    print(f"{e}\nresult file not found. Creating one ...")
    st.session_state["manual_answer"] = extract_true_ones(st.session_state["original"])
    with open(manual_answers_file, "w") as f:
        f.write(json.dumps(st.session_state["manual_answer"]))

if "LLM_operating" not in st.session_state:
    st.session_state["LLM_operating"] = [
        p
        for p in st.session_state["original"]
        if not bool_cleaner(p.get("answer", False))
    ]
    st.session_state["plan_idx"] = 0


active_plan = st.session_state["LLM_operating"][st.session_state["plan_idx"]]
active_plan["answer"] = bool_cleaner(active_plan.get("answer"))


st.title(
    body=f"{st.session_state['plan_idx']} / {len(st.session_state['LLM_operating'])} -> {active_plan.get('IMRO')}"
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
            if st.button("submit") or active_plan["answer"]:
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
