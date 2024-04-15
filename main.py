import streamlit as st
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
from llama_index.core import ServiceContext



from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate  # Fix import


from pymongo import MongoClient

import os
import requests
import shutil

if "id" not in st.query_params:
    st.error("Url Is Not Correct. Please Provide the Correct Url")
    st.markdown('''
    # 🚨❌⚠️🚨
                

    ## *Oops! Looks like you've taken a wrong turn. Let's get you back on track!*
                
    #### **you can visit as [@homepage](https://agilesync.co) for more information.**
''')
    st.stop()
