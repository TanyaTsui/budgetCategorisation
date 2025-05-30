from budget.pdf_extractor import PdfStatementExtractor
from budget.preprocessor import BankStatementPreprocessor
from budget.categoriser import BankStatementCategoriser

def main(): 
    time_period = '2024Oct_2025Mar'
    creditCardStatements_folder_path = 'data/raw/credit_card'
    bankStatement_path = 'data/raw/bank_account/2024Oct_2025Mar_abnamro.csv'

    PdfStatementExtractor(creditCardStatements_folder_path, time_period).run()
    BankStatementPreprocessor(bankStatement_path, time_period).run()
    BankStatementCategoriser(time_period).run()
    
if __name__ == '__main__':
    main()
