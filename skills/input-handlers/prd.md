# Input Handler: PRD / BRD / Technical Spec

1. **Map the document before extracting anything.**
   - List its sections and features.
   - Note the Scope and Out-of-scope sections, and do not test anything out of scope.
   - Note personas and roles, global rules (pricing, limits, auth) and non-functional requirements.
2. **Split it into testable units.**
   - Create one `feature` for each distinct capability.
   - Under each feature, create a requirement for each behaviour.
   - Use the document's own IDs if it has them. Otherwise use `REQ-` IDs, with `source_ref: "PRD §<section> <title>"`.
3. **Handle global rules.**
   - A rule that applies across features, such as "all monetary values in INR with 2 decimals" or "all pages require login", is a requirement under a `GLOBAL` feature or the most relevant one.
   - Its cases cover each feature that relies on it, but only where the risk is real. Do not repeat the same check for every feature.
4. **Non-functional requirements** (performance, availability, accessibility, security):
   - Extract them only if they are stated with a measurable target.
   - Unmeasurable NFRs become `gaps`, not tests. For example, "should be fast" becomes a gap.
5. **Look for conflicts.** Contradictions between sections, such as a limit stated differently, are blocking clarifications.
6. **Technical specs:**
   - Also extract data constraints (field types, lengths, nullability), state machines, events and their side effects, and failure modes such as retries and timeouts.
   - These drive Boundary, Business Rule and Error Handling cases.
7. **Size the suite** with the guide in `scenario-design.md` for each feature. Do not spread a fixed total across all features.
