import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const API_BASE = 'http://localhost:8000';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, metricsRes] = await Promise.all([
        axios.get(`${API_BASE}/dashboard/stats`),
        axios.get(`${API_BASE}/metrics?days=7`)
      ]);
      setStats(statsRes.data);
      setMetrics(metricsRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="spinner"></div>;
  }

  if (error) {
    return <div style={{ color: 'red', padding: '20px' }}>{error}</div>;
  }

  const testStatusData = [
    { name: 'Passed', value: stats?.tests_passed_today || 0, color: '#16a34a' },
    { name: 'Failed', value: stats?.tests_failed_today || 0, color: '#dc2626' },
    { name: 'Blocked', value: stats?.tests_blocked_today || 0, color: '#ea8c00' },
  ];

  const chartData = metrics.slice().reverse().map(m => ({
    date: new Date(m.date).toLocaleDateString(),
    passRate: parseFloat(m.pass_rate.toFixed(2)),
    passed: m.passed_tests,
    failed: m.failed_tests,
  }));

  return (
    <div>
      <div className="dashboard-grid">
        <div className="stat-card">
          <div className="stat-label">Total Test Cases</div>
          <div className="stat-value">{stats?.total_test_cases || 0}</div>
          <div className="stat-sublabel">Active test cases</div>
        </div>

        <div className="stat-card success">
          <div className="stat-label">Pass Rate</div>
          <div className="stat-value">{stats?.pass_rate || 0}%</div>
          <div className="stat-sublabel">Overall quality metric</div>
        </div>

        <div className="stat-card critical">
          <div className="stat-label">Critical Defects</div>
          <div className="stat-value">{stats?.critical_defects || 0}</div>
          <div className="stat-sublabel">Require immediate action</div>
        </div>

        <div className="stat-card error">
          <div className="stat-label">Total Defects</div>
          <div className="stat-value">{stats?.total_defects || 0}</div>
          <div className="stat-sublabel">All open issues</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px', marginBottom: '24px' }}>
        {/* Today's Test Results */}
        <div className="chart-container">
          <div className="chart-title">Today's Test Results</div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={testStatusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {testStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* 7-Day Pass Rate Trend */}
        <div className="chart-container">
          <div className="chart-title">7-Day Pass Rate Trend</div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value) => `${value}%`} />
              <Line type="monotone" dataKey="passRate" stroke="#0066cc" strokeWidth={2} dot={{ fill: '#0066cc' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Test Results Over Time */}
      <div className="chart-container">
        <div className="chart-title">Test Results Over Time (7 Days)</div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="passed" fill="#16a34a" />
            <Bar dataKey="failed" fill="#dc2626" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">Quick Stats Summary</div>
        </div>
        <div className="card-body">
          <table className="table">
            <tbody>
              <tr>
                <td><strong>Today's Passed Tests:</strong></td>
                <td><span className="badge passed">{stats?.tests_passed_today || 0}</span></td>
              </tr>
              <tr>
                <td><strong>Today's Failed Tests:</strong></td>
                <td><span className="badge failed">{stats?.tests_failed_today || 0}</span></td>
              </tr>
              <tr>
                <td><strong>Today's Blocked Tests:</strong></td>
                <td><span className="badge blocked">{stats?.tests_blocked_today || 0}</span></td>
              </tr>
              <tr>
                <td><strong>Overall Pass Rate:</strong></td>
                <td><strong>{stats?.pass_rate || 0}%</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
