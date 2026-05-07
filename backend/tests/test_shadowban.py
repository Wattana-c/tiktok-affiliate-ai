from datetime import datetime, timedelta
import uuid
import pytest
from app.models.account import Account
from app.models.post_queue import PostQueue
from app.services.posting.shadowban_detector import check_and_update_shadowban

def test_shadowban_logic():
    from app.db.database import SessionLocal
    db = SessionLocal()

    # Create account
    uid = str(uuid.uuid4())
    acc = Account(platform="tiktok", account_name=f"sb_test_{uid}")
    db.add(acc)
    db.commit()
    db.refresh(acc)

    # Need at least 15 posts to test shadowban logic properly
    # 5 baseline posts (high views)
    for i in range(5):
        q = PostQueue(account_id=acc.id, status="posted", views=10000, posted_time=datetime.now() - timedelta(days=2))
        db.add(q)

    # 10 recent posts (very low views) - Drop is 10000 to 10 (99.9% drop)
    for i in range(10):
        q = PostQueue(account_id=acc.id, status="posted", views=10, posted_time=datetime.now() - timedelta(minutes=i))
        db.add(q)

    db.commit()

    # Run detector
    is_sb = check_and_update_shadowban(acc.id, db)

    # Assert detection triggers
    assert is_sb == True

    # Assert DB reflects
    db.refresh(acc)
    assert acc.is_shadowbanned == True

    # Check latest post error message is populated with reason
    latest_post = db.query(PostQueue).filter(PostQueue.account_id == acc.id).order_by(PostQueue.posted_time.desc()).first()
    assert "Shadowban detected" in latest_post.error_message

    db.close()
