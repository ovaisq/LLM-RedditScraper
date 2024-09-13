#!/usr/bin/env bash
# ©2024, Ovais Quraishi
cd analysis_frontend
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
