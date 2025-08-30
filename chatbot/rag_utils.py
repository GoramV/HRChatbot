import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from django.conf import settings

class RAGProcessor:
    def __init__(self):
        # Set Google API Key
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            max_tokens=500
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
        
        # Create system prompt
        self.system_prompt = (
            "You are an HR assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "questions about company HR policies. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise and professional."
            "\n\n"
            "{context}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", "{input}"),
            ]
        )
    
    def process_documents(self, documents):
        """Process a list of document objects and create a vector store"""
        all_docs = []
        
        for document in documents:
            # Create a temporary file to handle the document
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(document.file.read())
                temp_path = temp_file.name
            
            # Process based on document type
            if document.document_type == 'pdf':
                loader = PyPDFLoader(temp_path)
                docs = loader.load()
            else:  # txt
                loader = TextLoader(temp_path)
                docs = loader.load()
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            # Add to our document collection
            all_docs.extend(docs)
        
        # Split documents
        split_docs = self.text_splitter.split_documents(all_docs)
        
        # Create vector store
        vector_store = Chroma.from_documents(split_docs, self.embeddings)
        
        return vector_store
    
    def get_answer(self, vector_store, query):
        """Get answer for a query using the RAG system"""
        # Create retriever
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        
        # Create question-answer chain
        question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        
        # Create RAG chain
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        # Get response
        response = rag_chain.invoke({"input": query})
        
        return response["answer"]