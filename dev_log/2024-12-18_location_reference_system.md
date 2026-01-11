# Dev Note: Location Reference System Implementation

## Date
2024-12-18

## Task/Issue
Implement efficient location reference system for LLM tagging using official continent-country and country-admin1 lists

## Problem Statement
Currently, the LLM tags articles with "Countries" and "Hazards" without any reference to official location names. Need to:
1. Use official names from continent-country list for country identification
2. Include admin1 subdivisions when possible and relevant
3. Make the process token-efficient (avoid passing full lists in every prompt)

## Analysis
- Current implementation in `src/services/signal_processor.py` uses free-form country extraction
- Reference data structure:
  - `continent_country.csv`: Continent,Country (e.g., "Africa,Algeria")
  - `country_admin1.csv`: admin0,admin1 (e.g., "Afghanistan,Ghazni")
- LLM prompt is in `risk_evaluation_prompt` (lines 125-157)
- Response parsing in `parse_ai_response` method (lines 259-344)

## Solution Design
1. **LocationReferenceManager class**: Load and manage reference data efficiently
2. **In-memory lookup structures**: Hash maps for fast country/admin1 lookups
3. **Smart prompt enhancement**: Include relevant location hints without full lists
4. **Two-stage location extraction**:
   - Primary: Match against official country names
   - Secondary: If country found in admin1 list, attempt admin1 matching

## Implementation Details

### LocationReferenceManager Class (lines 14-143)
- Loads continent-country and country-admin1 CSV data once at initialization
- Creates efficient lookup structures: hash sets and dictionaries
- Provides methods for country matching, admin1 lookup, and location context generation
- Uses fuzzy matching for country identification in text

### Key Methods Implemented:
1. `_load_continent_country_data()` - Loads official country names by continent
2. `_load_country_admin1_data()` - Loads admin1 subdivisions by country
3. `find_matching_countries()` - Finds countries mentioned in text using fuzzy matching
4. `generate_location_context_for_prompt()` - Creates location guidance for LLM without full lists
5. `enhance_location_extraction()` - Post-processes LLM output to use official names and add admin1

### Integration with ArticleProcessor:
- Initialize LocationReferenceManager in `__init__()` (line 297)
- Pre-analyze articles to find suspected countries (line 582)
- Generate dynamic location context for each prompt (line 583)
- Enhanced prompt formatting with location context (lines 586-590)
- Post-process extracted countries for official names and admin1 data (lines 718-720)

### Prompt Modifications:
- Updated rule to use "official UN/WHO country names only" (line 285)
- Added dynamic `{location_context}` placeholder (line 289)
- Context includes admin1 guidance for relevant countries without token waste

## Testing/Validation
Ready for testing with real articles. The system should now:
1. Use official country names from reference data
2. Include admin1 subdivisions when identifiable
3. Be token-efficient (no full lists in prompts)
4. Handle multiple countries per article (Iran + Iraq example)

## Files Modified
- `src/services/signal_processor.py` - Added LocationReferenceManager class and integrated location matching
- `dev_log/dev_note_template.md` - Created dev note template
- `dev_log/2024-12-18_location_reference_system.md` - This dev note

## Next Steps
1. Test with sample articles to validate location extraction
2. Monitor token usage to ensure efficiency
3. Fine-tune fuzzy matching thresholds if needed
4. Consider adding location confidence scores for better validation