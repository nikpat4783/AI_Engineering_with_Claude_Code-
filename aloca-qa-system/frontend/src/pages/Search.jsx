import React, { useState } from 'react';
import { useSearch } from '../api/hooks';

export default function Search() {
  const [query, setQuery] = useState('');
  const { execute, status, value, error } = useSearch();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (query.trim()) {
      await execute(query);
    }
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-group">
          <label htmlFor="search-input">Search the Web</label>
          <div className="search-input-group">
            <input
              id="search-input"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter a search query..."
              className="search-input"
              disabled={status === 'pending'}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={status === 'pending' || !query.trim()}
            >
              {status === 'pending' ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>
      </form>

      {status === 'pending' && (
        <div className="spinner-container">
          <div className="spinner"></div>
          <p>Searching...</p>
        </div>
      )}

      {status === 'error' && (
        <div className="empty-state">
          <div className="empty-state-icon">⚠️</div>
          <div className="empty-state-title">Search Unavailable</div>
          <p>
            {error?.message || 'Search is currently unavailable. Please check that APIFY_API_TOKEN is configured and try again.'}
          </p>
        </div>
      )}

      {status === 'success' && value && value.results.length === 0 && (
        <div className="empty-state">
          <div className="empty-state-icon">🔍</div>
          <div className="empty-state-title">No Results</div>
          <p>No results found for "{value.query}". Try a different search query.</p>
        </div>
      )}

      {status === 'success' && value && value.results.length > 0 && (
        <div className="search-results">
          <div className="results-header">
            <p>Found {value.results.length} result(s) for "{value.query}"</p>
          </div>
          <div className="results-list">
            {value.results.map((result, index) => (
              <div key={index} className="result-card">
                <a
                  href={result.url}
                  target="_blank"
                  rel="noreferrer"
                  className="result-title"
                >
                  {result.title}
                </a>
                <p className="result-url">{result.url}</p>
                <p className="result-snippet">{result.snippet}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {status === 'idle' && (
        <div className="empty-state">
          <div className="empty-state-icon">🌐</div>
          <div className="empty-state-title">Web Search</div>
          <p>Enter a search query to get started.</p>
        </div>
      )}
    </div>
  );
}
