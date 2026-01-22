# %%
import json
import sqlite3
import streamlit as st
from typing import List

from Tools import setup_colors, colorise, INDICATORS, DAS

SQLITE_DB_PATH = "./data/database.db"
setup_colors()

# %%
st.set_page_config(layout="wide")


if "imro_list" not in st.session_state:
    with sqlite3.connect(SQLITE_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"select imro from landuse where feasability_text IS NOT NULL AND indicators IS NULL ORDER BY imro"
        )
        st.session_state["imro_list"] = [row[0] for row in cursor.fetchall()]
        st.session_state["imro_idx"] = 0

# Extracting the plan information:
imro: str = st.session_state["imro_list"][st.session_state["imro_idx"]]

with sqlite3.connect(SQLITE_DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT feasability_text, feasability_en, indicators, land_dev FROM landuse WHERE imro = ?",
        (imro,),
    )
    (feasability_text, feasability_en, indicators, land_dev) = cursor.fetchone()

    if indicators is None:
        answered: str = "<span class=redHighlight> INDICATORS NOT FOUND </span>"
        indicators: List[str] = []
    else:
        answered: str = "reviewed!"

    land_dev = land_dev if land_dev is not None else ""

with st.container():
    st.markdown(
        f"# {st.session_state['imro_idx'] + 1}/{len(st.session_state['imro_list'])} -> {imro} -> {answered}",
        unsafe_allow_html=True,
    )


FEAStext, INDlist = st.columns([3, 2], border=True, gap="small")

with FEAStext:
    with st.container(height=600):
        st.markdown(
            body=colorise(feasability_en),
            unsafe_allow_html=True,
        )
    with st.container(height=200):
        st.markdown(
            body=colorise(land_dev),
            unsafe_allow_html=True,
        )


with INDlist:
    submit, prev, next_ = st.columns([1, 1, 1])
    Agreements, costRecovery = st.columns([1, 1], border=True, gap="small")
    answers = dict()
    with Agreements:
        for k, name in DAS.items():
            answers[k] = st.checkbox(label=name, value=(k in indicators), key=k + imro)

    with costRecovery:
        for k, name in INDICATORS.items():
            answers[k] = st.checkbox(label=name, value=(k in indicators), key=k + imro)

    with submit:
        if st.button("submit", use_container_width=True):
            indicators: List[str] = [k for k, v in answers.items() if v]
            with sqlite3.connect(SQLITE_DB_PATH) as conn:
                cursor = conn.cursor()
                sql_upsert = f"""
                UPDATE landuse
                SET 
                indicators = '{json.dumps(indicators)}'
                WHERE imro = '{imro}';
                """
                cursor.execute(sql_upsert)
                conn.commit()
            st.session_state["imro_idx"] += 1
            st.rerun()

    with prev:
        if st.button("previous", use_container_width=True):
            st.session_state["imro_idx"] -= 1
            st.rerun()

    with next_:
        if st.button("next", use_container_width=True):
            st.session_state["imro_idx"] += 1
            st.rerun()
