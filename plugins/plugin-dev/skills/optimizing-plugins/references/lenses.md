# Optimization Lenses Reference

Detailed criteria for each of the 6 analytical lenses used by the plugin optimizer.

## Lens 1: Trigger Fidelity

**Core question:** Will Claude invoke this skill/command at the right moment?

### What to Check

**Skill descriptions:**
- Uses third-person format ("This skill..." not "Use this skill...")
- Contains specific trigger phrases in quotes
- Includes action verbs matching user vocabulary
- Specifies when NOT to use (if ambiguous with other skills)
- Length: 50-200 words optimal

**Trigger phrase quality:**
- Concrete nouns: "bugs", "tests", "API", "database"
- Action verbs: "debug", "fix", "create", "analyze"
- Context phrases: "before committing", "when stuck", "after writing"

**Red flags:**
- Vague words: "help", "assist", "general", "various"
- Missing action context: when in workflow?
- Overlapping triggers with other skills

### Evaluation Questions

1. Would a user naturally say words that match this description?
2. Does Claude have enough context to know when to invoke?
3. Are there false-positive triggers that would cause wrong invocation?

### Example Improvements

**Before:** "Use for debugging problems"
**After:** "Use when encountering bugs, test failures, or unexpected behavior — before proposing fixes"

**Before:** "Helps with code review"
**After:** "Reviews code for bugs, security issues, and style violations. Use after completing a feature or before creating a pull request."

---

## Lens 2: Token Economy

**Core question:** Does every token earn its keep?

### What to Check

**File sizes:**
- SKILL.md under 500 lines (optimal: 200-400)
- Reference files used for detailed content
- No redundant information across files

**Progressive disclosure:**
- Essential info in SKILL.md
- Detailed criteria in references/
- Scripts for deterministic operations

**Content efficiency:**
- No verbose explanations of obvious things
- Tables instead of paragraphs where appropriate
- Examples are minimal but sufficient

### Evaluation Questions

1. Could this be shorter without losing clarity?
2. Is detailed content properly delegated to references?
3. Are there redundant sections saying the same thing?

### Example Improvements

**Before:** Long paragraph explaining when to use each option
**After:** Decision table with criteria and recommendations

**Before:** Inline code examples repeated in multiple places
**After:** Single reference file with examples, linked from SKILL.md

---

## Lens 3: Structural Clarity

**Core question:** Can Claude navigate and understand efficiently?

### What to Check

**Navigation:**
- Clear section headings
- Table of contents for files >100 lines
- Logical flow from overview to details

**Reference depth:**
- One level deep (SKILL.md → references/)
- No chains: A → B → C
- Clear what lives where

**Consistency:**
- Same heading style throughout
- Consistent formatting patterns
- Predictable structure across similar components

### Evaluation Questions

1. Can Claude find specific information quickly?
2. Is the document structure self-explanatory?
3. Would a new reader understand the organization?

### Example Improvements

**Before:** Mixed heading levels, inconsistent formatting
**After:** H2 for major sections, H3 for subsections, consistent patterns

**Before:** Important details buried in paragraphs
**After:** Key information in bullet points or tables at section start

---

## Lens 4: Degrees of Freedom

**Core question:** Does specificity match task fragility?

### What to Check

**Task fragility assessment:**
- Fragile tasks (security, data integrity): Need rigid instructions
- Creative tasks (design, exploration): Need flexible guidance
- Mixed tasks: Clear which parts are rigid vs flexible

**Instruction specificity:**
- Rigid: Exact steps, exact commands, exact formats
- Flexible: Principles, options, guidelines

**Decision points:**
- Are choices explicit or implicit?
- Does Claude know when to ask vs decide?

### Evaluation Questions

1. For fragile operations: Are instructions precise enough to prevent mistakes?
2. For creative tasks: Is there room for Claude to adapt?
3. Are the boundaries between rigid and flexible clear?

### Example Improvements

**Before:** "Validate the input before processing"
**After:** "Validate input using schema at `schemas/input.json`. Reject with specific error if: missing required fields, invalid types, values out of range."

**Before:** Rigid steps for exploratory task
**After:** "Explore the codebase to understand X. Consider: [list of approaches]. Choose based on what you find."

---

## Lens 5: Resilience

**Core question:** What happens when things go wrong?

### What to Check

**Error handling:**
- Are failure modes documented?
- What should Claude do when X fails?
- Are there recovery paths?

**Hooks:**
- Do hooks handle errors gracefully?
- Is stderr captured and reported?
- Non-zero exit codes handled?

**Agents:**
- What if the agent can't complete?
- Are there explicit failure instructions?
- Timeout handling?

**MCP:**
- Server connection failures?
- Malformed responses?
- Authentication errors?

### Evaluation Questions

1. What happens if the primary approach fails?
2. Are error messages actionable?
3. Is there a graceful degradation path?

### Example Improvements

**Before:** "Run the validation script"
**After:** "Run validation script. If it fails: check error message, report to user with suggested fix, offer to proceed with manual validation."

**Before:** No error handling in hook
**After:** Hook returns structured error with actionable message

---

## Lens 6: Plugin Coherence

**Core question:** Does this work as a unified whole?

### What to Check

**Naming conventions:**
- Consistent naming across skills, commands, agents
- Names reflect function
- No confusing overlaps

**Component boundaries:**
- Each component has clear responsibility
- No overlapping functionality
- Dependencies are explicit

**Handoffs:**
- How do components work together?
- Are transitions documented?
- Is the user journey clear?

**Documentation:**
- README reflects actual capabilities
- No orphaned or undocumented components
- Examples show realistic usage

### Evaluation Questions

1. Does the plugin feel like one cohesive tool?
2. Would a new user understand what each part does?
3. Are component relationships clear?

### Example Improvements

**Before:** Skills with overlapping triggers, unclear which to use
**After:** Clear differentiation in descriptions, explicit "use X when... use Y when..."

**Before:** Command invokes skill but relationship undocumented
**After:** Command docs explain delegation, skill docs reference command

---

## Cross-Cutting Patterns

When analyzing, watch for these cross-lens issues:

**Description ↔ Implementation mismatch:**
- Description promises X but instructions do Y
- Triggers don't match actual capability

**Redundancy across components:**
- Same instructions in multiple skills
- Duplicate error handling logic

**Missing integration:**
- Components that should reference each other don't
- No guidance on combined usage

**Inconsistent quality:**
- Some skills polished, others rough
- Uneven documentation depth
