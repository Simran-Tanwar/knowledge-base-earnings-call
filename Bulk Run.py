import openai
import os
from llama_index import SimpleDirectoryReader , VectorStoreIndex , load_index_from_storage, StorageContext
import pandas as pd
from get_transcript import get_transcript
from functions import knowledge_base

openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"

knowledge_base = knowledge_base()

folder_path = "D:/college stuff/Intern_Aviso/Knowlegde_base_earnings_call/transcript"

# Get list of companies and ticker symbols
file_path = 'D:/college stuff/Intern_Aviso/Knowlegde_base_earnings_call/Companies.xlsx'
df = pd.read_excel(file_path, sheet_name="Bulk run")
company_names = df["Company"].tolist()
ticker_sym = df["Ticker Symbol"].tolist()

#Get transcript of companies
transcript_dict = {}
for company in company_names:
    transcript = knowledge_base.get_transcript(company,folder_path)
    transcript_dict[company] = transcript

#Get Index (vector data base)
docs = knowledge_base.load_docs(folder_path)
data = knowledge_base.data(company_names,docs,ticker_sym)

index = knowledge_base.create_index(docs)
index.storage_context.persist("./storage")

#Get response
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine()
qs = ['What was the total revenue of {} for this quarter?',
      'How has the revenue growth rate changed compared to the previous period of the {}?',
      'Which product or market segments contributed the most to the overall revenue of the {}?'
      ]
response_dict = {}
response_arr = []
for company in company_names:
    company_qs = []
    for i in range(0,len(qs)):
        q = qs[i].format(company)
        company_qs.append(q)
    responses = []
    for i in range(0,len(company_qs)):
        response = query_engine.query(company_qs[i])
        responses.append(response)

    for i, response in enumerate(responses):
        response_dict = {
            "Company Name": company,
            "Ticker symbol": data[company]["ticker_symbol"],
            "Query": company_qs[i],
            "Response": response
        }
        response_arr.append(response_dict)

final_df = pd.DataFrame(response_arr)
final_df.to_excel('final_results.xlsx', index=False)