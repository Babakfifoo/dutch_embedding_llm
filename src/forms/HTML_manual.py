
import json
# %%

with open('../../data/HTML_query_results.json', 'r') as f:
    data = json.load(f)


def get_plan_query(k):
    return "\n".join(data.get(k, {}).get('translations', []))

# with app.state:
#     current_document_index = 0
#     current_document = data.get(str(current_document_index), "")
#     questions = [
#         "Does the land use plan need explitation plan?",
#         "Is there an exploitation plan made for this land use plan?",
#     ]
#     answers = ["" for _ in questions]


with tgb.Page() as page:
    tgb.text(value=get_plan_query(k='t_NL.IMRO.0119.BPNVL2020-BPC1'), mode="md")

if __name__ == "__main__":
    Gui(page=page).run(title="Plan Data")