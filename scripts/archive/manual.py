# %%
import streamlit as st
import json
from pathlib import Path
from scripts.Tools import setup_colors, COLOR_DICT

setup_colors()


def colorise(s):
    for k, v in COLOR_DICT.items():
        s = s.replace(k, f'<span class="{v}">{k}</span>')
        s = s.replace("story", "recovery")
    return s


def merge_sentences(paragraph_ids, sentences):
    merged_paragraphs = {}

    for pid, sentence in zip(paragraph_ids, sentences):
        if pid in merged_paragraphs:
            merged_paragraphs[pid] += " " + sentence
        else:
            merged_paragraphs[pid] = sentence

    return merged_paragraphs


# %%
manual_answers_file = Path("./data/plan_documents/manual.json")

if manual_answers_file.exists():
    with open(manual_answers_file, "r") as f:
        st.session_state["manual_answer"] = json.loads(f.read())
else:
    st.session_state["manual_answer"] = {}

if "plan_data" not in st.session_state:
    with open("./data/plan_documents/translated_selected_sents.json", "r") as f:
        st.session_state["plan_data"] = json.loads(f.read())

    st.session_state["plan_idx"] = 1939  # len(st.session_state["manual_answer"].keys())


active_plan = st.session_state["plan_data"][st.session_state["plan_idx"]]

if active_plan["IMRO"] not in st.session_state["manual_answer"].keys():
    st.markdown(
        f"# {st.session_state['plan_idx']} / {len(st.session_state['plan_data'])} -> {active_plan.get('IMRO')}"
    )
elif not any(list(st.session_state["manual_answer"][active_plan["IMRO"]].values())):
    # if all values are false
    st.markdown(
        f"# {st.session_state['plan_idx']} / {len(st.session_state['plan_data'])} -> {active_plan.get('IMRO')}"
    )
else:
    st.markdown(
        f'# <span class="greenHighlight">{st.session_state["plan_idx"]} / {len(st.session_state["plan_data"])} -> {active_plan.get("IMRO")}</span>',
        unsafe_allow_html=True,
    )

Information, Questions = st.columns([2, 1])
# %%
with Information:
    with st.container(height=700):
        information = merge_sentences(
            paragraph_ids=[x.split(":")[0] for x in active_plan.get("id")],
            sentences=active_plan.get("en"),
        )
        st.markdown(
            body=colorise("\n\n".join(list(information.values()))),
            unsafe_allow_html=True,
        )
# %%

MANUAL_QUESTIONS = {
    "DCP": "Development Contributions Plans (DCP)",
    "DA": "Development Agreements (DA)",
    "PLD": "Public Land Development (PLD)",
    "PDP": "Partly DA, and partly PLD",
    "DUO": "Both DA and PLD",
    "INI": "Initiator/private party",
    "FEE": "Levies and Fees",
    "PPP": "Public Private Participation (PPP)",
    "MUN": "Public Budget",
    "HS": "Housing association",
    "CO": "Conservative Plans",
    "LES": "Land Exploitation Scheme",
    "K10": "Less than 10,00€ cost",
    "SFS": "Space for Space",  # Check this one for all the plans.
    "INV": "Invalid",
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
            existing_answers[k] = st.checkbox(
                label=MANUAL_QUESTIONS[k], value=default_index
            )

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
