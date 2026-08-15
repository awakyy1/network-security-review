# Erratum: CTU-13 prospective selection timestamp

The original pre-download selection record has SHA-256
`b7ec32a07c2013b2d9882021a9c6dd6ba98008b0a81e45dbb698342f2ea86537`.
Its `selection_frozen_at` value was mistyped as `16:43:00-03:00`.

The local filesystem chronology observed immediately after acquisition was:

- original selection record created and last written: `16:37:57`;
- Scenario 11 download file created: `16:38:25`;
- Scenario 6 download file created: `16:38:41`.

The corrected record uses `16:37:57-03:00`, retains the same dataset roles,
candidate grid and gates, and links back to the original hash. The correction
does not claim that a Git checkout can reproduce NTFS creation timestamps; its
purpose is to disclose the transcription error rather than silently rewrite
the prospective history. Neither selected flow had been parsed or evaluated
when the error was found.
