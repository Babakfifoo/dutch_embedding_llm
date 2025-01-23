
# there is no question number 10 so we can verify LLM is not hallucinating
questions = """
    Question 01: Is municipality the landowner of the planned area?
    Question 02: Is developer the landowner of the planned area?
    Question 03: Is the initiator the landowner of the area?
    Question 04: Is plan area on municipal land?
    Question 05: Is the municipality responsible for the costs?
    Question 06: Is the landowner responsible for costs?
    Question 07: Is the private sector responsible for costs?
    Question 08: Is the initiator responsible for costs?
    Question 09: Is costs covered by land sales?
    Question 11: Is costs covered by cost recovery?
    Question 12: Is there a need for expoitation plan?
    Question 13: Is it mentioned that exploitation plan is NOT needed?
    Question 14: Is it mentioned that operating plan is NOT needed?
    Question 15: Is municipality going to sell land?
    Question 16: Is municipality agreement mentioned?
    Question 17: Do municipality and initiator have an agreement?
    Question 18: Is the plan for housing construction?
    Question 19: Is land require preparation?
    Question 20: Is municipality taking care of land preperation?
    Question 21: Is the initiator taking care of land preparation?
    Question 22: Is there joint venture mentioned?
    Question 23: Is there a name of a company mentioned?
    Question 24: Is there a company owned by the municipality?
    Question 25: Is there PPP, PPS or Public Private Participation mentioned?
"""

Prompt: str = """
**Prompt:**

**Instructions:**

* **Context:** You are an expert in urban planning, specifically regarding economic feasibility in Dutch land use plans.
* **Task:** Answer the following questions about the provided plan text.
* **Answer Format:**
    * Respond with "yes", "no", or "Not mentioned" for each question.
    * Output the answers in JSON format:
        * Keys: Question numbers.
        * Values: Corresponding answers ("yes," "no," or "Not mentioned").
    * Do not provide any additional explanations or text.

**Text:**

{plan_string}

**Questions:**

{questions}

**Output:**

```json
{{ "01": "No", "02": "Not mentioned", "03": "Not mentioned", "04": "Yes", "05": "Not mentioned", "06": "No", "07": "No", "08": "Not mentioned", "11": "Not mentioned", "12": "Not mentioned", "13": "Yes", "14": "Not mentioned", "15": "Not mentioned", "16": "Yes", "17": "Yes", "18": "Yes", "19": "No", "20": "No", "21": "No", "22": "Not mentioned", "23": "Not mentioned", "24": "Not mentioned", "25": "Not mentioned"}}
```
"""
