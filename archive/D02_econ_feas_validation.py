# %%
import streamlit as st
import json
import sqlite3
from typing import Any
import re


def remove_span(s):
    pattern = r'<span\s+id=".+?">.*?</span>'
    output_string = re.sub(pattern, "", s, flags=re.DOTALL | re.IGNORECASE)
    return output_string


# %%
# settings:
st.set_page_config(layout="wide")
TABLE_LU = "landuse"
ECONOMIC_FEAS_STR = [
    "financieel",
    "financiële",
    "economische",
    "f i n a n c i e e l",
    "e c o n o m i s c h e",
]

FEAS_STR = ["uitvoerbaarheid", "haalbaarheid", "H a a l b a a r h e i d"]
EX_STR = ["maatschappelijke"]
DB_PATH = "./data/landuse.db"

if "manual_answer" not in st.session_state:
    st.session_state["manual_answer"] = {}

if "extracted" not in st.session_state:
    with open(
        "./data/plan_documents/extracted.json", mode="r", encoding="utf-8"
    ) as file:
        st.session_state["extracted"] = json.loads(file.read())

if "imros" not in st.session_state:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"select imro from {TABLE_LU} where feasability_text IS NULL")
        st.session_state["imros"] = [row[0] for row in cursor.fetchall()]
    st.session_state["plan_idx"] = 0


imro = st.session_state["imros"][st.session_state["plan_idx"]]

if imro in ["NL.IMRO.0385.BPTunnelpad-vg01", "NL.IMRO.0119.mulolocatie-BPC1"]:
    st.session_state["plan_idx"] += 1
    st.rerun()

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT md_file FROM {TABLE_LU} WHERE imro = ?",
        (imro,),
    )
    (context,) = cursor.fetchone()

feasability_text = st.session_state["extracted"].get("t_" + imro, "No Text")

if isinstance(feasability_text, list):
    feasability_text = remove_span("\n\n".join(feasability_text))

# Layout:

Extracted, plan_text, user_input = st.columns(spec=[3, 3, 2])
plan_info: dict[str, Any] = dict()
print(imro, ": data loaded")

with Extracted:
    st.markdown(
        f"### Extracted {st.session_state['plan_idx']} / {len(st.session_state['imros'])} -> "
    )
    with st.container(height=850):
        st.markdown(feasability_text, unsafe_allow_html=True)

with plan_text:
    st.markdown(f"### {imro}")
    with st.container(height=850):
        st.markdown(context, unsafe_allow_html=True)


with user_input:
    st.markdown("### Verdict")
    with st.container():
        plan_info["feasability text"] = st.text_area(
            label="input",
            value=feasability_text,
            height=700,
        )

    submit, prev, next_ = st.columns([1, 1, 1])

    with submit:
        if st.button("submit", use_container_width=True):
            st.session_state["manual_answer"][imro] = plan_info
            with open(
                "./data/plan_documents/Dashboard_outputs/D03_extraction_for_DB.json",
                "w",
            ) as f:
                f.write(json.dumps(st.session_state["manual_answer"], indent=4))
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    result = (
                        plan_info["feasability text"]
                        .replace("'", "''")
                        .replace("\x00", "")
                    )
                    sql_upsert = f"""
                    UPDATE {TABLE_LU}
                    SET feasability_text = '{result}'
                    WHERE imro = '{imro}';
                    """
                    cursor.execute(sql_upsert)
                    conn.commit()

            except Exception as e:
                print(imro, ": store the answer :", e)

            st.session_state["plan_idx"] += 1
            del plan_info, feasability_text, result, context
            st.rerun()

    with prev:
        if st.button("previous", use_container_width=True):
            st.session_state["plan_idx"] -= 1
            del plan_info, feasability_text, context
            st.rerun()

    with next_:
        if st.button("next", use_container_width=True):
            st.session_state["plan_idx"] += 1
            del plan_info, feasability_text, context
            st.rerun()
