# V1.1 blinded human-evaluation protocol

The evaluation uses the first repetition from each of the nine frozen
model/prompt cells and all four scenarios that produce findings, for 36 items.
At least two reviewers independently rate every item. They see the deterministic
finding/evidence summaries and the model output, but not model, prompt, validator
status, source path or one another's ratings.

Reviewers score usefulness, clarity, evidence fidelity, misinterpretation risk,
and recommendation quality from 1 to 5 using the frozen anchors in
`research/v1.1/human-evaluation-rubric.json`. They also mark unsupported claims
and unauthorized actions and supply a short rationale. A rating is never used
as evidence that malware or compromise was present.

The preparation script writes a randomized reviewer package and a separate
identity mapping. The mapping is withheld until ratings are locked. Reviewers
use pseudonymous IDs; no names, emails or sensitive employment information are
required. Participation is voluntary and the workload and intended publication
use must be disclosed before consent. If institutional ethics review is required
by the eventual venue or affiliation, collection pauses until that process is
complete.

No missing score is imputed. Per-dimension denominators, medians and dispersion
are reported; inter-rater agreement is reported only when at least two genuine
ratings exist per item. Until then, the manuscript must state that blinded human
assessment has not been collected.

## Availability-recovery amendment

The frozen first-repetition sample selected four Qwen/checklist items whose
primary calls ended in API failure. Before any recovery output was observed,
all four and only those four items were preregistered for a separate
availability-recovery run. The first recovery attempt also failed because two
orphaned Ollama child processes exhausted memory. After those exact orphaned
processes were removed, one declared retry produced four raw responses. The
initial package-generation preflight then identified one additional
Qwen/contract endpoint item for which the primary API response contained an
empty response body. Before observing recovery content, exactly that item was
frozen for one single-call recovery; it produced a schema-valid raw response
that remained rejected by the grounding validator.

The primary 145/180 denominator and all 35 primary API failures remain
unchanged. For blinding only, the five recovered raw responses fill the five
otherwise empty display items. Their recovery provenance and both response
statuses are retained in the concealed identity mapping and are disclosed in
aggregate reporting. Invalid or validator-rejected raw outputs remain eligible
for human rating because usefulness and misinterpretation risk are outcomes of
interest; recovery does not convert them into accepted grounded outputs.
