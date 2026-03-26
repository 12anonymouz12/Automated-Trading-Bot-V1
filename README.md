# 📈 Automated Trading Bot (Angel One API)

This project is a **Python-based automated trading bot** built using the **Angel One SmartAPI**, designed to execute trades based on a **Range Filter strategy**. It follows a modular architecture, making it easy to extend, test, and customize.

---

## 🚀 Features

- 📊 Automated trade execution using Angel One API  
- 📉 Range Filter strategy for signal generation  
- 🔐 Secure login with OTP + MPIN  
- ⚙️ Configurable parameters via `config.json`  
- 🧩 Modular design (data, signals, orders, risk separated)  
- 🧪 Backtesting using historical OHLC data  
- 📝 Logging system for trades and errors  

---

## 🗂️ Project Structure
├── config.json
├── main.py
├── login.py
├── login_test.py
├── data_fetcher.py
├── signal_generator.py
├── order_manager.py
├── risk_manager.py
├── backtest.py
├── logs/
├── *.csv

---

## ⚙️ How It Works

1. Login using Angel One SmartAPI  
2. Fetch market data (live or historical)  
3. Generate buy/sell signals using Range Filter  
4. Apply risk management rules  
5. Execute trades automatically  
6. Log results for tracking  

---

## 🛠️ Tech Stack

- Python  
- Angel One SmartAPI  
- Pandas  
- JSON  

---

## 📌 Strategy Overview

The Range Filter strategy reduces market noise by filtering price movements within a defined range.  
Trades are triggered when price breaks out of the filtered range, indicating potential trends.

---

## 🧪 Backtesting

- Uses CSV OHLC data (e.g., TATAPOWER, YESBANK)  
- Helps evaluate strategy performance before live deployment  

---

This project is for educational purposes only. Trading involves financial risk. Use at your own discretion.
