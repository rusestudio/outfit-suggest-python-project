from dotenv import load_dotenv
import os

load_dotenv()

SERVICE_KEY = os.getenv("KMA_KEY_DCODE")
VWORLD_KEY = os.getenv("VWORLD_CODE")