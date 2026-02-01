import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from src.database.operations import db
from src.database.models import Trade, Position

def clean_trades():
    print("🧹 Cleaning up DB...")
    with db.get_session() as session:
        # Delete Trades
        t_num = session.query(Trade).delete()
        # Delete Positions
        p_num = session.query(Position).delete()
        
        print(f"✅ Deleted {t_num} trades and {p_num} positions.")

if __name__ == "__main__":
    clean_trades()
