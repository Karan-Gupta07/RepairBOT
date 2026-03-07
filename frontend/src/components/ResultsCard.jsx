import { useState } from 'react';

export default function ResultsCard({ data }) {
  const [showInstructions, setShowInstructions] = useState(false);

  const rep = (data.repairability || '').toLowerCase();
  const diff = (data.difficulty || '').toLowerCase().replace(/\s+/g, '');
  const cost =
    data.estimated_cost_usd != null ? `$${data.estimated_cost_usd}` : '—';
  const timeStr = data.estimated_time || '—';
  const products = data.products || {};
  const parts = products.parts || [];
  const tools = products.tools || [];
  const linkSource =
    products.source === 'shopify' ? '' : ' (search Google Shopping)';
  const steps = data.repair_steps || [];

  return (
    <div className="result">
      <div className="result-header">
        <span className={`badge ${rep}`}>
          Repairability: {data.repairability || '—'}
        </span>
        <span className={`badge ${diff}`}>
          Difficulty: {data.difficulty || '—'}
        </span>
        <span className="cost">Est. {cost}</span>
        <div className="result-meta">
          <span>⏱ {timeStr}</span>
        </div>
      </div>

      <div className="result-body">
        <p className="description">{data.brief_description || ''}</p>

        {rep === 'low' && (
          <p className="low-repair-note">
            This item may not be easily repairable. Consider professional repair
            or replacement. If the image was unclear, try uploading a sharper
            photo.
          </p>
        )}

        {steps.length > 0 && (
          <>
            <button
              type="button"
              className="btn-instructions"
              aria-expanded={showInstructions}
              onClick={() => setShowInstructions((v) => !v)}
            >
              📋{' '}
              {showInstructions
                ? 'Hide instructions'
                : 'Step-by-step instructions'}
            </button>
            <div
              className={`instructions-panel${showInstructions ? ' open' : ''}`}
            >
              <h4>Repair steps</h4>
              <ol className="steps-list">
                {steps.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ol>
            </div>
          </>
        )}

        {(data.parts_needed?.length > 0 || data.tools_needed?.length > 0) && (
          <ul className="meta-list">
            {data.parts_needed?.length > 0 && (
              <li>
                <strong>Parts</strong> {data.parts_needed.join(', ')}
              </li>
            )}
            {data.tools_needed?.length > 0 && (
              <li>
                <strong>Tools</strong> {data.tools_needed.join(', ')}
              </li>
            )}
          </ul>
        )}

        {parts.length > 0 || tools.length > 0 ? (
          <>
            {parts.length > 0 && (
              <>
                <p className="section-title">
                  Parts to buy
                  {linkSource && (
                    <span className="section-hint">{linkSource}</span>
                  )}
                </p>
                <div className="link-grid">
                  {parts
                    .filter((p) => p?.url)
                    .map((p, i) => (
                      <a
                        key={i}
                        className="link-item"
                        href={p.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <span>{p.title || 'Part'}</span>
                        <span className="arrow">→</span>
                      </a>
                    ))}
                </div>
              </>
            )}
            {tools.length > 0 && (
              <>
                <p className="section-title">
                  Tools to buy
                  {linkSource && (
                    <span className="section-hint">{linkSource}</span>
                  )}
                </p>
                <div className="link-grid">
                  {tools
                    .filter((t) => t?.url)
                    .map((t, i) => (
                      <a
                        key={i}
                        className="link-item"
                        href={t.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <span>{t.title || 'Tool'}</span>
                        <span className="arrow">→</span>
                      </a>
                    ))}
                </div>
              </>
            )}
          </>
        ) : (
          <>
            <p className="section-title">Parts &amp; tools</p>
            <p className="no-links-msg">
              No specific parts or tools suggested for this repair.
            </p>
          </>
        )}

        <p className="disclaimer">
          ⚠️ Repair at your own risk. Seek professional help when in doubt.
        </p>
      </div>
    </div>
  );
}
