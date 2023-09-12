# 데이터 마이그레이션 - 데이터 동기화 배치 프로그램

데이터 마이그레이션 진행 중, 발생하는 정합성이 틀어진 데이터에 대한 재동기화 배치 프로그램

## 1. 기술스택

- Python3.8
- FastAPI
- SQLite

## 2. 사용 목적

![마이그레이션 일괄 Insert 스토어드 프로시저](https://github.com/2023-team-judy-coding-test-study/coding-test/assets/70069253/dc0cf1e9-8696-491c-a42e-a61074e5237b)

1. 서비스 구조 개선을 위한 데이터 마이그레이션을 Batch Insert 방식의 스토어드 프로시저를 작성하여 진행
2. 시간이 지남에 따라 일부 데이터에 대해 구버전, 신버전 데이터의 정합성이 맞지 않는 것을 확인
3. 구버전 -> 신버전으로의 재동기화하고자 배치 프로그램 개발

## 2. 동작 방식

![정합성이 틀어진 데이터 재동기화](https://github.com/2023-team-judy-coding-test-study/coding-test/assets/70069253/dd3c4b9f-36dd-4eb3-af35-f1a0cb1b9199)

1. 서버 실행 후 `@scheduler.scheduled_job` 에 의해 설정한 시간에 배치 프로그램이 실행됨. (main.py)
2. 스케쥴러에 의해 실행되는 작업 실행 (tasks.py)
    1. 게시글 전체 조회
    2. 게시글 별 구버전 댓글 데이터를 ZeroOffest 방식으로 1000개씩 조회
    3. 불러온 데이터에 대해 재동기화 대상 데이터인지 유효성 검사
    4. 해당 데이터 관련 신버전 데이터 생성

작업(task) 일부 소스 코드

```python
# tasks.py/_sync_comment_from_v1_to_v2
def _sync_comment_from_v1_to_v2(db: Session, post_id: int):
    """
    V1 -> V2 데이터 동기화하는 함수
 
    :param db: DB 커넥션 객체
    :param post_id: 게시글 ID
    """
    start_id = 0
    chunk_size = 1000

    while start_id >= 0:
        # 1,000개 단위로 데이터 조회
        v1comments: List[V1Comment] = _find_chunk_v1comment_by(
            db=db,
            post_id=post_id,
            start_id=start_id,
            chunk_size=chunk_size
        )

        for v1comment in v1comments:
            # 동기화 대상 판별
            if _check_sync_target(db, v1comment) is False:
                continue

            # 관련 데이터 동기화
            _sync_comment_info(db, v1comment)

        # 다음 페이지 설정
        start_id = v1comments[-1].id if v1comments else -1
```

## 실행 방법

1. `sh init_server.sh`
    - 초기 설정
2. `alembic init migrations`
    - migrations 디렉터리와 alembic.ini 생성
3. `alembic.ini` 파일 내 소스 변경
    ```
   ...(생략)...
   sqlalchemy.url = sqlite:///./myapi.db
   ...(생략)...
    ```
4. `migrations/env.py` 파일 내 소스 변경
    ```
    (... 생략 ...)
    import models
    (... 생략 ...)
    # add your model's MetaData object here
    # for 'autogenerate' support
    # from myapp import mymodel
    # target_metadata = mymodel.Base.metadata
    target_metadata = models.Base.metadata
    (... 생략 ...)
    ```
5. `alembic revision --autogenerate`
    - 리비전 파일 생성
6. `alembic upgrade head`
    - 리비전 파일 생성
7. `sh start_server.sh`


