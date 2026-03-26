import requests
import json
import pyotp

# ====== USER INPUTS ======
api_key     = "xleHKxHr"        # From Angel One Developer Dashboard
client_code = "AABL614325"    # e.g. P123456
mpin        = "2531"   # Your MPIN
totp_secret = "633B4JNLNM656U3P57P4XYMNDM"    # From Angel One's 2FA setup (base32 format)

# Generate TOTP
totp = pyotp.TOTP(totp_secret).now()
print(f"Generated TOTP: {totp}")

# Headers required by Angel One API
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-UserType": "USER",
    "X-SourceID": "WEB",
    "X-ClientLocalIP": "127.0.0.1",
    "X-ClientPublicIP": "YOUR_PUBLIC_IP",   # Find via https://ifconfig.me
    "X-MACAddress": "AA:BB:CC:DD:EE:FF",   # Use your actual MAC address
    "X-PrivateKey": api_key,
    "User-Agent": "Mozilla/5.0"            # Mimic a browser to avoid bot blocking
}

# Request payload
payload = {
    "clientcode": client_code,
    "mpin": mpin,
    "totp": totp
}

# API endpoint for MPIN login
url = "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByMpin"

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Handle response
try:
    data = response.json()
    print("Login Response:", json.dumps(data, indent=4))
except json.JSONDecodeError:
    print("Raw Response Text:", response.text)
