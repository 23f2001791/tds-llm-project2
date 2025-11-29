# solver.py
import re
import time
import json
import base64
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def decode_base64_from_html(html_text: str) -> str:
    """Find and decode any atob('...') or atob(`...`) content in the HTML."""
    matches = re.findall(r'atob\(["`\' ]*([A-Za-z0-9+/=\n\r]+)["`\' ]*\)', html_text)
    decoded_strings = []
    for m in matches:
        try:
            decoded = base64.b64decode(m).decode('utf-8', errors='ignore')
            decoded_strings.append(decoded)
        except Exception:
            continue
    return "\n".join(decoded_strings) if decoded_strings else None


def extract_submit_url(text: str, base_url: str) -> str:
    """Extract submit URL (relative or absolute) from HTML or text."""
    # Look for something ending with /submit
    match = re.search(r'https?://[^\s"\'<>]+/submit', text)
    if match:
        return match.group(0)

    # Try relative path
    match = re.search(r'["\'](/[^"\']*submit[^"\']*)["\']', text)
    if match:
        rel = match.group(1)
        # Combine with base URL domain
        from urllib.parse import urljoin
        return urljoin(base_url, rel)

    return None


def safe_get(url: str):
    """Simple wrapper for GET requests with timeout and basic error handling."""
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return ""


def solve_demo_task(page, current_url: str, email: str, secret: str):
    """
    Handles known demo tasks hosted at https://tds-llm-analysis.s-anand.net/demo
    The page may include hints like 'Download CSV', 'audio', etc.
    """
    html = page.content()
    text = page.inner_text("body") if page.locator("body").count() > 0 else ""

    # Default answer
    answer_value = "NA"

    # --- DEMO step 1: Just return NA ---
    if "demo" in current_url and "scrape" not in current_url and "audio" not in current_url:
        answer_value = "NA"

    # --- DEMO step 2: scrape data ---
    elif "demo-scrape" in current_url:
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find("a", href=True)
        if link:
            scrape_url = link["href"]
            if not scrape_url.startswith("http"):
                from urllib.parse import urljoin
                scrape_url = urljoin(current_url, scrape_url)
            page.goto(scrape_url)
            code_text = page.inner_text("body") if page.locator("body").count() > 0 else ""
            # Extract secret code
            match = re.search(r"secret\s*[:=]\s*([A-Za-z0-9_-]+)", code_text)
            if match:
                answer_value = match.group(1)
            else:
                answer_value = code_text.strip()

    # --- DEMO step 3: audio + CSV ---
    elif "demo-audio" in current_url:
        soup = BeautifulSoup(html, "html.parser")
        csv_link = soup.find("a", href=re.compile(r"\.csv"))
        span = soup.find("span")
        cutoff = None
        if span:
            try:
                cutoff = float(span.text.strip())
            except Exception:
                pass
        if csv_link:
            csv_url = csv_link["href"]
            if not csv_url.startswith("http"):
                from urllib.parse import urljoin
                csv_url = urljoin(current_url, csv_url)
            csv_data = safe_get(csv_url)
            lines = csv_data.strip().splitlines()
            if len(lines) > 1:
                headers = lines[0].split(",")
                value_index = headers.index("value") if "value" in headers else None
                sum_val = 0
                if value_index is not None:
                    for row in lines[1:]:
                        cols = row.split(",")
                        try:
                            val = float(cols[value_index])
                            if cutoff is None or val > cutoff:
                                sum_val += val
                        except Exception:
                            continue
                    answer_value = sum_val

    return answer_value


def solve_quiz_task(email: str, secret: str, start_url: str, timeout_seconds: int = 170):
    """
    Main quiz-solving loop.
    Uses Playwright (Chromium) to load each quiz page, find task, compute answer, and submit.
    """
    start_time = time.time()
    url_chain = []
    attempts = []
    current_url = start_url

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        while current_url and (time.time() - start_time < timeout_seconds):
            url_chain.append(current_url)
            try:
                page.goto(current_url, wait_until="networkidle", timeout=20000)
            except Exception:
                attempts.append({"error": f"Failed to load {current_url}"})
                break

            html = page.content()
            text = page.inner_text("body") if page.locator("body").count() > 0 else ""
            decoded = decode_base64_from_html(html)
            if decoded:
                text += "\n" + decoded

            # --- Determine answer ---
            answer_value = None

            if "tds-llm-analysis.s-anand.net/demo" in current_url:
                answer_value = solve_demo_task(page, current_url, email, secret)
            else:
                # Generic fallback: just send placeholder
                answer_value = "NA"

            # --- Find submit URL ---
            submit_url = extract_submit_url(html + "\n" + text, current_url)
            if not submit_url:
                attempts.append({
                    "url": current_url,
                    "error": "No submit URL found."
                })
                break

            # --- Submit answer ---
            payload = {
                "email": email,
                "secret": secret,
                "url": current_url,
                "answer": answer_value
            }

            try:
                resp = requests.post(submit_url, json=payload, timeout=20)
                response_json = {}
                try:
                    response_json = resp.json()
                except Exception:
                    response_json = {"raw_text": resp.text}

                attempts.append({"payload": payload, "response": response_json})

                # --- Move to next URL ---
                if response_json.get("url"):
                    current_url = response_json["url"]
                    continue
                else:
                    break

            except Exception as e:
                attempts.append({
                    "url": current_url,
                    "error": f"Submit failed: {str(e)}"
                })
                break

        browser.close()

    return {
        "status": "finished",
        "results": {
            "email": email,
            "url_chain": url_chain,
            "attempts": attempts
        }
    }
