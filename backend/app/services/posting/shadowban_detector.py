import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.post_queue import PostQueue
from app.models.account import Account

logger = logging.getLogger(__name__)

def check_and_update_shadowban(account_id: int, db: Session) -> bool:
    """
    Evaluates if an account is shadowbanned based on a severe drop in recent views.
    Logic: If the average views of the last 10 posts drops by >80% compared
    to the historical baseline, the account is marked as shadowbanned.
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account or account.is_shadowbanned:
        return False

    # Get all posted items for this account, ordered by most recent first
    posts = db.query(PostQueue).filter(
        PostQueue.account_id == account_id,
        PostQueue.status == "posted",
        PostQueue.views.isnot(None)
    ).order_by(PostQueue.posted_time.desc()).all()

    # We need at least 15 posts to compare 10 recent against 5+ baseline
    if len(posts) < 15:
        return False

    recent_posts = posts[:10]
    baseline_posts = posts[10:]

    recent_views_sum = sum(p.views or 0 for p in recent_posts)
    baseline_views_sum = sum(p.views or 0 for p in baseline_posts)

    recent_avg = recent_views_sum / len(recent_posts)
    baseline_avg = baseline_views_sum / len(baseline_posts)

    if baseline_avg > 0 and recent_avg < (baseline_avg * 0.2):
        # Drop > 80%
        account.is_shadowbanned = True
        db.commit()
        db.refresh(account)

        reason = f"Shadowban detected for account {account.account_name} ({account_id}). Recent avg views: {recent_avg:.1f}, Baseline avg: {baseline_avg:.1f} (>80% drop)"
        logger.error(reason)

        # Log to the latest post as well
        if recent_posts:
            latest_post = recent_posts[0]
            latest_post.error_message = (latest_post.error_message or "") + f" | {reason}"
            db.commit()

        return True

    return False
