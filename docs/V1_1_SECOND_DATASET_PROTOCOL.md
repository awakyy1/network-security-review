# V1.1 second-dataset protocol

The selected source is the Botnet Group Activity Dataset (Mendeley Data DOI
10.17632/4vftxh97m8.1; associated Data in Brief article DOI
10.1016/j.dib.2021.107334), distributed under CC BY-NC 3.0. Scenario 1 was
selected before downloading the archive or inspecting scenario-level labels.

The archive hash and byte count must match the pre-recorded values. The archive
is listed before extraction, and only the selected `dataset_result.binetflow`
plus documentation needed for interpretation is extracted. Raw data and all
temporary material remain on `E:`.

This source has `.binetflow`-compatible flow fields, but it is synthetic and its
group activity is derived from CTU-13 patterns. It can therefore test parser and
detector implementation transfer, not independent real-world generalization.
Metrics are reported separately and cannot be pooled with CTU-13 development,
retrospective or confirmatory results. No threshold is changed after inspecting
Scenario 1; the frozen V1.1 detector configuration is replayed as-is.
