# Input Handler: Multiple Inputs

Use this handler when more than one input is supplied, such as a story with a
screenshot, or a PRD with an API spec and existing tests.

1. **Classify each input separately.** Each one gets its own entry in `inputs[]`.
2. **Extract from each input with its own handler.** Keep each item's `source_ref` pointing at its own input, for example `"login.png: header"` or `"story.md AC2"`.
3. **Reconcile the extracted items.**
   - **Same behaviour from two sources.** Keep one item, preferring the more authoritative source (spec over screenshot, stated over observed over inferred). Mention the other source in the `source_ref`: `"story.md AC2; login.png: error banner"`.
   - **One source fills another's gap.** Record it as `stated` or `observed` and cite that source. For example, a screenshot can show the exact error text a story omits.
   - **Contradiction.** For example, the story says the minimum password is 8 and the design hint says 6. This is a **blocking** clarification. Never pick one silently.
4. **Generate one unified suite.** Use a single ID sequence per feature, with no duplicate cases across sources (`skills/duplicate-review.md`).
5. **Existing tests among the inputs.** Run `existing-test-cases.md` against the reconciled requirements rather than the inferred ones.
