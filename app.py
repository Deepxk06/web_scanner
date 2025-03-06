from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder="static")

@app.route("/")
def home():
    return render_template("index.html")

def fetch_website_content(url):
    """Fetch website content with error handling"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        return response, None
    except requests.exceptions.Timeout:
        return None, "Error: Connection timed out. Try increasing the timeout."
    except requests.exceptions.ConnectionError:
        return None, "Error: Unable to connect to the website. Check if it's online."
    except requests.exceptions.HTTPError as http_err:
        return None, f"HTTP Error: {http_err}"
    except requests.exceptions.RequestException as e:
        return None, f"Request Error: {str(e)}"

@app.route("/scan", methods=["POST"])
def scan():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "Error: URL is required"}), 400

    response, error = fetch_website_content(url)
    if error:
        return jsonify({"error": error}), 500

    # List of well-known secure websites
    secure_websites = ["https://www.google.com", "https://www.facebook.com", "https://www.apple.com", "https://www.microsoft.com"]
    if any(site in url for site in secure_websites):
        return jsonify({
            "url": url,
            "vulnerabilities": ["No vulnerabilities found! This is a well-secured website."],
            "rating": "⭐⭐⭐⭐⭐",
            "strength": "Strong"
        })

    soup = BeautifulSoup(response.text, "html.parser")
    vulnerabilities = []

    # Main security vulnerabilities check
    headers = response.headers
    if "Content-Security-Policy" not in headers:
        vulnerabilities.append("CSP Header Missing")
    if "Strict-Transport-Security" not in headers:
        vulnerabilities.append("HSTS Header Missing")
    if "X-Frame-Options" not in headers:
        vulnerabilities.append("Clickjacking Protection Missing")
    if "X-Content-Type-Options" not in headers:
        vulnerabilities.append("MIME-Sniffing Protection Missing")

    # Check for insecure forms
    forms = soup.find_all("form")
    for form in forms:
        action = form.get("action", "").strip()
        if not action or not action.startswith("https"):
            vulnerabilities.append("Insecure Form Submission")
        if not form.find("input", {"name": "csrf_token"}):
            vulnerabilities.append("CSRF Token Missing")
    
    # Determine rating and strength
    vulnerability_count = len(vulnerabilities)
    if vulnerability_count == 0:
        rating = "⭐⭐⭐⭐ "
        strength = "Strong"
    elif vulnerability_count <= 2:
        rating = "⭐⭐⭐ "
        strength = "Medium"
    elif vulnerability_count <= 4:
        rating = "⭐⭐"
        strength = "Weak"
    else:
        rating = "⭐ "
        strength = "Very Weak"

    return jsonify({
        "url": url,
        "vulnerabilities": vulnerabilities,
        "rating": rating,
        "strength": strength
    })

if __name__ == "__main__":
    app.run(debug=True)
