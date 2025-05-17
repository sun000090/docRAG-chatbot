from langchain_community.document_loaders import FileSystemBlobLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import PyMuPDFParser

class dataReader:
    def __init__(self):
        self.locs = './docs'

    def dataReaders(self):
        loader = GenericLoader(
        blob_loader=FileSystemBlobLoader(
            path=self.locs,
            glob="*.pdf",
        ),
        blob_parser=PyMuPDFParser(),
        )

        docs = loader.load()

        return docs