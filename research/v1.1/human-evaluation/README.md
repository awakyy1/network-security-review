# Blinded human-evaluation package

The generated `reviewer-package-template.json` contains 36 randomized items.
Give an independent copy to each consenting reviewer together with
`../human-evaluation-rubric.json` and
`../../../docs/V1_1_HUMAN_EVALUATION_PROTOCOL.md`.

Each reviewer must:

1. choose a unique pseudonymous `reviewer_id` that contains no name, email or
   employment identifier;
2. rate every 1--5 dimension using the frozen anchors;
3. complete both Boolean safety checks;
4. provide a short rationale in `reviewer_note` for every item;
5. work independently and avoid opening `concealed-identity-mapping.json`.

The repository owner must lock the completed files before unblinding. Run the
aggregator with at least two completed packages:

```powershell
E:\tcc\.venv\Scripts\python.exe -m src.human_evaluation_analysis `
  --reviewer-package E:\path-on-non-system-drive\reviewer-01-complete.json `
  --reviewer-package E:\path-on-non-system-drive\reviewer-02-complete.json `
  --output E:\tcc\research\v1.1\human-evaluation\ratings-aggregate.json
```

The public aggregate excludes reviewer pseudonyms and free-text notes. The
concealed mapping is used only after ratings are locked. Until genuine completed
packages exist, the manuscript must continue to state that human ratings were
not collected.
