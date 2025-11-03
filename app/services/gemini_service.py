from google import genai
from google.genai import types


class GeminiService:
    """Service for Google Gemini AI integration"""

    API_KEY = "AIzaSyCtV2qGKDNEclbYAXlYuN_ZPK_x_e2mR-w"
    MODEL = "gemini-flash-lite-latest"

    @staticmethod
    def generate_outlier_analysis(outlier_data, dataset=None):
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

            dataset_context = ""
            if dataset:
                dataset_context = f"""
**DATASET CONTEXT:**
- File: {dataset.get('filename', 'Unknown')}
- Rows: {dataset.get('total_rows', 'Unknown')}
- Columns: {dataset.get('total_columns', 'Unknown')}
- Quality Score: {dataset.get('quality_score', 'Unknown')}
"""

            prompt = f"""You are a data quality analyst explaining statistical outliers to healthcare business stakeholders. Be CONCISE and ACTION-ORIENTED.

{dataset_context}

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

    @staticmethod
    def generate_issue_analysis(issue_payload):
        """Generate AI-powered analysis for any issue type."""
        issue_type = issue_payload.get('type', 'Unknown')
        dataset = issue_payload.get('dataset') or {}

        if issue_type == 'Statistical Outlier':
            outlier_stats = issue_payload.get('outlier_stats')
            if not outlier_stats:
                raise Exception('Outlier statistics missing for outlier analysis')
            return GeminiService.generate_outlier_analysis(outlier_stats, dataset=dataset)

        try:
            client = genai.Client(api_key=GeminiService.API_KEY)

            dataset_context = ""
            if dataset:
                dataset_context = f"""
**DATASET CONTEXT:**
- File: {dataset.get('filename', 'Unknown')}
- Rows: {dataset.get('total_rows', 'Unknown')}
- Columns: {dataset.get('total_columns', 'Unknown')}
- Quality Score: {dataset.get('quality_score', 'Unknown')}
"""

            column_context = ""
            column_details = issue_payload.get('column_details') or {}
            if column_details:
                column_context = f"""
**COLUMN SUMMARY:**
- Inferred Type: {column_details.get('type', 'Unknown')}
- Total Values: {column_details.get('totalValues', 'Unknown')}
- Non-empty Values: {column_details.get('nonEmptyValues', 'Unknown')}
- Missing Values: {column_details.get('missingCount', 'Unknown')} ({column_details.get('missingPercentage', 'N/A')}%)
- Unique Values: {column_details.get('uniqueCount', 'Unknown')} ({column_details.get('uniquePercentage', 'N/A')}%)
"""

            percentage_val = issue_payload.get('percentage')
            if isinstance(percentage_val, (int, float)):
                percentage_text = f"{percentage_val:.2f}%"
            elif percentage_val is None:
                percentage_text = "N/A"
            else:
                percentage_text = f"{percentage_val}%"

            issue_details = f"""
**ISSUE DETAILS:**
- Type: {issue_type}
- Column: {issue_payload.get('column') or 'Dataset-level'}
- Severity: {issue_payload.get('severity', 'N/A')}
- Affected Records: {issue_payload.get('count', 'Unknown')}
- Percentage Impact: {percentage_text}
- Description: {issue_payload.get('description', 'N/A')}
"""

            prompt = f"""You are a data quality analyst supporting healthcare business stakeholders. Provide clear, actionable guidance.

{dataset_context}

{issue_details}

{column_context}

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
            raise Exception(f"Failed to generate issue analysis: {str(e)}")

