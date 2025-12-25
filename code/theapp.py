import os
import re
import time
import tempfile
import numpy as np
import pyttsx3
import torch
import sounddevice as sd
import soundfile as sf
from playsound import playsound
from faster_whisper import WhisperModel
from gtts import gTTS
import mysql.connector
import google.generativeai as genai
# ---------- 🎧 REPLY SPEECH ----------

# Initialize pyttsx3 once (offline voice)
engine = pyttsx3.init()
engine.setProperty('rate', 180)  # adjust speaking speed
engine.setProperty('volume', 1.0)

def speak_text(text, lang="en"):
    """
    Hybrid Text-to-Speech:
    - Tries gTTS (online, fluent Tamil & English)
    - Falls back to pyttsx3 (offline, reliable)
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tfile = f.name
    try:
        # Prefer gTTS for Tamil & English fluency
        gTTS(text, lang=lang).save(tfile)
        play_audio(tfile)
        time.sleep(0.25)
        os.remove(tfile)
    except Exception as e:
        print(f"⚠️ gTTS failed ({e}). Falling back to offline voice.")
        print(f"🗣️ {text}")
        try:
            # Fallback to pyttsx3
            engine.say(text)
            engine.runAndWait()
        except Exception as e2:
            print(f"⚠️ Offline TTS also failed: {e2}")

# ---------- 💾 DATABASE CONNECTION (NEW) ----------

# ⚠️ UPDATE THESE with your local MySQL server details
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',        # Or your MySQL username
    'password': 'Carrots@123',        
    'database': 'college_ivr_erp_updated'
}

def get_db_connection():
    """Establishes a new database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to DB: {err}")
        return None

def get_student_by_regno(regno):
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT s.*, d.dept_name 
            FROM STUDENT s 
            JOIN DEPARTMENT d ON s.dept_id = d.dept_id 
            WHERE s.reg_no = %s
        """, (regno,))
        
        student = cursor.fetchone()
        
        if not student:
            print(f"No student found with regno: {regno}")
            return None
            
        student_id = student['student_id']
        
        cursor.execute("SELECT balance FROM FEES WHERE student_id = %s", (student_id,))
        fees_data = cursor.fetchone()
        if fees_data:
            student['fees_due'] = "Yes" if fees_data['balance'] > 0 else "No"
            student['fees_balance'] = fees_data['balance']
        else:
            student['fees_due'] = "No"
            student['fees_balance'] = 0

        cursor.execute("""
            SELECT AVG(a.attendance_percentage) AS avg_attendance
            FROM ATTENDANCE a
            JOIN ENROLLMENT e ON a.enroll_id = e.enroll_id
            WHERE e.student_id = %s
        """, (student_id,))
        attendance_data = cursor.fetchone()
        if attendance_data and attendance_data['avg_attendance']:
            student['attendance'] = f"{attendance_data['avg_attendance']:.2f}"
        else:
            student['attendance'] = "N/A"

        cursor.execute("""
            SELECT grade
            FROM MARKS m
            JOIN ENROLLMENT e ON m.enroll_id = e.enroll_id
            WHERE e.student_id = %s
            ORDER BY m.mark_id DESC
            LIMIT 1
        """, (student_id,))
        grade_data = cursor.fetchone()
        student['grade'] = grade_data['grade'] if grade_data else "N/A"

        cursor.execute("""
            SELECT s.subject_name
            FROM SUBJECT s
            JOIN ENROLLMENT e ON s.subject_id = e.subject_id
            WHERE e.student_id = %s
        """, (student_id,))
        subjects_data = cursor.fetchall()
        student['subjects'] = [row['subject_name'] for row in subjects_data]

        cursor.execute("""
            SELECT SUM(s.credits) AS total_credits
            FROM SUBJECT s
            JOIN ENROLLMENT e ON s.subject_id = e.subject_id
            WHERE e.student_id = %s
        """, (student_id,))
        credits_data = cursor.fetchone()
        if credits_data and credits_data['total_credits']:
            student['credits'] = credits_data['total_credits']
        else:
            student['credits'] = 0
            
        student['department'] = student['dept_name']
        student['upcoming_exam'] = "N/A" 

        return student

    except mysql.connector.Error as err:
        print(f"SQL Error in get_student_by_regno: {err}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ---------- 🔧 CONFIG ----------
GENAI_KEY = os.getenv("GEMINI_API_KEY")
if GENAI_KEY:
    genai.configure(api_key=GENAI_KEY)
    model_ai = genai.GenerativeModel("gemini-2.5-flash")
else:
    print("⚠️ GEMINI_API_KEY not set. Using gTTS for voice replies.")
    model_ai = None

# ---------- 🧠 RAG SETUP ----------
import chromadb
from chromadb.utils import embedding_functions

# Connect to the ERP data collection
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.Client()
collection = client.get_or_create_collection("erp_data", embedding_function=embedder)

def ask_generative_model(query, student, lang="en"):
    try:
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        context_docs = [doc for doc in results["documents"][0]]
        context = "\n".join(context_docs)

        reply_language = "Tamil" if lang == "ta" else "English"

        prompt = f"""
