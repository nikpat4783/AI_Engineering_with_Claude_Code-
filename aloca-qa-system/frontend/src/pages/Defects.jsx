import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export default function Defects() {
  const [defects, setDefects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    severity: 'medium',
    assigned_to: '',
  });

  useEffect(() => {
    fetchDefects();
  }, [statusFilter, severityFilter]);

  const fetchDefects = async () => {
    try {
      setLoading(true);
      let url = `${API_BASE}/defects`;
      const params = [];
      if (statusFilter) params.push(`status=${statusFilter}`);
      if (severityFilter) params.push(`severity=${severityFilter}`);
      if (params.length) url += '?' + params.join('&');

      const response = await axios.get(url);
      setDefects(response.data);
    } catch (err) {
      console.error('Error fetching defects:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddDefect = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/defects`, formData);
      setFormData({ title: '', description: '', severity: 'medium', assigned_to: '' });
      setShowModal(false);
      fetchDefects();
    } catch (err) {
      alert('Error creating defect: ' + err.message);
    }
  };

  const handleUpdateStatus = async (defectId, newStatus) => {
    try {
      await axios.patch(`${API_BASE}/defects/${defectId}`, {
        status: newStatus,
      });
      fetchDefects();
    } catch (err) {
      alert('Error updating defect: ' + err.message);
    }
  };

  const getSeverityStats = () => {
    const critical = defects.filter(d => d.severity === 'critical').length;
    const high = defects.filter(d => d.severity === 'high').length;
    const medium = defects.filter(d => d.severity === 'medium').length;
    const low = defects.filter(d => d.severity === 'low').length;
    return { critical, high, medium, low };
  };

  const getStatusStats = () => {
    const open = defects.filter(d => d.status === 'open').length;
    const inProgress = defects.filter(d => d.status === 'in_progress').length;
    const resolved = defects.filter(d => d.status === 'resolved').length;
    const closed = defects.filter(d => d.status === 'closed').length;
    return { open, inProgress, resolved, closed };
  };

  const stats = getSeverityStats();
  const statusStats = getStatusStats();

  if (loading) return <div className="spinner"></div>;

  return (
    <div>
      {/* Stats Cards */}
      <div className="dashboard-grid">
        <div className="stat-card critical">
          <div className="stat-label">Critical Defects</div>
          <div className="stat-value">{stats.critical}</div>
        </div>
        <div className="stat-card warning">
          <div className="stat-label">High Priority</div>
          <div className="stat-value">{stats.high}</div>
        </div>
        <div className="stat-card error">
          <div className="stat-label">Open Defects</div>
          <div className="stat-value">{statusStats.open}</div>
        </div>
        <div className="stat-card success">
          <div className="stat-label">Resolved</div>
          <div className="stat-value">{statusStats.resolved}</div>
        </div>
      </div>

      {/* Filters and Actions */}
      <div style={{ marginBottom: '24px', display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
        <select
          className="form-control"
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          style={{ maxWidth: '150px' }}
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        <select
          className="form-control"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ maxWidth: '150px' }}
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>

        <button className="btn btn-primary" onClick={() => setShowModal(true)} style={{ marginLeft: 'auto' }}>
          + New Defect
        </button>
      </div>

      {/* Defects Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">Defects ({defects.length})</div>
        </div>
        <div className="card-body">
          {defects.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">✓</div>
              <div className="empty-state-title">No defects found</div>
              <p>Great! No matching defects with current filters</p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Assigned To</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {defects.map(defect => (
                  <tr key={defect.id}>
                    <td>
                      <div>
                        <strong>{defect.title}</strong>
                        <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                          {defect.description.substring(0, 50)}...
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${defect.severity}`}>
                        {defect.severity}
                      </span>
                    </td>
                    <td>
                      <select
                        className="form-control"
                        value={defect.status}
                        onChange={(e) => handleUpdateStatus(defect.id, e.target.value)}
                        style={{ width: '120px', padding: '6px' }}
                      >
                        <option value="open">Open</option>
                        <option value="in_progress">In Progress</option>
                        <option value="resolved">Resolved</option>
                        <option value="closed">Closed</option>
                      </select>
                    </td>
                    <td>{defect.assigned_to || '-'}</td>
                    <td style={{ fontSize: '12px', color: '#6b7280' }}>
                      {new Date(defect.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <button className="btn btn-sm btn-secondary">
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* New Defect Modal */}
      <div className={`modal ${showModal ? 'show' : ''}`}>
        <div className="modal-content">
          <div className="modal-header">New Defect</div>
          <form onSubmit={handleAddDefect}>
            <div className="form-group">
              <label className="form-label">Title *</label>
              <input
                type="text"
                className="form-control"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
                placeholder="Brief title of the defect"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Description *</label>
              <textarea
                className="form-control"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows="4"
                required
                placeholder="Detailed description of the issue"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Severity *</label>
              <select
                className="form-control"
                value={formData.severity}
                onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
              >
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Assign To</label>
              <input
                type="text"
                className="form-control"
                value={formData.assigned_to}
                onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
                placeholder="Team member name"
              />
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                Create Defect
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
