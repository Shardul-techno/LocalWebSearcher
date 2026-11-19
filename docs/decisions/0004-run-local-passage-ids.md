# 0004: Assign passage IDs when a passage is first shown

- Candidate slices remain temporary until selected for an LLM prompt.
- Final IDs are monotonic and unique within a run.
- The saved run contains only passages actually shown to the model.
- This keeps run files auditable and avoids implying unseen text supported the answer.
- A future local-file source can use the same passage and ranking flow.
