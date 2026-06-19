# Troubleshooting

## `ModuleNotFoundError: No module named 'src'`

Run commands from the repository root:

```bash
python src/main.py
```

## PowerShell blocks npm

Use the command shim directly:

```bash
npm.cmd install
npm.cmd run dev
```

## No detections for uploaded videos

The current production-grade CV model is not trained. Use labeled dataset paths or click Seed Demo to verify the full pipeline.

## Dashboard cannot reach API

Confirm the backend is running:

```bash
curl http://localhost:8000/api/health
```

If the frontend is on a different port, add it to `CORS_ORIGINS`.
