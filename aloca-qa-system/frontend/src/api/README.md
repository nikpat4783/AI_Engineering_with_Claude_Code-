# API Handlers - Async/Await Utilities

This directory contains all async/await-based API handlers for the ALOCA+ frontend.

## Structure

```
src/api/
├── client.ts          # Base axios client with error handling
├── dashboard.ts       # Dashboard and metrics endpoints
├── testCases.ts       # Test case and result endpoints
├── defects.ts         # Defect management endpoints
├── hooks.ts           # React hooks for API calls
├── index.ts           # Central exports
└── README.md          # This file
```

## Core Concepts

### 1. ApiClient (client.ts)

Base HTTP client with built-in error handling and async/await support.

```typescript
import { apiClient } from './api/client';

// GET request
const data = await apiClient.get<DataType>('/endpoint');

// POST request
const result = await apiClient.post<DataType>('/endpoint', { field: 'value' });

// PATCH request
const updated = await apiClient.patch<DataType>('/endpoint/id', { field: 'new-value' });

// DELETE request
await apiClient.delete('/endpoint/id');
```

### 2. API Handlers

Each resource has its own handler module with async methods:

**Dashboard API:**
```typescript
import { dashboardApi } from './api';

const stats = await dashboardApi.getStats();
const metrics = await dashboardApi.getMetrics(7);
const newMetric = await dashboardApi.generateMetrics();
const health = await dashboardApi.getHealthStatus();
```

**Test Cases API:**
```typescript
import { testCasesApi } from './api';

// CRUD operations
const testCase = await testCasesApi.createTestCase({ name, description, module });
const allTests = await testCasesApi.listTestCases();
const specific = await testCasesApi.getTestCase(testCaseId);

// Results
const result = await testCasesApi.createTestResult({ test_case_id, status, execution_time_ms });
const results = await testCasesApi.listTestResults(testCaseId);

// Combined operations (uses Promise.all)
const { testCase, results } = await testCasesApi.getTestCaseWithResults(testCaseId);

// Search
const searchResults = await testCasesApi.searchTestCases('query');
```

**Defects API:**
```typescript
import { defectsApi } from './api';

// CRUD operations
const defect = await defectsApi.createDefect({ title, description, severity });
const allDefects = await defectsApi.listDefects();
const specific = await defectsApi.getDefect(defectId);

// Updates
const updated = await defectsApi.updateDefect(defectId, { status, assigned_to });
const statusUpdated = await defectsApi.updateDefectStatus(defectId, 'resolved');
const assigned = await defectsApi.assignDefect(defectId, 'user');

// Filtering
const critical = await defectsApi.getCriticalDefects();
const open = await defectsApi.getOpenDefects();
const stats = await defectsApi.getDefectStats(defectsArray);
```

## Usage Patterns

### Direct API Call (Component or Service)

```typescript
import { testCasesApi } from './api';

async function loadTestCases() {
  try {
    const testCases = await testCasesApi.listTestCases();
    setTestCases(testCases);
  } catch (error) {
    setError(error.message);
  }
}
```

### Using React Hooks (Recommended for Components)

```typescript
import { useTestCases, useCreateTestCase } from './api/hooks';

function TestCasesComponent() {
  // Fetch data automatically
  const { value: testCases, status, error } = useTestCases();
  
  // Manual create function
  const { execute: createTestCase, status: createStatus } = useCreateTestCase();

  const handleCreate = async (data) => {
    try {
      await createTestCase(data);
      // Refresh list
    } catch (err) {
      console.error('Create failed:', err);
    }
  };

  if (status === 'pending') return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {testCases?.map(tc => (
        <div key={tc.id}>{tc.name}</div>
      ))}
    </div>
  );
}
```

## Error Handling

All async handlers include consistent error handling:

```typescript
import { apiClient } from './api/client';

try {
  const data = await apiClient.get('/endpoint');
  // Handle success
} catch (error) {
  // Error is automatically logged to console
  const message = error.message;
  // Handle error
}
```

## Available Hooks

### Data Fetching Hooks (auto-fetch on mount)
- `useDashboardStats()` - Dashboard statistics
- `useMetrics(days?)` - Historical metrics
- `useTestCases(module?)` - Test cases list
- `useTestResults(testCaseId?)` - Test results
- `useDefects(status?, severity?)` - Defects list
- `useCriticalDefects()` - Critical defects only
- `useOpenDefects()` - Open defects only

### Create Hooks (manual fetch)
- `useCreateTestCase()` - Create test case
- `useCreateTestResult()` - Record test result
- `useCreateDefect()` - Create defect

### Update Hooks
- `useUpdateDefect(defectId)` - Update defect

### Utility Hooks
- `useHealthStatus()` - Server health check
- `useDefectStats(defects)` - Calculate defect statistics

## Hook Return Type

All hooks return:
```typescript
{
  execute: async (params?) => Promise<T>,  // Function to execute (if manual)
  status: 'idle' | 'pending' | 'success' | 'error',
  value: T | null,                         // Result data
  error: Error | null                      // Error object
}
```

## Centralized Import

Import all at once:
```typescript
import { dashboardApi, testCasesApi, defectsApi, apiClient } from './api';
```

Or use the convenience object:
```typescript
import api from './api';

await api.dashboard.getStats();
await api.testCases.listTestCases();
await api.defects.getOpenDefects();
```

## Authentication

Set authentication token:
```typescript
import { apiClient } from './api/client';

apiClient.setAuthToken('jwt-token-here');
```

Clear authentication:
```typescript
apiClient.clearAuthToken();
```

## Types

All TypeScript types are exported:

```typescript
import type {
  DashboardStats,
  QualityMetric,
  TestCase,
  TestCaseCreate,
  TestResult,
  TestResultCreate,
  Defect,
  DefectCreate,
  DefectUpdate,
  DefectStats,
} from './api';
```

## Best Practices

1. **Use hooks in components** - Cleaner, handles loading/error states
2. **Use API classes directly** - In services, utilities, non-React code
3. **Always handle errors** - Try/catch blocks or error states
4. **Batch requests** - Use `Promise.all()` for parallel calls
5. **Reuse client instance** - Don't create new axios instances
6. **Type your data** - Use TypeScript types for safety

## Migration from Old Code

**Before (without async/await):**
```typescript
axios.get('http://localhost:8000/test-cases').then(res => {
  setTestCases(res.data);
}).catch(err => {
  setError(err.message);
});
```

**After (with async/await):**
```typescript
try {
  const testCases = await testCasesApi.listTestCases();
  setTestCases(testCases);
} catch (error) {
  setError(error.message);
}
```

## Adding New API Handlers

1. Create new file in `src/api/resource.ts`
2. Import `apiClient` from `./client`
3. Create handler class with async methods
4. Export instance: `export const resourceApi = new ResourceApi()`
5. Add to `index.ts` exports
6. Add hooks to `hooks.ts` if needed

Template:
```typescript
import { apiClient } from './client';

class ResourceApi {
  async getAll(): Promise<Resource[]> {
    return await apiClient.get<Resource[]>('/resources');
  }

  async create(data: ResourceCreate): Promise<Resource> {
    return await apiClient.post<Resource>('/resources', data);
  }
}

export const resourceApi = new ResourceApi();
```
