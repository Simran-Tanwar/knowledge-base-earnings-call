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

