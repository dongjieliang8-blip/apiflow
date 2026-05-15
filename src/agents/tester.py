"""Tester Agent -- generates test cases for each discovered API endpoint."""

from src.utils.api import DeepSeekClient

SYSTEM_PROMPT = """You are the **Tester Agent** in a multi-agent API testing pipeline.
Your role: given a list of API endpoints, generate comprehensive test cases.

For each endpoint, generate tests covering:
1. **Happy path**: valid request with correct parameters
2. **Boundary**: min/max values, empty strings, zero, negative numbers
3. **Missing required fields**: omit required parameters
4. **Invalid input**: wrong types, malformed data
5. **Authentication**: unauthenticated access to protected endpoints
6. **Edge cases**: special characters in path, very large payloads, etc.

Output a JSON object with this exact structure:
{
  "test_suite": [
    {
      "endpoint": "GET /api/users/{id}",
      "tests": [
        {
          "name": "get_user_happy_path",
          "description": "Fetch existing user with valid ID",
          "method": "GET",
          "url": "http://localhost:5000/api/users/1",
          "headers": {"Authorization": "Bearer test-token"},
          "body": null,
          "expected_status": 200,
          "expected_response_shape": {"id": "integer", "name": "string"},
          "assertions": ["response has 'name' field", "id matches requested id"],
          "priority": "high"
        },
        {
          "name": "get_user_not_found",
          "description": "Fetch non-existent user returns 404",
          "method": "GET",
          "url": "http://localhost:5000/api/users/999999",
          "headers": {"Authorization": "Bearer test-token"},
          "body": null,
          "expected_status": 404,
          "expected_response_shape": {"error": "string"},
          "assertions": ["error message indicates user not found"],
          "priority": "high"
        }
      ]
    }
  ],
  "total_tests": N,
  "coverage_summary": "Brief description of test coverage"
}

Generate at least 3-5 test cases per endpoint. Prioritize thorough coverage.
Use realistic test data values. All URLs should use the base_url from the analysis."""


def generate_tests(analysis: dict, client: DeepSeekClient) -> dict:
    """Generate test cases from endpoint analysis results."""
    prompt = (
        "Here is the API endpoint analysis:\n\n"
        + str(analysis)
        + "\n\nGenerate comprehensive test cases for all endpoints listed above."
    )
    return client.chat_json(SYSTEM_PROMPT, prompt)
