import os
import faiss
import numpy as np
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI as GoogleChat
from langchain.chains import RetrievalQA

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_text_from_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    return docs

def create_vector_store(pdf_path):
    docs = extract_text_from_pdf(pdf_path)

    embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  
    vector_store = FAISS.from_documents(docs, embedding_model, allow_dangerous_deserialization=True)
    
    vector_store.save_local("vector_db")

def load_vector_store():
    return FAISS.load_local(
        "vector_db", 
        GoogleGenerativeAIEmbeddings(model="models/embedding-001"), 
        allow_dangerous_deserialization=True
    )

def generate_quiz(prompt, pdf_path):
    if not os.path.exists("vector_db/index.faiss"):
        create_vector_store(pdf_path)

    vector_store = load_vector_store()

    llm = GoogleChat(model="gemini-1.5-pro-latest", temperature=0.7)  # Use `model` instead of `model_name`

    qa_chain = RetrievalQA.from_chain_type(llm, retriever=vector_store.as_retriever())

    return qa_chain.run(prompt)