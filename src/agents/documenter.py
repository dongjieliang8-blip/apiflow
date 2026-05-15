"""Documenter Agent -- generates OpenAPI 3.0 documentation from endpoint analysis."""

from src.utils.api import DeepSeekClient

SYSTEM_PROMPT = """You are the **Documenter Agent** in a multi-agent API testing pipeline.
Your role: generate complete OpenAPI 3.0 (Swagger) specification from endpoint analysis.

Output a JSON object with this exact structure:
{
  "openapi": "3.0.3",
  "info": {
    "title": "API Documentation",
    "description": "Auto-generated API documentation by APIFlow",
    "version": "1.0.0"
  },
  "servers": [{"url": "http://localhost:5000", "description": "Development server"}],
  "paths": {
    "/api/users/{id}": {
      "get": {
        "operationId": "getUserById",
        "summary": "Get user by ID",
        "tags": ["users"],
        "parameters": [
          {"name": "id", "in": "path", "required": true, "schema": {"type": "integer"}}
        ],
        "responses": {
          "200": {"description": "Successful response", "content": {"application/json": {"schema": {"type": "object"}}}},
          "404": {"description": "User not found"}
        }
      }
    }
  },
  "components": {
    "securitySchemes": {
      "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
      }
    },
    "schemas": {}
  }
}

Rules:
- Generate valid OpenAPI 3.0.3 structure.
- Include request/response schemas for all endpoints with documented fields.
- Use Python-friendly naming for operationId (snake_case).
- Group endpoints by tags.
- Include error response schemas (4xx, 5xx) where applicable.
- The output must be valid JSON that can be rendered by Swagger UI or Redoc."""


def generate_docs(analysis: dict, client: DeepSeekClient) -> dict:
    """Generate OpenAPI documentation from endpoint analysis results."""
    prompt = (
        "Here is the API endpoint analysis:\n\n"
        + str(analysis)
        + "\n\nGenerate a complete OpenAPI 3.0 specification for all endpoints."
    )
    return client.chat_json(SYSTEM_PROMPT, prompt)
