import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from src.database.operations import db
from src.database.models import CoordinatorTrigger, TriggerStatus

def clean_triggers():
    print("🧹 Cleaning up Active Triggers...")
    with db.get_session() as session:
        # Find all ACTIVE triggers
        triggers = session.query(CoordinatorTrigger).filter(
            CoordinatorTrigger.status == TriggerStatus.ACTIVE
        ).all()
        
        count = 0
        for t in triggers:
            t.status = TriggerStatus.TRIGGERED # Or CANCELLED
            count += 1
            
        print(f"✅ Deactivated {count} triggers. (Status set to TRIGGERED)")

if __name__ == "__main__":
    clean_triggers()
