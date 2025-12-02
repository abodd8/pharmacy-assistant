import streamlit as st
import difflib
import requests

# ===== إعداد الصفحة العامة لستريملت =====
st.set_page_config(
    page_title="Pharmacy Assistant",
    page_icon="💊",
    layout="wide"
)

# ===================== إعداد المستخدمين =====================
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "12345", "role": "user"},
}

# ===================== بيانات الأدوية (حوالي 60 دواء) =====================
def get_default_medicines():
    return [
        {
            "name": "Paracetamol",
            "ingredients": "Paracetamol (Acetaminophen)",
            "benefits": "مسكن للألم وخافض للحرارة.",
            "side_effects": "غثيان، اضطراب معدي، أذى في الكبد مع الجرعات العالية.",
            "prescription": False,
        },
        {
            "name": "Ibuprofen",
            "ingredients": "Ibuprofen",
            "benefits": "مسكن ألم ومضاد التهاب وخافض حرارة.",
            "side_effects": "ألم معدة، قرحة معدية، نزيف مع الاستخدام الطويل.",
            "prescription": False,
        },
        {
            "name": "Aspirin",
            "ingredients": "Acetylsalicylic acid",
            "benefits": "مسكن ألم، خافض حرارة، مميع للدم بجرعات معينة.",
            "side_effects": "اضطراب معدي، نزيف، حساسية عند بعض المرضى.",
            "prescription": False,
        },
        {
            "name": "Diclofenac",
            "ingredients": "Diclofenac sodium",
            "benefits": "مسكن قوي ومضاد التهاب للمفاصل والعضلات.",
            "side_effects": "ألم معدي، ارتفاع إنزيمات الكبد، قرحة.",
            "prescription": True,
        },
        {
            "name": "Naproxen",
            "ingredients": "Naproxen",
            "benefits": "مسكن ومضاد التهاب للمفاصل والآلام المزمنة.",
            "side_effects": "اضطرابات هضمية، صداع، دوار.",
            "prescription": True,
        },
        {
            "name": "Tramadol",
            "ingredients": "Tramadol hydrochloride",
            "benefits": "مسكن قوي للآلام المتوسطة إلى الشديدة.",
            "side_effects": "دوار، نعاس، إدمان عند سوء الاستخدام.",
            "prescription": True,
        },
        {
            "name": "Codeine",
            "ingredients": "Codeine phosphate",
            "benefits": "مسكن للألم ومضاد للسعال.",
            "side_effects": "إمساك، نعاس، إدمان عند الاستخدام المفرط.",
            "prescription": True,
        },
        {
            "name": "Amoxicillin",
            "ingredients": "Amoxicillin",
            "benefits": "مضاد حيوي واسع الطيف لعلاج التهابات مختلفة.",
            "side_effects": "إسهال، طفح جلدي، حساسية.",
            "prescription": True,
        },
        {
            "name": "Azithromycin",
            "ingredients": "Azithromycin",
            "benefits": "مضاد حيوي لالتهابات الجهاز التنفسي والجلد.",
            "side_effects": "غثيان، إسهال، ألم بطن.",
            "prescription": True,
        },
        {
            "name": "Ciprofloxacin",
            "ingredients": "Ciprofloxacin",
            "benefits": "مضاد حيوي لالتهابات البول والجهاز الهضمي.",
            "side_effects": "غثيان، دوار، تأثير على الأوتار.",
            "prescription": True,
        },

        # ==============================  باقي المجموعة ==============================
        {
            "name": "Metronidazole",
            "ingredients": "Metronidazole",
            "benefits": "لعلاج التهابات الجهاز الهضمي والأسنان.",
            "side_effects": "طعم معدني، غثيان، صداع.",
            "prescription": True,
        },
        {
            "name": "Omeprazole",
            "ingredients": "Omeprazole",
            "benefits": "يقلل حموضة المعدة ويعالج القرحة.",
            "side_effects": "صداع، إسهال.",
            "prescription": False,
        },
        {
            "name": "Pantoprazole",
            "ingredients": "Pantoprazole",
            "benefits": "يستخدم لعلاج حموضة المعدة.",
            "side_effects": "غثيان، انتفاخ.",
            "prescription": False,
        },
        {
            "name": "Metformin",
            "ingredients": "Metformin",
            "benefits": "لعلاج داء السكري النوع الثاني.",
            "side_effects": "غثيان، إسهال.",
            "prescription": True,
        },
        {
            "name": "Gliclazide",
            "ingredients": "Gliclazide",
            "benefits": "يخفض سكر الدم.",
            "side_effects": "هبوط سكر.",
            "prescription": True,
        },
        {
            "name": "Amlodipine",
            "ingredients": "Amlodipine",
            "benefits": "لعلاج ارتفاع الضغط.",
            "side_effects": "تورم القدمين.",
            "prescription": True,
        },
        {
            "name": "Losartan",
            "ingredients": "Losartan",
            "benefits": "لعلاج الضغط وحماية الكلى.",
            "side_effects": "دوار، ارتفاع بوتاسيوم.",
            "prescription": True,
        },
        {
            "name": "Lisinopril",
            "ingredients": "Lisinopril",
            "benefits": "مخفض للضغط.",
            "side_effects": "سعال جاف.",
            "prescription": True,
        },
        {
            "name": "Hydrochlorothiazide",
            "ingredients": "HCT",
            "benefits": "مدر للبول لعلاج الضغط.",
            "side_effects": "نقص بوتاسيوم.",
            "prescription": True,
        },
        {
            "name": "Furosemide",
            "ingredients": "Furosemide",
            "benefits": "مدر قوي.",
            "side_effects": "جفاف، دوار.",
            "prescription": True,
        },
        {
            "name": "Cetirizine",
            "ingredients": "Cetirizine",
            "benefits": "مضاد حساسية.",
            "side_effects": "نعاس بسيط.",
            "prescription": False,
        },
        {
            "name": "Loratadine",
            "ingredients": "Loratadine",
            "benefits": "مضاد حساسية بدون نعاس.",
            "side_effects": "جفاف فم.",
            "prescription": False,
        },
        {
            "name": "Prednisone",
            "ingredients": "Prednisone",
            "benefits": "كورتيزون لعلاج الالتهابات.",
            "side_effects": "زيادة وزن، ضغط.",
            "prescription": True,
        },
        {
            "name": "Warfarin",
            "ingredients": "Warfarin",
            "benefits": "مميع دم.",
            "side_effects": "نزيف.",
            "prescription": True,
        },
        {
            "name": "Clopidogrel",
            "ingredients": "Clopidogrel",
            "benefits": "مضاد صفائح.",
            "side_effects": "نزيف.",
            "prescription": True,
        },
        {
            "name": "Diazepam",
            "ingredients": "Diazepam",
            "benefits": "مهدئ ومرخي عضلات.",
            "side_effects": "نعاس وإدمان.",
            "prescription": True,
        },
        {
            "name": "Sertraline",
            "ingredients": "Sertraline",
            "benefits": "مضاد اكتئاب.",
            "side_effects": "غثيان، أرق.",
            "prescription": True,
        },
        {
            "name": "Fluoxetine",
            "ingredients": "Fluoxetine",
            "benefits": "مضاد اكتئاب.",
            "side_effects": "قلق، غثيان.",
            "prescription": True,
        },
        {
            "name": "Vitamin D",
            "ingredients": "Cholecalciferol",
            "benefits": "علاج نقص فيتامين د.",
            "side_effects": "آمن غالبًا.",
            "prescription": False,
        },
        {
            "name": "Folic Acid",
            "ingredients": "Folic acid",
            "benefits": "مهم للحوامل وصحة الدم.",
            "side_effects": "آمن غالبًا.",
            "prescription": False,
        },
    ]


