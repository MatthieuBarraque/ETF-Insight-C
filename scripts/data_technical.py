#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yfinance as yf
import json
import os
import sys
import time
from datetime import datetime
import threading
import queue
import pandas as pd


RAW_DATA_FILE = 'data/raw/etf_list.json'
DATA_DIR = 'data/processed/technical/'
LOG_FILE = 'logs/data_technical.log'
MAX_THREADS = 5 
MAX_RETRIES = 3
SLEEP_TIME = 1 

error_queue = queue.Queue()

def setup_logging():
    if not os.path.exists('logs/'):
        os.makedirs('logs/')
    with open(LOG_FILE, 'w') as f:
        f.write('')

def log_error(message):
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp} - ERROR - {message}\n")

def load_etf_list():
    """
    Charge la liste des ETF depuis le fichier JSON.
    """
    try:
        with open(RAW_DATA_FILE, 'r') as f:
            data = json.load(f)
        etf_list = []
        for secteur in data['Secteurs']:
            for domaine in secteur['Domaines']:
                for etf in domaine['ETFs']:
                    etf_info = {
                        'Ticker': etf['Ticker'],
                        'Secteur': secteur['Nom'],
                        'Domaine': domaine['Nom'],
                        'Nom': etf['Nom']
                    }
                    etf_list.append(etf_info)
        return etf_list
    except Exception as e:
        log_error(f"Erreur lors du chargement du fichier ETF : {e}")
        sys.exit(1)

def calculate_technical_indicators(df):
    """
    Calcule les indicateurs techniques pour un DataFrame donné.
    """
    indicators = {}
    indicators['SMA_20'] = df['Close'].rolling(window=20).mean().iloc[-1]
    indicators['SMA_50'] = df['Close'].rolling(window=50).mean().iloc[-1]
    indicators['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
    indicators['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean().iloc[-1]

    delta = df['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up / ema_down
    indicators['RSI_14'] = 100 - (100 / (1 + rs.iloc[-1]))

    # MACD
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    indicators['MACD'] = macd.iloc[-1]
    indicators['MACD_Signal'] = signal.iloc[-1]
    indicators['MACD_Hist'] = indicators['MACD'] - indicators['MACD_Signal']

    return indicators

def fetch_technical_data(etf_info):
    """
    Récupère les données techniques pour un ETF spécifique.
    """
    symbol = etf_info['Ticker']
    retries = 0
    while retries < MAX_RETRIES:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period='1y', interval='1d')
            if df.empty:
                raise ValueError("Aucune donnée historique disponible pour cet ETF.")

            indicators = calculate_technical_indicators(df)
            indicators['Ticker'] = symbol
            indicators['Nom'] = etf_info['Nom']
            indicators['Secteur'] = etf_info['Secteur']
            indicators['Domaine'] = etf_info['Domaine']
            indicators['Timestamp'] = int(time.time())

            output_file = f"{DATA_DIR}{symbol}.json"
            with open(output_file, 'w') as f:
                json.dump(indicators, f, default=str)
            return
        except Exception as e:
            retries += 1
            log_error(f"Erreur lors de la récupération des données techniques pour {symbol} (Tentative {retries}/{MAX_RETRIES}): {e}")
            time.sleep(SLEEP_TIME)
    error_data = {
        'Ticker': symbol,
        'Timestamp': int(time.time()),
        'ErrorCode': 1,
        'ErrorMessage': f"Échec de la récupération des données techniques après {MAX_RETRIES} tentatives.",
        'Secteur': etf_info['Secteur'],
        'Domaine': etf_info['Domaine'],
        'Nom': etf_info['Nom']
    }
    output_file = f"{DATA_DIR}{symbol}.json"
    with open(output_file, 'w') as f:
        json.dump(error_data, f)

def worker(etf_queue):
    while True:
        try:
            etf_info = etf_queue.get_nowait()
        except queue.Empty:
            break
        fetch_technical_data(etf_info)
        etf_queue.task_done()

def fetch_all_technical_data(etf_list):
    """
    Récupère les données techniques pour tous les ETF en utilisant un pool de threads.
    """
    etf_queue = queue.Queue()
    for etf_info in etf_list:
        etf_queue.put(etf_info)

    threads = []
    for _ in range(min(MAX_THREADS, len(etf_list))):
        thread = threading.Thread(target=worker, args=(etf_queue,))
        thread.start()
        threads.append(thread)

    etf_queue.join()

    for thread in threads:
        thread.join()

def main():
    setup_logging()
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    etf_list = load_etf_list()
    try:
        print(f"{datetime.now().isoformat()} - Démarrage de la récupération des données techniques...")
        fetch_all_technical_data(etf_list)
        print(f"{datetime.now().isoformat()} - Récupération des données techniques terminée.")
    except Exception as e:
        log_error(f"Erreur générale dans le script : {e}")

if __name__ == '__main__':
    main()
