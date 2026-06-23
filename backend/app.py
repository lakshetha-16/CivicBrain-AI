from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# Load API key from .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use currently available model
model = genai.GenerativeModel("gemini-2.5-flash")


def extract_json(raw):

    try:
        start = raw.find("{")
        end = raw.rfind("}")

        if start == -1 or end == -1:
            return None

        return json.loads(raw[start:end+1])

    except:
        return None


def fallback_analysis(text):

    text=text.lower()

    category="Other"
    department="Municipal Department"
    severity="Medium"
    score=60

    if any(x in text for x in ["garbage","waste","trash"]):
        category="Waste"
        department="Waste Management Department"
        score=95
        severity="High"

    elif any(x in text for x in ["road","traffic","pothole"]):
        category="Road"
        department="Road Transport Department"
        score=85
        severity="High"

    elif any(x in text for x in ["water","pipe","drain"]):
        category="Water"
        department="Water Supply Department"
        score=80
        severity="Medium"

    elif any(x in text for x in ["electricity","power"]):
        category="Electricity"
        department="Electricity Board"
        score=75
        severity="Medium"

    return {
        "category":category,
        "severity":severity,
        "risk":{
            "status":"Yes",
            "reason":"Health or public safety impact detected"
        },
        "department":department,
        "priority_score":score,
        "recommended_action":"Immediate field inspection and action required"
    }


@app.route("/analyze", methods=["POST"])
def analyze():

    data=request.get_json()
    text=data.get("text","")

    prompt=f"""
Return ONLY valid JSON.

Issue:
{text}

Format:

{{
"category":"string",
"severity":"Low|Medium|High",
"risk":{{
"status":"Yes or No",
"reason":"string"
}},
"department":"string",
"priority_score":number,
"recommended_action":"string"
}}
"""

    try:

        response=model.generate_content(prompt)

        parsed=extract_json(response.text)

        if parsed:
            return jsonify({
                "result":parsed
            })

        else:
            return jsonify({
                "result":fallback_analysis(text)
            })

    except Exception as e:

        print("Backend Error:",e)

        return jsonify({
            "result":fallback_analysis(text)
        })


if __name__=="__main__":
    app.run(debug=True)