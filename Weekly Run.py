import openai
import os
from llama_index import SimpleDirectoryReader , VectorStoreIndex , load_index_from_storage, StorageContext, Document
import pandas as pd
from get_transcript import get_transcript
from functions import knowledge_base

openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"

knowledge_base = knowledge_base()

folder_path = "D:/college stuff/Intern_Aviso/Knowlegde_base_earnings_call/transcript"

storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)

file_path = 'D:/college stuff/Intern_Aviso/Knowlegde_base_earnings_call/Companies.xlsx'
df = pd.read_excel(file_path, sheet_name="Bulk run")
company_names = df["Company"].tolist()
ticker_sym = df["Ticker Symbol"].tolist()

docs = knowledge_base.load_docs(folder_path)
data = knowledge_base.data(company_names,docs,ticker_sym)

file_path = 'D:/college stuff/Intern_Aviso/Knowlegde_base_earnings_call/Companies.xlsx'
df = pd.read_excel(file_path, sheet_name="weekly run")
new_list = df["Company"].tolist()
new_ticker_sym = df["Ticker Symbol"].tolist()
new_ticker_symbols = {}
for i ,company in enumerate(new_list):
    new_ticker_symbols[company] =new_ticker_sym[i]
#print(new_ticker_symbols)


for company in company_names:
    if company in new_list:
        doc_id = data[company]["doc_id"]
        index.delete_ref_doc(ref_doc_id=doc_id,delete_from_docstore=True)
        transcript = "hello its updated transcript, total revenue is $80 millions."
        file_path = folder_path + "/" + company + '_new_transcript.txt'
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(transcript)
        doc = Document(text = transcript)
        doc.doc_id = doc_id
        doc.metadata = {"Ticker Symbol":data[company]["ticker symbol"]}
        #document = [doc]
        index.insert(doc)

for company in new_list:
    if company not in company_names:
        transcript = knowledge_base.get_transcript(company,folder_path)
        doc = Document(text = transcript)
        doc.metadata = {"Ticker Symbol": new_ticker_symbols[company]}
        data[company]["ticker symbols"] = new_ticker_symbols[company]
        doc.doc_id = "EC_"+data[company]["ticker symbols"]+"_"+company
        data[company]["doc_id"] = "EC_"+data[company]["ticker symbols"]+"_"+company

query_engine = index.as_query_engine()
response = query_engine.query('What was the total revenue of Walmart?')
print(response)