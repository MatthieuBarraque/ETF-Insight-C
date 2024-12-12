#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yfinance as yf
import json
import time
import os
import sys
import threading
import queue
from datetime import datetime
import pytz

RAW_DATA_FILE = 'data/raw/etf_list.json'
DATA_DIR = 'data/processed/ETF_individual/'
LOG_FILE = 'logs/data_acquisition.log'
UPDATE_INTERVAL = 3600
MAX_RETRIES = 3

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
        etf_symbols = []
        for secteur in data['Secteurs']:
            for domaine in secteur['Domaines']:
                for etf in domaine['ETFs']:
                    etf_info = {
                        'Ticker': etf['Ticker'],
                        'Secteur': secteur['Nom'],
                        'Domaine': domaine['Nom'],
                        'Nom': etf['Nom']
                    }
                    etf_symbols.append(etf_info)
        return etf_symbols
    except Exception as e:
        log_error(f"Erreur lors du chargement du fichier ETF : {e}")
        sys.exit(1)

def fetch_etf_data(etf_info):
    """
    Récupère les données pour un ETF spécifique.
    """
    symbol = etf_info['Ticker']
    retries = 0
    while retries < MAX_RETRIES:
        try:
            ticker = yf.Ticker(symbol)
            market_state = ticker.info.get('marketState', 'CLOSED')
            timezone = ticker.info.get('exchangeTimezoneName', 'UTC')
            current_time = datetime.now(pytz.timezone(timezone))
            market_close_time = ticker.info.get('regularMarketTime', None)
            if market_close_time:
                market_close_time = datetime.fromtimestamp(market_close_time, pytz.timezone(timezone))
            else:
                market_close_time = 'N/A'

            data = ticker.history(period='1d', interval='1m')
            if data.empty:
                raise ValueError("Aucune donnée disponible pour cet ETF.")

            latest_data = data.tail(1).iloc[0].to_dict()
            latest_data['Ticker'] = symbol
            latest_data['Timestamp'] = int(time.time())
            latest_data['Secteur'] = etf_info['Secteur']
            latest_data['Domaine'] = etf_info['Domaine']
            latest_data['Nom'] = etf_info['Nom']
            latest_data['MarketState'] = market_state
            latest_data['MarketCloseTime'] = market_close_time.isoformat() if market_close_time != 'N/A' else 'N/A'
            latest_data['ErrorCode'] = 0  # Pas d'erreur
            output_file = f"{DATA_DIR}{symbol}.json"
            with open(output_file, 'w') as f:
                json.dump(latest_data, f)
            return
        except Exception as e:
            retries += 1
            log_error(f"Erreur lors de la récupération des données pour {symbol} (Tentative {retries}/{MAX_RETRIES}): {e}")
            time.sleep(1)

    error_data = {
        'Ticker': symbol,
        'Timestamp': int(time.time()),
        'ErrorCode': 1,  # Code d'erreur pour échec de récupération
        'ErrorMessage': f"Échec de la récupération des données après {MAX_RETRIES} tentatives.",
        'Secteur': etf_info['Secteur'],
        'Domaine': etf_info['Domaine'],
        'Nom': etf_info['Nom']
    }
    output_file = f"{DATA_DIR}{symbol}.json"
    with open(output_file, 'w') as f:
        json.dump(error_data, f)

def fetch_and_store_all_data(etf_list):
    """
    Récupère les données pour tous les ETF en parallèle.
    """
    threads = []
    for etf_info in etf_list:
        thread = threading.Thread(target=fetch_etf_data, args=(etf_info,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def main():
    setup_logging()
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    etf_list = load_etf_list()
    while True:
        try:
            print(f"{datetime.now().isoformat()} - Démarrage de la récupération des données...")
            fetch_and_store_all_data(etf_list)
            print(f"{datetime.now().isoformat()} - Récupération terminée. Attente de {UPDATE_INTERVAL} secondes.")
        except Exception as e:
            log_error(f"Erreur générale dans le script : {e}")
        time.sleep(UPDATE_INTERVAL)

if __name__ == '__main__':
    main()
