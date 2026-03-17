from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from database import notices_collection, subscribers_collection, admins_collection
from email_utils import send_email
from bson import ObjectId
import pytz

app = FastAPI()

# ---------------- TIMEZONE ----------------
UTC = pytz.UTC
IST = pytz.timezone('Asia/Kolkata')

# ---------------- SCHEDULER ----------------
scheduler = BackgroundScheduler(timezone=UTC)
scheduler.start()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------------- HELPER FUNCTIONS ----------------

def get_utc_now():
    """Get current time in UTC"""
    return datetime.now(UTC)

def get_ist_now():
    """Get current time in IST"""
    return datetime.now(IST)

def parse_frontend_datetime(dt_string):
    """
    Parse datetime from frontend (browser sends IST time as naive string)
    Convert to UTC for storage in MongoDB
    """
    if not dt_string:
        return None
    
    try:
        # Frontend sends: "2026-03-15T17:29" (this is IST time from browser)
        # Parse as naive datetime
        naive_dt = datetime.fromisoformat(dt_string)
        
        # Attach IST timezone (because browser is in IST)
        ist_dt = IST.localize(naive_dt)
        
        # Convert to UTC for storage
        utc_dt = ist_dt.astimezone(UTC)
        
        print(f"📅 Frontend sent: {dt_string}")
        print(f"   Interpreted as IST: {ist_dt.strftime('%d %b %Y, %I:%M %p IST')}")
        print(f"   Converted to UTC: {utc_dt.strftime('%d %b %Y, %I:%M %p UTC')}")
        
        return utc_dt
        
    except Exception as e:
        print(f"❌ Error parsing datetime '{dt_string}': {e}")
        return None

def utc_to_ist_iso(utc_dt):
    """Convert UTC datetime to IST and return ISO string"""
    if not utc_dt:
        return None
    
    # Ensure it has UTC timezone
    if utc_dt.tzinfo is None:
        utc_dt = UTC.localize(utc_dt)
    
    # Convert to IST
    ist_dt = utc_dt.astimezone(IST)
    
    # Return ISO format (frontend will parse this correctly)
    return ist_dt.isoformat()

def delete_expired_notices():
    """Background job to delete expired notices"""
    current_time = get_utc_now()
    result = notices_collection.delete_many({
        "expiry_date": {"$lt": current_time}
    })
    if result.deleted_count > 0:
        ist_time = current_time.astimezone(IST)
        print(f"🗑️ Deleted {result.deleted_count} expired notices at {ist_time.strftime('%I:%M %p IST')}")

# Schedule cleanup every 5 minutes
scheduler.add_job(delete_expired_notices, 'interval', minutes=5)

# ---------------- MODELS ----------------

class Student(BaseModel):
    user_id: str
    name: str
    email: str
    password: str
    department: str
    year: int
    categories: list[str]

class Notice(BaseModel):
    title: str
    content: str
    category: str
    department: str = ""
    year: int = 0
    expiry_date: str = None

# ---------------- ADMIN LOGIN ----------------

@app.post("/admin/login")
def admin_login(data: dict):
    admin = admins_collection.find_one({
        "username": data["username"],
        "password": data["password"]
    })
    if admin:
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")

# ---------------- STUDENT REGISTER ----------------

@app.post("/student/register")
def student_register(student: Student):
    existing = subscribers_collection.find_one({"user_id": student.user_id})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    subscribers_collection.insert_one(student.dict())
    return {"message": "Student registered successfully"}

# ---------------- STUDENT LOGIN ----------------

@app.post("/student/login")
def student_login(data: dict):
    student = subscribers_collection.find_one({
        "user_id": data["user_id"],
        "password": data["password"]
    })
    if student:
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")

# ---------------- REMINDER FUNCTION ----------------

def send_expiry_reminder(notice_data, students):
    """Send reminder email before expiry"""
    for student in students:
        try:
            send_email(
                to_email=student["email"],
                subject=f"⏰ Reminder: {notice_data['title']} expires soon",
                body=f"{notice_data['content']}\n\nThis notice will expire in 24 hours."
            )
        except Exception as e:
            print(f"❌ Error sending reminder to {student['email']}: {e}")

# ---------------- ADD NOTICE ----------------

