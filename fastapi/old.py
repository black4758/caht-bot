import os
import io
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pinecone import Pinecone, ServerlessSpec
import fitz  # PyMuPDF 라이브러리
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- 초기화 ---

# FastAPI 앱 생성
app = FastAPI(title="PDF Q&A API with PyMuPDF and Gemini")

# 텍스트 캐시 디렉토리 생성
TEXT_CACHE_DIR = "text_cache"
os.makedirs(TEXT_CACHE_DIR, exist_ok=True)

# Pinecone 클라이언트 초기화
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
if not pinecone_api_key or not pinecone_environment:
    raise RuntimeError("PINECONE_API_KEY and PINECONE_ENVIRONMENT must be set.")
pc = Pinecone(api_key=pinecone_api_key)

# UpstageEmbeddings는 그대로 사용합니다.
upstage_api_key = os.getenv("UPSTAGE_API_KEY")
if not upstage_api_key:
    raise RuntimeError("UPSTAGE_API_KEY environment variable must be set.")
from langchain_upstage import UpstageEmbeddings
embeddings = UpstageEmbeddings(api_key=upstage_api_key, model="solar-embedding-1-large")


# Gemini LLM 모델 초기화
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# 텍스트 분할기 인스턴스 생성
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)

INDEX_NAME = "card"
EMBEDDING_DIMENSION = 4096

# 인덱스 존재 여부 확인 후 없으면 생성
if INDEX_NAME not in pc.list_indexes().names():
    print(f"Creating a new Pinecone index: {INDEX_NAME} with dimension {EMBEDDING_DIMENSION}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=pinecone_environment
        )
    )

# --- API 엔드포인트 ---

@app.post("/upsert-pdf/")
async def upsert_pdf(
    title: str = Form(...),
    file: UploadFile = File(...)
):
    """
    PDF 파일에서 직접 텍스트를 추출하고, 조각으로 나눈 후 임베딩하여 Pinecone에 저장합니다.
    추출된 텍스트는 파일로 캐싱하여 재사용합니다.
    """
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        index = pc.Index(INDEX_NAME)
        dummy_vector = [0.0] * EMBEDDING_DIMENSION
        
        existing_vectors = index.query(
            vector=dummy_vector,
            filter={'pdf_title': title},
            top_k=1,
            include_metadata=False,
            include_values=False
        )

        if existing_vectors['matches']:
            raise HTTPException(
                status_code=409,
                detail=f"ID '{title}'는 이미 존재합니다. 다른 제목을 사용해주세요."
            )

        text_file_path = os.path.join(TEXT_CACHE_DIR, f"{title}.txt")

        if os.path.exists(text_file_path):
            print(f"Loading text from cache: {text_file_path}")
            with open(text_file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            print("No cache found. Extracting text directly from PDF with PyMuPDF...")
            pdf_content = await file.read()
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            
            text = " ".join(text_parts)
            doc.close()

            print(f"Saving text to cache: {text_file_path}")
            with open(text_file_path, "w", encoding="utf-8") as f:
                f.write(text)

        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

        chunks = text_splitter.split_text(text)
        embeddings_list = embeddings.embed_documents(chunks)

        vectors_to_upsert = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
            vector_id = f'{title}-{i}'
            vectors_to_upsert.append({
                'id': vector_id,
                'values': embedding,
                'metadata': {'original_text': chunk, 'pdf_title': title}
            })

        # ⚠️ [수정] Pinecone의 요청 크기 제한(4MB)을 피하기 위해 데이터를 배치로 나누어 업로드
        batch_size = 100  # 한 번에 업로드할 벡터 수
        print(f"Upserting {len(vectors_to_upsert)} vectors in batches of {batch_size}...")
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            print(f"Upserting batch {i // batch_size + 1}...")
            index.upsert(vectors=batch)

        return {
            "message": f"Successfully split into {len(chunks)} chunks, embedded, and stored!",
            "base_id": title,
            "chunk_count": len(chunks)
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/query-pdf/")
async def query_pdf( # ⚠️ [수정] 함수 이름의 '-'를 '_'로 변경
    title: str = Form(...),
    question: str = Form(...)
):
    """
    특정 PDF(title)에 대해 질문(question)하고 Gemini를 통해 답변을 받습니다.
    """
    try:
        vectorstore = PineconeVectorStore(
            index_name=INDEX_NAME,
            embedding=embeddings,
            text_key='original_text'
        )

        retriever = vectorstore.as_retriever(
            search_kwargs={'filter': {'pdf_title': title}}
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever
        )
 
        result = qa_chain.invoke(question)

        return {"answer": result['result'], "source_document_id": title}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during query: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the PDF Q&A API with PyMuPDF and Gemini"}
