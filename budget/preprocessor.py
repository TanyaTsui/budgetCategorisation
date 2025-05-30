import pandas as pd 

class BankStatementPreprocessor(): 
    
    def __init__(self, bankStatement_path, time_period): 
        self.creditCardStatement_path = f'data/processed/creditCardStatements_{time_period}.csv'
        self.bankStatement_path = bankStatement_path
        self.processed_csv_path = f'data/processed/statements_combined_{time_period}.csv'

    def run(self): 
        self.preprocess_bank_statements() 
        self.preprocess_creditcard_statements()
        self.combine_statements()

    def preprocess_bank_statements(self): 
        # bankStatement_path = "data/raw/bank_account/2024Oct_2025Mar_abnamro.csv"
        df = pd.read_csv(self.bankStatement_path, index_col=False)
        df = df[~df.description.str.contains('NL13ZZZ332005960000')]

        if 'category' not in df.columns:
            df['category'] = None
        df['description'] = df['description'].fillna("")
        df.rename(columns={'transactiondate': 'date'}, inplace=True)
        df['date'] = pd.to_datetime(df.date, format='%Y%m%d')
        
        df = df[['date', 'amount', 'description', 'category']]
        self.bankStatement_df = df 

    def preprocess_creditcard_statements(self): 
        # creditCardStatement_path = 'data/processed/creditCardStatements.csv'
        df = pd.read_csv(self.creditCardStatement_path)
        df = df[df.amount < 0] 
        df['category'] = None 

        df['date'] = pd.to_datetime(df.date, format='%d/%m/%y')
        df = df[['date', 'description', 'amount', 'category']]
        self.creditCardStatement_df = df 

    def combine_statements(self): 
        combined = pd.concat([self.bankStatement_df, self.creditCardStatement_df])
        combined.to_csv(self.processed_csv_path, index=False)

