import { apiClient } from './client';

export interface Defect {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  test_case_id?: string;
  assigned_to?: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
}

export interface DefectCreate {
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  test_case_id?: string;
  assigned_to?: string;
}

export interface DefectUpdate {
  status?: 'open' | 'in_progress' | 'resolved' | 'closed';
  assigned_to?: string;
  description?: string;
}

export interface DefectStats {
  critical: number;
  high: number;
  medium: number;
  low: number;
  open: number;
  inProgress: number;
  resolved: number;
  closed: number;
}

class DefectsApi {
  async createDefect(defect: DefectCreate): Promise<Defect> {
    return await apiClient.post<Defect>('/defects', defect);
  }

  async listDefects(
    status?: string,
    severity?: string
  ): Promise<Defect[]> {
    const params: Record<string, string> = {};
    if (status) params.status = status;
    if (severity) params.severity = severity;

    return await apiClient.get<Defect[]>('/defects', params);
  }

  async getDefect(defectId: string): Promise<Defect> {
    return await apiClient.get<Defect>(`/defects/${defectId}`);
  }

  async updateDefect(defectId: string, update: DefectUpdate): Promise<Defect> {
    return await apiClient.patch<Defect>(`/defects/${defectId}`, update);
  }

  async updateDefectStatus(
    defectId: string,
    status: Defect['status']
  ): Promise<Defect> {
    return await this.updateDefect(defectId, { status });
  }

  async assignDefect(defectId: string, assignee: string): Promise<Defect> {
    return await this.updateDefect(defectId, { assigned_to: assignee });
  }

  async getDefectStats(defects: Defect[]): Promise<DefectStats> {
    const stats: DefectStats = {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      open: 0,
      inProgress: 0,
      resolved: 0,
      closed: 0,
    };

    defects.forEach(d => {
      stats[d.severity as keyof DefectStats]++;
      const statusKey = d.status.replace('_', '') as keyof DefectStats;
      if (statusKey in stats) {
        stats[statusKey]++;
      }
    });

    return stats;
  }

  async getDefectsBySeverity(severity: Defect['severity']): Promise<Defect[]> {
    return await this.listDefects(undefined, severity);
  }

  async getDefectsByStatus(status: Defect['status']): Promise<Defect[]> {
    return await this.listDefects(status);
  }

  async getCriticalDefects(): Promise<Defect[]> {
    return await this.getDefectsBySeverity('critical');
  }

  async getOpenDefects(): Promise<Defect[]> {
    return await this.getDefectsByStatus('open');
  }
}

export const defectsApi = new DefectsApi();
export default DefectsApi;
