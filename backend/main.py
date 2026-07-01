from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import random
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, SessionLocal
from models import Base, Telemetry, Incident
from routers import auth_router, incidents_router, telemetry_router
from seed_data import seed_data


from database import get_db
from auth import get_current_user
from models import Base, Telemetry, Incident, User

async def generate_telemetry():
    subsystems = {
        'smart_home': {
            'energy_usage': {'value': 5.0, 'unit': 'kW', 'min': 0, 'max': 10},
            'occupancy': {'value': 3, 'unit': 'persons', 'min': 0, 'max': 10},
            'temperature': {'value': 22.0, 'unit': '°C', 'min': 15, 'max': 30},
        },
        'autonomous_car': {
            'battery_level': {'value': 80.0, 'unit': '%', 'min': 0, 'max': 100},
            'speed': {'value': 45.0, 'unit': 'km/h', 'min': 0, 'max': 120},
        },
        'smart_train': {
            'speed': {'value': 60.0, 'unit': 'km/h', 'min': 0, 'max': 150},
            'passenger_count': {'value': 100, 'unit': 'persons', 'min': 0, 'max': 300},
        },
        'ev_charging': {
            'power_output': {'value': 7.2, 'unit': 'kW', 'min': 0, 'max': 22},
            'state_of_charge': {'value': 50.0, 'unit': '%', 'min': 0, 'max': 100},
        },
        'smart_parking': {
            'occupied_spaces': {'value': 20, 'unit': 'spaces', 'min': 0, 'max': 50},
            'turnover_rate': {'value': 3.5, 'unit': 'cars/hour', 'min': 0, 'max': 10},
        },
        'warehouse': {
            'inventory_level': {'value': 500, 'unit': 'items', 'min': 0, 'max': 1000},
            'temperature': {'value': 18.0, 'unit': '°C', 'min': 10, 'max': 25},
        }
    }

    prev_values = {}
    for sub, metrics in subsystems.items():
        for metric, info in metrics.items():
            prev_values[(sub, metric)] = info['value']

    while True:
        db = SessionLocal()
        try:
            for sub, metrics in subsystems.items():
                for metric, info in metrics.items():
                    delta = random.uniform(-0.5, 0.5)
                    new_val = prev_values[(sub, metric)] + delta
                    new_val = max(info['min'], min(info['max'], new_val))
                    prev_values[(sub, metric)] = new_val

                    telemetry = Telemetry(
                        subsystem=sub,
                        metric_key=metric,
                        metric_value=new_val,
                        unit=info['unit'],
                        recorded_at=datetime.utcnow()
                    )
                    db.add(telemetry)
            db.commit()
        except Exception as e:
            print(f"Error generating telemetry: {e}")
            db.rollback()
        finally:
            db.close()

        await asyncio.sleep(random.uniform(5, 10))

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        seed_data()
    except Exception as e:
        print(f"Warning: seed_data failed at startup: {e}")
    task = asyncio.create_task(generate_telemetry())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="NEXUS CITY OS Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # تم التعديل إلى False
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(incidents_router.router)
app.include_router(telemetry_router.router)

@app.get("/")
def root():
    return {"message": "NEXUS CITY OS Backend is running"}

@app.get("/dashboard/stats")
# def get_dashboard_stats(db: Session = Depends(SessionLocal)):
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    إحصائيات سريعة للـ Dashboard:
    - عدد الحوادث النشطة
    - عدد الأنظمة الفرعية (ثابت)
    - متوسط قيم telemetry لكل نظام (آخر قيمة مسجلة لكل متريك)
    """
    active_incidents = db.query(Incident).filter(Incident.status == 'active').count()
    total_subsystems = 6  # ثابت حسب التصميم

    # الحصول على أحدث قيمة لكل متريك في كل نظام
    latest_per_subsystem = {}
    subsystems = ['smart_home', 'autonomous_car', 'smart_train', 'ev_charging', 'smart_parking', 'warehouse']
    for sub in subsystems:
        latest = db.query(Telemetry).filter(Telemetry.subsystem == sub).order_by(Telemetry.recorded_at.desc()).first()
        if latest:
            # نأخذ آخر قيمة مسجلة (قد لا تكون لكل المتريك، لكنها تمثل أحدث نقطة)
            latest_per_subsystem[sub] = {
                'metric_key': latest.metric_key,
                'metric_value': latest.metric_value,
                'unit': latest.unit
            }
        else:
            latest_per_subsystem[sub] = None

    return {
        "active_incidents": active_incidents,
        "total_subsystems": total_subsystems,
        "latest_telemetry": latest_per_subsystem
    }