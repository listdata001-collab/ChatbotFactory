#!/usr/bin/env python3
"""
Simple script to add database performance indices
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_indices():
    with app.app_context():
        try:
            # Critical indices for performance
            indices = [
                'CREATE INDEX IF NOT EXISTS idx_user_telegram_id ON "user"(telegram_id)',
                'CREATE INDEX IF NOT EXISTS idx_chat_bot_user ON chat_history(bot_id, user_telegram_id)', 
                'CREATE INDEX IF NOT EXISTS idx_chat_created_desc ON chat_history(created_at DESC)',
                'CREATE INDEX IF NOT EXISTS idx_kb_bot_id ON knowledge_base(bot_id)',
                'CREATE INDEX IF NOT EXISTS idx_bot_user_id ON bot(user_id)',
                'CREATE INDEX IF NOT EXISTS idx_user_subscription ON "user"(subscription_type)',
                'CREATE INDEX IF NOT EXISTS idx_bot_active ON bot(is_active)',
            ]
            
            for index_sql in indices:
                try:
                    db.session.execute(text(index_sql))
                    print(f"✅ {index_sql.split()[-1]}")
                except Exception as e:
                    if 'already exists' not in str(e).lower():
                        print(f"❌ {e}")
            
            db.session.commit()
            print("🚀 Performance indices added successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = add_indices()
    sys.exit(0 if success else 1)