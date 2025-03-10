# %%
import json
import pandas as pd
import re
from typing import List
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm


def find_yes_no(s):
    if s is None:
        return None
    if bool(re.search(r"\byes\b", s.lower())):
        return 1
    if bool(re.search(r"\bno\b", s.lower())):
        return 0
    return 0


def process_ans_str(ans_str: str) -> List[str]:
    count_newline = len(re.findall("\n", ans_str))
    count_comma = len(re.findall(",", ans_str))
    if (count_newline > 10) and (count_comma > 10):
        ans_str = ans_str.replace("\n", "")
    elif count_newline > 10:
        ans_str = ans_str.replace("\n", ",")
    elif count_comma > 10:
        pass
    else:
        raise ValueError("The is no delimeter")
    ans_str = ans_str.replace("{", "").replace("}", "")
    result: List[str] = [x.strip() for x in ans_str.split(",")]
    return result


def extract_q_substrings(text):
    """
    Extracts substrings from a string that start with 'Q' followed by one or two digits.

    Args:
        text: The input string.

    Returns:
        A list of matching substrings.  Returns an empty list if no matches are found.
    """
    pattern = (
        r"Q\d{1,2}"  # r"" for raw string, \d for digits, {1,2} for 1 or 2 occurrences
    )
    matches = re.findall(pattern, text)[0]
    return matches


with open("../data/plan_documents/manual_answers/HTML_manual.json", "r") as f:
    manual_answers = json.loads(f.read())

manual_answers = pd.DataFrame(manual_answers).T.reset_index()
manual_answers.columns = [
    "IMRO",
    "Land allocation",
    "Exploitation Plan",
    "Anterior Agreement",
    "Municipallity Budget",
    "building plan",
    "Invalid",
]

manual_answers = (
    manual_answers.melt("IMRO")
    .rename(columns={"variable": "question", "value": "manual"})
    .dropna()
)
manual_answers = manual_answers.pivot_table(
    values="manual", columns="question", index="IMRO"
)
manual_answers = (manual_answers == 1).astype(int)
manual_answers = manual_answers.query("Invalid != 1").drop(columns=["Invalid"])
# %%

with open("../data/plan_documents/answered/html_answers.json", "r") as f:
    answers = json.loads(f.read())

cleaned_answers = pd.DataFrame()
for item in answers:
    try:
        ans_str = process_ans_str(ans_str=item.get("answers", None))
        ans = pd.DataFrame(data=[x.split(":") for x in ans_str])
        if len(ans.columns) == 1:
            raise ValueError("Index is wrong.")
        ans.columns = ["question", "answer"]
        if len(ans["question"]) != 25:
            raise ValueError("Some answers are missing.")
        ans["question"] = ans["question"].apply(extract_q_substrings)
        ans["answer"] = ans["answer"].str.strip()
        ans["question"] = ans["question"].str.strip()
        ans["answer_cleaned"] = ans["answer"].apply(find_yes_no)
        ans["IMRO"] = item.get("IMRO")
        ans = ans.set_index(["IMRO", "question"])
        cleaned_answers = pd.concat([cleaned_answers, ans])
    except Exception as e:
        print(item.get("IMRO"), " Has error: ", e)
cleaned_answers = cleaned_answers.reset_index()

cleaned_answers["question"] = "Q" + cleaned_answers["question"].str.upper().str.replace(
    "Q", ""
).str.zfill(2)


cleaned_answers = cleaned_answers.drop(columns=["answer"]).pivot_table(
    values="answer_cleaned", columns="question", index="IMRO"
)
# %%
dataset = cleaned_answers.join(manual_answers).fillna(0)

columns = (
    # "exploitation_plan",
    # "land_issue",
    "anterior_agreement",
    # "municipal_land_sell",
    # "municipal_budget",
)

X = dataset.iloc[:, 0:25]
for col in columns:
    Y = dataset[col]
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.50, random_state=42
    )
    model = LogisticRegression(max_iter=1000, solver="liblinear")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"{col}: {round(accuracy * 100, 2)}")


# %%
with open("proper_sample.json", "w") as f:
    f.write(json.dumps(manual_answers.index.to_list()))

# %%
malfunctioning = y_test[y_test != y_pred].index
# %%
dataset[dataset.index.isin(malfunctioning)].corr().loc[:, ["anterior_agreement"]]
# %%
dataset.query("municipal_budget == 1*")
# %%
