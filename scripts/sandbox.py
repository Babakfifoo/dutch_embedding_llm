# %%

import json
# %%
with open("../data/plan_documents/results/inspecting_false/result_agreement_timing_20250320.json") as f:
    results = json.loads(f.read())
with open("../data/plan_documents/results/manual_inspection/inspection_agreement_timing_20250320.json") as f:
    inspected = json.loads(f.read())
with open("../data/plan_documents/answered/will agree.json") as f:
    llms = json.loads(f.read())
# %%
llms_cleaned = []
for item in llms:
    asn = json.loads(item.get("answer")).get("answer")
    if asn and (item.get("IMRO") not in inspected.keys()):
        llms_cleaned.append(item)

with open("../data/plan_documents/answered/missing.json", "w") as f:
    f.write(json.dumps(llms_cleaned))
# %%
