import json
from google import genai
from google.genai import types

class GeminiExtractor:
    def __init__(self, api_key: str, model_id: str = 'gemini-3-flash-preview'):
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id

    def extract_table(self, file_bytes: bytes, mime_type: str, prompt: str):
        """
        Calls the Gemini API to extract tabular data from a file.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    types.Part.from_bytes(
                        data=file_bytes,
                        mime_type=mime_type
                    ),
                    prompt + "\nExtract all rows from the table in this document. Return ONLY a JSON array."
                ]
            )

            # Clean and parse JSON
            raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(raw_text)

            return parsed_data if isinstance(parsed_data, list) else [parsed_data]

        except Exception as e:
            raise Exception(f"Extraction failed: {str(e)}")

