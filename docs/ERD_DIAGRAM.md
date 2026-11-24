python -c "code = '''# AI & Automation Module - Entity Relationship & Data Flow Diagram

This document contains the complete Mermaid ERD specifying data contracts, validation states, and pipeline relationships.

## Visual ERD & Data Pipeline Diagram

```mermaid
erDiagram
    KEYWORD_INTAKE {
        string raw_keywords PK \"User entered query\"
    }

    NORMALIZED_KEYWORDS {
        string original_input
        string normalized_query \"Sanitized query string\"
        list tokens \"Unique cleaned tokens\"
        list identified_connectors \"Filtered prepositions\"
        int token_count
        boolean is_valid
        string rejection_reason
    }

    AI_SEARCH_QUERY {
        list keywords \"Technology or skill terms\"
        list target_roles \"Extracted job titles\"
        string location \"Extracted city or country\"
        string industry \"Extracted domain\"
        string intent \"AI summary of search goal\"
    }

    SEARCH_RESPONSE {
        string status \"SUCCESS or FAILED\"
        string prompt_version \"1.0.0\"
        string error_message
    }

    VERIFIED_PROFILE {
        string first_name PK \"Mandatory recipient name\"
        string last_name
        string full_name
        string headline \"Professional title\"
        string connection_level \"Must be 1st degree\"
        string profile_url
    }

    INTERPRETED_PROFILE {
        string preferred_name \"Title-cased clean name\"
        string headline_clean
        boolean is_first_degree \"Security authorization flag\"
        int verified_data_points \"Count of grounded facts\"
    }

    PERSONALIZATION_REQUEST {
        string template PK \"Approved form letter with placeholders\"
    }

    MESSAGE_VALIDATION {
        string status \"PASS or REVIEW or FAIL\"
        list reasons \"Bullet audit trail\"
        list detected_hallucinations \"Captured unverified claims\"
    }

    PERSONALIZATION_RESPONSE {
        string status \"SUCCESS or FAILED\"
        string personalized_message \"Final generated outreach text\"
        string prompt_version \"1.0.0 or deterministic-fallback\"
    }

    KEYWORD_INTAKE ||--|| NORMALIZED_KEYWORDS : \"processed_by_KeywordNormalizer\"
    NORMALIZED_KEYWORDS ||--o| AI_SEARCH_QUERY : \"evaluated_by_AISearchQueryGenerator\"
    AI_SEARCH_QUERY ||--|| SEARCH_RESPONSE : \"encapsulated_in\"

    VERIFIED_PROFILE ||--|| INTERPRETED_PROFILE : \"interpreted_by_ProfileInterpreter\"
    VERIFIED_PROFILE ||--|| PERSONALIZATION_REQUEST : \"embedded_in\"
    PERSONALIZATION_REQUEST ||--|| PERSONALIZATION_RESPONSE : \"generated_by_PersonalizationEngine\"
    PERSONALIZATION_RESPONSE ||--|| MESSAGE_VALIDATION : \"audited_by_HallucinationValidator\"