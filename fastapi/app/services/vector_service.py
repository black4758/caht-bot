
from fastapi import HTTPException
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA

from app.core.dependencies import get_pinecone_index, embeddings, llm, text_splitter
from app.core.config import PINECONE_INDEX_NAME, EMBEDDING_DIMENSION

def upsert_text_to_pinecone(room_id: str, text: str):
    index = get_pinecone_index()

    dummy_vector = [0.0] * EMBEDDING_DIMENSION
    existing_vectors = index.query(
        vector=dummy_vector,
        filter={'room_id': room_id},
        top_k=1,
        include_metadata=False,
        include_values=False
    )

    if existing_vectors['matches']:
        raise HTTPException(
            status_code=409,
            detail=f"ID '{room_id}'는 이미 존재합니다. 다른 제목을 사용해주세요."
        )

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    chunks = text_splitter.split_text(text)
    embeddings_list = embeddings.embed_documents(chunks)

    vectors_to_upsert = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
        vector_id = f'{room_id}-{i}'
        vectors_to_upsert.append({
            'id': vector_id,
            'values': embedding,
            'metadata': {'original_text': chunk, 'room_id': room_id}
        })

    batch_size = 100
    print(f"Upserting {len(vectors_to_upsert)} vectors in batches of {batch_size}...")
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i + batch_size]
        print(f"Upserting batch {i // batch_size + 1}...")
        index.upsert(vectors=batch)
    
    return len(chunks)

def delete_vectors_by_room_id(room_id: str):
    index = get_pinecone_index()
    index.delete(filter={'room_id': room_id})
    print(f"Deleted vectors for room_id: {room_id}")

def query_from_pinecone(room_id: str, question: str) -> str:
    vectorstore = PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings,
        text_key='original_text'
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={'filter': {'room_id': room_id}}
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )

    result = qa_chain.invoke(question)
    return result['result']
