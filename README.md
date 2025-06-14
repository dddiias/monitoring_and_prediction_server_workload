# 🛰️ MPS – Monitoring & Prediction System
System for monitoring and predicting server workload based on time series analysis (telegram-bot)

[![Docker](https://img.shields.io/badge/ready-for-docker-blue?logo=docker)](https://docs.docker.com/)
[![License](https://img.shields.io/github/license/your-org/monitoring_and_prediction_server_workload)](LICENSE)
[![Made with ❤️](https://img.shields.io/badge/made%20with-%E2%9D%A4-red)](#)

A **plug-and-play DevOps toolkit** that

* collects **real-time server metrics** with Telegraf,
* stores them in **InfluxDB** via a **FastAPI** gateway,
* predicts future load using an **LSTM model**, and
* sends **smart, non-spammy alerts** through a Telegram bot.

> **Why MPS?** Lightweight enough for a single VPS, powerful enough for a fleet of servers.

---

## ✨ Features
|                                        | Description |
|----------------------------------------|-------------|
| **Agent layer**                        | Lightweight Telegraf agents push CPU, RAM, Disk & Net stats through HTTP. |
| **API layer (FastAPI)**                | Validates & persists metrics to InfluxDB, exposes swagger docs. |
| **Bot layer (Telegram)**               | Chat UI to add servers, view live graphs, fetch daily PDF reports, set thresholds, and see LSTM forecasts (MAE & RMSE included). |
| **ML layer (PyTorch)**                 | Daily cron retrains an LSTM on each server’s history; weights cached for instant inference. |
| **Alert scheduler**                    | Sends a single alert per resource every *N* minutes when thresholds are breached. |
| **One-command deployment**             | `docker compose up -d` spins up the whole stack. |

---

## 🏗️ Architecture
```mermaid
graph TD
    subgraph Clients
        U[User • Telegram]
    end
    subgraph Bot
        TB[Telegram Bot]
        S[Scheduler & Alerts]
    end
    subgraph Backend
        A(FastAPI)
        I[(InfluxDB)]
        M[[LSTM Service]]
    end
    subgraph Servers
        T1>Telegraf Agent]
        T2>Telegraf Agent]
    end
    U --> TB
    TB --REST--> A
    A --> I
    TB ..> I
    A --> M
    T1 --> A
    T2 --> A
    S -.-> TB
