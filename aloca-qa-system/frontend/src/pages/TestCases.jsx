import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export default function TestCases() {
  const [testCases, setTestCases] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showResultModal, setShowResultModal] = useState(false);
  const [selectedTestCase, setSelectedTestCase] = useState(null);
  const [filter, setFilter] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    module: '',
  });

  const [resultData, setResultData] = useState({
    status: 'pending',
    execution_time_ms: 0,
    notes: '',
  });

  useEffect(() => {
    fetchTestCases();
    fetchResults();
  }, []);

  const fetchTestCases = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/test-cases`);
      setTestCases(response.data);
    } catch (err) {
      console.error('Error fetching test cases:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchResults = async () => {
    try {
      const response = await axios.get(`${API_BASE}/test-results`);
      setResults(response.data);
    } catch (err) {
      console.error('Error fetching results:', err);
    }
  };

  const handleAddTestCase = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/test-cases`, formData);
      setFormData({ name: '', description: '', module: '' });
      setShowModal(false);
      fetchTestCases();
    } catch (err) {
      alert('Error creating test case: ' + err.response?.data?.detail || err.message);
    }
  };

  const handleAddResult = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/test-results`, {
        test_case_id: selectedTestCase.id,
        ...resultData,
      });
      setResultData({ status: 'pending', execution_time_ms: 0, notes: '' });
      setShowResultModal(false);
      setSelectedTestCase(null);
      fetchResults();
    } catch (err) {
      alert('Error creating test result: ' + err.message);
    }
  };

  const openResultModal = (testCase) => {
    setSelectedTestCase(testCase);
    setShowResultModal(true);
  };

  const getRecentResult = (testCaseId) => {
    return results.find(r => r.test_case_id === testCaseId);
  };

  const filteredTestCases = testCases.filter(tc =>
    tc.name.toLowerCase().includes(filter.toLowerCase()) ||
    tc.module.toLowerCase().includes(filter.toLowerCase())
  );

  if (loading) return <div className="spinner"></div>;

  return (
    <div>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px' }}>
        <input
          type="text"
          placeholder="Search test cases..."
          className="form-control"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{ maxWidth: '300px' }}
        />
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + New Test Case
        </button>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">Test Cases ({filteredTestCases.length})</div>
        </div>
        <div className="card-body">
          {filteredTestCases.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📋</div>
              <div className="empty-state-title">No test cases found</div>
              <p>Create your first test case to get started</p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Test Case Name</th>
                  <th>Module</th>
                  <th>Description</th>
                  <th>Last Result</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredTestCases.map(tc => {
                  const lastResult = getRecentResult(tc.id);
                  return (
                    <tr key={tc.id}>
                      <td><strong>{tc.name}</strong></td>
                      <td>{tc.module}</td>
                      <td>{tc.description.substring(0, 50)}...</td>
                      <td>
                        {lastResult ? (
                          <span className={`badge ${lastResult.status}`}>
                            {lastResult.status}
                          </span>
                        ) : (
                          <span className="badge pending">No result</span>
                        )}
                      </td>
                      <td>
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => openResultModal(tc)}
                        >
                          + Add Result
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Add Test Case Modal */}
      <div className={`modal ${showModal ? 'show' : ''}`}>
        <div className="modal-content">
          <div className="modal-header">New Test Case</div>
          <form onSubmit={handleAddTestCase}>
            <div className="form-group">
              <label className="form-label">Test Case Name *</label>
              <input
                type="text"
                className="form-control"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Module *</label>
              <input
                type="text"
                className="form-control"
                value={formData.module}
                onChange={(e) => setFormData({ ...formData, module: e.target.value })}
                placeholder="e.g., Authentication, Payment"
                required
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
              />
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                Create Test Case
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Add Result Modal */}
      <div className={`modal ${showResultModal ? 'show' : ''}`}>
        <div className="modal-content">
          <div className="modal-header">Add Test Result for {selectedTestCase?.name}</div>
          <form onSubmit={handleAddResult}>
            <div className="form-group">
              <label className="form-label">Status *</label>
              <select
                className="form-control"
                value={resultData.status}
                onChange={(e) => setResultData({ ...resultData, status: e.target.value })}
              >
                <option value="passed">Passed</option>
                <option value="failed">Failed</option>
                <option value="blocked">Blocked</option>
                <option value="pending">Pending</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Execution Time (ms) *</label>
              <input
                type="number"
                className="form-control"
                value={resultData.execution_time_ms}
                onChange={(e) => setResultData({ ...resultData, execution_time_ms: parseInt(e.target.value) })}
                min="0"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Notes</label>
              <textarea
                className="form-control"
                value={resultData.notes}
                onChange={(e) => setResultData({ ...resultData, notes: e.target.value })}
                rows="3"
                placeholder="Add any notes about this test execution..."
              />
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={() => { setShowResultModal(false); setSelectedTestCase(null); }}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                Record Result
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
