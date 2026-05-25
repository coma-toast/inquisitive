# Question Templates

Per-category question templates for the context-aware secondary question. The primary question is always the same ("What was the primary motivation behind this change?"). The secondary question should reference the specific original suggestion vs. user choice.

## Professional templates

| Category | Secondary question template |
|----------|---------------------------|
| **Intent** | "I suggested [approach], but you went with [choice]. Was my suggestion solving the wrong problem, or was there a different goal I missed?" |
| **User Experience** | "I suggested [approach], but you chose [choice]. How does this change improve the user's experience or flow?" |
| **Styling / Layout** | "I suggested [approach], but you chose [choice]. What specific visual or layout concern were you addressing?" |
| **Security** | "I suggested [approach], but you chose [choice]. What specific threat or vulnerability does this address?" |
| **Business Logic** | "I suggested [approach], but you chose [choice]. What business rule or requirement drove this decision?" |
| **Efficiency** | "I suggested [approach], but you chose [choice]. What metric or performance concern were you optimizing for?" |
| **Maintainability** | "I suggested [approach], but you chose [choice]. What aspect of code quality or future maintenance were you improving?" |
| **Reliability** | "I suggested [approach], but you chose [choice]. What failure mode or edge case were you handling?" |
| **Compatibility** | "I suggested [approach], but you chose [choice]. What compatibility concern — platform, API, dependency — needed addressing?" |
| **Developer Experience** | "I suggested [approach], but you chose [choice]. What developer workflow friction were you reducing?" |
| **Data Integrity** | "I suggested [approach], but you chose [choice]. What data quality or correctness concern drove this change?" |
| **Compliance / Policy** | "I suggested [approach], but you chose [choice]. What policy, regulatory, or legal requirement drove this?" |

## George/Phoebe templates

| Category | Secondary question template |
|----------|---------------------------|
| **Intent** | "George think [approach]. Human pick [choice]. What problem human fix?" |
| **User Experience** | "George think [approach]. Human pick [choice]. Human use thing better now?" |
| **Styling / Layout** | "George think [approach]. Human pick [choice]. Thing look different. Why?" |
| **Security** | "George think [approach]. Human pick [choice]. Bad guy not get in now?" |
| **Business Logic** | "George think [approach]. Human pick [choice]. Business rule change?" |
| **Efficiency** | "George think [approach]. Human pick [choice]. Thing go faster now?" |
| **Maintainability** | "George think [approach]. Human pick [choice]. Code cleaner now?" |
| **Reliability** | "George think [approach]. Human pick [choice]. Thing break less now?" |
| **Compatibility** | "George think [approach]. Human pick [choice]. Work on more things now?" |
| **Developer Experience** | "George think [approach]. Human pick [choice]. Human work easier now?" |
| **Data Integrity** | "George think [approach]. Human pick [choice]. Data more right now?" |
| **Compliance / Policy** | "George think [approach]. Human pick [choice]. Rules happy now?" |

## Context analysis heuristics

Before asking, analyze the change to determine the most likely category:

1. **Look at the file type and content:**
   - CSS, SCSS, theme files → Styling/Layout
   - DTOs, validators, schemas → Data Integrity
   - API handlers, middleware → Security (if auth/permissions), Business Logic (if rules)
   - Tests → Reliability
   - README, docs → User Experience / Developer Experience

2. **Look at the diff:**
   - Mostly visual/class changes → Styling/Layout
   - Error handling blocks → Reliability
   - Performance optimizations (caching, queries) → Efficiency
   - Config/version changes → Compatibility
   - Comments, renames, extraction → Maintainability

3. **Look at the user's instruction:**
   - "Make it look/feel better" → UX or Styling
   - "Prevent X from happening" → Security or Reliability
   - "Make it faster" → Efficiency
   - "Make it easier to understand/change" → Maintainability
   - "Make it work on platform X" → Compatibility

If the category is ambiguous, default to the primary question without a category-specific template.
