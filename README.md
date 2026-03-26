# 📈 Automated Trading Bot (Angel One SmartAPI)

A modular, production-oriented **algorithmic trading system** built in Python using the **Angel One SmartAPI**.  
The bot implements a **Range Filter–based strategy** to identify trend breakouts while minimizing market noise, with support for configurable risk management and backtesting.

---

## 🚀 Overview

This project is designed as a **scalable and extensible trading framework**, separating concerns across data acquisition, signal generation, order execution, and risk control. It enables both **live trading** and **strategy validation using historical data**.

---

## ✨ Key Features

- **Automated Trade Execution**  
  Seamless integration with Angel One SmartAPI for real-time order placement and management  

- **Strategy Engine (Range Filter)**  
  Filters price noise and detects breakout conditions for signal generation  

- **Secure Authentication**  
  Login flow using OTP + MPIN  

- **Config-Driven Architecture**  
  Centralized configuration (`config.json`) for instruments, parameters, and risk settings  

- **Modular Design**  
  Clean separation of components for maintainability and scalability  

- **Backtesting Capability**  
  Evaluate strategy performance using historical OHLC datasets  

- **Logging & Debugging Support**  
  Structured logging for trades, signals, and system events  

---

## ⚙️ System Workflow

1. **Authenticate** with Angel One SmartAPI  
2. **Fetch Market Data** (live or historical)  
3. **Generate Trading Signals** via Range Filter logic  
4. **Apply Risk Controls** (position sizing, limits, etc.)  
5. **Execute Orders** through broker API  
6. **Log & Monitor** system activity  

---

## 🧠 Strategy Description

The **Range Filter Strategy** is designed to reduce market noise by smoothing price action within a defined range.  
Trade signals are generated when the price **breaks out of the filtered range**, indicating potential directional momentum.

---

## 🛠️ Technology Stack

- **Language:** Python  
- **API:** Angel One SmartAPI  
- **Data Handling:** Pandas  
- **Configuration:** JSON  

---

## 🧪 Backtesting

The framework supports offline testing using historical OHLC datasets (CSV format), enabling:

- Strategy validation before deployment  
- Performance evaluation across instruments  
- Parameter tuning and optimization  

---

This project is intended for **educational and research purposes only**.  
Algorithmic trading involves substantial financial risk. The author assumes no responsibility for any financial losses incurred through the use of this software.
