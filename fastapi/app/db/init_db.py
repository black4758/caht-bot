import asyncio
import urllib.parse  # 1. URL 인코딩을 위해 라이브러리를 import 합니다.
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from app.core.config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

# 2. config에서 가져온 비밀번호를 URL 인코딩 처리합니다.
# 이렇게 하면 비밀번호에 '@', '#', '?' 등 특수문자가 있어도 안전합니다.
encoded_password = urllib.parse.quote_plus(MYSQL_PASSWORD)

# 3. 인코딩된 비밀번호를 사용하여 데이터베이스 연결 URL을 생성합니다.
DATABASE_URL = f"mysql+aiomysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}/{MYSQL_DB}"

Base = declarative_base()

class Room(Base):
    __tablename__ = "rooms"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    title = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)


# echo=True는 실행되는 SQL 쿼리를 터미널에 출력해주는 옵션입니다. (디버깅에 유용)
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def init_db():
    """데이터베이스 테이블을 생성합니다."""
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Commented out to prevent data loss on startup
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """FastAPI DI를 위한 데이터베이스 세션 생성 함수입니다."""
    async with AsyncSessionLocal() as session:
        yield session

if __name__ == "__main__":
    # 이 스크립트를 직접 실행하면 데이터베이스 테이블이 생성됩니다.
    # 프로젝트 초기 설정 시 한 번만 실행하면 됩니다.
    print("Initializing database...")
    asyncio.run(init_db())
    print("Database initialized.")
