#ifndef DATA_STRUCTURES_H
#define DATA_STRUCTURES_H

#include <time.h>

typedef struct {
    char ticker[10];
    char nom[100];
    char secteur[100];
    char domaine[100];
    time_t timestamp;
} ETFBaseInfo;

typedef struct {
    double SMA_20;
    double SMA_50;
    double EMA_20;
    double EMA_50;
    double RSI_14;
    double MACD;
    double MACD_Signal;
    double MACD_Hist;
} TechnicalIndicators;

typedef struct {
    char *date;
    double total_assets;
    double total_liabilities;
    double equity;
} BalanceSheet;

typedef struct {
    char *date;
    double revenue;
    double net_income;
} IncomeStatement;

typedef struct {
    char *date;
    double operating_cash_flow;
    double investing_cash_flow;
    double financing_cash_flow;
} CashFlow;

typedef struct {
    char *date;
    char firm[100];
    char to_grade[10];
    char from_grade[10];
    char action[10];
} Recommendation;

typedef struct {
    char *key;
    char **values;
    size_t count;
} CalendarEvent;

typedef struct {
    ETFBaseInfo base_info;
    TechnicalIndicators technical_indicators;
    BalanceSheet *balance_sheets;
    size_t balance_sheet_count;
    IncomeStatement *income_statements;
    size_t income_statement_count;
    CashFlow *cash_flows;
    size_t cash_flow_count;
    Recommendation *recommendations;
    size_t recommendation_count;
    CalendarEvent calendar;
} ETFData;

void init_etf_data(ETFData *etf);
void free_etf_data(ETFData *etf);

int parse_indicator_json(const char *filename, ETFData *etf);
int parse_financials_json(const char *filename, ETFData *etf);
int parse_technical_json(const char *filename, ETFData *etf);
int parse_additional_json(const char *filename, ETFData *etf);

#endif // DATA_STRUCTURES_H
