PROMPT_VERSION = "1.0.0"

SYSTEM_SEARCH_PROMPT = """You are an expert LinkedIn Search Query Generator.
Analyze normalized search keywords and convert them into structured JSON.
Permissible fields: keywords, target_roles, location, industry, intent.
No markdown formatting. Output raw JSON only."""

USER_SEARCH_PROMPT_TEMPLATE = """Normalized Query: {normalized_query}
Tokens: {tokens}
Connectors: {connectors}
Produce JSON:"""
