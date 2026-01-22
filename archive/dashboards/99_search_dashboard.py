import streamlit as st
import json
from tools import COLOR_DICT, setup_colors
import pandas as pd

setup_colors()


def colorise(s):
    for k, v in COLOR_DICT.items():
        s = s.replace(k, f'<span class="{v}">{k}</span>')
        s = s.replace("story", "recovery")
    return s


if "translations" not in st.session_state:
    with open("./data/plan_documents/translated_selected_sents.json") as f:
        st.session_state["translations"] = pd.DataFrame(json.loads(f.read()))


def search_and_print(query):
    if query not in st.session_state["translations"].IMRO.to_list():
        st.warning("IMRO NOT FOUND!")
        return None
    row = st.session_state["translations"].query("IMRO == @query")

    result = "\n\n".join(row.iloc[0, 3])
    with st.container():
        st.markdown(colorise(result), unsafe_allow_html=True)
    return None


with st.container():
    search_IMRO = st.text_input("IMRO")
    if st.button("search"):
        search_and_print(search_IMRO.strip().replace("\t", ""))
