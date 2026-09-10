import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'shobhit_university_secret_key_2026_dev_key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_timetable')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'student_timetable')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    PORT = int(os.getenv('PORT', 5000))
