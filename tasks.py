from typing import List

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from common.util.sqlalchemy_util import transactional
from database import get_db
from models import V1Comment, Post, MappingComment, V2Comment


@transactional
def task_comment_migration(db: Session = Depends(get_db)):
    """
    모든 게시글에 달린 댓글 정보를 V1 -> V2로 동기화
    :param db: DB 커넥션 객체
    """

    # 게시글 전체 조회
    posts: List[Post] = _find_all_post(db)

    # 게시글 관련 댓글 정보 동기화
    for post in posts:
        _sync_comment_from_v1_to_v2(db, post.id)


def _find_all_post(db: Session):
    items = db.query(Post).all()

    return items


def _sync_comment_from_v1_to_v2(db: Session, post_id: int):
    """
    V1 -> V2 데이터 동기화하는 함수
    :param db: DB 커넥션 객체
    :param post_id: 게시글 ID
    :return:
    """
    start_id = 0
    chunk_size = 1000

    while start_id >= 0:
        print(f"동기화 시작 comment_id: {start_id}\n")
        # 1,000개 단위로 데이터 조회
        v1comments: List[V1Comment] = _find_chunk_v1comment_by(
            db=db,
            post_id=post_id,
            start_id=start_id,
            chunk_size=chunk_size
        )
        print("v1comment 조회 성공")

        for v1comment in v1comments:
            # 동기화 대상 판별
            if _check_sync_target(db, v1comment) is False:
                continue

            # 관련 데이터 동기화
            _sync_comment_info(db, v1comment)
        print("v2comment 관련 데이터 생성 성공")

        # 다음 페이지 설정
        start_id = v1comments[-1].id if v1comments else -1
        print(f"\n동기화 종료 comment_id: {start_id}\n")


def _find_chunk_v1comment_by(db: Session, post_id: int, start_id=0, chunk_size=10000) -> List[V1Comment]:
    """
    Offset를 항상 0으로 설정하고, Chunk Size 만큼 데이터를 일괄 조회하는 함수
    :param db: 커넥션 객체
    :param post_id: 게시글 ID
    :param start_id: 조회 시작
    :param chunk_size: 조회할 데이터 크기
    :return:
    """
    query: Query = db.query(V1Comment)
    items = query.filter(V1Comment.post_id == post_id, V1Comment.id > start_id).limit(chunk_size).all()

    return items


def _check_sync_target(db: Session, v1comment: V1Comment) -> bool:
    if _valid_comment(v1comment) is False:
        return False

    if _has_already_mapping_comment(db, v1comment):
        return False

    return True


def _valid_comment(v1comment: V1Comment) -> bool:
    if not v1comment.id:
        return False

    if not v1comment.post_id:
        return False

    if v1comment.parent_comment_id:
        return False


def _has_already_mapping_comment(db: Session, v1comment: V1Comment) -> bool:
    query: Query = db.query(MappingComment)
    item = query.filter(MappingComment.v1comment_id == v1comment.id).first()

    if item:
        return True

    return False


def _sync_comment_info(db: Session, v1comment: V1Comment) -> None:
    """
    V1 정보와 연관된 여러 V2 데이터 동기화
    :param db: 커넥션 객체
    :param v1comment: V1 댓글
    :return:
    """
    v2comment: V2Comment = _create_v2comment(db, v1comment)
    mapping_comment: MappingComment = _create_mapping_comment(db, v1comment, v2comment)


def _create_v2comment(db, v1comment) -> V2Comment:
    v2comment = V2Comment(
        user_id=v1comment.user_id,
        post_id=v1comment.post_id,
        parent_comment_id=v1comment.parent_comment_id,
        content=v1comment.content,
        delete_yn=v1comment.delete_yn,
        created_at=v1comment.created_at,
    )

    db.add(v2comment)
    db.flush()

    return v2comment


def _create_mapping_comment(db, v1comment, v2comment) -> MappingComment:
    mapping_comment = MappingComment(
        v1comment_id=v1comment.id,
        v2comment_id=v2comment.id,
        created_by="MIGRATION",
    )

    db.add(mapping_comment)
    db.flush()

    return mapping_comment


if __name__ == '__main__':
    task_comment_migration()
