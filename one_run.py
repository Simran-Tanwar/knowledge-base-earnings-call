from get_transcript import get_transcript
from functions import knowledge_base
import os
from constant import common_path

knowledge_base = knowledge_base()
get_transcript = get_transcript()

storage_path = common_path+"storage"

master_list = knowledge_base.list_companies()
ticker_sym = list(master_list)
company_names = list(master_list.values())

if os.path.isdir(storage_path):
    new_list = knowledge_base.list_companies(file_path=common_path+"new_list.xlsx")
    n_ticker_symbols = list(new_list)
    n_company_names = list(new_list.values())

    index = knowledge_base.edit_index(new_list)
    master_list = knowledge_base.list_companies()
    ticker_sym = list(master_list)
else:
    folder_path = common_path+"transcript"
    doc_list = [knowledge_base.read_docs(knowledge_base.save_transcript(company_ticker, folder_path), company_ticker) for company_ticker in ticker_sym]
    index = knowledge_base.create_index(doc_list)
    index.storage_context.persist("./storage")

#get_response
qs = ['What was the total revenue for this quarter?',
      'How has the revenue growth rate changed compared to the previous period?',
      'Which product or market segments contributed the most to the overall revenue?'
      ]
response_dict = {}
for company_ticker in ticker_sym:
    company_name = get_transcript.get_company_name(company_ticker)
    response_arr = []
    for q in qs:
        response = knowledge_base.query_ticker(company_ticker, q)
        response_arr.append(response)
    response_dict[company_name] = response_arr
print(response_dict)