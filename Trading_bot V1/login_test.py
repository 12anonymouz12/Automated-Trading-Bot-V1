import json
from SmartApi import SmartConnect
import pyotp

# Load config
with open("config.json") as f:
    config = json.load(f)

creds = config["api_credentials"]

API_KEY = creds["api_key"]
CLIENT_CODE = creds["client_code"]
MPIN = creds["mpin"]
TOTP_SECRET = creds["totp_secret"]

# Initialize API
smart_api = SmartConnect(api_key=API_KEY)

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()

# Login
data = smart_api.generateSession(CLIENT_CODE, MPIN, totp)

if not data.get("status"):
    print("❌ Login failed:", data)
else:
    print("✅ Login successful!")
    print("Profile Info:", smart_api.getProfile(data["data"]["refreshToken"]))

    # Save tokens to config for later use
    creds["access_token"] = data["data"].get("jwtToken", "")
    creds["refresh_token"] = data["data"].get("refreshToken", "")
    creds["feed_token"] = data["data"].get("feedToken", "")

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
