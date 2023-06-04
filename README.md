
# 설치

- ```git clone https://github.com/choyeun/community-backend.git```
- ```cd community-backend```
- ```git branch develop/${your-name}```
- ```git checkout develop/${your-name}```
- ```python -m venv .venv```
- ```pip install -r requrierments.txt```

# 실행

- ```uvicorn main:app --reload --host:0.0.0.0 --port=8000```

# 업로드

- ```git add .```
- ```commit -m "바뀐 점"```
- ```push origin develop/${your-name}```
