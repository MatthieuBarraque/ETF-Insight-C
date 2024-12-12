#include "data_structures.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "include.h"
#include "cJSON.h"

void init_etf_data(ETFData *etf) {
    memset(etf, 0, sizeof(ETFData));
    etf->base_info.ticker[0] = '\0';
    etf->base_info.nom[0] = '\0';
    etf->base_info.secteur[0] = '\0';
    etf->base_info.domaine[0] = '\0';
    etf->base_info.timestamp = 0;    


    etf->balance_sheets = NULL;
    etf->balance_sheet_count = 0;
    etf->income_statements = NULL;
    etf->income_statement_count = 0;
    etf->cash_flows = NULL;
    etf->cash_flow_count = 0;
    etf->recommendations = NULL;
    etf->recommendation_count = 0;
    etf->calendar.key = NULL;
    etf->calendar.values = NULL;
    etf->calendar.count = 0;
}

void free_etf_data(ETFData *etf) {
    if (etf->balance_sheets) {
        for (size_t i = 0; i < etf->balance_sheet_count; i++) {
            free(etf->balance_sheets[i].date);
        }
        free(etf->balance_sheets);
    }

    if (etf->income_statements) {
        for (size_t i = 0; i < etf->income_statement_count; i++) {
            free(etf->income_statements[i].date);
        }
        free(etf->income_statements);
    }

    // Libérer les tableaux dynamiques pour cash_flows
    if (etf->cash_flows) {
        for (size_t i = 0; i < etf->cash_flow_count; i++) {
            free(etf->cash_flows[i].date);
        }
        free(etf->cash_flows);
    }

    if (etf->recommendations) {
        for (size_t i = 0; i < etf->recommendation_count; i++) {
            free(etf->recommendations[i].date);
        }
        free(etf->recommendations);
    }

    if (etf->calendar.values) {
        for (size_t i = 0; i < etf->calendar.count; i++) {
            free(etf->calendar.values[i]);
        }
        free(etf->calendar.values);
    }
    free(etf->calendar.key);
}

int parse_indicator_json(const char *filename, ETFData *etf) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Erreur lors de l'ouverture du fichier d'indicateurs");
        return -1;
    }
    
    fseek(file, 0, SEEK_END);
    long len = ftell(file);
    rewind(file);
    char *data = malloc(len + 1);
    if (!data) {
        fclose(file);
        fprintf(stderr, "Erreur d'allocation mémoire\n");
        return -1;
    }
    
    size_t read_size = fread(data, 1, (size_t)len, file);
    if (read_size != (size_t)len) {
        fclose(file);
        free(data);
        fprintf(stderr, "Erreur lors de la lecture du fichier %s\n", filename);
        return -1;
    }
    data[len] = '\0';
    fclose(file);
    
    cJSON *json = cJSON_Parse(data);
    free(data);
    if (!json) {
        fprintf(stderr, "Erreur de parsing JSON dans %s\n", filename);
        return -1;
    }
    
    cJSON *technical = cJSON_GetObjectItemCaseSensitive(json, "TechnicalIndicators");
    if (cJSON_IsObject(technical)) {
        cJSON *sma_20 = cJSON_GetObjectItemCaseSensitive(technical, "SMA_20");
        cJSON *sma_50 = cJSON_GetObjectItemCaseSensitive(technical, "SMA_50");
        cJSON *ema_20 = cJSON_GetObjectItemCaseSensitive(technical, "EMA_20");
        cJSON *ema_50 = cJSON_GetObjectItemCaseSensitive(technical, "EMA_50");
        cJSON *rsi_14 = cJSON_GetObjectItemCaseSensitive(technical, "RSI_14");
        cJSON *macd = cJSON_GetObjectItemCaseSensitive(technical, "MACD");
        cJSON *macd_signal = cJSON_GetObjectItemCaseSensitive(technical, "MACD_Signal");
        cJSON *macd_hist = cJSON_GetObjectItemCaseSensitive(technical, "MACD_Hist");
        
        if (cJSON_IsNumber(sma_20)) etf->technical_indicators.SMA_20 = sma_20->valuedouble;
        if (cJSON_IsNumber(sma_50)) etf->technical_indicators.SMA_50 = sma_50->valuedouble;
        if (cJSON_IsNumber(ema_20)) etf->technical_indicators.EMA_20 = ema_20->valuedouble;
        if (cJSON_IsNumber(ema_50)) etf->technical_indicators.EMA_50 = ema_50->valuedouble;
        if (cJSON_IsNumber(rsi_14)) etf->technical_indicators.RSI_14 = rsi_14->valuedouble;
        if (cJSON_IsNumber(macd)) etf->technical_indicators.MACD = macd->valuedouble;
        if (cJSON_IsNumber(macd_signal)) etf->technical_indicators.MACD_Signal = macd_signal->valuedouble;
        if (cJSON_IsNumber(macd_hist)) etf->technical_indicators.MACD_Hist = macd_hist->valuedouble;
    }
    
    cJSON_Delete(json);
    return 0;
}
