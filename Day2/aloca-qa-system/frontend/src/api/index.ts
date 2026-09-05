// Central export for all API handlers
// Use: import { dashboardApi, testCasesApi, defectsApi } from './api'

export { apiClient, default as ApiClient } from './client';
export type { default as ApiClient } from './client';

export { dashboardApi, default as DashboardApi } from './dashboard';
export type { DashboardStats, QualityMetric } from './dashboard';

export { testCasesApi, default as TestCasesApi } from './testCases';
export type {
  TestCase,
  TestCaseCreate,
  TestResult,
  TestResultCreate,
} from './testCases';

export { defectsApi, default as DefectsApi } from './defects';
export type { Defect, DefectCreate, DefectUpdate, DefectStats } from './defects';

export { searchApi, default as SearchApi } from './search';
export type { SearchResultItem, SearchResponse } from './search';

// Convenience batch imports
export const api = {
  dashboard: dashboardApi,
  testCases: testCasesApi,
  defects: defectsApi,
  search: searchApi,
};

export default api;
