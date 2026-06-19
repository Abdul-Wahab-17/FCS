import { useMemo, useState } from 'react';
import type { Violation } from '../types';
import { processVideoPath, uploadVideo } from '../utils/api';
import { formatBehavior, percent } from '../utils/formatters';

interface LiveFeedMonitorProps {
  violations: Violation[];
  onProcessed: (reports: Violation[]) => void;
}

export default function LiveFeedMonitor({
  violations,
  onProcessed,
}: LiveFeedMonitorProps) {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [videoPath, setVideoPath] = useState(
    'data/test/Carrying_Overload_with_Forklift/demo_overload.mp4'
  );
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const visibleDetections = useMemo(() => violations.slice(0, 4), [violations]);

  const hasCritical = visibleDetections.some((v) => v.severity === 'CRITICAL');
  const hasHigh     = visibleDetections.some((v) => v.severity === 'HIGH');
  const statusLabel = hasCritical
    ? '🔴 VIOLATION — CRITICAL'
    : hasHigh
    ? '🟠 VIOLATION — HIGH'
    : visibleDetections.length > 0
    ? '🟡 VIOLATIONS DETECTED'
    : '✅ COMPLIANT';

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
      onProcessed(result.reports);
      setMessage(`✔ ${result.count} compliance record(s) generated`);
    } catch (err) {
      setMessage(err instanceof Error ? `✘ ${err.message}` : '✘ Processing failed');
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
            <h2>📹 Live Feed Monitor</h2>
            <p className="subtle">Clip inspection · detection overlay · real-time analysis</p>
          </div>
          <span className={`status-pill ${statusCls}`}>{statusLabel}</span>
        </div>

        <div className="video-stage">
          {previewUrl ? (
            <video src={previewUrl} controls muted />
          ) : (
            <div className="factory-frame" aria-label="Factory floor preview">
              {/* HUD overlay */}
              <div className="feed-hud">
                <div className="feed-hud-top">
                  <span>CAM-01 · ZONE-A</span>
                  <span>REC ● LIVE</span>
                  <span style={{ opacity: 0.55 }}>FPS: 24.0</span>
                </div>
              </div>
              <div className="walkway" />
              <div className="machine machine-a" />
              <div className="machine machine-b" />
              <div className="forklift-shape" />
            </div>
          )}

          {/* Detection bounding boxes */}
          {visibleDetections.map((item, index) => (
            <div
              className={`detection-box ${item.severity.toLowerCase()}`}
              key={`${item.event_id}-${index}`}
              style={{
                left:   `${6 + index * 14}%`,
                top:    `${12 + index * 12}%`,
                width:  '20%',
                height: '26%',
              }}
            >
              <span className="detection-box-label">
                {item.severity} · {percent(item.confidence)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Control panel ── */}
      <aside className="panel control-panel">
        <div className="panel-header">
          <h2>⚙ Process Clip</h2>
        </div>

        <label className="field">
          <span>Dataset path</span>
          <input
            value={videoPath}
            onChange={(e) => setVideoPath(e.target.value)}
            disabled={Boolean(file)}
            placeholder="data/test/…"
          />
        </label>

        <label className="file-drop">
          <span>{file ? `📎 ${file.name}` : '＋ Choose or drop a video file'}</span>
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
                <span className="spinner" /> Analysing…
              </>
            ) : (
              '▶ Run Detection'
            )}
          </button>
          {file && (
            <button
              className="button secondary"
              type="button"
              onClick={() => handleFileChange(null)}
            >
              Clear
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
          <h3>Recent Detections</h3>
          {visibleDetections.length === 0 ? (
            <p className="subtle" style={{ paddingTop: 8 }}>
              No records yet. Process a clip or seed demo data.
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
