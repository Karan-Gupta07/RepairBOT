import { useState, useEffect, useCallback } from 'react';
import Landing from './components/Landing';
import UploadCard from './components/UploadCard';
import ResultsCard from './components/ResultsCard';

export default function App() {
  const [view, setView] = useState(
    window.location.hash === '#app' ? 'app' : 'landing'
  );
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastFile, setLastFile] = useState(null);

  useEffect(() => {
    const onHashChange = () => {
      setView(window.location.hash === '#app' ? 'app' : 'landing');
    };
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const handleAnalyze = useCallback(async (file) => {
    setLastFile(file);
    setLoading(true);
    setError(null);
    setResult(null);

    const form = new FormData();
    form.append('image', file);

    try {
      const res = await fetch('/analyze', { method: 'POST', body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Request failed');
      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleRetry = useCallback(() => {
    if (lastFile) handleAnalyze(lastFile);
  }, [lastFile, handleAnalyze]);

  if (view === 'landing') {
    return <Landing />;
  }

  return (
    <section className="app-wrap">
      <a
        href="#landing"
        className="back-link"
        onClick={(e) => {
          e.preventDefault();
          window.location.hash = '';
        }}
      >
        ← Back
      </a>
      <header className="app-header">
        <h2>RepairBOT</h2>
        <p>Upload a photo of the broken item</p>
      </header>

      <UploadCard onAnalyze={handleAnalyze} loading={loading} />

      <div>
        {loading && (
          <div className="loading-card">
            <div className="spinner" />
            <p className="loading-text">Analyzing your photo…</p>
          </div>
        )}
        {error && !loading && (
          <div className="error-card">
            <p>{error}</p>
            <button type="button" className="btn-retry" onClick={handleRetry}>
              Try again
            </button>
          </div>
        )}
        {result && !loading && !error && <ResultsCard data={result} />}
      </div>
    </section>
  );
}
