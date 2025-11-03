# Frontend - Project Management System

Streamlit frontend for the Project Management System.

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
streamlit run src/main.py
```

## Docker

```bash
docker build -t frontend .
docker run -p 8501:8501 frontend
```

## Structure

- `src/pages/` - Streamlit pages
- `src/components/` - Reusable components
- `src/services/` - API services
- `src/state/` - State management
- `src/utils/` - Utilities
- `src/config/` - Configuration
- `src/styles/` - CSS styles

