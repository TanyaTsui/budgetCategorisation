# 🧾 Personal Finance with ChatGPT

This project uses the ChatGPT API to categorize bank and credit card transactions based on their descriptions. It's a lightweight way to get more insight into where your money is going—especially if your bank doesn't do this for you.

## 📌 What It Does

1. **Extracts tables from PDF credit card statements**
2. **Cleans and combines bank and credit card transactions into one CSV**
3. **Uses the ChatGPT API to categorize each transaction (e.g., groceries, rent, transport)**

## 🔧 How It Works

### `PdfStatementExtractor()`
Converts credit card statement PDFs into `.csv` files using the ChatGPT API. The assistant is prompted to extract transactions in plain CSV format with standardized fields.

### `BankStatementPreprocessor()`
Cleans and combines bank and credit card `.csv` files. Also auto-labels known transactions like rent and savings to save API calls.

### `BankStatementCategoriser()`
Sends transaction descriptions in batches to a ChatGPT assistant and receives back labeled categories.

## 💡 Why Use This?

- Your bank doesn't categorize transactions
- You want more control than most budgeting apps offer
- You’re curious about using the ChatGPT API for lightweight automation
- It’s fast and cheap (400 rows ≈ $0.30 in API costs)

## 🚀 Getting Started

1. Clone the repo  
2. Set your OpenAI API key in a `.env` file:

    ```env
    OPENAI_API_KEY=your_key_here
    ```

3. Run the scripts:

    ```python
    PdfStatementExtractor().run()
    BankStatementPreprocessor().run()
    BankStatementCategoriser().run()
    ```

## 📝 Notes

- Uses the `gpt-4o` model via OpenAI's [Assistants API](https://platform.openai.com/docs/assistants).
- Instructions to the assistant are carefully designed to return machine-readable outputs (e.g., plain CSV, numbered lists).
- Works best with Dutch bank data, but can be adapted.

