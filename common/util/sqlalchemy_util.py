from database import SessionLocal


def transactional(func):
    def wrapper(*args, **kwargs):
        db = SessionLocal()
        try:
            result = func(db=db, *args, **kwargs)
            db.commit()

            return result

        except Exception as exc:
            db.rollback()
            raise exc
        finally:
            db.close()

    return wrapper
