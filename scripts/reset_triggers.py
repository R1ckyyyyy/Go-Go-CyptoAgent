import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from src.database.operations import db
from src.database.models import CoordinatorTrigger, TriggerStatus

def clear_pending_manual_triggers():
    print("🧹 Cleaning up stale MANUAL triggers...")
    with db.get_session() as session:
        # Find all ACTIVE triggers that are MANUAL
        triggers = session.query(CoordinatorTrigger).filter(
            CoordinatorTrigger.status == TriggerStatus.ACTIVE,
            CoordinatorTrigger.trigger_type == "MANUAL"
        ).all()
        
        count = 0
        for t in triggers:
            t.status = "CANCELLED"
            count += 1
            
        print(f"✅ Cancelled {count} stale manual triggers.")

if __name__ == "__main__":
    clear_pending_manual_triggers()
