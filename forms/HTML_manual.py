# %%
import streamlit as st
import json


def get_items(key, active_plan):
    item_idx: dict = active_plan.get("contexts", {}).get(key, None)
    for i in item_idx:
        st.markdown(body=active_plan.get("translations", {}).get(i, None))


# %%

if "data" not in st.session_state:
    with open("HTML_query_translations.json", "r") as f:
        st.session_state["data"] = json.load(fp=f)


if "plan_idx" not in st.session_state:
    st.session_state["plan_idx"] = 0
if "answers" not in st.session_state:
    st.session_state["answers"] = []


active_plan = st.session_state["data"][st.session_state["plan_idx"]]


st.title(body=active_plan.get("IMRO"))


st.markdown("## Information")

st.markdown("## Questions:")

answers = {"IMRO": active_plan.get("IMRO")}

key = "Anterior Agreement"
with st.container():
    st.subheader(body=key)
    get_items(key=key, active_plan=active_plan)
    st.subheader(body="Questions:")
    answers[key] = {}
    answers[key]["has Anterior Agreement"] = st.radio(
        label="Is there Anterior Agreement mentioned?",
        options=["Yes", "No", "None"],
        horizontal=True,
    )
    answers[key]["Anterior Agreement established"] = st.radio(
        label="is Anterior Agreement established?",
        options=["Yes", "No", "None"],
        horizontal=True,
    )
    
    
# key = "Exploitation Plan"
# with st.container():
#     st.subheader(body=key)
#     get_items(key=key, active_plan=active_plan)
#     st.subheader(body="Questions:")
#     answers[key] = {}
#     answers[key]["Needs Exploitation plan"] = st.radio(
#         label="Does exploitation plan or operation plan needed?",
#         options=["Yes", "No", "None"],
#         horizontal=True,
#     )
#     answers[key]["Does not need exploitation plan"] = st.radio(
#         label="Is exploitation plan or operation plan ommited or waivered?",
#         options=["Yes", "No", "None"],
#         horizontal=True,
#     )
    
# key = "Ownership"
# with st.container():
#     st.subheader(body=key)
#     get_items(key=key, active_plan=active_plan)
#     st.subheader(body="Questions:")
#     answers[key] = {}
#     answers[key]["municipality"] = st.radio(
#         label="Does Municipality own the land?",
#         options=["Yes", "No", "None"],
#         horizontal=True,
#     )
#     answers[key]["Initiator"] = st.radio(
#         label="Does Initiator own the land?",
#         options=["Yes", "No", "None"],
#         horizontal=True,
#     )
#     answers[key]["Private"] = st.radio(
#         label="Does Private own the land?",
#         options=["Yes", "No", "None"],
#         horizontal=True,
#     )

if st.button("submit"):
    st.session_state["answers"].append(answers)
    with open(f"./HTML_manual_{key}.json", "w") as f:
        f.write(json.dumps(st.session_state["answers"], indent=4))
    st.session_state["plan_idx"] += 1
    st.rerun()
