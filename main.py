from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# SQLite 데이터베이스 연결 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


class UserCreate(BaseModel):
    username: str
    password: str


Base.metadata.create_all(bind=engine)


def clear_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@app.post("/signup")
def signup(user: UserCreate):
    """
    회원 가입을 처리하는 핸들러 함수입니다.

    Parameters:
        - user (UserCreate): 회원 가입 요청으로 받은 UserCreate 모델의 인스턴스입니다.

    Returns:
        - dict: 회원 가입 성공 여부와 메시지를 담은 응답 딕셔너리를 반환합니다.
    """
    session = SessionLocal()

    # 이미 등록된 사용자인지 확인
    existing_user = session.query(User).filter_by(username=user.username).first()
    if existing_user:
        return {"success": False, "message": "이미 등록된 사용자입니다."}

    # 새로운 사용자 등록
    new_user = User(username=user.username, password=user.password)
    session.add(new_user)
    session.commit()

    return {"success": True, "message": "회원 가입이 완료되었습니다."}


@app.post("/signin")
def signin(user: UserCreate):
    """
    로그인을 처리하는 핸들러 함수입니다.

    Parameters:
        - user (UserCreate): 로그인 요청으로 받은 UserCreate 모델의 인스턴스입니다.

    Returns:
        - dict: 로그인 성공 여부와 메시지를 담은 응답 딕셔너리를 반환합니다.
    """
    session = SessionLocal()

    # 등록된 사용자인지 확인
    existing_user = session.query(User).filter_by(username=user.username).first()
    if not existing_user:
        return {"success": False, "message": "등록되지 않은 사용자입니다."}

    # 비밀번호 일치 여부 확인
    if user.password != existing_user.password:
        return {"success": False, "message": "잘못된 비밀번호입니다."}

    return {"success": True, "message": "로그인 성공"}


@app.get("/clear")
def clear():
    clear_database()
    return {"message": "Database cleared."}
