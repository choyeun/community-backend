from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
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

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    author_id = Column(Integer)

Base.metadata.create_all(bind=engine)

def clear_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup")
def signup(user: UserCreate):
    session = SessionLocal()

    existing_user = session.query(User).filter_by(username=user.username).first()
    if existing_user:
        return {"success": False, "message": "이미 등록된 사용자입니다."}

    new_user = User(username=user.username, password=user.password)
    session.add(new_user)
    session.commit()

    return {"success": True, "message": "회원 가입이 완료되었습니다."}

@app.post("/signin")
def signin(user: UserCreate):
    session = SessionLocal()

    existing_user = session.query(User).filter_by(username=user.username).first()
    if not existing_user:
        return {"success": False, "message": "등록되지 않은 사용자입니다."}

    if user.password != existing_user.password:
        return {"success": False, "message": "잘못된 비밀번호입니다."}

    return {"success": True, "message": "로그인 성공"}

def get_current_user(username: str, password: str, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter_by(username=username).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user


@app.get("/clear")
def clear():
    clear_database()
    return {"message": "Database cleared."}


class PostCreate(BaseModel):
    title: str
    content: str


@app.post("/posts")
def create_post(post: PostCreate, user: User = Depends(get_current_user)):
    session = SessionLocal()

    new_post = Post(title=post.title, content=post.content, author_id=user.id)
    session.add(new_post)
    session.commit()

    return {"message": "게시글이 생성되었습니다."}


@app.put("/posts/{post_id}")
def update_post(post_id: int, post: PostCreate, user: User = Depends(get_current_user)):
    session = SessionLocal()

    existing_post = session.query(Post).filter_by(id=post_id).first()
    if not existing_post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    if existing_post.author_id != user.id:
        raise HTTPException(status_code=403, detail="게시글을 수정할 권한이 없습니다.")

    existing_post.title = post.title
    existing_post.content = post.content
    session.commit()

    return {"message": "게시글이 수정되었습니다."}


@app.delete("/posts/{post_id}")
def delete_post(post_id: int, user: User = Depends(get_current_user)):
    session = SessionLocal()

    existing_post = session.query(Post).filter_by(id=post_id).first()
    if not existing_post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    if existing_post.author_id != user.id:
        raise HTTPException(status_code=403, detail="게시글을 삭제할 권한이 없습니다.")

    session.delete(existing_post)
    session.commit()

    return {"message": "게시글이 삭제되었습니다."}


@app.get("/posts/{post_id}")
def get_post(post_id: int, db: SessionLocal = Depends(get_db)):
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post

