# %%
import streamlit as st
import json
from itertools import groupby
from config import MANUAL_QUESTIONS
from pathlib import Path

st.set_page_config(layout="wide")

st.markdown(
    """
<style>
.orangeHighlight {
    color: #FFA500;
}
.initHighlight {
    color: #FFFF00;
}
.redHighlight {
    color:  #FF0000;
}
.sellHighlight {
    color:  #ff00ff ;
}
.issueHighlight {
    color:  #168f9c ;
}
.buildingplanHighlight {
    color:  #afc87d;
}
.purpleHighlight {
    color:  #2f6e5e;
}
.greenHighlight {
    color:  #00ff00;
}
.anteriorHighlight {
    color:  #00dd66;
}
.ownHighlight {
    color:  #7dafc8;
}
.schemeHighlight {
    color:  #00a0c8;
}
.budgetHighlight {
    color:  #FF0088;
}
.conservativeHighlight {
    color: #555555;
}
</style>
""",
    unsafe_allow_html=True,
)

color_dict = {
    "land": "orangeHighlight",
    "initiator": "initHighlight",
    "applicant": "initHighlight",
    "developer": "initHighlight",
    "cost": "redHighlight",
    "expense": "redHighlight",
    "fee": "redHighlight",
    "risk": "redHighlight",
    "operating plan": "purpleHighlight",
    "operating": "purpleHighlight",
    "exploitation": "purpleHighlight",
    "agreement": "greenHighlight",
    "contract": "greenHighlight",
    "sell": "sellHighlight",
    "sale": "sellHighlight",
    "price": "sellHighlight",
    "buy": "sellHighlight",
    "purchase": "sellHighlight",
    " owned": "ownHighlight",
    " own": "ownHighlight",
    "issuance": "issueHighlight",
    " issue": "issueHighlight",
    " issuing": "issueHighlight",
    "building plan": "buildingplanHighlight",
    "anterior": "anteriorHighlight",
    "Anterior": "anteriorHighlight",
    "scheme": "schemeHighlight",
    "project": "schemeHighlight",
    "budget": "budgetHighlight",
    "municipality": "budgetHighlight",
    "conservative": "conservativeHighlight",
}


def colorise(s):
    for k, v in color_dict.items():
        s = s.replace(k, f'<span class="{v}">{k}</span>')
        s = s.replace("story", "recovery")
    return s


# %%
manual_answers_file = "./data/plan_documents/manual_answers/manual_all.json"
try:
    with open(manual_answers_file, "r") as f:
        st.session_state["manual_answer"] = json.loads(f.read())
except:
    st.session_state["manual_answer"] = {}

if "plan_data" not in st.session_state:
    with open("./data/plan_documents/translated_selected_sents.json", "r") as f:
        st.session_state["plan_data"] = [x for x in json.loads(f.read())]
    st.session_state["plan_idx"] = len(st.session_state["manual_answer"].keys())


active_plan = st.session_state["plan_data"][st.session_state["plan_idx"]]

st.title(
    body=f"{st.session_state['plan_idx']} / {len(st.session_state['plan_data'])} -> {active_plan.get('IMRO')}"
)
Information, Questions = st.columns([2, 1])
# %%
with Information:
    st.markdown("#### Information")
    with st.container(height=700):
        para_idx = tuple(
            zip(
                [x.split(":")[0] for x in active_plan.get("id")], active_plan.get("en")
            )
        )

        for key, group in groupby(iterable=para_idx, key=lambda x: x[0]):
            listOfThings = colorise("\n\n".join([thing[1] for thing in group]))
            st.markdown(body=listOfThings, unsafe_allow_html=True)
# %%


with Questions:
    st.markdown("#### Answers:")
    with st.container(height=750):
        existing_answers = st.session_state["manual_answer"].get(
            active_plan.get("IMRO", None),
            dict(zip(MANUAL_QUESTIONS, [False] * len(MANUAL_QUESTIONS))),
        )

        for q in MANUAL_QUESTIONS:
            if existing_answers.get(str(q), None):
                default_index = existing_answers[str(q)]
            else:
                default_index = False
                existing_answers[q] = False
            existing_answers[q] = st.checkbox(label=q, value=default_index)

        submit, prev, next_ = st.columns([1, 1, 1])

        with submit:
            if st.button("submit"):
                st.session_state["manual_answer"][active_plan.get("IMRO")] = (
                    existing_answers
                )
                with open(
                    manual_answers_file, "w"
                ) as f:
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
