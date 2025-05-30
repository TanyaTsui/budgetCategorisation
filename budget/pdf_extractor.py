import os 
from dotenv import load_dotenv
import pandas as pd 
import openai
import io 
import time 

class PdfStatementExtractor: 
    
    def __init__(self, folder_path, time_period): 
        print('PdfStatementExtractor initialised')
        self.folder_path = folder_path # folder where credit card statments are 
        self.csv_path = f'data/processed/creditCardStatements_{time_period}.csv'
    
    def run(self): 
        self.load_openai_client() 
        self.deleteOldCsv() 
        self.createAssistant()
        self.getFileNames() 
        for file_name in self.file_names: 
            self.messageAssistant(file_name)
            self.runAssistant()
            self.recordOutput() 

    def load_openai_client(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=api_key)

    def deleteOldCsv(self): 
        file_path = self.csv_path 
        if os.path.exists(file_path):
            os.remove(file_path)

    def createAssistant(self): 
        self.assistant = self.client.beta.assistants.create(
            name="PDF Extractor",
            instructions=(
                "You are a helpful assistant that extracts tables from credit card statement PDFs "
                "and returns them in CSV format."
            ),
            model="gpt-4o", 
            tools=[{"type": "file_search"}],
        )

    def getFileNames(self): 
        folder_path = self.folder_path
        self.file_names = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                           if os.path.isfile(os.path.join(folder_path, f))]

    def messageAssistant(self, file_name): 
        print(f'processing {file_name}...')
        message_file = self.client.files.create(
        file=open(file_name, "rb"), purpose="assistants"
        )

        self.thread = self.client.beta.threads.create(
        messages=[
            {
            "role": "user",
            "content": (
                            "This is a credit card statement. Extract all transactions as a table with columns: "
                            "['date', 'description', 'amount'].\n\n"
                            "change the transactiondate values to DD/MM/YY format. "
                            "Change the amount values into numbers (floats) - with 'bij' representing a positive number, and 'af' a negative number"
                            "Return the transactions in plain CSV format, including the header row. Enclose all fields in double quotes."
                            "Do not add explanations or formatting (such as ``````), just output the CSV text."
                        ),
            # Attach the new file to the message.
            "attachments": [
                { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
            ],
            }
        ]
        )

    def runAssistant(self): 
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )

        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run.id)
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run failed with status: {run_status.status}")
            time.sleep(2)

        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        self.output = messages.data[0].content[0].text.value
        # print("GPT output:\n", output)  # Optional: see what GPT returned

    def recordOutput(self): 
        csv_path = self.csv_path
        df = pd.read_csv(io.StringIO(self.output))
        if os.path.exists(csv_path): 
            df.to_csv(csv_path, mode='a', index=False, header=False)
        else: 
            df.to_csv(csv_path, mode='w', index=False, header=True)
        print(f'results saved to {csv_path}')
