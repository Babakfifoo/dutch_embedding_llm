# %%
import sqlite3
import streamlit as st
import json
from pathlib import Path
import re
def remove_span(s):
    pattern = r'<span\s+id=".+?">.*?</span>'
    output_string = re.sub(pattern, "", s, flags=re.DOTALL | re.IGNORECASE)
    return output_string

def parse_markdown_headings(content):
    """Extracts H1/H2 headings containing specific Dutch keywords."""
    headings = []
    # Target keywords in lowercase
    targets = ["economische", "uitvoerbaarheid", "Financiële", "FinanciÃ«le"]
    
    lines = content.split('\n')
    for line in lines:
        # Match H1 or H2
        match = re.match(r'^(#+)\s+(.*)', line)
        if match:
            level = len(match.group(1))
            title = match.group(2)
            
            # Check if any target keyword is in the title (case-insensitive)
            if any(word in title.lower() for word in targets):
                # Create a URL-friendly ID
                anchor_id = title.lower().replace(" ", "-").replace(".", "")
                
                headings.append({
                    "level": level, 
                    "title": title, 
                    "id": anchor_id
                })
                
    return headings

def upsert_feasibility(db_path, imro_value, text):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        sql = """
            INSERT INTO landuse (imro, feasability_text)
            VALUES (?, ?)
            ON CONFLICT(imro) DO UPDATE SET
                feasability_text = excluded.feasability_text
        """
        st.success(f"{imro_value} successfully updated")
        cursor.execute(sql, (imro_value, text))
        conn.commit()
        

st.set_page_config(layout="wide")

MD_DIR = Path("./data/plan_documents/md")
DB_FP = Path("./data/database.db")
STARTING_IDX = 5

if "feasibility_input" not in st.session_state:
    st.session_state["feasibility_input"] = ""

if "fplist" not in st.session_state:
    st.session_state["fplist"] = [fp for fp in MD_DIR.iterdir() if fp.suffix == ".md"]
    st.session_state["idx_pos"] = STARTING_IDX - 1

plan_fp = st.session_state["fplist"][st.session_state["idx_pos"]]



with open(plan_fp, "r", encoding="utf-8") as f:
    plan_text = remove_span(f.read())
    active_plan = dict(
        IMRO= plan_fp.stem.replace("t_", ""),
        text= plan_text,
        fp = plan_fp,
        headings = parse_markdown_headings(plan_text)
    )
    
with sqlite3.connect(DB_FP) as conn:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT feasability_text FROM landuse WHERE imro = ?",
        (active_plan.get("IMRO"),) 
    )
    existing_extraction = cursor.fetchone()
    if existing_extraction is not None:
        active_plan["extracted"] = existing_extraction
    else:
        active_plan["extracted"]  = ""


plan_text, user_input = st.columns(spec=[3, 2])

st.sidebar.header("Table of Contents", width=500)
for h in active_plan.get("headings"):
    # Indent based on heading level
    indent = "\t" * (h['level'] - 1)
    # Create a link using markdown syntax [text](#anchor)
    st.sidebar.markdown(f"{indent}[{h['title']}](#{h['id']})")

with plan_text:
    st.markdown(
        f"### {st.session_state['idx_pos']} / {len(st.session_state['fplist'])} -> {active_plan.get('IMRO')}"
    )
    with st.container(height=1000):
        # We need to inject the anchors manually into the content
        processed_content = active_plan.get("text")
        for h in active_plan.get("headings"):
            # We wrap the heading in an HTML anchor tag so the sidebar links find it
            anchor_tag = f"<div id='{h['id']}'></div>\n\n"
            # Find the original heading line and prepend the anchor
            original_heading = f"{'#' * h['level']} {h['title']}"
            processed_content = processed_content.replace(original_heading, anchor_tag + original_heading)
    
        st.markdown(processed_content, unsafe_allow_html=True)

    

with user_input:
    st.markdown("### Extracted")


    with st.container():
        active_plan["feasability text"] = st.text_area(
            label="input",
            value=active_plan.get("extracted"),
            height=1000,
            key="feasibility_input"
        )

    submit, prev, next_ = st.columns([1, 1, 1])

with submit:
    if st.button("submit", use_container_width=70):
        upsert_feasibility(DB_FP, active_plan.get("IMRO"), active_plan["feasability text"])
        # st.session_state["manual_answer"][active_plan.get("IMRO")] = plan_info
        # with open(Extraction_QA, "w") as f:
        #     f.write(json.dumps(st.session_state["manual_answer"], indent=4))
        st.session_state["idx_pos"] += 1
        st.rerun()

with prev:
    if st.button("previous", use_container_width=70):
        st.session_state["idx_pos"] -= 1
        st.rerun()

with next_:
    if st.button("next", use_container_width=70):
        st.session_state["idx_pos"] += 1
        st.rerun()
