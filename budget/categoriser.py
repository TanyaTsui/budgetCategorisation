import openai 
import pandas as pd 
import os 
from dotenv import load_dotenv
import time 

class BankStatementCategoriser: 

    def __init__(self, time_period):
        self.gpt_model = 'gpt-4o'
        self.assistant_instructions = 'data/processed/assistant_instructions.txt' 

        self.bank_statement_path = f'data/processed/statements_combined_{time_period}.csv'
        self.results_path = f'results/statements_categorised_{time_period}.csv' 
        
        self.df = pd.read_csv(self.bank_statement_path) 
        self.batch_size = 20 

    def run(self): 
        self.load_openai_client() 
        self.delete_old_csv()
        self.create_assistant()
        for i in range(0, len(self.df), self.batch_size):
            self.get_descriptions(i)
            self.process_categorised_descriptions(i)

    def load_openai_client(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=api_key)

    def delete_old_csv(self): 
        file_path = self.results_path 
        if os.path.exists(file_path):
            os.remove(file_path)

    def create_assistant(self): 
        self.assistant = self.client.beta.assistants.create(
            name="Budget Categorisation Assistant",
            instructions=open(self.assistant_instructions).read(),
            model=self.gpt_model
        )

    def get_descriptions(self, i): 
        batch = self.df.iloc[i:i+self.batch_size]
        if batch['category'].notna().all():
            return # skip further processing 
        print(f"Processing rows {i}–{i + self.batch_size - 1} of {len(self.df)}")
        self.descriptions = batch['description'].tolist()

    def process_categorised_descriptions(self, i): 
        df = self.df 
        descriptions = self.descriptions

        try:
            categories = self.batch_categorize(descriptions)
            if len(categories) != len(descriptions):
                print("❌ Mismatch in returned categories, skipping this batch.")
                print(f'n descriptions: {len(descriptions)} - {descriptions}')
                print(f'n categories: {len(categories)} - {categories}')
                return

            df.loc[i:i+self.batch_size-1, 'category'] = categories
            df.to_csv(self.results_path, index=False)
            print(f"✅ Saved rows {i}–{i + self.batch_size - 1}")

        except Exception as e:
            print(f"❌ Error in batch {i}–{i + self.batch_size - 1}: {e}")
            return

    def batch_categorize(self, descriptions):
        # Number the descriptions to guide GPT
        numbered_descriptions = "\n".join([f"{i+1}. {desc}" for i, desc in enumerate(descriptions)])

        self.thread = self.client.beta.threads.create()
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=f'Descriptions: \n{numbered_descriptions}'
        )
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run failed with status: {run_status.status}")
            time.sleep(1)  # avoid hammering the API

        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        content = messages.data[0].content[0].text.value

        # Parse lines manually
        lines = content.splitlines()
        categories = []

        for line in lines:
            if "." in line:
                try:
                    _, category = line.split(".", 1)
                    categories.append(category.strip())
                except ValueError:
                    continue

        if len(categories) != 20:
            print(f"❌ GPT returned {len(categories)} categories instead of 20.")

        return categories