You are a college ERP assistant.

You understand:
- English
- Tamil
- Tanglish (Tamil written in English letters)

The user question may be in any of these. You MUST reply in {reply_language}.

You have two types of data:
1) General college info (library hours, bus pass, hostel rules, fests, etc.)
2) Student info (name, register number, department, attendance, subjects, fees, grades)

VERY IMPORTANT RULES:
- If a question asks specifically about TEACHERS, FACULTY, or STAFF handling a subject,
  and this information is NOT present in the context or student data, you MUST say you
  don’t have access to faculty details yet. Do NOT guess names.
- Do NOT treat the student's name as a teacher or staff member.
- If the information is not clearly present, say you don't know instead of inventing it.
- Keep answers brief, polite, and to the point.

Context:
{context}

Student Info (for this student only):
{student}

User question:
{query}

Now reply briefly and politely in {reply_language}.
"""

        if model_ai:
            result = model_ai.generate_content(prompt)
            return result.text.strip()
        else:
            return "I'm unable to use AI responses right now."
    except Exception as e:
        print(f"⚠️ RAG generation failed: {e}")
        return "I'm sorry, something went wrong while generating a response."

# ---------- 🎙️ RECORD ----------
def record_audio(filename="input.wav", duration=10, samplerate=16000):
    print(f"\n🎙️ Speak now ({duration}s)...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    sf.write(filename, audio, samplerate)
    normalize_audio(filename)
    print("✅ Recorded.")
    return filename

# ---------- 🔊 PLAY ----------
def play_audio(filepath):
    try:
        playsound(filepath)
    except Exception:
        if os.name == "nt":
            os.system(f"start {filepath}")
        elif os.name == "posix":
            os.system(f"xdg-open {filepath}")

# ---------- 🎚️ NORMALIZE ----------
def normalize_audio(filepath):
    audio, sr = sf.read(filepath)
    # avoid division by zero
    max_val = np.max(np.abs(audio)) if audio.size > 0 else 1.0
    if max_val == 0:
        max_val = 1.0
    audio = audio / max_val
    sf.write(filepath, audio, sr)

def seed_rag_database():
    print("🧠 Seeding RAG database...")
    
    # General college info (NOT student-specific)
    documents = [
        "Library hours are from 8:00 AM to 10:00 PM, Monday to Saturday.",
        "The college library is closed on Sundays and public holidays.",
        "To apply for a bus pass, please visit the administrative office (Room G0731) with your college ID card and a recent photograph.",
        "The administrative office is open from 9:00 AM to 4:00 PM on weekdays.",
        "Hostel curfew is 9:30 PM for all students. Late entry requires prior permission from the warden.",
        "For any maintenance issues in the hostel, please use the online complaint portal or contact the warden's office.",
        "The 'Drestein 2025' tech fest will be held in the first week of November. More details will be announced soon.",
        "Exam re-evaluation requests must be submitted within one week of the results being published. The fee is 500 rupees per subject."
    ]
    
    # Generate unique IDs for each document
    ids = [f"doc_{i}" for i in range(len(documents))]
    
    # Add to the collection
    collection.add(
        documents=documents,
        ids=ids
    )
    print(f"✅ Added {len(documents)} documents to ChromaDB.")

# Connect to the ERP data collection
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.Client() # You can make this persistent: client = chromadb.PersistentClient(path="/path/to/db")
collection = client.get_or_create_collection("erp_data", embedding_function=embedder)

# ❗️ Run this once to populate the database
# Check if collection is empty before seeding
if collection.count() == 0:
    seed_rag_database()
else:
    print(f"✅ RAG database already has {collection.count()} documents.")


# ---------- 🧠 LOAD WHISPER (GPU ENABLED, SAFE) ----------
def load_whisper_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "float32"

    print(f"🧠 Loading Whisper on: {device.upper()}")

    try:
        # Try 'small' — perfect for MX550
        model_size = "small"
        whisper = WhisperModel(model_size, device=device, compute_type=compute_type)
        print(f"✅ Loaded '{model_size}' model on {device.upper()} ({compute_type})")

    except RuntimeError as e:
        print(f"⚠️ GPU OOM or issue loading '{model_size}' model: {e}")
        print("🔄 Falling back to 'base' model on CPU...")

        whisper = WhisperModel("base", device="cpu", compute_type="float32")
        print("✅ Loaded 'base' model on CPU (float32)")

    return whisper


# Initialize once
whisper = load_whisper_model()


# ---------- 🧩 SAFE TRANSCRIPTION WRAPPER ----------
def transcribe_audio(filename):
    try:
        segments, info = whisper.transcribe(
            filename,
            task="transcribe",
            language=None,  # Auto-detect language
            beam_size=8,
            vad_filter=True,
            temperature=0.0
        )

        detected_lang = info.language
        print(f"🌐 Detected language: {detected_lang}")

        # ✅ Restrict to English and Tamil
        if detected_lang not in ["en", "ta"]:
            print(f"⚠️ Unsupported language detected ({detected_lang}). Asking user to repeat.")
            speak_text("Right now only English and Tamil are supported.")
            return ""

        text = " ".join([s.text for s in segments]).strip()

    except RuntimeError as e:
        # Handle OOM at runtime (in case model runs out of VRAM during transcription)
        if "CUDA out of memory" in str(e):
            print("💥 GPU out of memory during transcription. Retrying on CPU...")
            fallback_model = WhisperModel("base", device="cpu", compute_type="float32")
            segments, info = fallback_model.transcribe(filename)
            text = " ".join([s.text for s in segments]).strip()
        else:
            print("⚠️ Transcription failed:", e)
            text = ""

    return text


# ---------- 🔢 DIGIT HELPERS ----------
def clean_whisper_text(text):
    """Normalize Whisper transcription before digit parsing."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[,.?!;:—-]", " ", text)  # remove punctuation
    text = re.sub(r"\b(and|the|number|register|regno|reg)\b", " ", text)  # remove common filler words
    text = text.replace("simple", "single")  # sometimes misheard
    text = re.sub(r"\s+", " ", text).strip()
    return text

