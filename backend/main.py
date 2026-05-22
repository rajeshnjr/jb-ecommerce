import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="JB E-Commerce API")
security = HTTPBasic()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "jb_secret2026")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/api/products")
def get_products(db: Session = Depends(database.get_db)):
    products = db.query(models.Product).all()
    return products

@app.get("/api/admin/dashboard")
def get_admin_dashboard(
    admin: str = Depends(get_current_admin), 
    db: Session = Depends(database.get_db)
):
    total_revenue = db.query(func.sum(models.Order.total_amount)).scalar() or 0.0
    items_sold = db.query(func.sum(models.OrderItem.quantity)).scalar() or 0
    recent_orders = db.query(models.Order).order_by(models.Order.created_at.desc()).limit(5).all()
    
    return {
        "total_revenue": total_revenue,
        "total_items_sold": items_sold,
        "recent_orders": recent_orders
    }
