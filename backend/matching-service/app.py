"""
AI Matching Service - Gemini Integration
Analyzes CVs and calculates job-candidate match scores using Google Gemini
"""
import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import asyncio
import requests
import json

sys.path.append('../shared')
from database import Database
from event_bus import RabbitMQEventBus
from monitoring import MetricsMiddleware
from auth import require_auth

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://talentlink-erfan.nl", "http://localhost:*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBA9ZHfWSgwLUqnRvDSAwZYWPWB5GuiIXQ")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

database = Database(os.getenv("DATABASE_URL"), "matchingdb")
event_bus = RabbitMQEventBus(os.getenv("RABBITMQ_URL"))

MetricsMiddleware(app, "matching-service")

# ============================================================================
# GEMINI AI FUNCTIONS
# ============================================================================

def analyze_cv_with_gemini(cv_text: str, job_description: str, required_skills: list,
                           required_technologies: list, experience_years: int) -> dict:
    """Use Gemini AI to analyze CV against job requirements"""

    prompt = f"""
You are an expert HR recruiter analyzing a candidate's CV for a job position.

Job Requirements:
- Description: {job_description}
- Required Skills: {', '.join(required_skills) if required_skills else 'Not specified'}
- Required Technologies: {', '.join(required_technologies) if required_technologies else 'Not specified'}
- Required Experience: {experience_years} years

Candidate's CV:
{cv_text[:4000]}  # Limit to 4000 chars

Please analyze the match between the candidate and the job requirements and provide:

1. Match Score (0-100): A numerical score indicating how well the candidate matches the job requirements
2. Matching Skills: List of skills from the requirements that the candidate has
3. Missing Skills: List of skills from the requirements that the candidate lacks
4. Experience Assessment: Whether the candidate meets the experience requirement
5. Summary: A 2-3 sentence summary explaining the match score

Return your response in the following JSON format:
{{
    "match_score": 85,
    "matching_skills": ["Python", "React"],
    "missing_skills": ["AWS"],
    "experience_met": true,
    "summary": "The candidate is a strong match for this position..."
}}
"""

    try:
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            print(f"Gemini API error: {response.status_code} - {response.text}")
            return get_fallback_analysis(required_skills, required_technologies)

        result = response.json()

        # Extract text from response
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0]['content']
            if 'parts' in content and len(content['parts']) > 0:
                text = content['parts'][0]['text']

                # Try to parse JSON from response
                # Remove markdown code blocks if present
                text = text.replace('```json', '').replace('```', '').strip()

                try:
                    analysis = json.loads(text)
                    return analysis
                except json.JSONDecodeError:
                    print(f"Failed to parse Gemini response as JSON: {text}")
                    return get_fallback_analysis(required_skills, required_technologies)

        return get_fallback_analysis(required_skills, required_technologies)

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return get_fallback_analysis(required_skills, required_technologies)


def get_fallback_analysis(required_skills, required_technologies):
    """Fallback analysis when Gemini API fails"""
    return {
        "match_score": 50,
        "matching_skills": [],
        "missing_skills": required_skills + required_technologies,
        "experience_met": False,
        "summary": "Unable to analyze CV automatically. Manual review recommended."
    }


# ============================================================================
# EVENT HANDLERS
# ============================================================================

def handle_application_submitted(event_data):
    """Handle ApplicationSubmitted event"""
    try:
        application_id = event_data['payload']['application_id']
        job_id = event_data['payload']['job_id']
        employee_id = event_data['payload']['employee_id']
        cv_id = event_data['payload'].get('cv_id')

        print(f"📊 Processing match analysis for application {application_id}")

        # Fetch job details
        job_response = requests.get(f"http://job-service:5001/api/jobs/{job_id}")
        if job_response.status_code != 200:
            print(f"Failed to fetch job: {job_response.status_code}")
            return

        job_data = job_response.json()

        # Fetch CV text
        cv_text = ""
        if cv_id:
            cv_response = requests.get(
                f"http://cv-service:5003/api/cv/{cv_id}/text",
                headers={"Authorization": request.headers.get("Authorization", "")}
            )
            if cv_response.status_code == 200:
                cv_text = cv_response.json().get('extracted_text', '')

        if not cv_text:
            print("No CV text available, using fallback analysis")
            analysis = get_fallback_analysis(
                job_data.get('required_skills', []),
                job_data.get('required_technologies', [])
            )
        else:
            # Analyze with Gemini
            analysis = analyze_cv_with_gemini(
                cv_text,
                job_data.get('description', ''),
                job_data.get('required_skills', []),
                job_data.get('required_technologies', []),
                job_data.get('experience_years', 0)
            )

        # Update application with match score
        update_payload = {
            "match_score": analysis.get('match_score', 0),
            "match_summary": json.dumps(analysis)
        }

        # This would call application service to update
        print(f"✅ Match analysis complete: Score={analysis.get('match_score')} for application {application_id}")

        # For now, just log it (in production, would update application service via API)

    except Exception as e:
        print(f"Error handling application submitted event: {e}")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route("/api/matching/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "matching-service"}), 200


@app.route("/api/matching/analyze", methods=["POST"])
@require_auth
def analyze_match():
    """Manually trigger CV-Job match analysis"""
    try:
        data = request.json
        cv_text = data.get('cv_text', '')
        job_description = data.get('job_description', '')
        required_skills = data.get('required_skills', [])
        required_technologies = data.get('required_technologies', [])
        experience_years = data.get('experience_years', 0)

        if not cv_text or not job_description:
            return jsonify({"error": "CV text and job description are required"}), 400

        analysis = analyze_cv_with_gemini(
            cv_text,
            job_description,
            required_skills,
            required_technologies,
            experience_years
        )

        return jsonify(analysis), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/matching/test-gemini", methods=["GET"])
def test_gemini():
    """Test Gemini API connection"""
    try:
        test_prompt = "Say 'Hello from Gemini!' and nothing else."

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{
                    "text": test_prompt
                }]
            }]
        }

        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "message": "Gemini API is working",
                "response": response.json()
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Gemini API returned {response.status_code}",
                "details": response.text
            }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================================
# EVENT CONSUMER (Background Thread)
# ============================================================================

def start_event_consumer():
    """Start consuming events from RabbitMQ"""
    import threading

    def consume():
        try:
            # Subscribe to application submitted events
            asyncio.run(event_bus.subscribe("ApplicationSubmittedEvent", handle_application_submitted))

            # Start consuming
            event_bus.start_consuming(
                queue_name="matching-service-queue",
                routing_keys=["application.submitted"]
            )
        except Exception as e:
            print(f"Error in event consumer: {e}")

    consumer_thread = threading.Thread(target=consume, daemon=True)
    consumer_thread.start()
    print("✅ Event consumer started")


if __name__ == "__main__":
    # Start event consumer in background
    # start_event_consumer()  # Commented out for now - enable in production

    port = int(os.getenv("PORT", 5004))
    app.run(host="0.0.0.0", port=port, debug=False)
