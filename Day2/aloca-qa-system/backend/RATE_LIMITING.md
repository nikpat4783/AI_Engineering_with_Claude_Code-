# Rate Limiting Implementation

## Overview

Rate limiting has been implemented using the `slowapi` library to protect the ALOCA+ QA System API from abuse and DOS attacks. All endpoints now have appropriate rate limits based on their operational characteristics.

## Implementation Details

### Configuration

The rate limiter is initialized in `backend/main.py` (lines 33-42):

```python
# Rate Limiting Configuration
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )
```

**Key Features:**
- Uses IP address (`get_remote_address`) as the rate limit key
- Returns HTTP 429 (Too Many Requests) when limit exceeded
- Provides clear error message to clients
- Rate limits are per-minute

### Rate Limits by Endpoint

| Endpoint | Method | Limit | Rationale |
|----------|--------|-------|-----------|
| `/` | GET | 300/min | Root endpoint, not resource intensive |
| `/health` | GET | 200/min | Health checks should be frequent for monitoring |
| `/dashboard/stats` | GET | 60/min | Aggregated query, moderate cost |
| `/test-cases` | POST | 10/min | Creation limited to prevent spam |
| `/test-cases` | GET | 100/min | List operation, efficient query |
| `/test-cases/{id}` | GET | 100/min | Single record retrieval, efficient |
| `/test-results` | POST | 20/min | Creation limited but more than test cases |
| `/test-results` | GET | 100/min | List operation, efficient query |
| `/defects` | POST | 10/min | Creation limited to prevent spam |
| `/defects` | GET | 100/min | List operation, efficient query |
| `/defects/{id}` | GET | 100/min | Single record retrieval, efficient |
| `/defects/{id}` | PATCH | 20/min | Updates limited but more than creation |
| `/metrics` | GET | 60/min | Historical data, moderate cost |
| `/metrics/generate` | POST | 5/min | Expensive aggregation, most restricted |

## Rationale for Rate Limits

### Tier 1: Creation Endpoints (10-20/min)
- **POST /test-cases**: 10/min - Test case creation requires database writes
- **POST /test-results**: 20/min - More frequent test result recording expected
- **POST /defects**: 10/min - Defect creation is less frequent

### Tier 2: Read Endpoints (100/min)
- **GET /test-cases, /test-results, /defects**: 100/min - Standard list queries
- GET operations are lightweight and cacheable
- Suitable for frontend dashboard auto-refresh (every 30 seconds = 2/min)

### Tier 3: Update Endpoints (20/min)
- **PATCH /defects/{id}**: 20/min - Updates are less frequent than creation
- Still allows frequent status changes and assignments

### Tier 4: Dashboard Endpoints (60/min)
- **GET /dashboard/stats**: 60/min - Aggregated query with multiple database operations
- Suitable for auto-refresh every 30 seconds from single client
- Prevents dashboard from overloading with rapid requests

### Tier 5: Metrics Generation (5/min)
- **POST /metrics/generate**: 5/min - Most expensive operation
- Full aggregation across all test results and defects
- Should be called programmatically on schedule, not by user

### Tier 6: Health/Root Endpoints (200-300/min)
- **GET /health**: 200/min - Monitoring and health checks
- **GET /**: 300/min - Root endpoint, minimal processing

## Monitoring Rate Limits

### Client Perspective

When rate limit is exceeded, clients receive:

```json
HTTP 429 Too Many Requests

{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### For Developers

Rate limits can be adjusted in `backend/main.py` by changing the `@limiter.limit()` decorator:

```python
@app.post("/test-cases")
@limiter.limit("10/minute")  # Change this number
def create_test_case(...):
    pass
```

**Format:** `"{count}/{period}"` where period can be:
- `minute`
- `hour`
- `day`
- `second`

## Typical Usage Scenarios

### Dashboard Auto-Refresh (30 seconds)
- GET /dashboard/stats: 2 requests/minute
- GET /test-cases: 2 requests/minute
- GET /defects: 2 requests/minute
- **Total: 6/minute** - Well within limits

### Normal User Workflow
- Creating test case: 1-2/minute
- Recording test results: 5-10/minute
- Creating defects: 1-2/minute
- Viewing/filtering: 10-20/minute
- **Total: ~20-30/minute** - Within limits

### Heavy Load Scenario
- Bulk test execution: ~15-20 test results/minute
- Dashboard refresh: ~2/minute
- **Total: ~20/minute** - Within limits

## Dependencies

Rate limiting requires:
```
slowapi==0.1.9
python-jose==3.3.0
```

These have been added to `backend/requirements.txt`.

## Installation

After updating requirements:

```bash
cd backend
pip install -r requirements.txt
```

## Testing Rate Limits

To test rate limiting:

```bash
# Test endpoint 1: Health check (200/min limit)
for i in {1..10}; do curl http://localhost:8000/health; done

# Test endpoint 2: Create test case (10/min limit)
for i in {1..15}; do
  curl -X POST http://localhost:8000/test-cases \
    -H "Content-Type: application/json" \
    -d '{"name":"test-'"$i"'","description":"test","module":"api"}'
done
# After 10 requests, should get 429 Too Many Requests
```

## Future Enhancements

Possible improvements:
1. **Per-user rate limiting**: When authentication is implemented, use user ID instead of IP
2. **Tiered access**: Premium users get higher limits
3. **Burst allowance**: Use token bucket algorithm for smoother rate limiting
4. **Metrics collection**: Track rate limit violations for analytics
5. **Configurable limits**: Move limits to environment variables

## Security Notes

- Rate limiting is IP-based, so behind a proxy or load balancer you may need to configure the `get_remote_address` function
- For production, consider:
  - Using Redis for distributed rate limiting (across multiple servers)
  - Implementing DDoS protection at infrastructure level
  - Monitoring for rate limit abuse patterns
  - Having whitelist for trusted clients (if needed)

---

**Last Updated**: September 5, 2026
**Status**: IMPLEMENTED
**Coverage**: All 14 endpoints with rate limiting
