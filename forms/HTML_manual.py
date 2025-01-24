# %%
import streamlit as st
import pandas as pd
import json
# %%

if "data" not in st.session_state:
    with open('./data/HTML_query_results.json', 'r') as f:
        st.session_state["data"] = json.load(fp=f)

if "stored_data" not in st.session_state:
    with open("./data/HTML_manual.json", "r") as f:
        st.session_state["stored_data"] = json.loads(f.read())

if "IMRO_list" not in st.session_state:
    st.session_state["IMRO_list"] = list(st.session_state["data"] .keys())
if "plan_idx" not in st.session_state:
    st.session_state["plan_idx"] = 0
if "answers" not in st.session_state:
    st.session_state["answers"] = {}

st.session_state["IMRO"] = st.session_state["IMRO_list"][st.session_state["plan_idx"]]
st.session_state["plan_info"] = st.session_state["data"].get(st.session_state["IMRO"])


st.title(body=st.session_state["IMRO_list"][st.session_state["plan_idx"]])


st.markdown("## Information")
if st.session_state["plan_info"] is None:
    st.session_state["plan_idx"] += 1
    st.rerun()
for i, item in enumerate(st.session_state["plan_info"].get("translations", []), start=1):
    st.markdown(f"{i}. {item}")

st.markdown("## Questions:")

questions = [
    "Is there exploitation plan needed for the land use plan?",
    "Is exploitation plan is prepared for the land use plan?"
]
if st.session_state["stored_data"].get(st.session_state["IMRO"], None) is None:
    df = pd.DataFrame(
        data=[
        {"question": "Is there exploitation plan needed for the land use plan?", "yes": False, "no": False, "None": False},
        {"question": "Is exploitation plan is prepared for the land use plan?", "yes": False, "no": False, "None": False},
    ])
else:
    df = pd.DataFrame(st.session_state["stored_data"].get(st.session_state["IMRO"]))
    print(df)

st.session_state["df"] = st.data_editor(df)

if st.button("submit"):
    with open("./data/HTML_manual.json", "w") as f:
        st.session_state["stored_data"][st.session_state["IMRO"]] = st.session_state["df"] .to_dict()
        print(st.session_state["stored_data"][st.session_state["IMRO"]])
        f.write(json.dumps(st.session_state["stored_data"], indent=4))
    st.session_state["plan_idx"] += 1
    st.rerun()