def spoken_to_digits(text):
    """Robust parser: handles 'double 2', 'triple 0', word digits and numeric tokens."""
    print(f"🧩 Raw text before parsing: {text}")

    # normalize punctuation etc
    text = text.lower().replace(",", " ").replace("-", " ").replace(".", " ")
    # token includes Tamil range and digits
    tokens = re.findall(r"[a-zA-Z\u0B80-\u0BFF]+|\d+", text)
    print(f"🔍 Tokenized words: {tokens}")

    digit_map = {
        # English + common mishears
        "zero": "0", "oh": "0", "o": "0",
        "one": "1", "won": "1",
        "two": "2", "to": "2", "too": "2",
        "three": "3", "tree": "3",
        "four": "4", "for": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8", "ate": "8",
        "nine": "9",
        # Tamil digits (examples)
        "பூஜ்ஜியம்": "0", "ஒன்று": "1", "இரண்டு": "2", "மூன்று": "3",
        "நான்கு": "4", "ஐந்து": "5", "ஆறு": "6", "ஏழு": "7", "எட்டு": "8", "ஒன்பது": "9",
        # Tanglish
        "onnu": "1", "rendu": "2", "moonnu": "3", "naalu": "4",
        "anchu": "5", "aaru": "6", "elu": "7", "ettu": "8", "onpathu": "9"
    }

    multiplier_words = {
        "double": 2, "dubble": 2, "டபுள்": 2, "rubble": 2, "bubble": 2, "hubble": 2,
        "triple": 3, "tripple": 3, "tribble": 3, "டிரிபுள்": 3, "ripple": 3, "shipple": 3
    }

    out = ""
    i = 0
    while i < len(tokens):
        w = tokens[i]

        # If multiplier word, expand either next token if it's a word or a digit
        if w in multiplier_words:
            mult = multiplier_words[w]
            if i + 1 < len(tokens):
                nxt = tokens[i + 1]
                # next could be a word mapped in digit_map or a raw digit like '2'
                if nxt in digit_map:
                    out += digit_map[nxt] * mult
                    print(f"🧠 Multiplier detected: {w} {nxt} → {digit_map[nxt]} x {mult}")
                    i += 2
                    continue
                elif re.fullmatch(r"\d", nxt):
                    out += nxt * mult
                    print(f"🧠 Multiplier detected: {w} {nxt} → {nxt} x {mult}")
                    i += 2
                    continue
                else:
                    # if next token unknown, skip multiplier gracefully
                    print(f"⚠️ Multiplier {w} followed by unknown token '{nxt}'")
                    i += 1
                    continue

        # Normal mapping for word digits
        if w in digit_map:
            out += digit_map[w]
            print(f"➡️ Mapped {w} → {digit_map[w]}")
        elif re.fullmatch(r"\d", w):
            out += w
            print(f"➡️ Raw digit found: {w}")
        else:
            print(f"❌ Ignored unknown token: {w}")

        i += 1

    # fallback: extract any digits present
    if not out:
        out = "".join(re.findall(r"\d", text))
        if out:
            print(f"📎 Extracted digits from text fallback: {out}")

    # post-fix: handle excessive repeats (limit runs of same digit to 2)
    out = re.sub(r"(\d)\1{3,}", r"\1\1\1", out)  # if 4+ repeats, reduce to 3 (adjust as you like)

    print(f"✅ Final parsed digits: {out}")
    return out

