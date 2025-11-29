IITM BS – Tools in Data Science – Project 2
LM Analysis Quiz – Automated Solver (IITM BS – Tools in Data Science)

This project implements an API endpoint that automatically solves quiz tasks provided during the LLM Analysis Quiz conducted as part of the Tools in Data Science (Sep 2025) course at IIT Madras BS in Data Science.

The project uses:

FastAPI (backend API)

Playwright + Chromium (headless browser for JS-rendered quizzes)

BeautifulSoup4 (HTML parsing)

Requests (API communication)

HuggingFace Spaces (deployment)

🚀 Project Features

✔ Accepts POST requests containing:

{
  "email": "<your email>",
  "secret": "<your secret>",
  "url": "<quiz URL>"
}


✔ Verifies secret securely
✔ Loads the quiz page using Playwright (JS executed)
✔ Extracts hidden instructions (Base64, atob(), innerHTML, DOM, etc.)
✔ Solves demo tasks:

/demo → simple

/demo-scrape → secret extraction

/demo-audio → CSV processing with cutoff
✔ Submits answer to the quiz submit URL
✔ Supports multi-step quizzes (follow-up URLs)
✔ Fully compliant with IITM evaluation rules
✔ 3-minute timeout safety handled

📌 API Endpoint

For this project, the deployed endpoint is:

https://kalletikarthik-llm-project.hf.space/task

Request Format
POST /task
Content-Type: application/json


Body:

{
  "email": "23f2001791@ds.study.iitm.ac.in",
  "secret": "23f2001791",
  "url": "https://example.com/quiz-123"
}

📂 Repository Structure
.
├── app.py              # FastAPI backend
├── solver.py           # Main quiz solver logic (Playwright, parsing)
├── models.py           # Pydantic models for request validation
├── requirements.txt    # Python dependencies
├── Dockerfile          # HF Space container instructions
├── LICENSE             # MIT License
└── README.md           # Documentation (this file)

🧠 How the Solver Works
1️⃣ Receive request

Validates JSON + secret; rejects unauthorized access.

2️⃣ Start headless browser

Using Playwright with Chromium.

3️⃣ Visit quiz URL

Executes JavaScript and retrieves rendered HTML.

4️⃣ Identify task type

Handles:

Plain HTML questions

Base64 encoded instructions inside JS

Links to CSV files

Scraping pages for hidden secrets

5️⃣ Compute answer

Depending on question type, applies:

String extraction

Regex

CSV aggregation

Cutoff-based filtering

6️⃣ Extract submit URL

Dynamically found using regex (no hardcoding).

7️⃣ POST answer

Formats and submits JSON payload to quiz submission endpoint.

8️⃣ If new URL is provided

The solver continues automatically until:

No new URL

Timeout (3 min)

Error

🧪 Test Your Endpoint

You can test your deployment using:

{
  "email": "23f2001791@ds.study.iitm.ac.in",
  "secret": "23f2001791",
  "url": "https://tds-llm-analysis.s-anand.net/demo"
}

🐋 Deployment on HuggingFace Spaces

The project uses a Docker Space with this command:

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]


Chromium + Playwright dependencies are preinstalled.

🔐 Environment Variables
EXPECTED_SECRET=23f2001791


Used to validate incoming requests.

📄 License

This project is licensed under the MIT License.
See LICENSE for details.

🧑‍🎓 Author

Karthik Kalleti
IIT Madras BS – Data Science
Email: 23f2001791@ds.study.iitm.ac.in
