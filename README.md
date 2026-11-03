Install Python 3.10 or newer.

Open this folder in VS Code.

Open the terminal in this folder and run:

pip install -r requirements.txt
streamlit run app.py

Enter your Gemini API key in the app sidebar.

For Streamlit Community Cloud, push app.py and requirements.txt to GitHub, then add GEMINI_API_KEY in the app's Secrets settings.

This version reads text-based PDFs. Scanned/image-only PDFs need OCR
