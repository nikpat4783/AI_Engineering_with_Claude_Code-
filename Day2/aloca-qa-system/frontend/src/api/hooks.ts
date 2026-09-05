import { useState, useEffect, useCallback } from 'react';
import { dashboardApi, testCasesApi, defectsApi, searchApi } from './index';
import type {
  DashboardStats,
  QualityMetric,
  TestCase,
  TestResult,
  Defect,
  DefectStats,
  SearchResponse,
} from './index';

// Generic async data hook
export function useAsync<T>(
  asyncFunction: () => Promise<T>,
  immediate = true
) {
  const [status, setStatus] = useState<'idle' | 'pending' | 'success' | 'error'>('idle');
  const [value, setValue] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async () => {
    setStatus('pending');
    setValue(null);
    setError(null);

    try {
      const response = await asyncFunction();
      setValue(response);
      setStatus('success');
      return response;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
      setStatus('error');
      throw err;
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { execute, status, value, error };
}

// Dashboard hooks
export function useDashboardStats() {
  return useAsync(async () => await dashboardApi.getStats());
}

export function useMetrics(days = 7) {
  return useAsync(async () => await dashboardApi.getMetrics(days));
}

export function useHealthStatus() {
  return useAsync(async () => await dashboardApi.getHealthStatus(), false);
}

// Test Cases hooks
export function useTestCases(module?: string) {
  return useAsync(async () => await testCasesApi.listTestCases(module));
}

export function useTestCase(testCaseId: string) {
  return useAsync(
    async () => await testCasesApi.getTestCase(testCaseId),
    !!testCaseId
  );
}

export function useTestResults(testCaseId?: string) {
  return useAsync(
    async () => await testCasesApi.listTestResults(testCaseId),
    !!testCaseId
  );
}

export function useCreateTestCase() {
  const [status, setStatus] = useState<'idle' | 'pending' | 'success' | 'error'>('idle');
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async (data: any) => {
    setStatus('pending');
    setError(null);

    try {
      const result = await testCasesApi.createTestCase(data);
      setStatus('success');
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to create test case');
      setError(error);
      setStatus('error');
      throw error;
    }
  }, []);

  return { execute, status, error };
}

export function useCreateTestResult() {
  const [status, setStatus] = useState<'idle' | 'pending' | 'success' | 'error'>('idle');
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async (data: any) => {
    setStatus('pending');
    setError(null);

    try {
      const result = await testCasesApi.createTestResult(data);
      setStatus('success');
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to create test result');
      setError(error);
      setStatus('error');
      throw error;
    }
  }, []);

  return { execute, status, error };
}

// Defects hooks
export function useDefects(status?: string, severity?: string) {
  return useAsync(async () => await defectsApi.listDefects(status, severity));
}

export function useDefect(defectId: string) {
  return useAsync(
    async () => await defectsApi.getDefect(defectId),
    !!defectId
  );
}

export function useCriticalDefects() {
  return useAsync(async () => await defectsApi.getCriticalDefects());
}

export function useOpenDefects() {
  return useAsync(async () => await defectsApi.getOpenDefects());
}

export function useCreateDefect() {
  const [status, setStatus] = useState<'idle' | 'pending' | 'success' | 'error'>('idle');
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async (data: any) => {
    setStatus('pending');
    setError(null);

    try {
      const result = await defectsApi.createDefect(data);
      setStatus('success');
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to create defect');
      setError(error);
      setStatus('error');
      throw error;
    }
  }, []);

  return { execute, status, error };
}

export function useUpdateDefect(defectId: string) {
  const [status, setStatus] = useState<'idle' | 'pending' | 'success' | 'error'>('idle');
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async (data: any) => {
    setStatus('pending');
    setError(null);

    try {
      const result = await defectsApi.updateDefect(defectId, data);
      setStatus('success');
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update defect');
      setError(error);
      setStatus('error');
      throw error;
    }
  }, [defectId]);

  return { execute, status, error };
}

export function useDefectStats(defects: Defect[]) {
  const [stats, setStats] = useState<DefectStats | null>(null);

  useEffect(() => {
    (async () => {
      const stats = await defectsApi.getDefectStats(defects);
      setStats(stats);
    })();
  }, [defects]);

  return stats;
}

// Search hooks
export function useSearch() {
  const [status, setStatus] = useState<'idle' | 'pending' | 'success' | 'error'>('idle');
  const [value, setValue] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async (query: string) => {
    setStatus('pending');
    setError(null);
    try {
      const result = await searchApi.search(query);
      setValue(result);
      setStatus('success');
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Search failed');
      setError(error);
      setStatus('error');
      throw error;
    }
  }, []);

  return { execute, status, value, error };
}