# ===================== دوال الذكاء البسيط =====================
def score_medicine(m, query_lower: str) -> int:
    all_text = f"{m['name']} {m['ingredients']} {m['benefits']} {m['side_effects']}".lower()
    words = [w for w in query_lower.split() if len(w) >= 3]
    score = 0
    for w in words:
        if w in all_text:
            score += 1
    return score


def format_answer(m):
    base = (
        f"اسم الدواء: {m['name']}\n\n"
        f"المكونات:\n{m['ingredients']}\n\n"
        f"الفوائد:\n{m['benefits']}\n\n"
        f"الأعراض الجانبية:\n{m['side_effects']}"
    )
    if m["prescription"]:
        warning = "\n\n⚠️ هذا الدواء يتطلب وصفة طبية."
    else:
        warning = "\n\nℹ️ يُصرف بدون وصفة."
    return base + warning


def is_greeting(text: str) -> bool:
    t = text.lower().strip()
    G = ["السلام عليكم", "مرحبا", "هلا", "اهلا", "hi", "hello", "hey"]
    return any(g in t for g in G)


def is_thanks(text: str) -> bool:
    t = text.lower().strip()
    T = ["شكرا", "شكراً", "thanks", "thank you"]
    return any(x in t for x in T)


def find_closest_medicine_by_name(text: str, medicines):
    t = text.lower()
    words = [w for w in t.split() if len(w) >= 3]
    best_ratio, best_med, best_word = 0, None, None

    for w in words:
        for m in medicines:
            ratio = difflib.SequenceMatcher(None, w, m["name"].lower()).ratio()
            if ratio > best_ratio:
                best_ratio, best_med, best_word = ratio, m, w

    if best_ratio >= 0.75:
        return best_med, best_word, best_ratio

    return None, None, None


