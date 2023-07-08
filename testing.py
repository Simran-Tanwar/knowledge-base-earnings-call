import openai
import os
from llama_index import SimpleDirectoryReader , VectorStoreIndex , load_index_from_storage, StorageContext
import pandas as pd
#from get_transcript import get_transcript
from functions import knowledge_base

openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"

folder_path = "D:/college stuff/Intern_Aviso/Knowlegde_base_earnings_call/transcript"

knowledge_base = knowledge_base()

# Get list of companies and ticker symbols
file_path = 'D:/college stuff/Intern_Aviso/Knowlegde_base_earnings_call/Companies.xlsx'
df = pd.read_excel(file_path, sheet_name="Sheet1")
company_names = df["Company"].tolist()
ticker_sym = df["Ticker Symbol"].tolist()

#Get transcript of companies
transcript_dict = {}
for company in company_names:
    transcript = knowledge_base.get_transcript(company, folder_path)
    transcript_dict[company] = transcript

#Get Index (vector data base)
docs = knowledge_base.load_docs(folder_path)
doc_id_dict = {}
ticker_symbols = {}
for i ,company in enumerate(company_names):
    ticker_symbols[company] = ticker_sym[i]
    docs[i].metadata = {"Ticker_symbol": ticker_symbols[company]}
    docs[i].doc_id = "EC_"+ticker_symbols[company]+"_"+company
    doc_id_dict[company] = docs[i].doc_id


index = knowledge_base.create_index(docs)
index.storage_context.persist("./storage")

#Get response
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)

company_name = input("Give company name, you want to query about.")
qs = ['What was the total revenue of {} for this quarter?',
      'How has the revenue growth rate changed compared to the previous period of the {}?',
      'Which product or market segments contributed the most to the overall revenue of the {}?'
      ]

company_qs = []
for i in range(len(qs)):
    q = qs[i].format(company_name)
    company_qs.append(q)

query_engine = index.as_query_engine()
response_arr = knowledge_base.get_response(query_engine,company_qs)
print(response_arr)
#print(response_arr['What was the total revenue of '+company_name+' for this quarter?'])
#print(response_dict['How has the revenue growth rate changed compared to the previous period of the '+company_name+'?'])
#print(response_dict['Which product or market segments contributed the most to the overall revenue of the '+company_name+'?'])




