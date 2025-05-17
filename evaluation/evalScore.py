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

class ragResponseEvaluator:
    def __init__(self):
        self.openaiKey = os.getenv('OPENAIKEY')
        self.username_ = os.getenv('USER_NAME')
        self.password_ = os.getenv('PASSWORD')
        self.database_url_ = os.getenv('DATABASEURL')
        self.port_ = os.getenv('PORT')

    def ragsEvalPipeline(self, questions):  
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

        responses_score = []
        docs, scores = zip(*retriever.similarity_search_with_score(questions))
        for doc, score in zip(docs, scores):
            responses_score.append({'docs':doc,'score':score})

        k_ = [3,5,10]
        lambda_multi_ = [i*0.1 for i in range(1,10)]

        responses = []
        for i in k_:
            for j in lambda_multi_:
                retriever_ = retriever.as_retriever(search_type="mmr", search_kwargs={"k":i, "lambda_multi":j})
                responses.append({'k':i,'lambda':j,'response':retriever_.invoke(questions)})
        return responses_score, responses