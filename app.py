from flask import Flask, request
import oracledb
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

# Connect to Oracle
connection = oracledb.connect(user="PROJECT", password="1234", dsn="localhost:1521/XEPDB1")
cursor = connection.cursor()

BANK_CUSTOMER_CARE = "+18001030123"  # Replace with actual number

@app.route("/handle_response", methods=["POST"])
def handle_response():
    """Handles customer response when they press 1."""
    
    print("🔹 Received Data:", request.form)  # Debugging Line

    call_sid = request.form.get("CallSid")
    digits = request.form.get("Digits")

    print(f"📞 Extracted CallSid: {call_sid}, Digits: {digits}")  # Debugging Line

    if digits == "1":
        cursor.execute("SELECT Account_No FROM CallLogs WHERE Call_Status = 'Initiated' ORDER BY Call_Date DESC FETCH FIRST 1 ROW ONLY")
        result = cursor.fetchone()
        
        if result:
            account_no = result[0]
            
            # Update CallLogs to record customer response
            cursor.execute("""
                UPDATE CallLogs SET Call_Status = 'Transferred' WHERE Account_No = :1 AND Call_Status = 'Initiated'
            """, (account_no,))
            connection.commit()

            response = VoiceResponse()
            response.say("You are being transferred to our customer care.")
            response.dial(BANK_CUSTOMER_CARE)
            return str(response)
    
    response = VoiceResponse()
    response.say("Invalid input. Goodbye.")
    return str(response)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
