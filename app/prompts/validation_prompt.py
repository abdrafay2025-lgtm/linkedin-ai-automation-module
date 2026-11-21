"""
Message Validation & Grounding Prompts (Version 1.0.0).
Evaluates generated messages for hallucinations, tone drift, and template fidelity.
"""

PROMPT_VERSION = "1.0.0"

SYSTEM_VALIDATION_PROMPT = """You are an uncompromising AI safety and compliance auditor.
Your job is to rigorously verify that an outreach message contains ZERO hallucinations.

RULES:
1. Every factual statement about the recipient must be directly supported by the verified profile data.
2. If the message claims the sender saw a post, repo, podcast, or achievement not present in the verified data, flag it as UNVERIFIED.
3. Check that the tone is professional, polite, and not aggressive or spammy.
4. Output must be strictly PASS, REVIEW, or FAIL with bullet-pointed justification.
"""

USER_VALIDATION_TEMPLATE = """Original Template:
\"\"\"
{template}
\"\"\"

Verified Profile Data:
- Name: {preferred_name}
- Headline: {headline}

Generated Message to Evaluate:
\"\"\"
{generated_message}
\"\"\"

Audit Verdict:"""