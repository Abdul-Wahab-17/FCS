# Setup Guide

## Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/database_init.py
python src/main.py
```

Open `http://localhost:8000/docs`.

## Dashboard

```bash
cd src/dashboard
npm install
npm run dev
```

Open `http://localhost:5173`.

## Dataset

Download from Kaggle and extract into `data/train` and `data/test`.

The folder names should match the behavior classes listed in the README.
