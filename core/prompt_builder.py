
def build_prompt(scenario, perspectives, detail):

    detail_instructions = {
        "Short": (
            "Keep each outcome concise and easy to understand."
        ),

        "Detailed": (
            "Explain the causes, developments, "
            "and consequences of each outcome."
        ),

        "Comprehensive": (
            "Provide an in-depth analysis covering "
            "immediate changes, long-term consequences, "
            "social effects, economic effects, "
            "and unexpected developments."
        )
    }

    system_prompt = """
    You are an expert hypothetical scenario analyst.

    Your job is to explore alternative realities using
    creativity, logical reasoning, and contextual analysis.

    Follow these instructions:

    1. Treat every scenario as hypothetical.
    2. Generate distinct and meaningful outcomes.
    3. Explain why each outcome could happen.
    4. Consider short-term and long-term consequences.
    5. Distinguish speculation from established facts.
    6. Never present fictional predictions as guaranteed facts.
    7. Do not provide actionable harmful instructions.
    8. Use clear headings and structured explanations.
    """

    user_prompt = f"""
    Explore this hypothetical scenario:

    {scenario}

    Generate exactly {perspectives} different possible outcomes.

    Analysis depth: {detail}

    {detail_instructions[detail]}

    For every outcome, explain:

    1. Outcome title
    2. What happens
    3. Why it happens
    4. Short-term consequences
    5. Long-term consequences

    Finally, provide an overall analysis comparing
    the different possible outcomes.
    """

    return system_prompt, user_prompt
