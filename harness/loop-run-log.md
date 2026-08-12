# Loop Run Log

This append-only log records durable summaries. Never include secrets, production data, provider payloads, or raw CI output that may contain credentials.

| Started at | Mode        | Items | Result  | Evidence | Human action                                 |
| ---------- | ----------- | ----: | ------- | -------- | -------------------------------------------- |
| Template   | report-only |     0 | Not run | —        | Configure a scheduler only after CI is green |
