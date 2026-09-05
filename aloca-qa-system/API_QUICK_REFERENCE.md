# API Quick Reference - Async/Await Handlers

**Location**: `frontend/src/api/`

---

## 🚀 Quick Start

### Import Everything
```typescript
import { dashboardApi, testCasesApi, defectsApi } from './api';
import { useDashboardStats, useDefects } from './api/hooks';
```

### Make API Calls
```typescript
// Dashboard
const stats = await dashboardApi.getStats();
const metrics = await dashboardApi.getMetrics(7);

// Test Cases
const testCases = await testCasesApi.listTestCases();
const result = await testCasesApi.createTestResult({...});

// Defects
const critical = await defectsApi.getCriticalDefects();
const updated = await defectsApi.updateDefect(id, {...});
```

### Use in React Components
```typescript
function MyComponent() {
  const { value: stats, status, error } = useDashboardStats();
  
  if (status === 'pending') return <Loading />;
  if (error) return <Error />;
  return <StatsDisplay {...stats} />;
}
```

---

## 📚 API Handlers

### Dashboard API
| Method | Signature | Returns |
|--------|-----------|---------|
| `getStats()` | `async () => Promise<DashboardStats>` | Dashboard stats |
| `getMetrics(days)` | `async (days?: number) => Promise<QualityMetric[]>` | Historical metrics |
| `generateMetrics()` | `async () => Promise<QualityMetric>` | New metric snapshot |
| `getHealthStatus()` | `async () => Promise<{status: string}>` | Server health |

### Test Cases API
| Method | Signature | Returns |
|--------|-----------|---------|
| `createTestCase(data)` | `async (data: TestCaseCreate) => Promise<TestCase>` | Created test case |
| `listTestCases(module?)` | `async (module?: string) => Promise<TestCase[]>` | All test cases |
| `getTestCase(id)` | `async (id: string) => Promise<TestCase>` | Single test case |
| `createTestResult(data)` | `async (data: TestResultCreate) => Promise<TestResult>` | Test result |
| `listTestResults(testCaseId?)` | `async (testCaseId?: string) => Promise<TestResult[]>` | Results |
| `searchTestCases(query)` | `async (query: string) => Promise<TestCase[]>` | Search results |
| `getTestCaseWithResults(id)` | `async (id: string) => Promise<{...}>` | Test case + results |

### Defects API
| Method | Signature | Returns |
|--------|-----------|---------|
| `createDefect(data)` | `async (data: DefectCreate) => Promise<Defect>` | Created defect |
| `listDefects(status?, severity?)` | `async (status?: string, severity?: string) => Promise<Defect[]>` | Filtered defects |
| `getDefect(id)` | `async (id: string) => Promise<Defect>` | Single defect |
| `updateDefect(id, data)` | `async (id: string, data: DefectUpdate) => Promise<Defect>` | Updated defect |
| `updateDefectStatus(id, status)` | `async (id: string, status: string) => Promise<Defect>` | Status updated |
| `assignDefect(id, assignee)` | `async (id: string, assignee: string) => Promise<Defect>` | Assigned |
| `getCriticalDefects()` | `async () => Promise<Defect[]>` | Critical only |
| `getOpenDefects()` | `async () => Promise<Defect[]>` | Open only |
| `getDefectStats(defects)` | `async (defects: Defect[]) => Promise<DefectStats>` | Stats |

---

## 🪝 React Hooks

### Auto-Fetch Hooks
```typescript
// Fetch automatically on mount
const { value: stats, status, error } = useDashboardStats();
const { value: metrics } = useMetrics(7);
const { value: testCases } = useTestCases('Auth');
const { value: defects } = useDefects('open', 'critical');
const { value: critical } = useCriticalDefects();
const { value: open } = useOpenDefects();
```

### Manual-Execute Hooks
```typescript
// Execute when needed
const { execute: create, status } = useCreateTestCase();
await create({ name, description, module });

const { execute: createResult, status } = useCreateTestResult();
await createResult({ test_case_id, status, execution_time_ms });

const { execute: createDefect, status } = useCreateDefect();
await createDefect({ title, description, severity });

const { execute: update, status } = useUpdateDefect(defectId);
await update({ status: 'resolved' });
```

### Return Type
```typescript
{
  execute?: async (params?) => Promise<T>,  // Manual execution
  status: 'idle' | 'pending' | 'success' | 'error',
  value?: T | null,                         // Data (if auto-fetch)
  error: Error | null
}
```

---

## 🎯 Common Patterns

### Pattern 1: Load Data on Mount
```typescript
function Dashboard() {
  const { value: stats } = useDashboardStats();
  return <div>{stats?.total_test_cases}</div>;
}
```

### Pattern 2: Handle Create with Loading
```typescript
function CreateTestCase() {
  const { execute: create, status } = useCreateTestCase();
  
  const handleSubmit = async (data) => {
    await create(data);
    // Refresh list, show toast, etc.
  };
  
  return (
    <button onClick={handleSubmit} disabled={status === 'pending'}>
      {status === 'pending' ? 'Creating...' : 'Create'}
    </button>
  );
}
```

### Pattern 3: Parallel Requests
```typescript
const [stats, metrics] = await Promise.all([
  dashboardApi.getStats(),
  dashboardApi.getMetrics(7),
]);
```

### Pattern 4: Error Handling
```typescript
try {
  const result = await testCasesApi.createTestCase(data);
} catch (error) {
  console.error('Create failed:', error.message);
  setError(error.message);
}
```

### Pattern 5: Conditional Fetching
```typescript
const { value: results } = useTestResults(
  testCaseId ? testCaseId : undefined
);
// Only fetches if testCaseId exists
```

---

## 📦 Types

### Import Types
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

### Usage
```typescript
function MyComponent(props: { testCase: TestCase }) {
  return <div>{props.testCase.name}</div>;
}

async function createTC(data: TestCaseCreate) {
  const result = await testCasesApi.createTestCase(data);
  const tc: TestCase = result;
}
```

---

## 🔐 Error Handling

### Try/Catch Pattern
```typescript
try {
  const data = await dashboardApi.getStats();
  setStats(data);
} catch (error) {
  setError(error.message); // Generic message
  console.error(error);    // Full error to console
}
```

### Hook Error State
```typescript
const { value, error, status } = useDashboardStats();

if (status === 'error') {
  return <ErrorMessage message={error?.message} />;
}
```

---

## 🔌 Authentication

### Set Token
```typescript
import { apiClient } from './api/client';
apiClient.setAuthToken('jwt-token-here');
```

### Clear Token
```typescript
apiClient.clearAuthToken();
```

---

## ✨ Client Features

### Base HTTP Client (`client.ts`)
```typescript
import { apiClient } from './api/client';

// GET
const data = await apiClient.get('/endpoint', { param: 'value' });

// POST
const result = await apiClient.post('/endpoint', { field: 'value' });

// PATCH
const updated = await apiClient.patch('/endpoint/id', { field: 'new' });

// DELETE
await apiClient.delete('/endpoint/id');
```

---

## 📖 Documentation

See `frontend/src/api/README.md` for:
- Complete API reference
- Advanced patterns
- Testing examples
- Migration guide
- Best practices

---

## 🔄 All Async/Await

✅ No `.then()` chains  
✅ No callback hell  
✅ Consistent error handling  
✅ Type-safe  
✅ Easy to test  
✅ Easy to mock  

---

**Ready to use! 🚀**
