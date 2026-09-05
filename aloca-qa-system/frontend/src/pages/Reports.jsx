import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';

const API_BASE = 'http://localhost:8000';

export default function Reports() {
  const [metrics, setMetrics] = useState([]);
  const [testCases, setTestCases] = useState([]);
  const [defects, setDefects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reportType, setReportType] = useState('summary');

  useEffect(() => {
    fetchReportData();
  }, []);

  const fetchReportData = async () => {
    try {
      setLoading(true);
      const [metricsRes, testCasesRes, defectsRes] = await Promise.all([
        axios.get(`${API_BASE}/metrics?days=30`),
        axios.get(`${API_BASE}/test-cases`),
        axios.get(`${API_BASE}/defects`),
      ]);
      setMetrics(metricsRes.data);
      setTestCases(testCasesRes.data);
      setDefects(defectsRes.data);
    } catch (err) {
      console.error('Error fetching report data:', err);
    } finally {
      setLoading(false);
    }
  };

  const generatePDFReport = () => {
    const content = generateReportContent();
    alert('Report generation would export to PDF:\n\n' + content.substring(0, 200) + '...');
  };

  const generateExcelReport = () => {
    const content = generateReportContent();
    alert('Report generation would export to Excel:\n\n' + content.substring(0, 200) + '...');
  };

  const downloadTxtReport = () => {
    const content = generateReportContent();
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `aloca-qa-report-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const generateReportContent = () => {
    const totalTests = testCases.length;
    const totalDefects = defects.length;
    const criticalDefects = defects.filter(d => d.severity === 'critical').length;
    const avgPassRate = metrics.length > 0
      ? (metrics.reduce((sum, m) => sum + m.pass_rate, 0) / metrics.length).toFixed(2)
      : 0;

    return `ALOCA+ QA System Report
Generated: ${new Date().toLocaleString()}

SUMMARY
-------
Total Test Cases: ${totalTests}
Total Defects: ${totalDefects}
Critical Defects: ${criticalDefects}
Average Pass Rate: ${avgPassRate}%

METRICS (Last 30 Days)
---------------------
${metrics.map(m => `${new Date(m.date).toDateString()}: ${m.pass_rate.toFixed(2)}% pass rate, ${m.passed_tests} passed, ${m.failed_tests} failed`).join('\n')}`;
  };

  if (loading) return <div className="spinner"></div>;

  const chartData = metrics.slice().reverse().map(m => ({
    date: new Date(m.date).toLocaleDateString(),
    passRate: parseFloat(m.pass_rate.toFixed(2)),
    defectsOpen: m.defects_open,
    defectsCritical: m.defects_critical,
  }));

  const moduleStats = testCases.reduce((acc, tc) => {
    const existing = acc.find(m => m.name === tc.module);
    if (existing) {
      existing.count++;
    } else {
      acc.push({ name: tc.module, count: 1 });
    }
    return acc;
  }, []);

  const severityStats = [
    { name: 'Critical', value: defects.filter(d => d.severity === 'critical').length },
    { name: 'High', value: defects.filter(d => d.severity === 'high').length },
    { name: 'Medium', value: defects.filter(d => d.severity === 'medium').length },
    { name: 'Low', value: defects.filter(d => d.severity === 'low').length },
  ];

  const statusStats = [
    { name: 'Open', value: defects.filter(d => d.status === 'open').length },
    { name: 'In Progress', value: defects.filter(d => d.status === 'in_progress').length },
    { name: 'Resolved', value: defects.filter(d => d.status === 'resolved').length },
    { name: 'Closed', value: defects.filter(d => d.status === 'closed').length },
  ];

  return (
    <div>
      {/* Report Controls */}
      <div style={{ marginBottom: '24px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        <select
          className="form-control"
          value={reportType}
          onChange={(e) => setReportType(e.target.value)}
          style={{ maxWidth: '200px' }}
        >
          <option value="summary">Summary Report</option>
          <option value="detailed">Detailed Report</option>
          <option value="trend">Trend Report</option>
          <option value="defect">Defect Report</option>
        </select>
        <button className="btn btn-primary" onClick={generatePDFReport}>
          📄 Export PDF
        </button>
        <button className="btn btn-primary" onClick={generateExcelReport}>
          📊 Export Excel
        </button>
        <button className="btn btn-primary" onClick={downloadTxtReport}>
          📥 Download TXT
        </button>
      </div>

      {/* Summary Stats */}
      <div className="dashboard-grid">
        <div className="stat-card">
          <div className="stat-label">Total Test Cases</div>
          <div className="stat-value">{testCases.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Defects</div>
          <div className="stat-value">{defects.length}</div>
        </div>
        <div className="stat-card critical">
          <div className="stat-label">Critical Issues</div>
          <div className="stat-value">{defects.filter(d => d.severity === 'critical').length}</div>
        </div>
        <div className="stat-card success">
          <div className="stat-label">Avg Pass Rate</div>
          <div className="stat-value">
            {metrics.length > 0
              ? (metrics.reduce((sum, m) => sum + m.pass_rate, 0) / metrics.length).toFixed(1)
              : 0}%
          </div>
        </div>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '24px' }}>
        {/* 30-Day Pass Rate */}
        <div className="chart-container">
          <div className="chart-title">30-Day Pass Rate Trend</div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip formatter={(value) => `${value}%`} />
              <Line type="monotone" dataKey="passRate" stroke="#0066cc" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Defect Trend */}
        <div className="chart-container">
          <div className="chart-title">Defect Trend (30 Days)</div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="defectsOpen" fill="#dc2626" name="Open" />
              <Bar dataKey="defectsCritical" fill="#9c0a1b" name="Critical" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Test Cases by Module */}
        <div className="chart-container">
          <div className="chart-title">Test Cases by Module</div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={moduleStats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0066cc" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Defects by Severity */}
        <div className="chart-container">
          <div className="chart-title">Defects by Severity</div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={severityStats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#ea8c00" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Defects by Status */}
        <div className="chart-container">
          <div className="chart-title">Defects by Status</div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statusStats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#16a34a" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Quality Score Card */}
        <div className="chart-container">
          <div className="chart-title">Quality Metrics Summary</div>
          <div style={{ padding: '20px' }}>
            <table className="table" style={{ marginBottom: 0 }}>
              <tbody>
                <tr>
                  <td><strong>Test Modules:</strong></td>
                  <td>{moduleStats.length}</td>
                </tr>
                <tr>
                  <td><strong>Total Test Cases:</strong></td>
                  <td>{testCases.length}</td>
                </tr>
                <tr>
                  <td><strong>Critical Defects:</strong></td>
                  <td><span className="badge critical">{defects.filter(d => d.severity === 'critical').length}</span></td>
                </tr>
                <tr>
                  <td><strong>Open Issues:</strong></td>
                  <td><span className="badge error">{defects.filter(d => d.status === 'open').length}</span></td>
                </tr>
                <tr>
                  <td><strong>Resolved Issues:</strong></td>
                  <td><span className="badge success">{defects.filter(d => d.status === 'resolved').length}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Detailed Report Section */}
      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <div className="card-title">Report Summary</div>
        </div>
        <div className="card-body">
          <div style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '12px', backgroundColor: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
            {generateReportContent()}
          </div>
        </div>
      </div>
    </div>
  );
}
