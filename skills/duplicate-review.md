# Skill: Duplicate Review

`qa_tools check` (dedupe stage) **finds** candidate pairs. You **decide** what
to do with each one.

| Finding | Meaning | Default action |
|---|---|---|
| `exact-duplicate` (error) | Same steps, data and expected result | Delete one. Merge its `source_refs` into the case you keep. |
| `near-duplicate` (warning) | Same check with the same test data, reworded | Merge into one case. Keep the clearer wording and the union of `source_refs`. |
| `data-variants` (warning, one per group) | Same steps and expected result, different test data: a data-driven set | Check each member's value. **Keep** it if the value is a distinct partition or boundary, such as 0 vs 11 or "missing field A" vs "missing field B". **Merge or drop** it if the value sits in the same class as another member, such as 3 vs 4 characters when the minimum is 8. |
| `overlapping-scenario` (warning) | Similar titles for the same refs | Read both. If they verify the same outcome, merge them. If not, rename them so the difference is obvious. |

The script also misses some duplicates, so check for these yourself:

- **Category twins.** A `Negative` case and a `Validation` case that submit the same invalid value. Keep one.
- **Subsumed cases.** Case A checks X, and case B checks X plus Y with the same setup. Keep B, unless A protects a Critical path that should stay isolated.
- **Duplicates across inputs.** When several inputs describe the same behaviour, keep one case and list both sources in `source_refs`.

## After merging

1. Renumber the IDs so there are no gaps in each feature.
2. Update the `test_case_refs` in `review_findings`.
3. Rerun `check`.
