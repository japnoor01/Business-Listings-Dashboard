"""
Business Listings Dashboard - FastAPI Backend
Connects to MySQL, provides REST APIs for dashboard data
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
import json
import logging
from dotenv import load_dotenv

# ─── Load environment variables from .env if present ─────────
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ─── Logging ────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── App ────────────────────────────────────────────────────
app = FastAPI(
    title="Business Listings Dashboard API",
    description="REST API for Business Listings Dashboard with MySQL backend",
    version="1.0.0"
)

# ─── CORS ───────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Database Configuration ─────────────────────────────────
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "business_dashboard")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLite fallback for demo (when MySQL unavailable)
SQLITE_URL = "sqlite:///./business_dashboard.db"

Base = declarative_base()

# ─── Models ─────────────────────────────────────────────────
class ListingMaster(Base):
    __tablename__ = "listing_master"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    source = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── Database Setup ─────────────────────────────────────────
def get_engine():
    """Try MySQL first, fall back to SQLite"""
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Connected to MySQL")
        return engine
    except Exception as e:
        logger.warning(f"⚠️  MySQL unavailable ({e}), using SQLite")
        engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
        return engine


engine = get_engine()
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Pydantic Schemas ────────────────────────────────────────
class ListingCreate(BaseModel):
    business_name: str = Field(..., max_length=255)
    category: str = Field(..., max_length=100)
    city: str = Field(..., max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    source: str = Field(..., max_length=50)


class ListingResponse(BaseModel):
    id: int
    business_name: str
    category: str
    city: str
    address: Optional[str]
    phone: Optional[str]
    source: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class BulkInsertRequest(BaseModel):
    listings: List[ListingCreate]


class CountItem(BaseModel):
    name: str
    count: int


class DashboardSummary(BaseModel):
    total_listings: int
    total_cities: int
    total_categories: int
    total_sources: int


# ─── Startup: Auto-seed data ─────────────────────────────────
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        count = db.query(ListingMaster).count()
        if count == 0:
            # Load and seed from JSON
            json_path = os.path.join(os.path.dirname(__file__), "data", "listings.json")
            if not os.path.exists(json_path):
                json_path = os.path.join(os.path.dirname(__file__), "..", "data", "listings.json")
            
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    data = json.load(f)
                
                batch = []
                for item in data:
                    listing = ListingMaster(
                        business_name=item["business_name"],
                        category=item["category"],
                        city=item["city"],
                        address=item.get("address"),
                        phone=item.get("phone"),
                        source=item["source"],
                        created_at=datetime.strptime(item["created_at"], "%Y-%m-%d %H:%M:%S")
                    )
                    batch.append(listing)
                
                db.bulk_save_objects(batch)
                db.commit()
                logger.info(f"✅ Seeded {len(batch)} listings from JSON")
            else:
                logger.warning("No listings.json found for seeding")
        else:
            logger.info(f"ℹ️  Database already has {count} listings")
    except Exception as e:
        logger.error(f"Startup seeding error: {e}")
        db.rollback()
    finally:
        db.close()


# ─── Routes ─────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"message": "Business Listings Dashboard API", "status": "running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        count = db.query(ListingMaster).count()
        return {"status": "healthy", "total_records": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── INSERT API ──────────────────────────────────────────────

@app.post("/api/listings/bulk", tags=["Listings"], summary="Bulk insert listings")
def bulk_insert_listings(request: BulkInsertRequest, db: Session = Depends(get_db)):
    """Bulk insert scraped business listings into the database"""
    try:
        objects = [
            ListingMaster(
                business_name=l.business_name,
                category=l.category,
                city=l.city,
                address=l.address,
                phone=l.phone,
                source=l.source,
            )
            for l in request.listings
        ]
        db.bulk_save_objects(objects)
        db.commit()
        return {"inserted": len(objects), "message": f"Successfully inserted {len(objects)} listings"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/listings", tags=["Listings"], response_model=ListingResponse, summary="Insert single listing")
def create_listing(listing: ListingCreate, db: Session = Depends(get_db)):
    """Insert a single business listing"""
    db_listing = ListingMaster(**listing.dict())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


# ─── FETCH ALL (with pagination) ─────────────────────────────

@app.get("/api/listings", tags=["Listings"], summary="Fetch paginated listings")
def get_listings(skip: int = 0, limit: int = 50, city: Optional[str] = None,
                 category: Optional[str] = None, source: Optional[str] = None,
                 db: Session = Depends(get_db)):
    """Fetch listings with optional filters and pagination"""
    query = db.query(ListingMaster)
    if city:
        query = query.filter(ListingMaster.city == city)
    if category:
        query = query.filter(ListingMaster.category == category)
    if source:
        query = query.filter(ListingMaster.source == source)
    
    total = query.count()
    listings = query.offset(skip).limit(limit).all()
    return {"total": total, "skip": skip, "limit": limit, "data": listings}


# ─── DASHBOARD APIS ───────────────────────────────────────────

@app.get("/api/dashboard/summary", tags=["Dashboard"], response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db)):
    """Get overall dashboard summary statistics"""
    from sqlalchemy import func, distinct
    total = db.query(ListingMaster).count()
    cities = db.query(func.count(distinct(ListingMaster.city))).scalar()
    categories = db.query(func.count(distinct(ListingMaster.category))).scalar()
    sources = db.query(func.count(distinct(ListingMaster.source))).scalar()
    return DashboardSummary(
        total_listings=total,
        total_cities=cities,
        total_categories=categories,
        total_sources=sources,
    )


@app.get("/api/dashboard/city-wise", tags=["Dashboard"], response_model=List[CountItem])
def get_city_wise(db: Session = Depends(get_db)):
    """Get city-wise business count"""
    from sqlalchemy import func
    results = (
        db.query(ListingMaster.city, func.count(ListingMaster.id).label("count"))
        .group_by(ListingMaster.city)
        .order_by(func.count(ListingMaster.id).desc())
        .all()
    )
    return [CountItem(name=r.city, count=r.count) for r in results]


@app.get("/api/dashboard/category-wise", tags=["Dashboard"], response_model=List[CountItem])
def get_category_wise(db: Session = Depends(get_db)):
    """Get category-wise business count"""
    from sqlalchemy import func
    results = (
        db.query(ListingMaster.category, func.count(ListingMaster.id).label("count"))
        .group_by(ListingMaster.category)
        .order_by(func.count(ListingMaster.id).desc())
        .all()
    )
    return [CountItem(name=r.category, count=r.count) for r in results]


@app.get("/api/dashboard/source-wise", tags=["Dashboard"], response_model=List[CountItem])
def get_source_wise(db: Session = Depends(get_db)):
    """Get source-wise business count"""
    from sqlalchemy import func
    results = (
        db.query(ListingMaster.source, func.count(ListingMaster.id).label("count"))
        .group_by(ListingMaster.source)
        .order_by(func.count(ListingMaster.id).desc())
        .all()
    )
    return [CountItem(name=r.source, count=r.count) for r in results]


@app.get("/api/dashboard/top-categories-by-city", tags=["Dashboard"])
def get_top_categories_by_city(city: str, limit: int = 5, db: Session = Depends(get_db)):
    """Get top categories for a specific city"""
    from sqlalchemy import func
    results = (
        db.query(ListingMaster.category, func.count(ListingMaster.id).label("count"))
        .filter(ListingMaster.city == city)
        .group_by(ListingMaster.category)
        .order_by(func.count(ListingMaster.id).desc())
        .limit(limit)
        .all()
    )
    return [{"name": r.category, "count": r.count} for r in results]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
