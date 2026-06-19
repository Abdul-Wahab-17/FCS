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
  const [videoPath, setVideoPath] = useState(
    'data/test/Carrying_Overload_with_Forklift/demo_overload.mp4'
  );
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [scanResults, setScanResults] = useState<Violation[]>([]);

  const visibleDetections = useMemo(() => scanResults.slice(0, 4), [scanResults]);

  const hasCritical = visibleDetections.some((v) => v.severity === 'CRITICAL');
  const hasHigh     = visibleDetections.some((v) => v.severity === 'HIGH');
  const statusLabel = hasCritical
    ? '🔴 SEVERE INFRACTION DETECTED'
    : hasHigh
    ? '🟠 HIGH RISK ANOMALY'
    : visibleDetections.length > 0
    ? '🟡 ANOMALY DETECTED'
    : '✅ OPTIMAL STATE';

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
      setMessage(
        result.count > 0
          ? `✔ ${result.count} data vectors extracted successfully`
          : '✘ No violations detected — check the video path or upload a labeled clip'
      );
    } catch (err) {
      setMessage(err instanceof Error ? `✘ ${err.message}` : '✘ Telemetry failure');
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
            <h2>📹 Real-Time Optical Surveillance</h2>
            <p className="subtle">Optical array · AI detection overlay · low-latency stream</p>
          </div>
          <span className={`status-pill ${statusCls}`}>{statusLabel}</span>
        </div>

        <div className="video-stage radar-container">
          {previewUrl ? (
            <video src={previewUrl} controls muted />
          ) : (
            <div className="radar-stage" aria-label="Digital Twin Radar Preview">
              {/* HUD overlay */}
              <div className="feed-hud">
                <div className="feed-hud-top">
                  <span>ARRAY-01 · SECTOR-A</span>
                  <span>SYNC ● ACTIVE</span>
                  <span style={{ opacity: 0.55 }}>LATENCY: 12ms</span>
                </div>
              </div>
              
              {/* Radar Grid and Sweep */}
              <div className="radar-grid"></div>
              <div className="radar-sweep"></div>
              
              {/* Radar Points (pulsing dots simulating detection nodes) */}
              <div className="radar-node node-1"></div>
              <div className="radar-node node-2"></div>
              <div className="radar-node node-3"></div>
            </div>
          )}

          {/* Detection bounding boxes */}
          {visibleDetections.map((item, index) => (
            <div
              className={`detection-box ${item.severity.toLowerCase()}`}
              key={`${item.event_id}-${index}`}
              style={{
                left:   `${15 + index * 10}%`,
                top:    `${20 + index * 15}%`,
                width:  '18%',
                height: '22%',
              }}
            >
              <span className="detection-box-label">
                {item.severity} · MATRIX: {percent(item.confidence)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Control panel ── */}
      <aside className="panel control-panel">
        <div className="panel-header">
          <h2>⚙ Execute Matrix Analysis</h2>
        </div>

        <label className="field">
          <span>Target Dataset Path</span>
          <input
            value={videoPath}
            onChange={(e) => setVideoPath(e.target.value)}
            disabled={Boolean(file)}
            placeholder="data/test/…"
          />
        </label>

        <label className="file-drop">
          <span>{file ? `📎 ${file.name}` : '＋ Inject optical payload (MP4)'}</span>
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
            disabled={processing}
            style={{ flex: 1 }}
          >
            {processing ? (
              <>
                <span className="spinner" /> Synthesizing Data…
              </>
            ) : (
              '▶ Initialize Scan'
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

        {/* Recent detections */}
        <div className="detection-summary">
          <h3>Surveillance Telemetry</h3>
          {visibleDetections.length === 0 ? (
            <p className="subtle" style={{ paddingTop: 8 }}>
              Standby mode. Initiate scan to acquire optical data.
            </p>
          ) : (
            visibleDetections.map((item) => (
              <div className="summary-row" key={item.event_id}>
                <span style={{ fontSize: 13 }}>{formatBehavior(item.behavior_class)}</span>
                <div className="confidence-bar-wrap">
                  <div className="confidence-bar">
                    <div
                      className="confidence-bar-fill"
                      style={{ width: `${item.confidence * 100}%` }}
                    />
                  </div>
                  <strong style={{ fontSize: 12, minWidth: 36 }}>
                    {percent(item.confidence)}
                  </strong>
                  <span className={`severity-chip ${item.severity.toLowerCase()}`}>
                    {item.severity}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </aside>
    </section>
  );
}
