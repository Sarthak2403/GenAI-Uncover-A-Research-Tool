import os
import streamlit as st
import pickle
import time
from langchain import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv()

llm = OpenAI(temperature=0.9, max_tokens=500) 

st.title("Uncover: News Research Tool 📈")
st.sidebar.title("News Article URLs")

urls=[]
file_path = "faiss_store_openai.pkl"
for i in range(3):
    url = st.sidebar.text_input(f"Article {i+1}", "") 
    urls.append(url)

process_url_clicked = st.sidebar.button("Process")

main_placeholder = st.empty()

if process_url_clicked:
    loader = UnstructuredURLLoader(urls=urls) 
    main_placeholder.text("Data Loading...Started...✅✅✅")
    data = loader.load()

    main_placeholder.text("Text Splitting...Started...✅✅✅")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " "],
        chunk_size=1000 )
    split_data = text_splitter.split_documents(data) 

    embeddings = OpenAIEmbeddings()

    vectorstore_openai = FAISS.from_documents(split_data, embeddings)
    main_placeholder.text("Embedding Vector Started Building...✅✅✅")
    time.sleep(2 )

    # with open(file_path, "wb") as f:
    #     pickle.dump(vectorstore_openai, f)
    vectorstore_openai.save_local("faiss_store_openai")
    with open(file_path, "wb") as f:
        pickle.dump("faiss_store_openai", f)
    
    vectorstore_openai = FAISS.load_local("faiss_store_openai", embeddings, allow_dangerous_deserialization=True)

query = main_placeholder.text_input("Question: ")

if query:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            vectorstore = pickle.load(f)
            embeddings = OpenAIEmbeddings()
            vectorstore_openai = FAISS.load_local("faiss_store_openai", embeddings, allow_dangerous_deserialization=True)
            chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever = vectorstore_openai.as_retriever())
            result = chain({"question": query}, return_only_outputs = True)
            st.header("Answer: ")
            st.write (result["answer"])
            sources = result.get("sources", "")
            if sources:
                st.subheader("Sources:")
                sources_list = sources.split("\n") 
                for source in sources_list:
                    st.write(source)

