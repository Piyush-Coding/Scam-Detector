from flask import Flask, render_template, request
import google.generativeai as genai
import os
import PyPDF2

#Initialize Flask app
app = Flask(__name__)

# Set up the Google API key
os.environ["Google API key"] = "AIzaSyB4R9rh1WKq6GTe0bRIMTAZGIA-oZkLoqk"
genai.configure(api_key=os.environ["Google API key"])

#Initialize the Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

#function
def predict_fake_or_real_email_content(text):
    prompt = f"""
    You are an expert in identifying scam messages in text, email etc. Analyze the given text.

    - **Real/Lefitimate** (Authentic, safe message)
    - **Scam/Fake** (Phishing, fraud, or suspicious message)

    **for the following Text:***
    {text}

    **Return a clear message indicating whether this content is real or a scam.
    If it is a scam, mention why it seems fraudulent. If it is real, state that it is legitimate.**

    **Only return the classification message and nothing else.**
    Note: Don't return empty or null, you only need to return message for the input text.
    """

    response = model.generate_content(prompt)
    return response.text.strip()


def url_detection(url):
    prompt = f"""
    You are an advanced AI model specializing in URL security classification. 

    1. Benign**: Safe, trusted, and non-malicious websites such as google.com. wilipedia.org, amazon.com.
    2. Phishing**: Fraudulent websites designed to steal personal information. You are an AI model specializing in URL security; explain Phishing as fraudulent websites designed to steal personal data (e.g., http://secure-login.paypal.com/), including common traits like misspelled domains or fake login pages.
    3. Malware**: URLs that distribute viruses, ransomware, or malicious software. You are an AI model specializing in URL security; explain Malware as websites distributing viruses or malicious software (e.g., http://free-download-software.xyz/), including traits like automatic downloads or suspicious pop-ups.
    4. Defacement**: Hacked or defaced websites that display unauthorized content, usually altered by attackers.

    **Example URLs and Classification:**
    - **Benign**: "https://www.microsoft.com/"
    - **Phishing**: "http://secure-login.paypal.com/"
    - **Malware**: "http://free-download-software.xyz/"
    - **Defacements**: "http://hacked-websites.com/"

    **Input URL:** {url}

    **Output Format:**
    - Return only a string class name
    - Example output for a phishing site:

    Analyze the URL and return the correct classification (Only name in lowercase such as benign etc.)
    Note: Don't return empty or null, at any cost return the corrected class
    """

    response = model.generate_content(prompt)
    return response.text if response else "Detection Failed."

#routes
@app.route("/")
def index():
    return render_template('index.html')
@app.route("/scam/", methods=['GET', 'POST'])
def detect_scam():
    if"file" not in request.files:
        return render_template("index.html", message="No file uploaded.")
    file = request.files['file']
    
    extracted_text = " "


    if file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file)
        extracted_text =" ",[page.extract_text() for page in pdf_reader.pages if page.extract_text()]

    elif file.filename.endswith(".txt"):
        extracted_text = file.read().decode("utf-8")

    else:
        return render_template('index.html', message="File is empty or text could not be extracted.")



    message = predict_fake_or_real_email_content((extracted_text))

    return render_template('index.html', message=message)


@app.route("/predict", methods=['GET', 'POST'])
def url_predict():
    if request.method=='POST':
        url = request.form.get("url", '').strip()

        if not url.startswith(("https://", "http://")):
            return render_template("index.html", message = "Your enter invalid url.")
        
        classification = url_detection(url)
        return render_template('index.html', input_url=url, predicted_class=classification)

#python main

if __name__=="__main__":
    app.run(debug=True)