def ask_ai(text, medicines):
    lower = text.lower().strip()

    # ترحيب
    if is_greeting(lower):
        return "وعليكم السلام 😊 كيف أقدر أساعدك؟"

    # شكر
    if is_thanks(lower):
        return "العفو 🌟 هذا واجبي!"

    # تصحيح اسم دواء
    guessed, wrong, r = find_closest_medicine_by_name(lower, medicines)
    if guessed:
        return f"هل تقصد **{guessed['name']}**؟ (تشابه {int(r*100)}%)\n\n" + format_answer(guessed)

    # بحث مبسط
    best_score, best_med = 0, None
    for m in medicines:
        s = score_medicine(m, lower)
        if s > best_score:
            best_score, best_med = s, m

    if best_med and best_score > 0:
        return "أقرب دواء لسؤالك هو:\n\n" + format_answer(best_med)

    return "لم أفهم سؤالك، جرب تكتب اسم الدواء أو المشكلة الصحية 👍"


# ===================== الجلسة =====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "medicines" not in st.session_state:
    st.session_state.medicines = get_default_medicines()
if "chat" not in st.session_state:
    st.session_state.chat = []


# ===================== تسجيل الدخول =====================
def login_page():
    st.title("💊 تسجيل الدخول")

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = USERS[username]
            st.success("تم تسجيل الدخول بنجاح ✔")
            st.experimental_rerun()
        else:
            st.error("❌ معلومات غير صحيحة")


# ===================== التطبيق الرئيسي =====================
def main_app():
    st.title("💊 Pharmacy Assistant – مساعد الصيدلية")

    user = st.session_state.user
    meds = st.session_state.medicines

    tab1, tab2, tab3 = st.tabs(["📋 قائمة الأدوية", "🤖 مساعد الذكاء", "🛠️ إدارة الأدمن"])

    # -------- tab 1 --------
    with tab1:
        st.subheader("قائمة الأدوية")
        show_rx = st.checkbox("عرض الأدوية ذات الوصفة الطبية فقط")

        data = []
        for m in meds:
            if show_rx and not m["prescription"]:
                continue
            data.append({
                "Name": m["name"],
                "Ingredients": m["ingredients"],
                "Benefits": m["benefits"],
                "Side Effects": m["side_effects"],
                "Prescription": "⚠️ نعم" if m["prescription"] else "لا"
            })

        st.dataframe(data)

    # -------- tab 2 --------
    with tab2:
        st.subheader("🤖 اسأل مساعد الصيدلية")

        for sender, msg in st.session_state.chat:
            if sender == "user":
                st.markdown(f"🧑 **أنت:** {msg}")
            else:
                st.markdown(f"🤖 **المساعد:** {msg}")

        message = st.text_input("اكتب سؤالك:")

        col1, col2 = st.columns(2)
        if col1.button("إرسال"):
            if message.strip():
                st.session_state.chat.append(("user", message))
                answer = ask_ai(message, meds)
                st.session_state.chat.append(("bot", answer))
                st.experimental_rerun()
        if col2.button("مسح المحادثة"):
            st.session_state.chat = []
            st.experimental_rerun()

    # -------- tab 3 --------
    with tab3:
        if not user["admin"]:
            st.error("❌ هذه الصفحة للأدمن فقط")
            return

        st.subheader("🛠️ إدارة الأدوية")

        st.markdown("### إضافة دواء جديد")
        with st.form("add_med"):
            name = st.text_input("اسم الدواء")
            ing = st.text_input("المكونات")
            ben = st.text_area("الفوائد")
            se = st.text_area("الأعراض الجانبية")
            rx = st.checkbox("يحتاج وصفة طبية؟")
            submit = st.form_submit_button("إضافة")
            if submit:
                st.session_state.medicines.append({
                    "name": name,
                    "ingredients": ing,
                    "benefits": ben,
                    "side_effects": se,
                    "prescription": rx,
                })
                st.success("✔ تم الإضافة")
                st.experimental_rerun()

        st.markdown("---")

        st.markdown("### حذف دواء")
        names = [m["name"] for m in meds]
        selected = st.selectbox("اختر دواء:", names)
        if st.button("حذف"):
            idx = names.index(selected)
            del st.session_state.medicines[idx]
            st.success("✔ تم الحذف")
            st.experimental_rerun()


# ===================== تشغيل =====================
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
