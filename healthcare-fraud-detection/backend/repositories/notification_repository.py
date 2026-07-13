"""
===========================================================
Healthcare Fraud Detection System
Notifications Repository
===========================================================

This module handles database queries and writes for notifications in Supabase.
"""

from typing import List, Dict, Any
from utils.supabase_client import supabase
from utils.logger import logger

def create_notification(recipient_id: int, message: str, severity: str = "info") -> bool:
    """
    Insert a new notification into Supabase.
    """
    try:
        payload = {
            "recipient_id": recipient_id,
            "message": message,
            "severity": severity,
            "read": False
        }
        res = supabase.table("notifications").insert(payload).execute()
        return bool(res.data)
    except Exception as e:
        logger.error(f"Error creating notification for user {recipient_id}: {e}")
        raise

def find_unread_notifications_by_recipient(user_id: int) -> List[Dict[str, Any]]:
    """
    Query unread notifications for a user, ordered by creation date descending.
    """
    try:
        res = supabase.table("notifications").select("*").eq("recipient_id", user_id).eq("read", False).order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        logger.error(f"Error finding unread notifications for user {user_id}: {e}")
        raise

def mark_notification_as_read(notification_id: int) -> bool:
    """
    Mark a specific notification as read in Supabase.
    """
    try:
        res = supabase.table("notifications").update({"read": True}).eq("notification_id", notification_id).execute()
        return bool(res.data)
    except Exception as e:
        logger.error(f"Error marking notification {notification_id} as read: {e}")
        raise
