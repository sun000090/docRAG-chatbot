from src.dataIngestion import dataReader
import pandas as pd
import numpy as np
import psycopg
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from dotenv import load_dotenv
import os

load_dotenv()

class ragGenerator:
    def __init__(self):
        self.openaiKey = os.getenv('OPENAIKEY')
        self.username_ = os.getenv('USER_NAME')
        self.password_ = os.getenv('PASSWORD')
        self.database_url_ = os.getenv('DATABASEURL')
        self.port_ = os.getenv('PORT')

    def embeddingPipeline(self):
        documents = dataReader().dataReaders()
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small",
                              api_key=self.openaiKey)
        
        text_splitter = SemanticChunker(embeddings=embeddings, breakpoint_threshold_type='percentile')
        docs_ = text_splitter.create_documents(texts = [x.page_content for x in documents],
                                       metadatas = [x.metadata for x in documents])
        
        for i in range(len(docs_)):
            docs_[i].metadata['ids'] = i

        connection_ = f"postgresql://{self.username_}:{self.password_}@{self.database_url_}:{self.port_}"
        curr = psycopg.Connection.connect(conninfo=connection_)
        try:
            curr.execute('truncate table langchain_pg_embedding;')
            curr.commit()
            curr.close()
        except Exception as e:
            curr.close()

        connection = f"postgresql+psycopg://{self.username_}:{self.password_}@{self.database_url_}:{self.port_}"
        collection_name = "my_docs"

        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=collection_name,
            connection=connection,
            use_jsonb=True,
        )

        ids = [(str(i.metadata['source'])+'_'+str(i.metadata['page'])+'_'+str(i.metadata['ids'])) for i in docs_]
        vector_store.add_documents(docs_, ids=ids)
        return
    
    def ragsPipeline(self, questions):  
        connection = f"postgresql+psycopg://{self.username_}:{self.password_}@{self.database_url_}:{self.port_}"
        collection_name = "my_docs"

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small",
                              api_key=self.openaiKey)

        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=collection_name,
            connection=connection,
            use_jsonb=True,
        )

        retriever = vector_store
        retriever_ = retriever.as_retriever(search_type="mmr", search_kwargs={"k":10, "lambda_multi":0.35})

        template = '''System: You're a helpful chatbot AI who converse with user based on questions.
                    You utilize the context and enrich your response to provide accurate and
                    relevant answers.
                    Questions: {questions}
                    Context: {context}

                    Given the question and context provide accurate reponses.
                    Do not generate out of context responses.
                    '''
        
        llm = ChatOpenAI(model='gpt-4o-mini', 
                 temperature=0.35,
                 max_tokens=3000,
                 api_key= self.openaiKey)
        
        prompt = PromptTemplate.from_template(template)
        model_llm = prompt | llm

        data_ = []
        data_.append([x.page_content for x in retriever_.invoke(questions)])

        responses = model_llm.invoke({'questions':questions,'context':data_})
        return responses.content