
import re


BLOCKED_PATTERNS = [
    r"\bhow to make a bomb\b",
    r"\bbuild an explosive device\b",
    r"\bmake a weapon to hurt\b",
    r"\bsteal someone.s password\b",
    r"\bdeploy ransomware\b",
    r"\bwrite malware to attack\b",
    r"\bhow to poison someone\b",
    r"\bhow to kill myself\b",
    r"\binstructions for suicide\b"
]


def validate_scenario(scenario):

    # Check empty input
    if not scenario or not scenario.strip():
        return False, "Please enter a scenario."

    scenario = scenario.strip()

    # Check minimum length
    if len(scenario) < 10:
        return False, "Please provide more details."

    # Check maximum length
    if len(scenario) > 1000:
        return False, "Scenario must be under 1000 characters."

    # Check potentially harmful content
    for pattern in BLOCKED_PATTERNS:

        if re.search(pattern, scenario, re.IGNORECASE):
            return False, (
                "This scenario cannot be processed because "
                "it contains potentially harmful content. "
                "Please try a different hypothetical scenario."
            )

    return True, "Scenario accepted."
