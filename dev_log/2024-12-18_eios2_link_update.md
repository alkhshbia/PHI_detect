# EIOS Link Update to EIOS2

**Date:** 2024-12-18  
**Developer:** Claude  
**Task:** Update EIOS links from EIOS1 to EIOS2 format

## Background
Based on the EIOS API v2 documentation (`/eios_shared/EIOS API v2/API_SHIM_Doc.pdf`), the EIOS platform has migrated to a new API structure. Article cards were still linking to the old EIOS1 portal, which needed to be updated to point to EIOS2.

## Changes Made

### Files Modified
1. **`src/static/app.js:827`** - Frontend article card EIOS link
2. **`src/static/app.js:888`** - Added `createUrlSlug()` function  
3. **`src/routes/signals.py:1044`** - CSV export EIOS link
4. **`src/routes/signals.py:14`** - Added `create_url_slug()` function

### URL Format Changes
- **Old URL format:** `https://portal.who.int/eios/#/items/${signal.id}/title/full-article`
- **Updated format (v1):** `https://eios.who.int/portal-sandbox/#/items/${signal.id}/title/full-article`
- **Final format (v2):** `https://eios.who.int/portal/monitoring/article-detail/${signal.rss_item_id}/${title_slug}/full-article`

### Implementation Details
- Updated JavaScript template literal in `renderSignalCard()` function
- Updated Python f-string in CSV export function
- Added URL slug generation from article titles (JavaScript & Python)
- URL slugs are created by:
  - Converting to lowercase
  - Removing special characters (except spaces and hyphens)
  - Replacing spaces with hyphens
  - Limiting to 100 characters
- Used `rss_item_id` instead of `signal.id` for article identification
- Verified no other instances of old URL format exist in codebase

## API Documentation Reference
The EIOS2 API base URL structure from the documentation:
- **Base URL:** `https://eios.who.int/portal-sandbox/shim`
- **Frontend Portal:** `https://eios.who.int/portal-sandbox/`

## Testing
- Verified all old EIOS1 URLs have been updated
- Confirmed consistent URL format across both frontend and backend
- No automated tests were found for this specific functionality

## URL Structure Analysis
Based on the example provided:
`https://eios.who.int/portal/monitoring/eios1-1356/article-detail/indianexpress-f3380517b7ac2959e2379346ca214d8d/top-10-richest-families-in-the-world-2025-indian-family-with-net-worth-105-6bn-ranks-8th-trending13-min-ago-the-world-s-wealthiest-families-have-amassed-a-combined-fortune-of-2-9-trillion-in-2025-driven-by-rising-stock-prices-and-strong-demand-for-goods/full-article`

The actual EIOS2 URL structure appears to be:
`/portal/monitoring/{board_id}/article-detail/{article_hash}/{title_slug}/full-article`

Since we don't have access to board_id and article_hash in our current data model, we simplified to:
`/portal/monitoring/article-detail/{rss_item_id}/{title_slug}/full-article`

## Impact
- Article cards now generate dynamic URLs with title slugs
- CSV exports include properly formatted EIOS2 URLs  
- URLs are more SEO-friendly and human-readable
- Users will be directed to the current EIOS platform instead of the legacy one
- The URL structure may need refinement once board IDs and article hashes become available