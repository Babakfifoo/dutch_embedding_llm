from . import prompts


LandPriceYN: prompts.PromptConfig = prompts.PromptConfig(
    topic="land_price_YN",
    description="Validating if land price is used for cost recovery",
    threshold=0,
    prompt="""
        # Context:

        {context}

        # Instructions
        
        Based on the provided context, are costs are recovered by selling land or land issuance?
        
        You must respond ONLY with a JSON object that strictly adheres to the following schema:
        
        {{
            "answer": <true_or_false>
        }}
        
        Where <true_or_false> is either the boolean `true` or `false`.
        Do not include any other text or explanation.
    """,
    schema=prompts.BoolAnswer.model_json_schema(),
)
