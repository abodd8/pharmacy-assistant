import streamlit as st
import difflib
import pandas as pd

# ================== إعداد الصفحة العامة ==================
st.set_page_config(
    page_title="Pharmacy Assistant",
    page_icon="💊",
    layout="wide",
)

# ================== تنسيق عام للتطبيق (ثيم أبيض) ==================
APP_CSS = """
<style>
/* خلفية التطبيق كاملة */
.stApp {
    background: #f5f7fb;
    font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* حاويات عامة */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* عنوان رئيسي */
.main-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #111827;
}

/* أنيميشن خفيفة للدخول */
.fade-in {
    animation: fadeIn 0.7s ease-out;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(8px);}
    to   {opacity: 1; transform: translateY(0);}
}

/* كرت تسجيل الدخول */
.login-card {
    max-width: 480px;
    margin: 2.5rem auto;
    padding: 2.2rem 2rem;
    background: rgba(255,255,255,0.96);
    border-radius: 18px;
    box-shadow: 0 18px 40px rgba(15,23,42,0.18);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(226,232,240,0.9);
}

/* أزرار */
.stButton>button {
    border-radius: 999px;
    font-weight: 600;
    padding: 0.5rem 1.6rem;
    border: none;
    background: linear-gradient(135deg,#2563eb,#0ea5e9);
    color: white;
    box-shadow: 0 10px 25px rgba(37,99,235,0.35);
}
.stButton>button:hover {
    background: linear-gradient(135deg,#1d4ed8,#0284c7);
}

/* حقول الإدخال */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea {
    background: #f9fafb;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
    border: 1px solid #2563eb !important;
}

/* التبويبات */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    padding: 0.4rem 1.3rem;
}

/* شريط علوي بسيط للعنوان */
.page-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}
.pill-logo {
    width: 40px;
    height: 40px;
    border-radius: 999px;
    background: linear-gradient(135deg,#f97316,#ec4899);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.4rem;
}
.page-header-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #111827;
}
.page-header-sub {
    font-size: 0.9rem;
    color: #6b7280;
}
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# ================== حسابات المستخدمين ==================
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "12345", "role": "user"},
}

# ================== بيانات الأدوية (حوالي 60 دواء) ==================
def get_default_medicines():
    meds = [
        # name, ingredients, benefits, side_effects, prescription
        ("Paracetamol", "Acetaminophen",
         "مسكن للآلام وخافض للحرارة.", "مشاكل كبدية عند الجرعة العالية.", False),
        ("Ibuprofen", "Ibuprofen",
         "مسكن للألم، مضاد التهاب، خافض حرارة.", "تهيج معدة، قرحة، مشاكل كلى.", False),
        ("Aspirin", "Acetylsalicylic acid",
         "مسكن ومضاد التهاب، ومميع للدم بجرعات صغيرة.", "نزيف معدي، حساسية، قرحة.", True),
        ("Amoxicillin", "Amoxicillin",
         "مضاد حيوي لعلاج التهابات مختلفة.", "إسهال، طفح جلدي، حساسية.", True),
        ("Azithromycin", "Azithromycin",
         "مضاد حيوي لالتهابات الجهاز التنفسي والجلد.", "غثيان، إسهال، اضطراب كبد.", True),
        ("Ciprofloxacin", "Ciprofloxacin",
         "مضاد حيوي واسع الطيف.", "اضطراب معدة، صداع، تهيج أوتار.", True),
        ("Metformin", "Metformin",
         "لعلاج السكري النوع الثاني.", "اضطرابات معدية، نقص B12 نادراً.", True),
        ("Insulin", "Insulin",
         "تنظيم سكر الدم في السكري.", "هبوط سكر، زيادة وزن.", True),
        ("Omeprazole", "Omeprazole",
         "يقلل حموضة المعدة وقرحة المعدة.", "صداع، إسهال، نقص مغنيسيوم مع الاستخدام الطويل.", False),
        ("Pantoprazole", "Pantoprazole",
         "يقلل إفراز الحمض لعلاج الارتجاع.", "صداع، ألم بطن.", False),
        ("Loratadine", "Loratadine",
         "مضاد هيستامين للحساسية.", "نعاس بسيط، جفاف فم.", False),
        ("Cetirizine", "Cetirizine",
         "مضاد هيستامين فعال للحساسية.", "نعاس، جفاف فم.", False),
        ("Prednisone", "Prednisone",
         "ستيرويد لعلاج الالتهابات الشديدة.", "زيادة وزن، ارتفاع ضغط، هشاشة عظام.", True),
        ("Hydrocortisone cream", "Hydrocortisone",
         "كريم موضعي لعلاج الحكة والالتهاب الجلدي.", "ترقق جلد مع الاستخدام الطويل.", False),
        ("Salbutamol inhaler", "Salbutamol",
         "يوسع القصبات في الربو.", "رجفة، خفقان قلب.", True),
        ("Fluticasone inhaler", "Fluticasone",
         "كورتيزون استنشاقي للربو المزمن.", "بحة صوت، فطريات فم إذا لم يتم المضمضة.", True),
        ("Atorvastatin", "Atorvastatin",
         "يخفض الكوليسترول.", "ألم عضلات، اضطراب كبد.", True),
        ("Simvastatin", "Simvastatin",
         "تخفيض الدهون في الدم.", "ألم عضلات، اضطراب كبد.", True),
        ("Losartan", "Losartan",
         "لعلاج ارتفاع ضغط الدم.", "دوخة، ارتفاع بوتاسيوم.", True),
        ("Amlodipine", "Amlodipine",
         "موسع أوعية لارتفاع الضغط والذبحة.", "تورم كاحل، صداع.", True),
        ("Enalapril", "Enalapril",
         "ACE inhibitor لعلاج الضغط وفشل القلب.", "كحة جافة، ارتفاع بوتاسيوم.", True),
        ("Furosemide", "Furosemide",
         "مدر بول لعلاج احتباس السوائل.", "جفاف، نقص بوتاسيوم.", True),
        ("Hydrochlorothiazide", "Hydrochlorothiazide",
         "مدر بول خفيف للضغط.", "اضطراب أملاح، زيادة سكر الدم.", True),
        ("Warfarin", "Warfarin",
         "مضاد تخثر لمنع الجلطات.", "نزيف خطير إذا ارتفعت الجرعة.", True),
        ("Clopidogrel", "Clopidogrel",
         "مضاد صفائح لمنع جلطة قلب/دماغ.", "نزيف، كدمات.", True),
        ("Diazepam", "Diazepam",
         "مهدئ ومرخي عضلات.", "نعاس شديد، إدمان.", True),
        ("Sertraline", "Sertraline",
         "مضاد اكتئاب من نوع SSRI.", "غثيان، أرق، ضعف جنسي.", True),
        ("Fluoxetine", "Fluoxetine",
         "مضاد اكتئاب يستخدم أيضاً للوسواس.", "أرق، فقدان شهية.", True),
        ("Vitamin D", "Cholecalciferol",
         "تعويض نقص فيتامين د.", "فرط كالسيوم نادراً مع الجرعات العالية.", False),
        ("Folic Acid", "Folic acid",
         "لعلاج ومنع فقر الدم بنقص الفوليك.", "نادراً غثيان بسيط.", False),
        ("Iron tablets", "Ferrous sulfate",
         "علاج فقر الدم بنقص الحديد.", "إمساك، تغير لون البراز.", False),
        ("Calcium tablets", "Calcium carbonate",
         "تقوية العظام ونقص الكالسيوم.", "إمساك، حصى كلى بجرعة عالية.", False),
        ("Levothyroxine", "Levothyroxine",
         "لعلاج قصور الغدة الدرقية.", "خفقان، فقدان وزن عند زيادة الجرعة.", True),
        ("Methimazole", "Methimazole",
         "لعلاج فرط نشاط الغدة الدرقية.", "نقص كريات دم، طفح جلدي.", True),
        ("Metoclopramide", "Metoclopramide",
         "لعلاج الغثيان والقيء.", "نعاس، اضطرابات حركية نادرة.", True),
        ("Ondansetron", "Ondansetron",
         "مضاد قوي للغثيان خاصة مع العلاج الكيماوي.", "إمساك، صداع.", True),
        ("Loperamide", "Loperamide",
         "يقلل الإسهال الحاد.", "إمساك، مغص.", False),
        ("ORS", "Glucose + electrolytes",
         "محلول تعويض أملاح في الإسهال.", "آمن غالباً.", False),
        ("Diclofenac", "Diclofenac",
         "مسكن قوي ومضاد التهاب.", "قرحة معدة، مشاكل كلى.", True),
        ("Naproxen", "Naproxen",
         "مسكن ومضاد التهاب للألم المزمن.", "تهيج معدة، نزيف.", True),
        ("Tramadol", "Tramadol",
         "مسكن أفيوني متوسط الشدة.", "دوخة، إدمان، تشنجات بجرعة عالية.", True),
        ("Morphine", "Morphine",
         "مسكن أفيوني قوي للألم الشديد.", "اكتئاب تنفسي، إدمان.", True),
        ("Saline nasal spray", "Sodium chloride",
         "ترطيب الأنف وعلاج الجفاف.", "آمن غالباً.", False),
        ("Chlorhexidine mouthwash", "Chlorhexidine",
         "غسول فم مطهر.", "تصبغ أسنان مؤقت، طعم مر.", False),
        ("Guaifenesin syrup", "Guaifenesin",
         "طارد للبلغم في الكحة الرطبة.", "غثيان بسيط.", False),
        ("Dextromethorphan", "Dextromethorphan",
         "مضاد سعال للكحة الجافة.", "دوخة، نعاس.", False),
        ("Insulin glargine", "Insulin glargine",
         "أنسولين طويل المفعول.", "هبوط سكر، زيادة وزن.", True),
        ("Insulin lispro", "Insulin lispro",
         "أنسولين سريع المفعول.", "هبوط سكر.", True),
        ("Ranitidine", "Ranitidine",
         "لتقليل حموضة المعدة (أوقف في دول كثيرة).", "صداع، إسهال.", True),
        ("Spironolactone", "Spironolactone",
         "مدر بول يحافظ على البوتاسيوم.", "ارتفاع بوتاسيوم، تضخم ثدي.", True),
        ("Magnesium oxide", "Magnesium oxide",
         "لعلاج نقص المغنيسيوم والإمساك أحياناً.", "إسهال.", False),
        ("Zinc tablets", "Zinc",
         "دعم المناعة وتحسين التئام الجروح.", "غثيان خفيف.", False),
        ("Multivitamin", "Vitamins + minerals",
         "تعويض نقص الفيتامينات.", "غثيان خفيف، بول غامق.", False),
    ]

    records = []
    for name, ing, ben, se, rx in meds:
        records.append(
            {
                "Name": name,
                "Ingredients": ing,
                "Benefits": ben,
                "Side Effects": se,
                "Prescription": "نعم" if rx else "لا",
            }
        )
    return records


# ================== تهيئة session_state ==================
if "medicines" not in st.session_state:
    st.session_state.medicines = get_default_medicines()

if "user" not in st.session_state:
    st.session_state.user = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # للشات العام

# ================== منطق الذكاء البسيط ==================
GREETINGS = ["hi", "hello", "hey", "السلام", "مرحبا", "اهلا", "هلا"]

def is_greeting(text: str) -> bool:
    t = text.lower()
    return any(g in t for g in GREETINGS)

def find_medicine_by_name(name: str):
    names = [m["Name"] for m in st.session_state.medicines]
    match = difflib.get_close_matches(name, names, n=1, cutoff=0.7)
    if match:
        for m in st.session_state.medicines:
            if m["Name"] == match[0]:
                return m, match[0]
    return None, None

def ai_answer(question: str) -> str:
    q_lower = question.lower().strip()

    # 1) رسائل الترحيب
    if is_greeting(q_lower):
        return (
            "أهلاً وسهلاً 👋\n\n"
            "أنا مساعد الصيدلية الذكي. يمكنك سؤالي عن:\n"
            "- استخدامات دواء معيّن\n"
            "- الأعراض الجانبية\n"
            "- اقتراح دواء بناءً على المكونات\n"
            "مع ملاحظة: هذه المعلومات للتثقيف فقط وليست بديلاً عن استشارة الطبيب."
        )

    # 2) محاولة معرفة اسم دواء مذكور في السؤال
    names = [m["Name"] for m in st.session_state.medicines]
    best = difflib.get_close_matches(question, names, n=1, cutoff=0.8)
    if best:
        med, _ = find_medicine_by_name(best[0])
        if med:
            return format_medicine_answer(med)

    # 3) تجربة استخراج كلمة تشبه اسم دواء من الجملة
    words = [w for w in q_lower.replace(",", " ").split() if len(w) > 3]
    best_med = None
    best_score = 0.0
    best_correct_name = None

    for w in words:
        med, correct = find_medicine_by_name(w)
        if med:
            score = difflib.SequenceMatcher(None, w.lower(), correct.lower()).ratio()
            if score > best_score:
                best_score = score
                best_med = med
                best_correct_name = correct

    if best_med:
        if best_score < 0.95:
            return (
                f"أظن أنك تقصد الدواء: **{best_correct_name}** 🤔\n\n"
                + format_medicine_answer(best_med)
            )
        else:
            return format_medicine_answer(best_med)

    return (
        "لم أجد دواءً مطابقاً في قاعدة البيانات الحالية.\n"
        "جرّب أن تكتب اسم الدواء بالإنجليزية أو جزءاً من اسمه، "
        "أو اسأل عن الأعراض الجانبية لدواء محدد."
    )

def format_medicine_answer(med: dict) -> str:
    return (
        f"**اسم الدواء:** {med['Name']}\n\n"
        f"**المكونات:** {med['Ingredients']}\n\n"
        f"**الفوائد / الاستخدامات:**\n{med['Benefits']}\n\n"
        f"**الأعراض الجانبية:**\n{med['Side Effects']}\n\n"
        f"**يحتاج وصفة طبية؟** {med['Prescription']}"
    )


# ================== صفحة تسجيل الدخول ==================
def login_page():
    left, right = st.columns([1.1, 1])

    with left:
        st.markdown(
            """
            <div class="login-card fade-in">
                <div class="page-header">
                    <div class="pill-logo">💊</div>
                    <div>
                        <div class="page-header-title">تسجيل الدخول</div>
                        <div class="page-header-sub">مساعد الصيدلية الذكي لمشروعك الجامعي</div>
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        username = st.text_input("اسم المستخدم", key="login_username")
        password = st.text_input("كلمة المرور", type="password", key="login_password")

        login_btn = st.button("دخول", use_container_width=True)

        if "login_message" not in st.session_state:
            st.session_state.login_message = ""

        if login_btn:
            user = USERS.get(username)
            if user and user["password"] == password:
                st.session_state.user = {
                    "username": username,
                    "role": user.get("role", "user"),
                }
                st.session_state.login_message = "تم تسجيل الدخول بنجاح ✔"
                st.success(st.session_state.login_message)
                st.rerun()
            else:
                st.session_state.login_message = "❌ اسم المستخدم أو كلمة المرور غير صحيحة"
                st.error(st.session_state.login_message)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
        st.markdown("### ")
        st.image(
            "https://img.lovepik.com/photo/48010/7998.jpg_wh860.jpg",
            caption="Pharmacy Assistant • Smart Medicine Helper",
            use_column_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ================== التطبيق الرئيسي بعد تسجيل الدخول ==================
def main_app(user: dict):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)

    # هيدر علوي
    st.markdown(
        f"""
        <div class="page-header">
            <div class="pill-logo">💊</div>
            <div>
                <div class="page-header-title">مساعد الصيدلية الذكي</div>
                <div class="page-header-sub">
                    مرحباً {user.get("username","")} – الدور: {"أدمن" if user.get("role")=="admin" else "مستخدم عادي"}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["📋 قائمة الأدوية", "🤖 مساعد الذكاء", "💬 شات عام"])

    # ============ التبويب 1: جدول الأدوية ============
    with tab1:
        st.subheader("قائمة الأدوية المتوفرة")

        df = pd.DataFrame(st.session_state.medicines)

        show_rx_only = st.checkbox("عرض الأدوية الموصوفة للطبيب فقط")
        if show_rx_only:
            df_show = df[df["Prescription"] == "نعم"]
        else:
            df_show = df

        st.dataframe(df_show, use_container_width=True, height=460)

        # قسم خاص بالأدمن فقط لإضافة دواء جديد
        if user.get("role") == "admin":
            st.markdown("---")
            st.markdown("#### إضافة دواء جديد (أدمن فقط)")
            with st.form("add_medicine_form"):
                name = st.text_input("اسم الدواء بالإنجليزية")
                ing = st.text_input("المكونات")
                ben = st.text_area("الفوائد / الاستخدامات")
                se = st.text_area("الأعراض الجانبية")
                rx_flag = st.checkbox("يحتاج وصفة طبية؟")
                submitted = st.form_submit_button("إضافة الدواء")

            if submitted:
                if not name.strip():
                    st.error("يجب إدخال اسم الدواء.")
                else:
                    st.session_state.medicines.append(
                        {
                            "Name": name.strip(),
                            "Ingredients": ing.strip(),
                            "Benefits": ben.strip(),
                            "Side Effects": se.strip(),
                            "Prescription": "نعم" if rx_flag else "لا",
                        }
                    )
                    st.success(f"تمت إضافة الدواء: {name}")
                    st.rerun()

    # ============ التبويب 2: AI Assistant ============
    with tab2:
        st.subheader("مساعد الذكاء الخاص بالأدوية")

        user_q = st.text_input(
            "اسأل عن دواء، جرعة عامة، أو أعراض جانبية (المعلومات تثقيفية فقط):",
            key="ai_question",
        )

        if st.button("اسأل الذكاء 🤖", key="ai_btn"):
            if not user_q.strip():
                st.warning("اكتب سؤالاً أولاً.")
            else:
                answer = ai_answer(user_q)
                st.markdown("#### الرد:")
                st.markdown(answer)

    # ============ التبويب 3: شات عام ============
    with tab3:
        st.subheader("شات عام بين مستخدمي النظام")

        for msg_user, msg_text in st.session_state.chat_history:
            st.markdown(f"**{msg_user}:** {msg_text}")

        new_msg = st.text_area("اكتب رسالة جديدة:", key="chat_input")
        if st.button("إرسال", key="chat_send"):
            if new_msg.strip():
                st.session_state.chat_history.append(
                    (user.get("username", "مستخدم"), new_msg.strip())
                )
                st.rerun()
            else:
                st.warning("الرسالة فارغة.")

    st.markdown("</div>", unsafe_allow_html=True)


# ================== نقطة التشغيل ==================
def main():
    user = st.session_state.user
    if user is None:
        login_page()
    else:
        # زر تسجيل خروج صغير في الشريط الجانبي
        with st.sidebar:
            st.markdown("### الحساب")
            st.write(f"المستخدم: {user.get('username')}")
            st.write(f"الدور: {'أدمن' if user.get('role')=='admin' else 'مستخدم'}")
            if st.button("تسجيل الخروج"):
                st.session_state.user = None
                st.rerun()

        main_app(user)


if __name__ == "__main__":
    main()
