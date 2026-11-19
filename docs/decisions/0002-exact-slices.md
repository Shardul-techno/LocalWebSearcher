# 0002: Store passage offsets into canonical page text

- Extracted page text is canonical and is never normalized before slicing.
- Every passage records exact start/end offsets and the page SHA-256.
- Rendering can reject mismatched quote data deterministically.
- Repeated text remains distinguishable through offsets and run-local IDs.
