from flask import Flask, request, jsonify
import theapp
import time

app = Flask(__name__)

# Global state: we only demo for one user at a time
current_student = None
current_lang = "en"


@app.route("/")
def index():
    print(">>> / route hit, returning improved inline HTML")
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>College ERP IVR</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: radial-gradient(circle at top, #0f172a 0, #020617 60%);
            color: #e5e7eb;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            margin: 0;
            padding: 24px;
        }
        .container {
            width: 100%;
            max-width: 900px;
            background: rgba(2, 6, 23, 0.97);
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.25);
            box-shadow:
                0 0 0 1px rgba(15, 23, 42, 0.9),
                0 18px 60px rgba(0,0,0,0.7);
            padding: 18px 20px 20px;
        }
        .header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
        }
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 999px;
            background: radial-gradient(circle at 30% 20%, #22c55e, #16a34a 40%, #15803d 80%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
        }
        h1 {
            margin: 0;
            font-size: 22px;
        }
        .sub {
            margin: 0;
            font-size: 13px;
            color: #9ca3af;
        }
        .grid {
            display: grid;
            grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
            gap: 16px;
            margin-top: 12px;
        }
        .panel {
            background: #020617;
            border-radius: 14px;
            border: 1px solid #1f2937;
            padding: 12px;
        }
        .panel-title {
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #9ca3af;
            margin-bottom: 6px;
        }
        .student-card {
            background: radial-gradient(circle at top left, #22c55e33, #020617);
            border-radius: 12px;
            padding: 10px 12px;
            margin-bottom: 8px;
            display: none;
        }
        .student-card h2 {
            margin: 0 0 4px;
            font-size: 16px;
        }
        .student-card p {
            margin: 1px 0;
            font-size: 13px;
            opacity: 0.9;
        }
        .tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 8px;
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid #1f2937;
            font-size: 11px;
            color: #e5e7eb;
            margin-top: 4px;
        }
        .tag-dot {
            width: 6px;
            height: 6px;
            border-radius: 999px;
            background: #22c55e;
            box-shadow: 0 0 8px #22c55e;
        }
        .chat {
            background: #020617;
            border-radius: 10px;
            border: 1px solid #1f2937;
            padding: 10px 10px;
            height: 290px;
            overflow-y: auto;
            font-size: 13px;
        }
        .msg {
            margin: 6px 0;
            padding: 7px 10px;
            border-radius: 10px;
            max-width: 80%;
            word-wrap: break-word;
            line-height: 1.4;
        }
        .user {
            background: #0369a1;
            margin-left: auto;
        }
        .bot {
            background: #111827;
        }
        .controls {
            margin-top: 8px;
            display: flex;
            gap: 8px;
        }
        input[type="text"] {
            padding: 8px 10px;
            border-radius: 999px;
            border: 1px solid #1f2937;
            background: #020617;
            color: #e5e7eb;
            outline: none;
            font-size: 13px;
        }
        input[type="text"]::placeholder {
            color: #6b7280;
        }
        /* Top row regno input */
        .reg-input {
            flex: 1;
            max-width: 230px;
            padding: 6px 10px;
            font-size: 12px;
        }
        /* Bottom text box */
        #textInput {
            flex: 1;
        }
        button {
            border: none;
            border-radius: 999px;
            padding: 8px 14px;
            cursor: pointer;
            font-weight: 500;
            font-size: 13px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        button:disabled {
            opacity: 0.6;
            cursor: default;
        }
        .btn-primary {
            background: #22c55e;
            color: #022c22;
        }
        .btn-ghost {
            background: #111827;
            color: #e5e7eb;
        }
        .top-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 10px;
            margin-bottom: 4px;
            flex-wrap: wrap;
        }
        .status {
            margin-top: 4px;
            font-size: 11px;
            color: #a5b4fc;
        }
        .pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 9px;
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.9);
            font-size: 11px;
            color: #e5e7eb;
        }
        .dot-pulse {
            width: 6px;
            height: 6px;
            border-radius: 999px;
            background: #22c55e;
            box-shadow: 0 0 9px #22c55e;
            animation: pulse 1s infinite alternate;
        }
        @keyframes pulse {
            from { opacity: 0.5; transform: scale(0.9); }
            to   { opacity: 1;   transform: scale(1.05); }
        }
        .hint {
            font-size: 11px;
            color: #9ca3af;
            margin-top: 6px;
        }
        .layout-right {
            font-size: 12px;
            color: #9ca3af;
        }
        .layout-right ul {
            padding-left: 16px;
            margin: 4px 0 0;
        }
        .layout-right li {
            margin-bottom: 2px;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="avatar">🎧</div>
        <div>
            <h1>College ERP Voice Assistant</h1>
            <p class="sub">Speak in English, Tamil, or Tanglish. Ask about attendance, fees, exams, subjects & more.</p>
        </div>
    </div>

    <div class="grid">
        <div class="panel">
            <div class="panel-title">Session</div>

            <div class="student-card" id="studentCard">
                <h2 id="stuName"></h2>
                <p id="stuReg"></p>
                <p id="stuDept"></p>
                <p id="stuExtra"></p>
                <div class="tag">
                    <span class="tag-dot"></span>
                    <span id="langTag">Language: Auto</span>
                </div>
            </div>

            <div class="top-row">
                <input id="regInput" class="reg-input" type="text" placeholder="Optional: enter register number">
                <button id="btnStart" class="btn-primary">
                    <span>🎙️ Start</span>
                </button>
                <button id="btnVoice" class="btn-ghost" disabled>
                    <span>🎤 Voice Query</span>
                </button>
                <button id="btnNew" class="btn-ghost">
                    <span>🔄 New Session</span>
                </button>
            </div>
            <div class="hint">
                • Enter a register number and press <b>Start</b>, <i>or</i> leave it blank to speak your regno by voice.<br>
                • After that, either type below or use <b>Voice Query</b>.
            </div>

            <div class="chat" id="chat"></div>

            <div class="controls">
                <input id="textInput" type="text" placeholder="Type your question… (e.g. 'What is my attendance?')">
                <button id="btnSend" class="btn-primary">Send</button>
            </div>

            <div class="status" id="status">Status: idle</div>
            <div class="status" id="liveIndicator" style="display:none;">
                <span class="pill">
                    <span class="dot-pulse"></span> Listening via laptop mic…
                </span>
            </div>
        </div>

        <div class="panel layout-right">
            <div class="panel-title">What you can ask</div>
            <ul>
                <li>"What is my attendance?"</li>
                <li>"Do I have any fees due?"</li>
                <li>"What subjects am I enrolled in?"</li>
                <li>"When is my next exam?"</li>
                <li>Tamil: "En attendance evlo?"</li>
                <li>Mix: "Sir, enakku fees balance iruka?"</li>
            </ul>
            <div class="hint" style="margin-top:8px;">
                This demo runs locally on your laptop. Voice recognition & replies are handled completely on-device
                using your Python backend and Whisper + Gemini/RAG.
            </div>
        </div>
    </div>
</div>

<script>
const chatEl = document.getElementById("chat");
const statusEl = document.getElementById("status");
const btnStart = document.getElementById("btnStart");
const btnVoice = document.getElementById("btnVoice");
const btnSend = document.getElementById("btnSend");
const btnNew = document.getElementById("btnNew");
const textInput = document.getElementById("textInput");
const regInput = document.getElementById("regInput");
const liveIndicator = document.getElementById("liveIndicator");
const langTag = document.getElementById("langTag");
const studentCard = document.getElementById("studentCard");

function addMsg(text, cls) {
    const div = document.createElement("div");
    div.className = "msg " + cls;
    div.textContent = text;
    chatEl.appendChild(div);
    chatEl.scrollTop = chatEl.scrollHeight;
}

function setBusy(isBusy, label) {
    btnStart.disabled = isBusy;
    btnSend.disabled = isBusy;
    // Voice button only active when we have a student
    btnVoice.disabled = isBusy || !studentCard || studentCard.style.display === "none";
    if (label) statusEl.textContent = "Status: " + label;
    liveIndicator.style.display = isBusy && label && label.toLowerCase().includes("record") ? "block" : "none";
}

btnStart.onclick = async () => {
    setBusy(true, "starting session...");
    addMsg("Starting session…", "bot");

    const reg = regInput.value.trim();
    let payload = {};
    if (reg) {
        payload.regno = reg;
        addMsg("Using register number: " + reg, "user");
        setBusy(true, "looking up register number…");
    } else {
        addMsg("Please say your register number into the laptop mic.", "bot");
        setBusy(true, "capturing register number via voice…");
    }

    try {
        const res = await fetch("/start_session", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (!data.ok) {
            addMsg("Error: " + data.message, "bot");
            setBusy(false, data.message);
            return;
        }

        studentCard.style.display = "block";
        document.getElementById("stuName").textContent = data.student.name;
        document.getElementById("stuReg").textContent = "Reg No: " + data.student.reg_no;
        document.getElementById("stuDept").textContent = "Department: " + data.student.department;
        document.getElementById("stuExtra").textContent =
            "Attendance: " + data.student.attendance +
            " | Fees due: " + data.student.fees_due +
            " | Balance: ₹" + data.student.fees_balance;

        addMsg(data.message, "bot");
        setBusy(false, "ready for queries.");
        btnVoice.disabled = false;
    } catch (err) {
        console.error(err);
        addMsg("Error starting session.", "bot");
        setBusy(false, "error while starting session.");
    }
};

btnSend.onclick = async () => {
    const text = textInput.value.trim();
    if (!text) return;

    addMsg(text, "user");
    textInput.value = "";
    setBusy(true, "sending text query…");

    try {
        const res = await fetch("/query", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({mode: "text", text})
        });
        const data = await res.json();

        if (!data.ok) {
            addMsg("Error: " + (data.error || "Unknown error"), "bot");
            setBusy(false, "error.");
            return;
        }

        addMsg(data.reply, "bot");
        if (data.lang) {
            langTag.textContent = "Language: " + (data.lang === "ta" ? "Tamil / Tanglish" : "English");
        }
        setBusy(false, data.end ? "session ended." : "ready.");
    } catch (err) {
        console.error(err);
        addMsg("Error sending query.", "bot");
        setBusy(false, "error.");
    }
};

btnVoice.onclick = async () => {
    setBusy(true, "recording voice query on laptop mic…");
    addMsg("[voice] Listening… speak into the laptop mic.", "bot");

    try {
        const res = await fetch("/query", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({mode: "voice"})
        });
        const data = await res.json();

        if (!data.ok) {
            addMsg("Error: " + (data.error || "Unknown error"), "bot");
            setBusy(false, "error.");
            return;
        }

        addMsg("You (recognized): " + data.user_text, "user");
        addMsg(data.reply, "bot");
        if (data.lang) {
            langTag.textContent = "Language: " + (data.lang === "ta" ? "Tamil / Tanglish" : "English");
        }
        setBusy(false, data.end ? "session ended." : "ready.");
    } catch (err) {
        console.error(err);
        addMsg("Error with voice query.", "bot");
        setBusy(false, "error.");
    }
};

