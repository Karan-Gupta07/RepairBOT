import { useState, useRef, useCallback, useEffect } from 'react';

function formatBytes(n) {
  if (n < 1024) return n + ' B';
  if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB';
  return (n / (1024 * 1024)).toFixed(1) + ' MB';
}

export default function UploadCard({ onAnalyze, loading }) {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragover, setDragover] = useState(false);
  const fileInputRef = useRef(null);
  const prevUrlRef = useRef(null);

  useEffect(() => {
    return () => {
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
    };
  }, []);

  const handleFile = useCallback((f) => {
    if (!f || !f.type.startsWith('image/')) return;
    setFile(f);
    if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
    const url = URL.createObjectURL(f);
    prevUrlRef.current = url;
    setPreviewUrl(url);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragover(false);
      const f = e.dataTransfer?.files?.[0];
      if (f && f.type.startsWith('image/')) handleFile(f);
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragover(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragover(false);
  }, []);

  const handleInputChange = useCallback(
    (e) => {
      const f = e.target.files?.[0];
      if (f) handleFile(f);
    },
    [handleFile]
  );

  const handleZoneClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleAnalyzeClick = useCallback(() => {
    if (file && onAnalyze) onAnalyze(file);
  }, [file, onAnalyze]);

  return (
    <div className={`upload-card${dragover ? ' dragover' : ''}`}>
      <div
        className="upload-zone"
        onClick={handleZoneClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          ref={fileInputRef}
          accept="image/*"
          onChange={handleInputChange}
        />
        <div className="upload-icon">📷</div>
        <p className="label">
          {file ? file.name : 'Drop an image here or click to choose'}
        </p>
        <p className="hint">JPEG, PNG or WebP — max 10MB</p>
      </div>

      {file && (
        <div className="preview-row">
          <img className="preview-img" src={previewUrl} alt="" />
          <div className="preview-info">
            <p className="preview-name">{file.name}</p>
            <p className="preview-size">{formatBytes(file.size)}</p>
          </div>
        </div>
      )}

      <button
        type="button"
        className="btn"
        disabled={!file || loading}
        onClick={handleAnalyzeClick}
      >
        Analyze repair
      </button>
    </div>
  );
}
