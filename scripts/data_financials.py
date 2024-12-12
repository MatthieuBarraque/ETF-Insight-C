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

RAW_DATA_FILE = 'data/raw/etf_list.json'
DATA_DIR = 'data/processed/financials/'
LOG_FILE = 'logs/data_financials.log'
MAX_THREADS = 5
MAX_RETRIES = 3
SLEEP_TIME = 1

error_queue = queue.Queue()

def setup_logging():
    if not os.path.exists('logs/'):
        os.makedirs('logs/')
    # Vider le fichier de log au démarrage
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

def fetch_financials(etf_info):
    """
    Récupère les états financiers pour un ETF spécifique.
    """
    symbol = etf_info['Ticker']
    retries = 0
    while retries < MAX_RETRIES:
        try:
            ticker = yf.Ticker(symbol)
            
            # Récupérer les états financiers
            financials = {
                'Ticker': symbol,
                'Nom': etf_info['Nom'],
                'Secteur': etf_info['Secteur'],
                'Domaine': etf_info['Domaine'],
                'Timestamp': int(time.time()),
                'BalanceSheet': ticker.balance_sheet.reset_index().to_dict(orient='records'),
                'IncomeStatement': ticker.financials.reset_index().to_dict(orient='records'),
                'CashFlow': ticker.cashflow.reset_index().to_dict(orient='records')
            }
            
            # Écrire les données dans un fichier JSON
            output_file = f"{DATA_DIR}{symbol}.json"
            with open(output_file, 'w') as f:
                json.dump(financials, f, default=str)
            return
        except Exception as e:
            retries += 1
            log_error(f"Erreur lors de la récupération des états financiers pour {symbol} (Tentative {retries}/{MAX_RETRIES}): {e}")
            time.sleep(SLEEP_TIME)
    # Si toutes les tentatives échouent
    error_data = {
        'Ticker': symbol,
        'Timestamp': int(time.time()),
        'ErrorCode': 1,  # Code d'erreur pour échec de récupération
        'ErrorMessage': f"Échec de la récupération des états financiers après {MAX_RETRIES} tentatives.",
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
        fetch_financials(etf_info)
        etf_queue.task_done()

def fetch_all_financials(etf_list):
    """
    Récupère les états financiers pour tous les ETF en utilisant un pool de threads.
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
    # Créer le répertoire de données s'il n'existe pas
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    etf_list = load_etf_list()
    try:
        print(f"{datetime.now().isoformat()} - Démarrage de la récupération des états financiers...")
        fetch_all_financials(etf_list)
        print(f"{datetime.now().isoformat()} - Récupération des états financiers terminée.")
    except Exception as e:
        log_error(f"Erreur générale dans le script : {e}")

if __name__ == '__main__':
    main()
