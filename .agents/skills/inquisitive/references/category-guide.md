# Category Guide

Full definitions with domain-specific examples for each of the 12 memory categories.

## 1. Intent

**What it captures:** The primary goal — why this change was made. This is the most important category. Every change has an intent, even if it also fits other categories.

**Three hierarchy levels:**
- **Company** — Broad business/organizational goal. Example: "Increase conversion from free to paid tier"
- **Repo** — What this specific project aims to do. Example: "This landing page exists to generate trial signups"
- **Task** — What this specific change is trying to accomplish. Example: "Move CTA button above the fold to improve click-through"

**Examples:**
- "Adding analytics tracking to understand user drop-off points"
- "Refactoring checkout flow to reduce cart abandonment"
- "Rewriting the onboarding to get users to the 'aha moment' faster"

## 2. User Experience

**What it captures:** How the change affects the end-user's interaction with the product — flow, usability, feedback, clarity, delight.

**Examples:**
- "Added loading states so users know something is happening"
- "Moved the search bar to the top where users expect it"
- "Simplified the multi-step form into a single page"
- "Added keyboard shortcuts for power users"
- "Changed button text from 'Submit' to 'Save Changes'"

## 3. Styling / Layout

**What it captures:** Visual design decisions — spacing, alignment, color, typography, layout structure, responsive behavior. Any change that affects what the user sees.

**Examples:**
- "Switched from a table to cards for better visual hierarchy"
- "Reduced padding to fit more content above the fold"
- "Changed the primary button color to increase contrast"
- "Added responsive breakpoints for tablet view"

## 4. Security

**What it captures:** Authentication, authorization, data protection, input validation, rate limiting, secrets management, vulnerability mitigation.

**Examples:**
- "Added input sanitization to prevent XSS attacks"
- "Implemented rate limiting on the login endpoint"
- "Moved API keys from code to environment variables"
- "Added CSRF tokens to forms"
- "Fixed a privilege escalation bug in the role system"

## 5. Business Logic

**What it captures:** Domain rules, calculations, workflows, state machines, pricing logic, eligibility checks. The "how the business works" encoded in code.

**Examples:**
- "Updated tax calculation for the new state regulations"
- "Changed the discount logic from percentage to fixed amount"
- "Added a minimum order threshold for free shipping"
- "Modified the subscription tier upgrade path"
- "Implemented the new refund policy logic"

## 6. Efficiency

**What it captures:** Performance optimization — speed, resource usage, memory, network calls, caching, bundle size, database queries.

**Examples:**
- "Added database indexing to speed up the search query"
- "Implemented lazy loading for images below the fold"
- "Replaced O(n²) algorithm with O(n log n)"
- "Added Redis caching for the dashboard API"
- "Reduced bundle size by tree-shaking unused imports"

## 7. Maintainability

**What it captures:** Code quality, organization, readability, tech debt reduction, naming, extraction, consistency. Changes that make the codebase easier to work with.

**Examples:**
- "Extracted the validation logic into a shared utility"
- "Renamed variables to be more descriptive"
- "Removed dead code and commented-out blocks"
- "Standardized error handling across all API routes"
- "Split the monster 500-line function into smaller ones"

## 8. Reliability

**What it captures:** Error handling, edge cases, retry logic, fallbacks, timeouts, graceful degradation, monitoring. Changes that prevent or handle failures.

**Examples:**
- "Added try-catch around the external API call"
- "Implemented exponential backoff for retries"
- "Added a fallback UI when the data fetch fails"
- "Fixed the null pointer exception on empty state"
- "Added health check endpoint for monitoring"

## 9. Compatibility

**What it captures:** Cross-browser, cross-platform, API versioning, dependency updates, migration paths, backward compatibility.

**Examples:**
- "Added polyfills for older browser support"
- "Updated the API client to work with the v3 endpoint"
- "Bumped the minimum Node version in engines field"
- "Added feature detection for the WebRTC API"
- "Ensured the layout works on both iOS and Android"

## 10. Developer Experience

**What it captures:** Tooling, local development, debugging, CI/CD, logging, error messages, documentation, build times, testing infrastructure.

**Examples:**
- "Added detailed error messages to the CLI tool"
- "Set up hot module reload for faster development"
- "Improved the test fixture generation script"
- "Added debug logging to the middleware pipeline"
- "Wrote a README with setup instructions"

## 11. Data Integrity

**What it captures:** Validation, consistency, correctness, schema enforcement, data migrations, type safety, constraints.

**Examples:**
- "Added a database constraint to prevent duplicate emails"
- "Wrote a migration to backfill missing timestamps"
- "Implemented validation on the user input DTO"
- "Fixed a bug where negative quantities were accepted"
- "Added TypeScript strict mode to catch type errors"

## 12. Compliance / Policy

**What it captures:** Legal requirements, regulatory compliance (GDPR, HIPAA, SOC2), organizational policy, licensing, accessibility (WCAG), data retention.

**Examples:**
- "Added cookie consent banner for GDPR compliance"
- "Implemented data retention/deletion policies"
- "Added accessible labels for screen reader support"
- "Ensured color contrast meets WCAG AA standards"
- "Added terms of service acceptance tracking"

---

## How to choose a category

When categorizing an entry, ask:

1. **Primary category:** What was the dominant reason for this change? If the user mentions multiple reasons, choose the one they emphasized first or most.
2. **Secondary category:** Was there an additional benefit or concern? Many changes serve multiple purposes.
3. **Intent override:** All changes have an intent. If none of the other 11 categories fit clearly, default to Intent.

**Common overlaps:**
- UX + Styling — visual + interaction changes
- Efficiency + Reliability — performance with error handling
- Security + Compliance — data protection for legal reasons
- Maintainability + DX — code quality for developer benefit
- Business Logic + Data Integrity — rules and their correctness
- Compatibility + Security — version updates that fix vulnerabilities
