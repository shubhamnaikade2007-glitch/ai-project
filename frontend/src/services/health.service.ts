// HealthFit AI - Health Metrics Service
import api from './api';
import { HealthMetric, OrganHealthScore, HealthSummary } from '../types';

const HealthService = {
  async getMetrics(params?: { metric_type?: string; days?: number; limit?: number }) {
    const { data } = await api.get<{ metrics: HealthMetric[]; count: number }>('/health/metrics', { params });
    return data;
  },

  async addMetric(payload: {
    metric_type: string; value: number;
    unit?: string; source?: string; notes?: string; recorded_at?: string;
  }) {
    const { data } = await api.post<{ metric: HealthMetric; message: string }>('/health/metrics', payload);
    return data;
  },

  async addMetricsBatch(metrics: Array<{ metric_type: string; value: number; unit?: string; source?: string }>) {
    const { data } = await api.post<{ added: number; errors: any[] }>('/health/metrics/batch', { metrics });
    return data;
  },

  async getLatestMetrics() {
    const { data } = await api.get<{ latest: Record<string, HealthMetric> }>('/health/metrics/latest');
    return data;
  },

  async deleteMetric(id: number): Promise<void> {
    await api.delete(`/health/metrics/${id}`);
  },

  async getOrganScores() {
    const { data } = await api.get<{ scores: OrganHealthScore[] }>('/health/organ-scores');
    return data;
  },

  async getHealthSummary(days?: number) {
    const { data } = await api.get<HealthSummary>('/health/summary', { params: { days } });
    return data;
  },

  async getTrend(metricType: string, days?: number) {
    const { data } = await api.get<{
      metric_type: string; unit: string;
      normal_range: { min: number | null; max: number | null };
      data: Array<{ date: string; value: number; status: string }>;
      count: number;
    }>(`/health/trends/${metricType}`, { params: { days } });
    return data;
  },
};

export default HealthService;
