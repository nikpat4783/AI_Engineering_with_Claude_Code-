import { apiClient } from './client';

export interface DashboardStats {
  total_test_cases: number;
  total_defects: number;
  pass_rate: number;
  critical_defects: number;
  tests_passed_today: number;
  tests_failed_today: number;
  tests_blocked_today: number;
}

export interface QualityMetric {
  id: string;
  date: string;
  total_test_cases: number;
  passed_tests: number;
  failed_tests: number;
  blocked_tests: number;
  pending_tests: number;
  pass_rate: number;
  defects_open: number;
  defects_critical: number;
  defects_high: number;
}

class DashboardApi {
  async getStats(): Promise<DashboardStats> {
    return await apiClient.get<DashboardStats>('/dashboard/stats');
  }

  async getMetrics(days: number = 7): Promise<QualityMetric[]> {
    return await apiClient.get<QualityMetric[]>('/metrics', { days });
  }

  async generateMetrics(): Promise<QualityMetric> {
    return await apiClient.post<QualityMetric>('/metrics/generate');
  }

  async getHealthStatus(): Promise<{ status: string }> {
    return await apiClient.get('/health');
  }
}

export const dashboardApi = new DashboardApi();
export default DashboardApi;
