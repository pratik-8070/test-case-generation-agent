# Input Handler: API Specification

Works for OpenAPI/Swagger (YAML or JSON), Postman collections, and prose API docs.

## Extract for each endpoint (one requirement per method + path)

- Method, path, summary, and the auth scheme (bearer, API key, OAuth scopes)
- Path, query and header parameters: required or optional, type, format, enum, min/max, pattern, default
- Request body schema: required fields, types, constraints, nested objects and arrays (minItems/maxItems)
- Responses for each status code: body schema, headers, error format
- Stated side effects (resource created, stock decremented, event emitted) and idempotency
- Rate limits and pagination, **only if stated**

Use `source_ref: "<METHOD> <path> → <part>"`. Examples:
- `"POST /orders → requestBody.quantity"`
- `"POST /orders → 409"`

Every documented response code is an AC for that endpoint. Every schema
constraint (min, max, enum, pattern, required) is a BR.

## Scenario checklist for each endpoint

| Category | Cases |
|---|---|
| Positive | Minimal valid request (required fields only); full valid request; each enum value when the behaviour differs |
| Validation | Each required field missing; wrong type; invalid format or pattern; value outside the enum |
| Boundary | min-1, min, max and max+1 for numbers, lengths and array sizes |
| Authentication | No credentials → 401; invalid or expired token → 401 |
| Authorization | Valid token without the required scope or role, or accessing another user's resource → 403 or 404, as documented |
| Negative | Unknown resource ID → 404; conflicting state → 409, if documented; unsupported method or content type, only if documented |
| Error Handling | The error body matches the documented error schema |
| Business Rule | Documented side effects happen on success and **do not** happen on failure |
| Edge Case | Extra or unknown fields; Unicode or very long strings where no max is given (flag as an assumption); duplicate submit if idempotency is stated |

## Writing API test cases

- **Steps** name the method, path, headers and body: "Send `POST /orders` with header `Authorization: Bearer <valid_token>` and body `test_data.body`".
- **Test data** puts the request body under `body`, plus a `headers` or `params` object.
- **Expected result** gives the status code, the key body fields, the response schema conformance, and the side-effect check. For example: "`201`; body has `id` (UUID) and `status: "PENDING"`; GET /orders/{id} returns the same order".
- **Undocumented status codes** must not be asserted as facts. If the spec does not say which code is returned for a case, flag it as an assumption or add a gap.
