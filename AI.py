import requests
import difflib
import mysql.connector
from datetime import datetime
from openai import OpenAI

# === CONFIGURATION ===
OPENAI_API_KEY = "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" 

# Database credentials
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Change if your MySQL has a password
    "database": "panicmode_compiler"
}

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# === 1️⃣ DATABASE CONNECTION ===
def connect_db():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"❌ Database connection error: {err}")
        return None


# === 2️⃣ FETCH OPEN SOURCE REFERENCE FROM GITHUB ===
def fetch_open_source_code(language, query):
    print(f"\n🔎 Searching open-source code for '{query}' in {language}...\n")
    search_url = f"https://api.github.com/search/code?q={query}+language:{language}&per_page=1"
    try:
        response = requests.get(search_url, headers={"Accept": "application/vnd.github.v3+json"})
        response.raise_for_status()
        items = response.json().get("items", [])
        if not items:
            print("⚠️ No matching open-source code found.")
            return None, None

        repo_url = items[0]["html_url"]
        raw_url = repo_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        print(f"✅ Found open-source reference: {repo_url}\n")
        raw_response = requests.get(raw_url)
        if raw_response.status_code == 200:
            return raw_response.text, repo_url
        else:
            print("⚠️ Could not fetch file content.")
            return None, repo_url
    except Exception as e:
        print("❌ GitHub API error:", e)
        return None, None


# === 3️⃣ COMPARE USER CODE VS OPEN SOURCE CODE ===
def compare_code(user_code, ref_code):
    user_lines = user_code.strip().splitlines()
    ref_lines = ref_code.strip().splitlines()
    diff = difflib.unified_diff(ref_lines, user_lines, fromfile='open_source', tofile='user_code', lineterm='')

    report = []
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            report.append(f"🟢 Added: {line[1:]}")
        elif line.startswith("-") and not line.startswith("---"):
            report.append(f"🔴 Missing/Changed: {line[1:]}")
    if not report:
        report.append("✅ Your code is almost identical to the open-source reference!")
    return "\n".join(report)


# === 4️⃣ AI EXPLANATION FOR CODE ERRORS ===
def ai_explain_issues(user_code, comparison_result, language):
    print("\n🧠 Generating AI explanation...")
    prompt = f"""
You are a programming tutor. The student wrote this {language} code:

{user_code}

Here’s a comparison result against a correct open-source version:

{comparison_result}

Explain what might be wrong in the student's code, line by line, in simple language.
Also, suggest how to fix it.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Lightweight and fast
            messages=[{"role": "user", "content": prompt}]
        )
        explanation = response.choices[0].message.content.strip()
        return explanation
    except Exception as e:
        print("❌ AI explanation error:", e)
        return "AI explanation unavailable due to API error."


# === 5️⃣ SAVE RESULTS INTO DATABASE ===
def save_to_database(language, topic, user_code, ref_code, diff_result, ai_explanation, ref_url):
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO codes (user_id, lang_id, code_text, submitted_at)
            VALUES (NULL, NULL, %s, %s)
        """, (user_code, datetime.now()))
        code_id = cursor.lastrowid

        # Save comparison + AI explanation as an “error report”
        full_report = f"{diff_result}\n\n🧠 AI Explanation:\n{ai_explanation}\n\nReference: {ref_url}"
        cursor.execute("""
            INSERT INTO errors (code_id, error_message, error_type)
            VALUES (%s, %s, %s)
        """, (code_id, full_report, f"AI_ANALYSIS_{language.upper()}"))

        conn.commit()
        print("\n💾 All results saved successfully in database!")
        print(f"🗂 Code ID: {code_id}")
    except Exception as e:
        print("❌ Database insert error:", e)
    finally:
        cursor.close()
        conn.close()


# === 6️⃣ MAIN PROGRAM ===
if __name__ == "__main__":
    print("=== 🤖 AI Compiler Assistant ===")
    language = input("Enter programming language (e.g. python, c, cpp, java): ").strip()
    topic = input("Enter what your code does (e.g. sorting, calculator): ").strip()

    print("\nPaste your code below (press ENTER twice to finish):")
    user_input_lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        user_input_lines.append(line)
    user_code = "\n".join(user_input_lines)

    ref_code, ref_url = fetch_open_source_code(language, topic)
    if ref_code:
        diff_result = compare_code(user_code, ref_code)
        print("\n=== 🧾 Comparison Report ===\n")
        print(diff_result)

        ai_explanation = ai_explain_issues(user_code, diff_result, language)
        print("\n=== 🧠 AI Explanation ===\n")
        print(ai_explanation)

        save_to_database(language, topic, user_code, ref_code, diff_result, ai_explanation, ref_url)
    else:
        print("❌ Could not fetch open-source code to compare.")