@app.post("/add_notice")
def add_notice(notice: Notice):
    # Get current time in UTC
    created_time_utc = get_utc_now()
    created_time_ist = created_time_utc.astimezone(IST)
    
    print(f"\n{'='*60}")
    print(f"📝 Creating notice: {notice.title}")
    print(f"⏰ Current time (IST): {created_time_ist.strftime('%d %b %Y, %I:%M %p')}")
    print(f"⏰ Current time (UTC): {created_time_utc.strftime('%d %b %Y, %I:%M %p')}")
    
    # Parse expiry date from frontend and convert to UTC
    expiry_date_utc = None
    if notice.expiry_date:
        expiry_date_utc = parse_frontend_datetime(notice.expiry_date)
    
    # If no expiry date, default to 30 days from now
    if not expiry_date_utc:
        expiry_date_utc = created_time_utc + timedelta(days=30)
        expiry_ist = expiry_date_utc.astimezone(IST)
        print(f"⏳ No expiry set, defaulting to 30 days: {expiry_ist.strftime('%d %b %Y, %I:%M %p IST')}")
    
    # Prepare notice document (store UTC times in MongoDB)
    notice_doc = {
        "title": notice.title,
        "content": notice.content,
        "category": notice.category,
        "created_at": created_time_utc,
        "expiry_date": expiry_date_utc
    }
    
    # Add optional fields
    if notice.department:
        notice_doc["department"] = notice.department
    if notice.year:
        notice_doc["year"] = notice.year
    
    # Insert to MongoDB
    result = notices_collection.insert_one(notice_doc)
    print(f"✅ Notice saved with ID: {result.inserted_id}")
    print(f"{'='*60}\n")

    # Find matching students
    student_query = {"categories": notice.category}
    if notice.department:
        student_query["department"] = notice.department
    if notice.year:
        student_query["year"] = notice.year
    
    students = list(subscribers_collection.find(student_query))

    # Send emails
    email_count = 0
    for student in students:
        try:
            send_email(
                to_email=student["email"],
                subject=f"📢 New Notice: {notice.title}",
                body=notice.content
            )
            email_count += 1
        except Exception as e:
            print(f"❌ Error sending email to {student['email']}: {e}")

    # Schedule reminder 24 hours before expiry
    reminder_time = expiry_date_utc - timedelta(minutes=5)#here we are changing
    if reminder_time > get_utc_now():
        scheduler.add_job(
            send_expiry_reminder,
            "date",
            run_date=reminder_time,
            args=[notice_doc, students]
        )

    # Return IST times to frontend
    return {
        "message": f"Notice added and emails sent to {email_count} students",
        "notice_id": str(result.inserted_id),
        "created_at": utc_to_ist_iso(created_time_utc),
        "expiry_date": utc_to_ist_iso(expiry_date_utc)
    }

# ---------------- GET ACTIVE NOTICES ----------------

@app.get("/notices")
def get_all_notices():
    """Get all non-expired notices"""
    current_time_utc = get_utc_now()
    
    # Find notices that haven't expired (compare UTC times)
    notices = list(notices_collection.find({
        "expiry_date": {"$gt": current_time_utc}
    }).sort("created_at", -1))

    # Convert to frontend format (IST times)
    for notice in notices:
        notice["_id"] = str(notice["_id"])
        
        # Convert UTC times to IST for display
        if "created_at" in notice and notice["created_at"]:
            notice["created_at"] = utc_to_ist_iso(notice["created_at"])
        
        if "expiry_date" in notice and notice["expiry_date"]:
            notice["expiry_date"] = utc_to_ist_iso(notice["expiry_date"])

    return notices

# ---------------- GET CATEGORY NOTICES ----------------

@app.get("/notices/{category}")
def get_category_notices(category: str):
    """Get non-expired notices for a specific category"""
    current_time_utc = get_utc_now()

    notices = list(notices_collection.find({
        "category": category,
        "expiry_date": {"$gt": current_time_utc}
    }).sort("created_at", -1))

    for notice in notices:
        notice["_id"] = str(notice["_id"])
        if "created_at" in notice and notice["created_at"]:
            notice["created_at"] = utc_to_ist_iso(notice["created_at"])
        if "expiry_date" in notice and notice["expiry_date"]:
            notice["expiry_date"] = utc_to_ist_iso(notice["expiry_date"])

    return notices

# ---------------- DELETE NOTICE ----------------

@app.delete("/notice/{notice_id}")
def delete_notice(notice_id: str):
    """Manually delete a notice"""
    try:
        result = notices_collection.delete_one({"_id": ObjectId(notice_id)})
        if result.deleted_count == 1:
            print(f"🗑️ Manually deleted notice: {notice_id}")
            return {"message": "Notice deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Notice not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid notice ID: {str(e)}")

# ---------------- HEALTH CHECK ----------------

@app.get("/")
def health_check():
    """Health check endpoint"""
    utc_time = get_utc_now()
    ist_time = get_ist_now()
    return {
        "status": "running",
        "utc_time": utc_time.isoformat(),
        "ist_time": ist_time.isoformat(),
        "ist_readable": ist_time.strftime('%d %b %Y, %I:%M %p IST'),
        "timezone_info": "Storing UTC, displaying IST"
    }

# ---------------- STARTUP EVENT ----------------

@app.on_event("startup")
async def startup_event():
    """Run cleanup on startup"""
    ist_time = get_ist_now()
    print("\n" + "="*60)
    print("🚀 Smart Notice Board API Started")
    print("="*60)
    print(f"⏰ Current IST Time: {ist_time.strftime('%d %b %Y, %I:%M %p')}")
    print(f"📍 Storage: UTC | Display: IST")
    print("🗑️ Running initial cleanup...")
    delete_expired_notices()
    print("✅ Server ready")
    print("="*60 + "\n")

# ---------------- SHUTDOWN EVENT ----------------

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    scheduler.shutdown()
    print("\n👋 API Stopped\n")