from fastapi import Depends
from sqlalchemy.orm import Session

from common.util.sqlalchemy_util import transactional
from database import get_db
from models import MappingComment, V2Comment, V1Comment, Post, User


@transactional
def create_dummy_data(db: Session = Depends(get_db)):
    """유저, 게시글, 댓글 정보를 초기화하는 함수

    :param db: 커넥션 객체
    """
    print("**초기 데이터 세팅 시작**\n")
    db.query(User).delete()
    db.query(Post).delete()
    db.query(V1Comment).delete()
    db.query(V2Comment).delete()
    db.query(MappingComment).delete()

    # 유저 생성
    print("1. 유저 생성")
    user = User(name="geunwoo", email="geunwoo.park.08@gmail.com", password="1234")
    db.add(user)
    db.flush()

    # 게시글 생성
    print("2. 유저 생성")
    post = Post(user_id=user.id, content="first post")
    db.add(post)
    db.flush()

    db.commit()

    # V1 댓글 생성 - 벌크 삽입 : 50만개
    print("3. V1 댓글 생성")
    items = [
        {
            "user_id": user.id,
            "post_id": post.id,
            "content": f"post_id: {post.id}의 {i}번째 댓글"
        } for i in range(1, 500000 + 1)]
    db.execute(
        V1Comment.__table__.insert(),
        items
    )
    db.flush()

    db.commit()

    # V2 댓글 생성 - 벌크 삽입 : 25만개
    print("4. V2 댓글 생성")
    items = [
        {
            "user_id": user.id,
            "post_id": post.id,
            "content": f"post_id: {post.id}의 {i}번째 댓글"
        } for i in range(1, 250000 + 1)]
    db.execute(
        V2Comment.__table__.insert(),
        items
    )

    # V1 댓글 - V2 댓글 매핑 데이터 생성 - 벌크 삽입 : 25만개
    print("5. V1 댓글 - V2 댓글 매핑 데이터 생성")
    items = [
        {
            "v1comment_id": i,
            "v2comment_id": i,
            "created_by": "MIGRATION"
        } for i in range(1, 250000 + 1)]
    db.execute(
        MappingComment.__table__.insert(),
        items
    )
    db.flush()

    db.commit()

    print("\n**초기 데이터 세팅 종료**")
