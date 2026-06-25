from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import os
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Text model
text_model=genai.GenerativeModel(
    "gemini-2.5-flash"
)

# Vision model
vision_model=genai.GenerativeModel(
    "gemini-2.5-flash"
)


def extract_json(raw):

    try:

        start=raw.find("{")
        end=raw.rfind("}")

        if start==-1 or end==-1:
            return None

        return json.loads(
            raw[start:end+1]
        )

    except:
        return None


def fallback_analysis(text):

    text=text.lower()

    category="Other"
    department="Municipal Department"
    severity="Medium"
    score=60

    if any(
        x in text
        for x in
        ["garbage","waste","trash"]
    ):

        category="Waste"
        department="Waste Management Department"
        severity="High"
        score=95

    elif any(
        x in text
        for x in
        ["pothole","road"]
    ):

        category="Road"
        department="Road Transport Department"
        severity="High"
        score=90


    return {

        "category":category,
        "severity":severity,
        "risk":{
            "status":"Yes",
            "reason":"Public impact detected"
        },
        "department":department,
        "priority_score":score,
        "recommended_action":
        "Immediate inspection required"
    }



@app.route("/analyze",methods=["POST"])
def analyze():

    try:

        text=request.form.get(
            "text",""
        )

        file=request.files.get(
            "image"
        )

        image_description=""

        # IMAGE ANALYSIS
        if file:

            image=Image.open(file)

            vision_response=vision_model.generate_content(
                [
                    "Describe the civic issue visible in this image",
                    image
                ]
            )

            image_description=vision_response.text


        final_text=text+" "+image_description


        prompt=f"""
Return ONLY valid JSON.

Issue:

{final_text}

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


        response=text_model.generate_content(
            prompt
        )

        parsed=extract_json(
            response.text
        )

        if parsed:

            return jsonify({
                "result":parsed
            })

        return jsonify({
            "result":
            fallback_analysis(
                final_text
            )
        })


    except Exception as e:

        print(
            "ERROR:",
            e
        )

        return jsonify({
            "result":
            fallback_analysis(
                text
            )
        })



if __name__=="__main__":

    app.run(
        debug=True
    )