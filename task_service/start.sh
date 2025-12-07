#!/usr/bin/env bash
# Wait for DB to be ready
sleep 10
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
