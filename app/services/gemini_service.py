from google import genai
from google.genai import types


class GeminiService:
    """Service for Google Gemini AI integration"""

    API_KEY = "AIzaSyCtV2qGKDNEclbYAXlYuN_ZPK_x_e2mR-w"
    MODEL = "gemini-flash-lite-latest"

    @staticmethod
    def generate_outlier_analysis(outlier_data):
        """
        Generate AI-powered analysis of statistical outliers using Google Gemini.

        Args:
            outlier_data (dict): Dictionary containing outlier statistics and values
                - column_name (str): Name of the column with outliers
                - mean (float): Mean value of the column
                - std_dev (float): Standard deviation
                - count (int): Number of outliers
                - sample_values (list): Sample outlier values
                - min_outlier (float): Minimum outlier value
                - max_outlier (float): Maximum outlier value
                - total_records (int): Total number of records
                - percentage (float): Percentage of records that are outliers

        Returns:
            str: LLM-generated analysis text
        """
        try:
            client = genai.Client(api_key=GeminiService.API_KEY)

            prompt = f"""You are a data quality analyst explaining statistical outliers to healthcare business stakeholders. Be CONCISE and ACTION-ORIENTED.

**OUTLIER STATISTICS:**
- Column: {outlier_data.get('column_name', 'Unknown')}
- Mean: {outlier_data.get('mean', 'N/A')} | Std Dev: {outlier_data.get('std_dev', 'N/A')}
- Outlier Count: {outlier_data.get('count', 0)} of {outlier_data.get('total_records', 0)} ({outlier_data.get('percentage', 0):.2f}%)
- Range: {outlier_data.get('min_outlier', 'N/A')} to {outlier_data.get('max_outlier', 'N/A')}
- Sample Values: {', '.join(map(str, outlier_data.get('sample_values', [])[:10]))}

**FORMAT INSTRUCTIONS:**
- Use simple language (avoid jargon)
- Keep paragraphs to 2-3 sentences MAXIMUM
- Actions must be 15 words or less

### Executive Summary

Provide exactly 3 bullets for quick scanning:
- **Key Finding:** [1 sentence describing the main issue]
- **Primary Risk:** [1 sentence on biggest concern]
- **Top Action:** [1 action, 15 words max]

### Impact Analysis

**Key Finding:** [2-3 sentences with specific metrics]

**Data Quality Impact:** [2-3 sentences on data reliability]

**Business Impact:** [2-3 sentences on operational/financial effects]

### Recommended Actions

- [Action 1 - max 15 words]
- [Action 2 - max 15 words]
- [Action 3 - max 15 words]
- [Action 4 - max 15 words]

### Healthcare Context

**Potential Causes:** [2-3 sentences on reasons in dental claims context]

**Risk Assessment:** [2-3 sentences on fraud/billing/data entry risks]

**Next Steps:** [1-2 sentences on what to investigate]"""

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]

            config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=12000)
            )

            response = client.models.generate_content(
                model=GeminiService.MODEL,
                contents=contents,
                config=config
            )

            return response.text

        except Exception as e:
            raise Exception(f"Failed to generate outlier analysis: {str(e)}")