btnNew.onclick = async () => {
    setBusy(true, "resetting session…");
    try {
        const res = await fetch("/reset_session", {
            method: "POST"
        });
        const data = await res.json();
        if (!data.ok) {
            addMsg("Error resetting session.", "bot");
            setBusy(false, "error.");
            return;
        }
        // Clear UI
        chatEl.innerHTML = "";
        regInput.value = "";
        textInput.value = "";
        studentCard.style.display = "none";
        langTag.textContent = "Language: Auto";
        btnVoice.disabled = true;
        addMsg("Session cleared. You can start again with a new register number.", "bot");
        setBusy(false, "idle");
    } catch (err) {
        console.error(err);
        addMsg("Error resetting session.", "bot");
        setBusy(false, "error.");
    }
};

textInput.addEventListener("keydown", e => {
    if (e.key === "Enter") btnSend.click();
});
</script>
</body>
</html>'''


@app.route("/start_session", methods=["POST"])
def start_session():
    """
    1. If regno is given in JSON, use it directly (text mode)
    2. Otherwise:
       - Speak greeting
       - Ask for regno via voice (existing flow)
    3. Look up student in DB
    4. Return student info + welcome text to show in UI
    """
    global current_student, current_lang

    data = request.get_json(silent=True) or {}
    regno = (data.get("regno") or "").strip()

    # ---- CASE 1: user typed register number ----
    if regno:
        print(f"▶ Using typed register number: {regno}")
        student = theapp.get_student_by_regno(regno)
        if not student:
            theapp.speak_text("That register number was not found. Please check and try again.", "en")
            return jsonify({"ok": False, "message": "Student not found. Please check the register number."})
    else:
        # ---- CASE 2: voice-based register number ----
        theapp.speak_text(
            "Welcome to your College ERP Assistant! Please say your register number.",
            lang="en",
        )
        regno = theapp.ask_regno()
        student = theapp.get_student_by_regno(regno)

        if not student:
            theapp.speak_text("That register number was not found. Please try again.", "en")
            return jsonify({"ok": False, "message": "Student not found. Please try again."})

    current_student = student
    current_lang = "en"  # default; will adjust per query

    welcome = f"Hello {student['name']}, you can now ask about attendance, fees, or exams."
    theapp.speak_text(welcome, lang="en")

    return jsonify({
        "ok": True,
        "message": welcome,
        "student": {
            "name": student["name"],
            "reg_no": student["reg_no"],
            "department": student.get("department", ""),
            "attendance": student.get("attendance", "N/A"),
            "fees_due": student.get("fees_due", "N/A"),
            "fees_balance": student.get("fees_balance", 0),
            "grade": student.get("grade", "N/A"),
        }
    })


@app.route("/reset_session", methods=["POST"])
def reset_session():
    """
    Clear current student + language so a new session can begin.
    """
    global current_student, current_lang
    current_student = None
    current_lang = "en"
    print("🔄 Session reset.")
    return jsonify({"ok": True})


@app.route("/query", methods=["POST"])
def handle_query():
    """
    Handle one query.
    Modes:
      - mode = "text": use text from the frontend
      - mode = "voice": record via laptop mic (like your current IVR)
    """
    global current_student, current_lang

    # No active session → user hasn't done Start yet
    if not current_student:
        return jsonify({
            "ok": False,
            "error": "No active student session. Please start session first."
        }), 400

    # ---- 1) Get payload from frontend ----
    data = request.get_json(force=True)
    mode = data.get("mode", "text")
    user_text = (data.get("text") or "").strip()

    # ---- 2) If mode is voice, record + transcribe via laptop mic ----
    if mode == "voice":
        theapp.speak_text("Please speak your query now.", lang=current_lang)
        theapp.record_audio("web_query.wav", duration=6)
        user_text = theapp.transcribe_audio("web_query.wav").strip()

    # Still nothing? Then error
    if not user_text:
        return jsonify({"ok": False, "error": "No query detected."})

    # ---- 3) Language / Tanglish detection ----
    text_lower = user_text.lower().strip()

    has_tamil_chars = bool(theapp.re.search(r"[\u0B80-\u0BFF]", text_lower))
    tanglish_words = [
        "enna", "evlo", "epdi", "seri", "illa", "illaye", "vendam",
        "aacha", "poiruven", "vechu", "pa", "da", "dei",
        "unga", "ungaloda", "madam", "sir", "paatha", "machan", "poda", "po", "thambi"
    ]
    is_tanglish = any(theapp.re.search(rf"\\b{w}\\b", text_lower) for w in tanglish_words)
    has_english_words = any(q in text_lower for q in ["what", "when", "how", "who", "where", "why"])
    is_mixed = is_tanglish and has_english_words

    if has_tamil_chars or is_tanglish or is_mixed:
        current_lang = "ta"
    else:
        current_lang = "en"

    # ---- 4) EXIT CHECK ----
    if theapp.is_exit_command(user_text):
        reply = "வணக்கம்!" if current_lang == "ta" else "Goodbye!"
        theapp.speak_text(reply, lang=current_lang)
        return jsonify({
            "ok": True,
            "user_text": user_text,
            "reply": reply,
            "lang": current_lang,
            "end": True
        })

    # ---- 5) HUMAN HANDOFF CHECK ----
    if theapp.is_human_handoff(user_text):
        reply_en = "Connecting you to a staff member. Please wait."
        reply_ta = "Staff-kitta connect panren. Wait pannunga."
        reply = reply_ta if current_lang == "ta" else reply_en

        theapp.speak_text(reply, lang=current_lang)
        return jsonify({
            "ok": True,
            "user_text": user_text,
            "reply": reply,
            "lang": current_lang,
            "end": False
        })

    # ---- 6) EVERYTHING ELSE → RAG + Gemini ----
    reply = theapp.ask_generative_model(user_text, current_student, lang=current_lang)
    theapp.speak_text(reply, lang=current_lang)
    time.sleep(0.3)

    return jsonify({
        "ok": True,
        "user_text": user_text,
        "reply": reply,
        "lang": current_lang,
        "end": False
    })


if __name__ == "__main__":
    # debug=False so the Whisper / audio stack doesn't get reloaded twice
    app.run(host="0.0.0.0", port=8000, debug=False)
