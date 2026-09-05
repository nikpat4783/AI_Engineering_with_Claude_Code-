import { apiClient } from './client';

export interface TestCase {
  id: string;
  name: string;
  description: string;
  module: string;
  created_at: string;
  updated_at: string;
}

export interface TestCaseCreate {
  name: string;
  description: string;
  module: string;
}

export interface TestResult {
  id: string;
  test_case_id: string;
  status: 'passed' | 'failed' | 'blocked' | 'pending';
  executed_at: string;
  execution_time_ms: number;
  notes?: string;
}

export interface TestResultCreate {
  test_case_id: string;
  status: 'passed' | 'failed' | 'blocked' | 'pending';
  execution_time_ms: number;
  notes?: string;
}

class TestCasesApi {
  async createTestCase(testCase: TestCaseCreate): Promise<TestCase> {
    return await apiClient.post<TestCase>('/test-cases', testCase);
  }

  async listTestCases(module?: string): Promise<TestCase[]> {
    return await apiClient.get<TestCase[]>('/test-cases', module ? { module } : {});
  }

  async getTestCase(testCaseId: string): Promise<TestCase> {
    return await apiClient.get<TestCase>(`/test-cases/${testCaseId}`);
  }

  async createTestResult(result: TestResultCreate): Promise<TestResult> {
    return await apiClient.post<TestResult>('/test-results', result);
  }

  async listTestResults(testCaseId?: string): Promise<TestResult[]> {
    return await apiClient.get<TestResult[]>('/test-results',
      testCaseId ? { test_case_id: testCaseId } : {}
    );
  }

  async searchTestCases(query: string): Promise<TestCase[]> {
    const testCases = await this.listTestCases();
    return testCases.filter(tc =>
      tc.name.toLowerCase().includes(query.toLowerCase()) ||
      tc.module.toLowerCase().includes(query.toLowerCase())
    );
  }

  async getTestCaseWithResults(testCaseId: string): Promise<{
    testCase: TestCase;
    results: TestResult[];
  }> {
    const [testCase, results] = await Promise.all([
      this.getTestCase(testCaseId),
      this.listTestResults(testCaseId),
    ]);
    return { testCase, results };
  }
}

export const testCasesApi = new TestCasesApi();
export default TestCasesApi;
