import streamlit as st
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


st.set_page_config(page_title=f"Chat with Project", page_icon="📚")

if "id" not in st.query_params:
    st.markdown('''
                # 🚨❌⚠️🚨 Look like you Find New World
                
                # No Problem!!
    
                ## To Chat with our AI Bot you can click 👉 <a href="https://chat.agilesync.co/?id=1" target="_self">Here!</a>
                ''', unsafe_allow_html=True)
    
    st.error("Url Is Not Correct. Please Provide the Correct Url")
    
    st.stop()

if "chat_engine" not in st.session_state.keys():
    with st.spinner(text="Loading and indexing the Documents – hang tight! This should take 1-2 minutes."):

        llm = Gemini(model="gemini-pro",api_key=st.secrets["GOOGLE_GEMINI_AI"])
        embed_model = GeminiEmbedding(api_key=st.secrets["GOOGLE_GEMINI_AI"])  # Fix typo
        service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)  # Fix variable name
        global data


        project_id = st.query_params["id"]

        client = MongoClient(st.secrets["MONGO_URI"])
        db = client[st.secrets["DB_NAME"]]
        collection = db["projects"]
        data = collection.find_one({"project_id": int(project_id)})
        
        if not data:
            st.error("Url Is Not Correct. Please Provide the Correct Url")
            st.markdown('''
            # 🚨❌⚠️🚨
                        
            ## *Oops! Looks like you've taken a wrong turn. Let's get you back on track!*
                        
            #### **you can visit as @[homepage](https://agilesync.co) for more information.**
        ''')
            

            st.stop()
        file_url = data["documents"]

        global project_title
        project_title = data["title"]


        try:
            # make dir of project_id
            os.mkdir(f"data/{project_id}")
            url = file_url
            r = requests.get(url, stream = True)
            with open(f"data/{project_id}/{project_id}.pdf","wb") as pdf:
                shutil.copyfileobj(r.raw, pdf)
        except:
            pass

        reader = SimpleDirectoryReader(f"data/{project_id}")
        documents = reader.load_data()

        index = VectorStoreIndex.from_documents(documents=documents, service_context=service_context)
    st.session_state.title = project_title
    st.session_state.owner = data["owner"]
    st.session_state.chat_engine = index.as_chat_engine(chat_mode="context", verbose=True)
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=st.secrets["GOOGLE_GEMINI_AI"], temperature=0.1)
    st.session_state.langchain_chat_engine = ConversationChain(llm=llm, verbose=True, memory=ConversationBufferMemory())





st.title(f"Chat With The Project {st.session_state.title}")

st.info(f"For more information about the project, contact @ {st.session_state.owner}")
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me questions ..."}
    ]
prompt = st.chat_input("Your question")

if prompt:  
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":   
    with st.spinner("Thinking..."):
        response = st.session_state.chat_engine.chat(prompt)
        response = response.response

        template = ChatPromptTemplate.from_messages([
                ("system", "Act as the AI Bot Which Give the Answer of the Question asked by the User. Using the Context which will be provided. Do not give the answer which is not relevant to the context. If the question is irrelevant with respect to the context then, kindly suggest to contact developer. Do not give incorrect answer. Context:  `{response}`"),
                ("human", st.session_state.messages[-1]["content"]),
                ("ai", st.session_state.messages[-2]["content"]),
                ("human", "{user_input}"),
            ])  
        messages1 = template.format_messages(
                user_input=prompt,
                response=response
            )
        response = st.session_state.langchain_chat_engine.predict(input=messages1)
        response = response.replace("AIMessage(content='", "").replace("')", "")
        st.write(response)
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)
