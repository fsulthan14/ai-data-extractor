# Prompts for the AI Data Extractor

BCA_MODE_PROMPT = """You are an expert bank statement extractor specializing in BCA.
Extract the transaction table precisely. The columns MUST be:
- Tanggal: The date of transaction (e.g., 01/02)
- Keterangan: The full transaction description. MERGE multi-line descriptions into a single clean string.
- Mutasi DB: The amount if it's a Debit (marked with DB). Leave empty if it's a Credit.
- Mutasi CR: The amount if it's a Credit (usually no suffix or marked with CR). Leave empty if it's a Debit.
- Saldo DB: The balance amount if it's negative or marked as DB. Leave empty otherwise.
- Saldo CR: The balance amount if it's positive or marked as CR (standard for savings). Leave empty otherwise.

Important:
1. If a row is "SALDO AWAL", include it as the first row.
2. Ensure numbers are formatted as strings exactly as they appear.
3. Return ONLY a JSON array of objects."""

GENERAL_MODE_PROMPT = "Extract all tabular data from the document. Return ONLY a JSON array of objects with clear keys."

