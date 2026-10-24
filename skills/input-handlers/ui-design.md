# Input Handler: UI Design / Screenshot

1. **Inventory what is visible.** Read the image and list:
   - screens or regions;
   - fields, with their labels, placeholders, the required markers (*) and any visible hints;
   - buttons, links, toggles, tabs, menus;
   - visible messages and states (error banners, disabled buttons, empty states);
   - navigation cues.
2. **Mark each item as observed or inferred.**
   - **observed** means it is visible in the design. These items become `origin: "observed"`, with `source_ref: "<image>: <region>"`.
   - **inferred** means it is not visible but is reasonably implied. For example, an `Email` field likely needs format validation, and a "Forgot password?" link likely navigates somewhere. These items become `origin: "inferred"`. Every case that uses one gets `assumption: true` and an `assumptions[]` entry.
3. **Never state invisible behaviour as fact.** Validation rules, limits, server responses and destinations are unknown from a static image unless the image shows them. Do not invent them.
4. **Choose scenarios.**
   - Observed elements give Positive, UI and Validation cases:
     - required-field emptiness when it is marked;
     - layout and state checks;
     - tab order, when it is relevant to the design;
     - responsive behaviour, if several breakpoints are shown.
   - Behaviour behind a button usually needs clarification. If submit, error or navigation outcomes are central and unknown, raise a **blocking** question, or flag every dependent case as an assumption if the user chose to proceed.
5. **Several screens in a flow.** Derive the navigation transitions and test each one shown.

In the run's `input-analysis.json`, keep a `context.ui_behavior` list of what
was observed. Put what was inferred in `assumptions[]`.
