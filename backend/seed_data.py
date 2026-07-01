import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Incident
from auth import get_password_hash
from datetime import datetime, timedelta
import random

admin_password = os.environ.get("ADMIN_SEED_PASSWORD", "admin123")

def seed_data():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash(admin_password),
                role="admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("Admin user created")
        else:
            print("Admin user already exists")

        if db.query(Incident).count() == 0:
            subsystems = ['smart_home', 'autonomous_car', 'smart_train', 'ev_charging', 'smart_parking', 'warehouse']
            titles = [
                "Temperature sensor offline",
                "Battery low warning",
                "Communication failure",
                "Overheating detected",
                "Unauthorized access attempt",
                "Power surge",
                "Water leak detected",
                "Camera malfunction",
                "Network latency high",
                "System reboot required"
            ]
            severities = ['low', 'medium', 'high', 'critical']
            statuses = ['active', 'resolved']
            for i in range(random.randint(5, 10)):
                incident = Incident(
                    subsystem=random.choice(subsystems),
                    title=random.choice(titles) + f" #{i+1}",
                    description=f"Sample incident description for {titles[i % len(titles)]}",
                    severity=random.choice(severities),
                    status=random.choice(statuses),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 5), hours=random.randint(0, 23)),
                )
                if incident.status == 'resolved':
                    incident.resolved_at = incident.created_at + timedelta(hours=random.randint(1, 48))
                    incident.resolved_by = admin.id
                db.add(incident)
            db.commit()
            print(f"Created {db.query(Incident).count()} sample incidents")
        else:
            print("Incidents already exist, skipping seeding")

    finally:
        db.close()

if __name__ == "__main__":
    seed_data()