# 🚀 Personal Finance Tracker: Professional API Backend

💰 Production-grade FastAPI backend for personal finance tracking with RBAC & analytics
A high-performance, asynchronous FastAPI backend designed for robust personal finance tracking. This system features granular Role-Based Access Control (RBAC), advanced financial analytics, and a resilient dual-database architecture.

---

## 💎 Key Features

- **🔐 Enterprise Security**: JWT-based authentication with `passlib` and `bcrypt`.
- **🛡️ Granular RBAC**: 
  - **Admin**: Full system control (Management + Analytics).
  - **Analyst**: Global data insights and trends.
  - **Viewer**: Personal financial management only.
- **📈 Advanced Analytics**: Real-time balance calculation, category breakdowns, and monthly trends.
- **⚖️ Dual-Mode Database**: Production-ready for **PostgreSQL** with a zero-config **SQLite** fallback for local developers.
- **🐳 DevOps Optimized**: Fully Dockerized with `docker-compose` support.
- **🧪 Quality Guarded**: 100% "Green" test suite using `pytest` and `httpx`.

---

## 🛠️ Architecture

Built using modern Python best practices:
- **FastAPI**: Asynchronous Request Handling.
- **SQLAlchemy 2.0**: Modern Async ORM patterns.
- **Pydantic v2**: Type-safe data validation and serialization.
- **Annotated Dependencies**: Clean and reusable dependency injection.

---

## 🚀 Quick Start

### Option 1: Local Development (SQLite)
No complex setup required. Simply run:
```powershell
python run_local.py
```
This script will verify your requirements and launch the API at `http://localhost:8000`.

### Option 2: Production Setup (Docker)
```powershell
docker-compose up --build
```

### 🧪 Seeding the Database
Initialize your environment with professional test data:
```powershell
python -m scripts.seed
```

---

## 🔑 Default Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@example.com` | `admin123` |
| **Analyst**| `analyst@example.com`| `analyst123` |
| **Viewer** | `viewer@example.com` | `viewer123` |

---

## 🧪 Testing

Run the full automated audit suite:
```powershell
$env:PYTHONPATH="."; pytest tests/ -v
```

---

## 📚 API Documentation

Once the server is running, explore the interactive documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🛡️ License
Provisional Internal Release - All Rights Reserved.
