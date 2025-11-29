IITM BS – Tools in Data Science – Project 2
LLM Analysis Quiz Solver (Docker Space)
This project implements an HTTP API that automatically solves quiz tasks involving JavaScript-rendered pages, scraping, CSV processing, and headless-browser automation.

Your API exposes:

POST /task
{
  "email": "your_email",
  "secret": "your_secret",
  "url": "https://example.com/quiz"
}
