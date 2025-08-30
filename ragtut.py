import os
# if not os.getenv("GOOGLE_API_KEY"):
#     os.environ["GOOGLE_API_KEY"] = <YOUR_GOOGLE_API_KEY>
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("resume.pdf")
data = loader.load()
from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(data)
from langchain.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
load_dotenv()
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vector_store = Chroma.from_documents(docs, embeddings)
retriver = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
retrived_docs = retriver.get_relevant_documents("What is his Jee rank")
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",temperature=0.3, max_tokens=500)
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriver, question_answer_chain)
response = rag_chain.invoke({"input": "what are the skills mentioned in the resume?"})
print(response["answer"])
