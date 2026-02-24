# SafeOpen

Explainability-driven pre-execution document security framework.

## Overview
SafeOpen is a research prototype developed for a master's thesis. It performs real-time file monitoring and applies hybrid risk analysis including:
- Static structural inspection
- Explainability-based indicators
- Machine learning risk scoring
- Risk fusion model
- Proportional mitigation (CDR / Sandbox)

## Features
- Filesystem monitoring daemon
- PDF active content detection
- JavaScript & OpenAction escalation
- SQLite audit logging
- Content Disarm and Reconstruction
- Firejail sandbox integration

## Architecture
Watcher → Static → Explainability → ML → Fusion → Decision → Mitigation

## Requirements
- Python 3.10+
- SQLite3
- Firejail (Linux)
- PyPDF2

## Disclaimer
This project is for academic research purposes only.