def is_exit_command(text):
    text = text.lower()
    return text in ["exit", "quit", "bye", "poiruven", "goodbye"]

def is_human_handoff(text):
    text = text.lower()
    phrases = [
        "connect me to staff",
        "talk to staff",
        "talk to a person",
        "talk to human",
        "speak to staff",
        "speak to a person",
        "connect to human",
        "call transfer"
    ]
    return any(p in text for p in phrases)

# ---------- 👤 GET REGISTER NUMBER (voice-only) ----------
def ask_regno():
    attempt = 1
    while True:
        print(f"\n🎧 Attempt #{attempt}: Recording register number\n")
        record_audio("reg.wav", 8)
        text = transcribe_audio("reg.wav").strip()
        print("🗣️ Heard:", text)

        regno = spoken_to_digits(text)

        print(f"➡️ Final parsed digits: {regno}")

        if len(regno) >= 12:
            print(f"✅ Detected register number: {regno}")
            return regno

        speak_text("I couldn’t get your register number clearly. Please repeat it.", lang="en")
        attempt += 1

def run_cli_ivr():
    # ---------- 👋 GREETING ----------
    greeting_file = "greeting.mp3"
    if not os.path.exists(greeting_file):
        gTTS("Welcome to your College ERP Assistant! Please say your register number.", lang='en').save(greeting_file)
    play_audio(greeting_file)
    time.sleep(0.25)  # let playback finish

    # ---------- 🔎 VALIDATE STUDENT ----------
    while True:
        regno = ask_regno()
        student = get_student_by_regno(regno)

        if student:
            print(f"✅ Student: {student['name']} ({student['reg_no']})\n")
            current_user = student["name"]
            break
        else:
            print(f"⚠️ Could not find regno {regno}. Let's try again.\n")
            speak_text("That register number wasn’t found. Please say it again.", lang="en")

    # Auto greet and start main loop immediately
    speak_text(f"Hello {student['name']}, you can now ask about attendance, fees, or exams.", lang="en")

    # Main loop
    while True:
        print("\n🎙️ Listening for query...")
        record_audio("input.wav", 5)
        text = transcribe_audio("input.wav").strip()
        print(f"🗣️ You said: {text}")

        if not text:
            continue

        # EXIT
        if is_exit_command(text):
            speak_text("வணக்கம்!", lang="ta")
            break

        # Language detect
        text_lower = text.lower().strip()
        has_tamil_chars = bool(re.search(r"[\u0B80-\u0BFF]", text_lower))
        tanglish_words = [
            "enna", "evlo", "epdi", "seri", "illa", "illaye", "vendam",
            "aacha", "poiruven", "vechu", "pa", "da", "dei",
            "unga", "ungaloda", "madam", "sir", "paatha", "machan", "poda", "po", "thambi"
        ]
        is_tanglish = any(re.search(rf"\b{w}\b", text_lower) for w in tanglish_words)
        has_english_words = any(q in text_lower for q in ["what", "when", "how", "who", "where", "why"])
        is_mixed = is_tanglish and has_english_words

        if has_tamil_chars or is_tanglish or is_mixed:
            lang = "ta"
        else:
            lang = "en"

        # HUMAN HANDOFF
        if is_human_handoff(text):
            reply_en = "Connecting you to a staff member. Please wait."
            reply_ta = "Staff-kitta connect panren. Wait pannunga."
            reply = reply_ta if lang == "ta" else reply_en
        else:
            # EVERYTHING ELSE → RAG
            print(f"🤖 Using RAG for query: {text}")
            reply = ask_generative_model(text, student, lang=lang)

        print("🤖:", reply)
        speak_text(reply, lang=lang)
        time.sleep(0.5)

        # Follow-up prompt
        followup_prompt = "Any more queries?" if lang == "en" else "இன்னும் கேள்விகள் இருக்கா?"
        speak_text(followup_prompt, lang=lang)

        time.sleep(2.0)
        print("\n🎧 Waiting for follow-up response...\n")
        time.sleep(1.5)

        record_audio("followup.wav", 5)
        followup_text = transcribe_audio("followup.wav").strip()
        print(f"🗣️ Follow-up response: {followup_text}")

        if not followup_text:
            print("🤔 No response detected. Listening again...")
            continue

        # If follow-up is basically "no more"
        if any(word in followup_text.lower() for word in ["no", "nah", "nothing", "illa", "illaye", "vendam"]):
            farewell = (
                "Okay, thank you for using your College ERP Assistant. Goodbye!"
                if lang == "en"
                else "சரி, நன்றி! வணக்கம்!"
            )
            speak_text(farewell, lang=lang)
            break

        # Otherwise treat as new query text in next iteration
        text = followup_text

if __name__ == "__main__":
    run_cli_ivr()
