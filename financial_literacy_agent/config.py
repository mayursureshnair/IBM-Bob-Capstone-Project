"""
Centralised configuration for the Digital Financial Literacy Agent.

Values here are used as hard-coded defaults and are overridden by
environment variables (WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL)
or by values passed directly to FinancialLiteracyAgent().
"""

# IBM Granite 4H Small on watsonx.ai
DEFAULT_MODEL_ID = "ibm/granite-4-h-small"

# Service endpoint (us-south Dallas)
DEFAULT_URL = "https://us-south.ml.cloud.ibm.com"

# Preconfigured project credentials (overridden by env vars when present)
DEFAULT_API_KEY = "7ia2KiMby_d_hdFi8Ej97yn1BTyDeHmu6tUX7oM2iM3y"
DEFAULT_PROJECT_ID = "e99b1dca-9779-43a3-a8de-dd0bbdb8e334"
