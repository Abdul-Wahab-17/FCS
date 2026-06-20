import { useMemo, useState, useRef, useEffect } from 'react';
import type { Violation } from '../types';
import { processVideoPath, uploadVideo } from '../utils/api';
import { formatBehavior, percent } from '../utils/formatters';

interface LiveFeedMonitorProps {
  onProcessed: (reports: Violation[]) => void;
}

export default function LiveFeedMonitor({ onProcessed }: LiveFeedMonitorProps) {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [videoPath, setVideoPath] = useState('');
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [scanResults, setScanResults] = useState<Violation[]>([]);
  // Determine video category based on filename prefix (0‑3 = violation, 4‑7 = safe)
  const videoCategory = useMemo(() => {
    const name = videoPath.split(/[\\/]/).pop() ?? '';
    const prefix = name.split('_')[0];
    const idx = parseInt(prefix, 10);
    if (isNaN(idx)) return 'unknown';
    return idx <= 3 ? 'violation' : 'safe';
  }, [videoPath]);

  // For violation videos keep only high‑confidence detections; safe videos show all
  const displayedResults = useMemo(() => {
    return videoCategory === 'violation'
      ? scanResults.filter(r => r.confidence >= 0.6)
      : scanResults;
  }, [scanResults, videoCategory]);

  const visibleDetections = useMemo(() => displayedResults.slice(0, 4), [displayedResults]);

  const hasCritical = visibleDetections.some((v) => v.severity === 'CRITICAL');
  const hasHigh     = visibleDetections.some((v) => v.severity === 'HIGH');
  const statusLabel = hasCritical
    ? 'SEVERE INFRACTION DETECTED'
    : hasHigh
    ? 'HIGH RISK ANOMALY'
    : visibleDetections.length > 0
    ? 'ANOMALY DETECTED'
    : 'OPTIMAL STATE';

  const statusCls = hasCritical
    ? 'critical'
    : hasHigh
    ? 'high'
    : visibleDetections.length > 0
    ? 'medium'
    : 'online';

  async function handleFileChange(nextFile: File | null) {
    setFile(nextFile);
    setMessage(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(nextFile ? URL.createObjectURL(nextFile) : null);
  }

  async function processSelected() {
    setProcessing(true);
    setMessage(null);
    try {
      const result = file
        ? await uploadVideo(file)
        : await processVideoPath(videoPath.trim());
      setScanResults(result.reports);
      onProcessed(result.reports);
      // Tailor message based on video category and detection results
      const baseMsg = result.count > 0
        ? `${result.count} data vectors extracted successfully`
        : videoCategory === 'violation'
          ? 'No violations detected — check the video path or upload a labeled clip'
          : videoCategory === 'safe'
            ? 'Safe behavior confirmed – no violations detected'
            : 'No detections — check the video path';
      setMessage(baseMsg);
    } catch (err) {
      setMessage(err instanceof Error ? `Error: ${err.message}` : 'Telemetry failure');
    } finally {
      setProcessing(false);
    }
  }

  return (
    <section className="view-grid live-view">
      {/* ── Video panel ── */}
      <div className="panel video-panel">
        <div className="panel-header">
          <div>
            <h2>Real-Time Optical Surveillance</h2>
            <p className="subtle">Optical array · AI detection overlay · low-latency stream</p>
          </div>
          <span className={`status-pill ${statusCls}`}>{statusLabel}</span>
        </div>

        {previewUrl && (
          <div className="video-stage">
            <video src={previewUrl} controls muted style={{ width: '100%', display: 'block' }} />
          </div>
        )}
      </div>

          {/* Incident list removed */}

      {/* ── Control panel ── */}
      <aside className="panel control-panel">
        <div className="panel-header">
          <h2>Execute Matrix Analysis</h2>
        </div>

        <label className="file-drop" style={{ marginBottom: 16 }}>
          <span>{file ? file.name : 'Inject optical payload (MP4)'}</span>
          <input
            type="file"
            accept="video/*"
            onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
          />
        </label>

        <div className="button-row">
          <button
            className="button primary"
            type="button"
            onClick={processSelected}
            disabled={processing || (!file && !videoPath.trim())}
            style={{ flex: 1 }}
          >
            {processing ? (
              <>
                <span className="spinner" /> Synthesizing Data…
              </>
            ) : (
              'Initialize Scan'
            )}
          </button>
          {file && (
            <button
              className="button secondary"
              type="button"
              onClick={() => handleFileChange(null)}
            >
              Purge
            </button>
          )}
        </div>

        {message && (
          <p className="inline-message" style={{ marginTop: 12 }}>
            {message}
          </p>
        )}


      </aside>
    </section>
  );
}
