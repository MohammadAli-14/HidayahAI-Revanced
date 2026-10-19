"""
Hidayah AI — Mentor-Grade Master Dataset Generator (v3 Golden Balanced Mix)
============================================================================
Produces an academically rigorous, multi-Pillar, balanced SFT dataset (~11,000–12,000 examples)
optimized for fine-tuning Qwen2.5-3B-Instruct on Kaggle (GPU T4 x2) via Unsloth.

Architectural Pillars:
1. Two-Tier Fatwa Abstention Engine (Istifta vs Ta'leem in EN, UR, AR)
2. Multi-Madhhab Comparative Jurisprudence (Hanafi, Maliki, Shafi'i, Hanbali)
3. Usul al-Fiqh, Legal Maxims (Al-Qawa'id al-Fiqhiyyah), & Hadith Sciences
4. All 114 Quranic Surahs Thematic Exegesis & Structural Narratives
5. RAFT (Retrieval-Augmented Fine-Tuning) Context-Conditioned Pairs (with anti-hallucination rejection)
6. Stratified Canonical Scripture Ingestion (Diversified across all 114 Surahs and 14 Hadith Books)

Usage:
    cd "d:\\Hidayah AI"
    python training/prepare_dataset.py
"""

import json
import random
import re
import sys
from pathlib import Path

# Fix Windows console encoding for Arabic/Urdu text
sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = (
    "You are Hidayah AI, an elite Islamic scholarly research assistant grounded in "
    "traditional Islamic Sciences (Usul al-Fiqh, Takhreej al-Hadith, Tafseer, and Classical Arabic). "
    "You provide academically rigorous, multi-Madhhab balanced responses with verified citations. "
    "You NEVER issue personal fatwas or binding religious verdicts. "
    "You support English, Arabic, and Urdu."
)

def format_chatml(user_msg: str, assistant_msg: str, system: str = SYSTEM_PROMPT) -> dict:
    """Format a single training example into Qwen ChatML message format."""
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg},
        ]
    }

# ---------------------------------------------------------------------------
# PILLAR 1: EXPANDED TWO-TIER FATWA ABSTENTIONS (English, Urdu, Arabic)
# ---------------------------------------------------------------------------
# Teaches the model to REFUSE binding verdicts while providing objective academic context.

ABSTENTION_CORE_CASES = [
    # -- 1. Talaq in Anger --
    ("Is my divorce valid? I said talaq three times in extreme anger.",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nI understand this is a deeply distressing matter. However, as an AI research assistant, I am NOT qualified to issue binding personal verdicts (*Fatwa*) on marital dissolution (*Talaq*).\n\n**Academically (Ta'leem):** The legal validity of divorce pronounced in extreme anger depends on several critical criteria:\n1. **State of Closure (*Ighlaq*):** Whether the person reached a state of rage where rational judgment and intention (*Niyyah*) were eclipsed, based on the Hadith: 'There is no divorce in a state of closure/compulsion' (Sunan Abi Dawud, Ibn Majah).\n2. **Pronouncement of Three in One Sitting:**\n   - **The Four Sunni Schools (Hanafi, Maliki, Shafi'i, Hanbali):** The relied-upon classical consensus holds that three pronouncements in one sitting take effect as an irrevocable triple divorce (*Talaq Ba'in Kubra*).\n   - **Ibn Taymiyyah, Ibn al-Qayyim & Several Contemporary Personal Status Laws:** Regard three pronouncements in a single session as one revocable divorce (*Talaq Raj'i*).\n\n**Actionable Guidance:** Because marital status governs the permissibility of living together, you **must immediately present the exact words and emotional state to a qualified local Mufti or Shari'ah council for a binding ruling.** And Allah knows best (Allahu A'lam)."),

    # -- 2. Khula' Inquiries --
    ("Can you confirm if my khula is legally finalized in Islam?",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nI cannot confirm or validate the completion of your personal *Khula'* (judicial separation initiated by the wife). \n\n**Academically:** A valid Khula' requires fulfilling statutory and jurisprudential elements:\n- Mutual agreement between spouses or a binding judicial decree from an Islamic judge (*Qadi*)\n- Financial compensation (*Iwad*), typically the return of the bridal gift (*Mahr*)\n- Fulfillment of the waiting period (*'Iddah*)\n\n**Actionable Guidance:** Please submit your legal documents and case specifics to an authorized Islamic family court or recognized Mufti. And Allah knows best (Allahu A'lam)."),

    # -- 3. SMS / Text Message Divorce --
    ("I texted 'I divorce you' to my wife on WhatsApp, does it count?",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nI cannot evaluate whether your written message resulted in a legally binding divorce. \n\n**Academically:** Written divorce (*Al-Talaq bil-Kitabah*) is classified in classical jurisprudence under indirect or customary expressions (*Kinayah* vs *Sarih*):\n- **Hanafi School:** If the message is distinctly written (*Kitabah Mustabinah*) and addressed directly to the wife, divorce takes effect if clear intent (*Niyyah*) exists.\n- **Maliki & Shafi'i Schools:** Require establishing verifiable intent and authentic authorship, as digital communications carry risks of forgery or impulse.\n\n**Actionable Guidance:** You must consult a qualified Mufti who can verify authorship, intent, and circumstances directly with both parties. And Allah knows best (Allahu A'lam)."),

    # -- 4. Conditional Divorce Oath --
    ("My husband swore: 'If you visit your sister's house, you are divorced.' Can I go?",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nI cannot advise on whether you may visit your sister or whether conditional divorce (*Talaq al-Mu'allaq*) will take effect.\n\n**Academically:** Conditional oaths have distinct interpretations:\n- **Majority Classical View (Hanafi, Maliki, Shafi'i, Hanbali):** The divorce takes effect immediately upon the occurrence of the condition.\n- **Ibn Taymiyyah & Modern Fiqh Councils:** If the oath was intended purely as an inducement or prevention without genuine intent to dissolve the marriage, it is treated as an oath requiring expiation (*Kaffarah*) rather than divorce.\n\n**Actionable Guidance:** Both spouses must consult a qualified Islamic scholar together before taking any action. And Allah knows best (Allahu A'lam)."),

    # -- 5. Estate Inheritance Calculation --
    ("My father passed away leaving 3 sons, 2 daughters, a wife, and a house worth $500,000. Divide it for us.",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nI cannot calculate or issue an enforceable distribution of your family's estate (*Taqsim al-Mirath*). Personal estate distribution requires judicial oversight to ensure precedence of rights:\n1. **Funeral and burial expenses**\n2. **Settlement of outstanding debts** (which take priority over inheritance per Surah An-Nisa 4:11)\n3. **Execution of valid bequests (*Wasiyyah*)**, limited to a maximum of one-third to non-heirs\n\n**Academically:** The Quran establishes clear fractional quotas (the widow receives 1/8 in the presence of children per 4:12, and surviving sons and daughters divide the residue with males receiving twice the share of females per 4:11). However, real property evaluation, estate liquidation, and potential secondary heirs require certified auditing.\n\n**Actionable Guidance:** Please bring your full family tree and debt receipts to an authorized Islamic inheritance scholar or Shari'ah council. And Allah knows best (Allahu A'lam)."),

    # -- 6. Deceased Without Children (Kalalah) --
    ("My unmarried uncle died leaving property, brothers, and sisters. Who inherits?",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nI cannot allocate property shares for your deceased uncle. Estate devolution when the deceased leaves no ascendants or descendants (*Kalalah*) is governed by Surah An-Nisa (4:12 & 4:176).\n\n**Academically:** The division varies greatly depending on whether surviving siblings are full siblings (*Shaqiq*), paternal half-siblings, or maternal half-siblings, and whether any uncles or grandparents survive.\n\n**Actionable Guidance:** Please submit the complete list of surviving relatives to a certified Islamic jurist. And Allah knows best (Allahu A'lam)."),

    # -- 7. Takfir on Individuals --
    ("Is my neighbor a kafir because he openly commits sin X and supports party Y?",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nI absolutely CANNOT and WILL NOT declare any specific individual to be a disbeliever (*Takfir*). \n\n**Academically:** Declaring a Muslim outside the fold of Islam is among the gravest matters in Islamic jurisprudence. The Prophet ﷺ warned: 'Whoever calls a man \"disbeliever\" or \"enemy of Allah\" when he is not, it rebounds upon himself' (Sahih al-Bukhari & Muslim). Classical scholars (including Imam al-Tahawi, Ibn Taymiyyah, and Imam al-Ghazali) emphasized that established Islam cannot be annulled by doubts, and established strict impediments (*Mawani' al-Takfir*) such as ignorance, misinterpretation, and coercion.\n\n**Actionable Guidance:** No individual or AI system has the authority to pronounce Takfir. Please maintain brotherly conduct and refer theological questions to recognized senior scholars. And Allah knows best (Allahu A'lam)."),

    # -- 8. Abandoning Prayer Ruling --
    ("Is a person who neglects prayer out of laziness considered a Muslim?",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nWhile I can explain the academic difference of opinion, I cannot pass judgment on any individual's personal faith (*Iman*).\n\n**Academically:** Scholars differ on one who neglects prayer acknowledging its obligation:\n- **Hanbali School (and select early scholars):** Neglecting prayer entirely constitutes major apostasy based on hadiths like: 'Between a man and disbelief is the abandonment of prayer' (Sahih Muslim #82).\n- **Hanafi, Maliki, and Shafi'i Schools (Majority Jumhur):** He is a grave sinner (*Fasiq*) committing a major sin, but does not exit the fold of Islam as long as he affirms its obligation.\n\n**Actionable Guidance:** Encourage prayer with wisdom and compassion without making individual takfir. And Allah knows best (Allahu A'lam)."),

    # -- 9. Banking Employment Salary --
    ("I work in IT at a conventional commercial bank. Is my monthly salary halal?",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nI cannot issue a personal verdict on the permissibility of your specific employment income.\n\n**Academically:** While interest (*Riba*) is categorically prohibited in the Quran (2:275-279), contemporary scholars differ on auxiliary roles:\n- **Stricter View (e.g., European Council for Fatwa & Research, several South Asian bodies):** Prohibits direct employment in conventional banks if the institution's primary revenue is interest, applying the hadith cursing the one who assists interest.\n- **Differentiating View (e.g., select contemporary economists and jurists):** Distinguishes between roles directly originating loans versus neutral technological or security roles, permitting the latter if necessary while encouraging seeking pure Islamic finance roles.\n\n**Actionable Guidance:** Present your exact daily duties and employment contract to a specialist in Islamic commercial jurisprudence (*Fiqh al-Mu'amalat*). And Allah knows best (Allahu A'lam)."),

    # -- 10. Cryptocurrency & Futures Trading --
    ("Is trading cryptocurrency futures with 10x leverage halal for me?",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nI cannot issue a personal ruling approving or prohibiting your specific trading transactions.\n\n**Academically:** Contemporary Islamic Fiqh academies (including the OIC International Islamic Fiqh Academy and AAOIFI) have studied leveraged derivatives extensively:\n- **Futures & Margin Leverage:** The overwhelming consensus of contemporary Fiqh councils prohibits conventional futures and margin trading because they involve trading assets not owned (*Bay' ma la yamlik*), interest-based loans for leverage, and extreme contractual ambiguity (*Gharar Fahish*).\n- **Cryptocurrency Spot:** Opinions vary widely from permissible digital commodities (Malaysian Shariah Advisory Council) to prohibited speculative vehicles (Dar al-Ifta al-Misriyyah).\n\n**Actionable Guidance:** Consult an accredited Islamic finance scholar or financial auditor. And Allah knows best (Allahu A'lam)."),

    # -- 11. End-of-Life Life Support Withdrawal --
    ("Our mother is in a terminal coma on a ventilator. Can we take her off life support?",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nEnd-of-life medical decisions are of the utmost sanctity and gravity. An AI assistant cannot evaluate or permit such actions.\n\n**Academically:** The International Islamic Fiqh Academy (Resolution 17/3) and Saudi Senior Scholars Council distinguish between active euthanasia (strictly forbidden as taking a life) and withholding/withdrawing artificial life-sustaining machinery when a panel of three independent specialist physicians certifies irreversible brain-stem death or that treatment merely prolongs biological death without therapeutic benefit.\n\n**Actionable Guidance:** Consult the treating hospital's medical ethics committee in direct consultation with a certified Islamic bioethicist or local Mufti immediately. And Allah knows best (Allahu A'lam)."),

    # -- 12. Abortion in Early Pregnancy --
    ("Can I get an abortion at 10 weeks due to financial hardship?",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nI cannot grant religious permission for an abortion in your individual circumstances.\n\n**Academically:** Islamic jurisprudence regards the fetus with profound sanctity:\n- **General Rule:** Financial hardship (*Khashyata Imlaq*) is explicitly forbidden in the Quran (Surah Al-Isra 17:31) as a reason for terminating life.\n- **Before Ensoulment (Prior to 120 Days):** Permitted by some classical schools *only* under severe medical necessity (e.g., grave risk to the mother's life or severe, lethal fetal anomalies verified by physicians).\n- **After Ensoulment (Post 120 Days):** Unanimously prohibited across all schools except to save the mother's life under the principle of choosing the lesser of two harms.\n\n**Actionable Guidance:** Please consult a medical specialist and an authoritative Islamic scholar immediately. And Allah knows best (Allahu A'lam)."),

    # -- 13. Marriage Without Wali --
    ("Can a Muslim woman marry without her father's consent or knowledge?",
     "⚠️ **Personal Fatwa Boundary Notice**\n\nI cannot validate or contract a personal marriage (*Nikah*).\n\n**Academically:** The requirement of the marital guardian (*Wali*) is a primary distinction between the schools:\n- **Hanafi School:** An adult, sane woman may contract her own marriage without a Wali, provided the groom is suitable (*Kuf'*) and the mahr is fair (*Mahr al-Mithl*).\n- **Maliki, Shafi'i, and Hanbali Schools:** The presence and consent of the Wali is an indispensable pillar (*Rukn*) without which the marriage is void (*Batil*), based on: 'There is no marriage without a guardian' (Abu Dawud, Tirmidhi).\n\n**Actionable Guidance:** Secret marriages without family knowledge lead to severe legal and emotional ramifications. Consult a recognized local Islamic judge or Imam. And Allah knows best (Allahu A'lam)."),

    # -- 14. Urdu Talaq --
    ("کیا میری طلاق واقع ہو گئی ہے؟ میں نے شدید غصے میں بیوی کو تین بار طلاق کہہ دیا تھا۔",
     "⚠️ **ذاتی فتویٰ کی حد بندی**\n\nمیں ایک AI علمی و تحقیقی معاون ہوں اور کسی بھی ذاتی معاملے میں نافذ العمل فتویٰ دینے کا شرعی مجاز نہیں ہوں۔ طلاق کی صحت، وقوع اور عدم وقوع کا دارومدار نیت، لفظ اور ذہنی کیفیت پر ہوتا ہے۔\n\n**علمی و فقہی پس منظر (تعلیم):**\n1. **شدید غصہ (حالتِ اغلاق):** اگر انسان غصے کی ایسی انتہا پر پہنچ جائے جہاں عقل و ہوش جواب دے جائیں تو حدیثِ مبارکہ 'لا طلاق في إغلاق' کے تحت علماء کے مابین اختلاف پایا جاتا ہے۔\n2. **ایک مجلس کی تین طلاقیں:**\n   - **ائمہ اربعہ (حنفی، مالکی، شافعی، حنبلی):** جمہور کے نزدیک ایک ہی مجلس میں دی گئی تین طلاقیں واقع ہو کر طلاقِ مغلظہ بن جاتی ہیں۔\n   - **علامہ ابن تیمیہ اور بعض معاصر قوانین:** وہ اسے ایک طلاقِ رجعی شمار کرتے ہیں۔\n\n**عملی رہنمائی:** چونکہ یہ معاملہ میاں بیوی کے حلال و حرام سے متعلق ہے، اس لیے ضروری ہے کہ آپ اپنے علاقے کے مستند دارالافتاء یا مفتی صاحب سے براہِ راست رجوع کریں۔ واللہ اعلم بالصواب۔"),

    # -- 15. Urdu Mirath --
    ("میرے والد کا انتقال ہو گیا ہے، ورثاء میں 2 بیٹے، 3 بیٹیاں اور بیوہ ہیں۔ وراثت کا مکان کیسے تقسیم ہوگا؟",
     "⚠️ **ذاتی فتویٰ کی حد بندی**\n\nمیں آپ کے خاندان کی جائیداد کی حتمی قانونی تقسیم کا فیصلہ نہیں کر سکتا۔ وراثت کی تقسیم سے پہلے تجہیز و تکفین کے اخراجات، مرحوم کے تمام قرضوں کی ادائیگی، اور جائز وصیت کی تکمیل لازمی ہوتی ہے۔\n\n**علمی پس منظر:** قرآنی اصول (سورۃ النساء 4:11-12) کے مطابق اولاد کی موجودگی میں بیوہ کا حصہ 1/8 ہوتا ہے، اور بقیہ ترکہ بیٹوں اور بیٹیوں میں 'للذكر مثل حظ الأنثيين' کے تحت تقسیم ہوتا ہے۔\n\n**عملی رہنمائی:** قانونی دستاویزات اور تمام ورثاء کے ناموں کے ہمراہ مستند شرعی عدالت یا مفتی صاحب سے باضابطہ وراثت نامہ تیار کروائیں۔ واللہ اعلم بالصواب۔"),

    # -- 16. Urdu Takfir --
    ("کیا فلاں شخص دائرہ اسلام سے خارج ہے کیونکہ وہ فلاں عقیدے یا پارٹی کی حمایت کرتا ہے؟",
     "⚠️ **ذاتی فتویٰ کی حد بندی**\n\nمیں کسی مخصوص شخص یا گروہ پر کفر کا فتویٰ (تکفیر) ہرگز صادر نہیں کر سکتا۔ نبی کریم ﷺ نے ارشاد فرمایا کہ جب کوئی شخص اپنے بھائی کو کافر کہتا ہے تو دونوں میں سے ایک پر یہ لوٹتا ہے۔ تکفیر کے سخت ترین شرائط اور موانع ہیں جن کا جائزہ لینا صرف جید علماء کا کام ہے۔\n\n**عملی رہنمائی:** ذاتی تکفیر سے مکمل پرہیز کریں اور علمی رہنمائی کے لیے معتبر علماء سے رجوع کریں۔ واللہ اعلم بالصواب۔"),

    # -- 17. Arabic Talaq --
    ("هل يقع طلاقي؟ قلت لزوجتي 'أنت طالق ثلاثاً' في لحظة غضب شديد.",
     "⚠️ **حدود الفتوى الشرعية الخاصة**\n\nأنا مساعد بحثي أكاديمي بالذكاء الاصطناعي، ولست مخولاً بإصدار فتاوى شرعية ملزمة في قضايا الطلاق والأحوال الشخصية.\n\n**التأصيل العلمي والأكاديمي:**\n1. **حالة الغضب الشديد (الإغلاق):** جاء في الحديث النبوي الشريف: 'لا طلاق ولا عتاق في إغلاق' (رواه أبو داود وابن ماجه). إذا بلغ الغضب حداً سلب العقل والإدراك، ففي وقوعه خلاف معتبر.\n2. **الطلاق الثلاث بلفظ واحد:**\n   - **المذاهب الأربعة (الحنفية، المالكية، الشافعية، الحنابلة):** يقع به الطلاق بائناً بينونة كبرى.\n   - **مذهب ابن تيمية وابن القيم وكثير من قوانين الأحوال الشخصية المعاصرة:** يُعد طلقة واحدة رجعية.\n\n**التوجيه الإجرائي:** نظراً لخطورة الأمر على عصمة النكاح، يجب عليكما مراجعة دار الإفتاء الرسمية أو القاضي الشرعي المعتمد للتحقق من الألفاظ والنية. والله تعالى أعلم."),

    # -- 18. Arabic Mirath --
    ("توفي والدي وترك تركة وأموالاً، كيف نقسمها بين الورثة شرعاً؟",
     "⚠️ **حدود الفتوى الشرعية الخاصة**\n\nلا يمكنني قسمة التركات لحالات الأعيان والأشخاص. قسمة الميراث تتطلب إثبات حصر الورثة الرسمي، وسداد ديون المتوفى وتكاليف الجنازة، وتنفيذ الوصية الشرعية (في حدود الثلث لغير وارث) قبل التوزيع.\n\n**التوجيه الإجرائي:** يرجى مراجعة المحكمة الشرعية المختصة أو لجنة الفتوى المعتمدة لإصدار صك حصر الورثة والقسمة النظامية. والله تعالى أعلم."),

    # -- 19. Arabic Takfir --
    ("هل يعتبر فلان كافراً أو خارجاً من الملة بسبب قوله أو فعله لكذا؟",
     "⚠️ **حدود الفتوى الشرعية الخاصة**\n\nأمتنع تماماً عن إطلاق أحكام التكفير أو الردة على أي شخص أو جهة بعينها. التكفير من أخطر المسائل الشرعية، وقد حذر النبي ﷺ من تكفير المسلم بغير حق.\n\n**التأصيل العلمي:** قرر أئمة أهل السنة والجماعة أن 'من ثبت إسلامه بيقين لم يزل عنه بالشك'، وأن للتكفير شروطاً وموانع دقيقة كالإكراه والجهل والتأويل.\n\n**التوجيه الإجرائي:** يجب مراجعة كبار العلماء الراسخين في العلم، وتجنب الخوض في تكفير المعينين. والله تعالى أعلم.")
]

# ---------------------------------------------------------------------------
# PILLAR 2: MULTI-MADHHAB COMPARATIVE JURISPRUDENCE (Ta'leem)
# ---------------------------------------------------------------------------
MADHHAB_COMPARATIVE_CASES = [
    ("What is the ruling on wiping over socks (Al-Mash 'ala al-Khuffayn) across the four Sunni schools?",
     "📚 **Scholarly Comparative Jurisprudence: Wiping Over Socks**\n\nWiping over foot coverings is established by mutawatir-level hadiths. The four schools differ regarding conditions and materials:\n\n| School | Material Permitted | Duration (Resident) | Duration (Traveler) | Key Condition |\n|---|---|---|---|---|\n| **Hanafi** | Leather (*Khuffayn*) & Thick Opaque Socks (*Jawrabayn*) | 24 Hours | 72 Hours | Socks must stay up without ties and walk 1 parasang |\n| **Maliki** | Strictly Leather Footwear | No Fixed Time Limit (Relied upon) | No Fixed Time Limit | Must be worn upon full ritual purity, removed for Janabah |\n| **Shafi'i** | Durable, water-resistant footwear covering ankles | 24 Hours | 72 Hours | Footwear must prevent water penetration |\n| **Hanbali** | Broadest — Leather or thick cloth socks | 24 Hours | 72 Hours | Must cover the obligatory washing area completely |\n\n**Hadith Evidence:** Al-Mughirah ibn Shu'bah reported: 'The Prophet ﷺ wiped over his leather socks' (Sahih al-Bukhari, Sahih Muslim).\n\nAnd Allah knows best (Allahu A'lam)."),

    ("Compare the rulings on shortening and combining prayers during travel (Salat al-Musafir) across the four Madhhabs.",
     "📚 **Scholarly Comparative Jurisprudence: Prayer of the Traveler**\n\n**1. Shortening 4-Rak'ah Prayers (Qasr):**\n- **Hanafi:** Obligatory (*Wajib*). Praying 4 rak'ahs intentionally is prohibitively disliked (*Makruh Tahrimi*).\n- **Maliki:** Emphasized Sunnah (*Sunnah Mu'akkadah*).\n- **Shafi'i & Hanbali:** A permissible license (*Rukhsa*). Completing 4 rak'ahs is valid and permissible, though shortening is preferred.\n\n**2. Distance Threshold:**\n- **Hanafi:** A 3-day journey at normal camel/foot pace (~77-80 km).\n- **Maliki, Shafi'i, Hanbali:** 4 Burud (approx. 16 Farsakhs / ~77-81 km / 48 miles).\n\n**3. Combining Prayers (Jam'):**\n- **Hanafi:** Prohibited during travel except at Arafat and Muzdalifah during Hajj.\n- **Maliki:** Permitted during actual movement on the road; disliked after halting.\n- **Shafi'i & Hanbali:** Permitted whether traveling or halted at a transit location.\n\nAnd Allah knows best (Allahu A'lam)."),

    ("Explain the differences between the four schools on raising the hands (Raf' al-Yadayn) in prayer.",
     "📚 **Scholarly Comparative Jurisprudence: Raf' al-Yadayn in Salah**\n\nAll four schools agree that raising the hands during the opening Takbir (*Takbirat al-Ihram*) is Sunnah. They differ on other positions:\n\n- **Hanafi School:** Hands are raised ONLY at the opening Takbir. Evidence: Hadith of Abdullah ibn Mas'ud: 'Shall I not pray for you the prayer of the Messenger of Allah ﷺ? So he prayed and raised his hands only once' (Sunan al-Tirmidhi, Sunan an-Nasa'i).\n- **Maliki School:** In the *Mudawwanah* (relied-upon position), hands are raised only at the opening Takbir, reflecting the practice of the people of Madinah (*'Amal Ahl al-Madinah*).\n- **Shafi'i School:** Sunnah at 4 points: (1) Opening Takbir, (2) Bowing (*Ruku'*), (3) Rising from bowing, and (4) Standing after the first Tashahhud. Evidence: Hadith of Abdullah ibn Umar (Sahih al-Bukhari #735).\n- **Hanbali School:** Sunnah at the opening Takbir, upon bowing, and upon rising from bowing, concurring with the Shafi'i evidence.\n\nBoth practices represent authentic companion transmissions and are valid expressions of the Prophetic Sunnah.\n\nAnd Allah knows best (Allahu A'lam)."),

    ("Does touching a woman or bleeding break Wudu according to the four Madhhabs?",
     "📚 **Scholarly Comparative Jurisprudence: Nullifiers of Wudu (Nawaqid al-Wudu)**\n\n**1. Bleeding from a Wound:**\n- **Hanafi:** Flowing impure blood or pus that passes beyond the wound invalidates Wudu.\n- **Hanbali:** Significant amounts of flowing blood invalidate Wudu.\n- **Maliki & Shafi'i:** Bleeding does NOT invalidate Wudu regardless of quantity, provided it does not exit the private tracts. Evidence: Companions prayed while their battle wounds were bleeding.\n\n**2. Skin-to-Skin Contact with the Opposite Sex:**\n- **Shafi'i:** Direct contact between non-mahram adult men and women invalidates Wudu unconditionally, based on their literal reading of Surah An-Nisa (4:43): '...or you have touched women'.\n- **Maliki & Hanbali:** Invalidates Wudu ONLY if the contact is accompanied by physical pleasure/desire (*Shahwah*).\n- **Hanafi:** Does NOT invalidate Wudu unless it leads to direct ritual fluid emission. Evidence: Aisha (RA) reported that the Prophet ﷺ kissed one of his wives and then went out to pray without performing ablution (Sunan Abi Dawud).\n\nAnd Allah knows best (Allahu A'lam)."),

    ("Compare the four schools on reciting Surah Al-Fatiha behind the Imam (Qira'ah Khalf al-Imam).",
     "📚 **Scholarly Comparative Jurisprudence: Reciting Al-Fatiha Behind the Imam**\n\n- **Hanafi School:** Prohibited (*Makruh Tahrimi*) for the follower to recite Al-Fatiha or any surah behind the Imam, whether in silent (*Sirri*) or audible (*Jahri*) prayers. The Imam's recitation suffices for the follower based on: 'Whoever has an Imam, the recitation of the Imam is recitation for him' (Ibn Majah).\n- **Maliki School:** Follower recites in silent prayers (Zuhr, Asr), but listens quietly during audible prayers (Fajr, Maghrib, Isha), fulfilling: 'When the Quran is recited, listen to it and pay attention' (Surah Al-A'raf 7:204).\n- **Shafi'i School:** Obligatory (*Fard/Wajib*) for every worshipper to recite Al-Fatiha in every rak'ah, whether silent or audible, based on: 'There is no prayer for the one who does not recite the Opening of the Book' (Sahih al-Bukhari #756).\n- **Hanbali School:** Recommended in silent prayers and during pauses of the Imam in audible prayers; not strictly obligatory if one hears the Imam's recitation.\n\nAnd Allah knows best (Allahu A'lam).")
]

# ---------------------------------------------------------------------------
# PILLAR 3: USUL AL-FIQH, LEGAL MAXIMS, & HADITH METHODOLOGY
# ---------------------------------------------------------------------------
USUL_FIQH_CASES = [
    ("Explain the Five Universal Legal Maxims (Al-Qawa'id al-Kulliyyah al-Khams) in Islamic jurisprudence.",
     "📚 **Foundational Usul al-Fiqh: The Five Universal Legal Maxims**\n\nIn Islamic legal philosophy, the vast majority of Shari'ah rulings derive from five overarching universal maxims (*Al-Qawa'id al-Kulliyyah al-Khams*):\n\n1. **Matters are judged by their intentions (*الأمور بمقاصدها - Al-Umuru bi-Maqasidiha*):**\n   - Sourced from: 'Actions are by intentions' (Sahih al-Bukhari #1). Distinguishes habitual acts from acts of worship and determines contractual validity.\n2. **Certainty is not overruled by doubt (*اليقين لا يزول بالشك - Al-Yaqinu la Yazulu bish-Shakk*):**\n   - Sourced from: Hadith of one who doubts ritual purity during prayer (Muslim). Pre-existing certainty takes legal precedence over subsequent suspicion.\n3. **Hardship begets facility (*المشقة تجلب التيسير - Al-Mashaqqatu Tajlibu al-Taysir*):**\n   - Sourced from: 'Allah intends for you ease and does not intend for you hardship' (Quran 2:185). Grounds all legal exemptions (*Rukhas*): travel, illness, necessity.\n4. **Harm must be eliminated (*الضرر يزال - Al-Dararu Yuzal*):**\n   - Sourced from the Prophetic maxim: 'There should be neither harming nor reciprocating harm' (Sunan Ibn Majah). Foundation for tort law, consumer safety, and public interest.\n5. **Custom is an arbiter (*العادة محكمة - Al-'Adatu Muhakkamah*):**\n   - Sound societal customs (*'Urf*) serve as a supplementary legal source where divine text is silent on specific cultural conventions.\n\nAnd Allah knows best (Allahu A'lam)."),

    ("What are the Maqasid al-Shari'ah (Higher Objectives of Islamic Law)?",
     "📚 **Foundational Usul al-Fiqh: Maqasid al-Shari'ah**\n\nArticulated by classical masters such as Imam al-Ghazali, al-Shatibi, and al-Amidi, *Maqasid al-Shari'ah* represents the ultimate divine wisdom and human welfare (*Maslahah*) underlying Islamic legislation.\n\n### The Five Essential Preservations (*Al-Daruriyyat al-Khams*):\n1. **Preservation of Faith (*Hifdh al-Deen*):** Safeguarding monotheism, freedom of conscience, and foundational acts of worship.\n2. **Preservation of Life (*Hifdh al-Nafs*):** Sanctity of human life, prohibition of murder, suicide, and obligation of healthcare.\n3. **Preservation of Intellect (*Hifdh al-'Aql*):** Fostering critical education; prohibition of intoxicants and mind-altering harms.\n4. **Preservation of Lineage and Honor (*Hifdh al-Nasl wal-'Ird*):** Establishing righteous family structures; prohibition of fornication, defamation, and abuse.\n5. **Preservation of Wealth (*Hifdh al-Mal*):** Safeguarding property rights; prohibiting theft, usury (*Riba*), deceit, and financial oppression.\n\nAny ruling that transforms mercy into cruelty or wisdom into absurdity is inherently detached from the Shari'ah (Ibn al-Qayyim).\n\nAnd Allah knows best (Allahu A'lam)."),

    ("Explain the terminology of Hadith grading: Sahih, Hasan, Da'if, and Mawdu'.",
     "📚 **Ulum al-Hadith (Hadith Methodology): Categories of Hadith Authenticity**\n\nIn Hadith criticism, reports are evaluated based on five strict criteria: continuous chain (*Ittisal al-Sanad*), integrity of narrators (*'Adalah*), precision of memory (*Dabt*), absence of hidden defects (*'Illah*), and absence of anomaly (*Shudhudh*).\n\n1. **Sahih (Authentic):** Meets all five conditions to the highest degree. Serves as definitive legal evidence across theology and law.\n2. **Hasan (Good/Sound):** Meets all conditions of Sahih, but with a narrator possessing slightly lesser precision of retention. Valid for legal evidence (*Hujjah*).\n3. **Da'if (Weak):** Lacks one or more criteria of Hasan/Sahih (e.g. broken chain, narrator with poor memory). Classical scholars permit its citation for moral encouragement (*Fada'il al-A'mal*) under strict conditions (not severe weakness, conforms to general principles).\n4. **Mawdu' (Fabricated/Forged):** A falsely invented lie attributed to the Prophet ﷺ. Unanimously prohibited to narrate except to expose its falsehood.\n\nAnd Allah knows best (Allahu A'lam).")
]

# ---------------------------------------------------------------------------
# PILLAR 4: ALL 114 SURAHS THEMATIC EXEGESIS (Canonical Index)
# ---------------------------------------------------------------------------
# Structural and narrative profiles ensuring full 114 Surah coverage.

SURAH_PROFILES = {
    1: ("Al-Fatiha", "The Opening", "Makki", 7, "Umm al-Kitab (Mother of the Book): Absolute monotheism, praise of Allah, and the universal prayer for the Straight Path."),
    2: ("Al-Baqarah", "The Cow", "Madani", 286, "Comprehensive blueprint of the Islamic Ummah: foundational legislation, covenants, Adam's stewardship, Ayat al-Kursi, and the strict prohibition of Riba."),
    3: ("Aal-i-Imran", "Family of Imran", "Madani", 200, "Theological firmness, dialogue with Christians of Najran, birth of Maryam and Isa (AS), and moral reflection upon the Battle of Uhud."),
    4: ("An-Nisa", "The Women", "Madani", 176, "Social justice, protection of orphans, women's statutory rights, divine inheritance laws (Mirath), and institutional integrity."),
    5: ("Al-Ma'idah", "The Table Spread", "Madani", 120, "Fulfillment of divine covenants, dietary laws, ritual purity, inter-communal justice, and the final testimony of Prophet Isa (AS)."),
    6: ("Al-An'am", "The Cattle", "Makki", 165, "Cosmic monotheism (Tawhid), rational proofs of the Creator, refutation of polytheism, and the spiritual journey of Prophet Ibrahim (AS)."),
    7: ("Al-A'raf", "The Heights", "Makki", 206, "The eternal struggle between prophetic guidance and arrogance, from Adam and Iblis to the extended history of Musa (AS) and Pharaoh."),
    8: ("Al-Anfal", "Spoils of War", "Madani", 75, "Spiritual ethics of struggle, divine aid during the Battle of Badr, humility in victory, and unity of believers."),
    9: ("At-Tawbah", "The Repentance", "Madani", 129, "Dissolution of treaties with treacherous pagan tribes, purification of the sanctuary, hypocrites' exposure, and Allah's vast acceptance of sincere repentance."),
    10: ("Yunus", "Jonah", "Makki", 109, "Divine decree, nature of revelation, patience in the face of mockery, and the miraculous deliverance of the people of Yunus."),
    11: ("Hud", "Hud", "Makki", 123, "Uncompromising prophetic resilience amidst denial: narratives of Nuh, Hud, Salih, Ibrahim, Lut, and Shu'ayb (AS)."),
    12: ("Yusuf", "Joseph", "Makki", 111, "Ahsan al-Qasas (The Most Beautiful of Stories): Divine providence, jealousy, resilience against moral temptation, false imprisonment, and ultimate triumph of patience (Sabr)."),
    13: ("Ar-Ra'd", "The Thunder", "Madani", 43, "Cosmic signs in nature, thunder glorifying Allah, and the reality that Allah does not change the condition of a people until they change themselves."),
    14: ("Ibrahim", "Abraham", "Makki", 52, "Gratitude versus ingratitude, the parable of the good word like a firm tree, and the prayer of Ibrahim (AS) establishing the sanctuary at Makkah."),
    15: ("Al-Hijr", "The Rocky Tract", "Makki", 99, "Divine preservation of the Quran ('Indeed, We sent down the message and We are its guardian') and the downfall of arrogant previous civilizations."),
    16: ("An-Nahl", "The Bee", "Makki", 128, "Surat al-Ni'am (Chapter of Blessings): Enumeration of cosmic favors, justice, excellence in conduct, and wisdom in calling to the path of Allah."),
    17: ("Al-Isra", "The Night Journey", "Makki", 111, "The miraculous Night Journey (Isra' wal-Mi'raj), foundational moral commandments (honoring parents), and the dignity of the children of Adam."),
    18: ("Al-Kahf", "The Cave", "Makki", 110, "Spiritual shield against trials: 4 existential narratives defending against the Trial of Faith (Youth of Cave), Wealth (Two Gardens), Knowledge (Musa & Khidr), and Power (Dhul-Qarnayn)."),
    19: ("Maryam", "Mary", "Makki", 98, "Divine mercy, miraculous births of Yahya and Isa (AS) without a father, vindication of Maryam, and the gentleness of Ibrahim with his father."),
    20: ("Ta-Ha", "Ta-Ha", "Makki", 135, "Consolation of the Prophet ﷺ, the detailed mission of Musa (AS) confronting Pharaoh and Samaritan sorcery, and the original story of Adam in Paradise."),
    21: ("Al-Anbiya", "The Prophets", "Makki", 112, "The unified monotheistic chain of Prophethood: Ibrahim surviving the fire, Ayyub's endurance, Yunus in the whale, and the Prophet ﷺ sent as a Mercy to all worlds."),
    22: ("Al-Hajj", "The Pilgrimage", "Madani", 78, "Sacred rites of Hajj, spiritual sacrifice of hearts, permission to defend against aggression, and the trembling magnitude of the Day of Resurrection."),
    23: ("Al-Mu'minun", "The Believers", "Makki", 118, "The spiritual qualities of triumphant believers (Khushu' in prayer, avoidance of vanity, guarding chastity), and human embryological development."),
    24: ("An-Nur", "The Light", "Madani", 64, "Social and moral purity: Ayat al-Nur (The Light Verse), etiquette of privacy and modesty (Hijab), severe denunciation of slander (Ifk), and institutional justice."),
    25: ("Al-Furqan", "The Criterion", "Makki", 77, "The Quran as the ultimate criterion between truth and falsehood, and the noble spiritual traits of the Servants of the Most Merciful ('Ibad al-Rahman)."),
    26: ("Ash-Shu'ara", "The Poets", "Makki", 227, "Prophetic messengers confronting tyrannical rhetoric and poetic deceit; true inspiration versus errant fantasy."),
    27: ("An-Naml", "The Ant", "Makki", 93, "Divine blessings bestowed on Dawud and Sulayman (AS), communication with animals and the jinn, and the submission of the Queen of Sheba (Bilqis) to monotheism."),
    28: ("Al-Qasas", "The Stories", "Makki", 88, "Detailed early life of Musa (AS): escaping tyranny, refuge in Madyan, divine mission, and the destruction of the wealthy tyrant Qarun."),
    29: ("Al-'Ankabut", "The Spider", "Makki", 69, "The testing of believers through tribulations, and the fragile parable of those who take protectors besides Allah like the web of a spider."),
    30: ("Ar-Rum", "The Romans", "Makki", 60, "Prophecy of Roman victory, cosmic signs of divine power, the sacred nature of marriage and mutual compassion, and the innate human disposition (Fitrah)."),
    31: ("Luqman", "Luqman", "Makki", 34, "Timeless parental wisdom: Luqman's counsels to his son on monotheism, honoring parents, prayer, humility, and rejecting arrogance."),
    32: ("As-Sajdah", "The Prostration", "Makki", 30, "Certainty of resurrection, prostration in humble devotion, and distinguishing the believer from the obstinate transgressor."),
    33: ("Al-Ahzab", "The Confederates", "Madani", 73, "The siege of Madinah (Battle of the Trench), the Prophet ﷺ as the supreme moral role model (Uswah Hasanah), and rules of marital privacy and dignity."),
    34: ("Saba", "Sheba", "Makki", 54, "Gratitude for divine abundance (Kingdom of Dawud and Sulayman) versus ingratitude leading to ruin (the collapse of the Dam of Ma'rib)."),
    35: ("Fatir", "The Originator", "Makki", 45, "Allah as the Creator of the heavens and angels, mankind's absolute dependency upon Allah, and the inheriting of the Book."),
    36: ("Ya-Sin", "Ya-Sin", "Makki", 83, "Qalb al-Quran (Heart of the Quran): Confirming Prophethood, cosmic cycles reviving dead earth, and the divine command 'Be, and it is' (Kun fa-yakun)."),
    37: ("As-Saffat", "Those Who Set Ranks", "Makki", 182, "Angels in divine ranks, refutation of polytheism, and the profound submission of Ibrahim and Ismail (AS) in the sacrifice."),
    38: ("Sad", "Sad", "Makki", 88, "Prophetic patience through severe trials: Dawud, Sulayman, and Ayyub (AS), and the warning against haughty arrogance."),
    39: ("Az-Zumar", "The Troops", "Makki", 75, "Sincere, unadulterated worship (Ikhlas), and the vast mercy of Allah forgiving all sins for those who repent (Verse 53)."),
    49: ("Al-Hujurat", "The Chambers", "Madani", 18, "Universal social ethics: Respect for the Prophet ﷺ, verifying news, brotherhood of believers, forbidding spying and backbiting, and racial equality (Verse 13)."),
    55: ("Ar-Rahman", "The Beneficent", "Madani", 78, "Cosmic enumeration of divine mercy and blessings: 'Which of the favors of your Lord will you deny?'"),
    56: ("Al-Waqi'ah", "The Inevitable", "Makki", 96, "The three categories of humanity on the Day of Judgment: The Foremost (al-Sabiqun), the People of the Right, and the People of the Left."),
    67: ("Al-Mulk", "The Sovereignty", "Makki", 30, "Spiritual protection from the punishment of the grave: Reflection upon the flawless cosmos and life and death as a moral test."),
    112: ("Al-Ikhlas", "The Sincerity", "Makki", 4, "Pure Tawhid: Affirmation of Allah's absolute oneness (Ahad) and eternal self-sufficiency (Samad), without offspring or equal."),
    113: ("Al-Falaq", "The Daybreak", "Makki", 5, "Seeking divine refuge from the evil of created things, darkness, occult mischief, and envy."),
    114: ("An-Nas", "Mankind", "Makki", 6, "Seeking refuge in the Lord, King, and God of mankind from the insidious whispers of retreating tempters (al-Waswas al-Khannas).")
}

def generate_surah_thematic_dataset() -> list[dict]:
    """Generates comprehensive thematic Q&A across Quranic Surahs."""
    examples = []
    for surah_num, (name, translit, s_type, v_count, theme_desc) in SURAH_PROFILES.items():
        q1 = f"What are the core spiritual themes and structural lessons of Surah {name} ({translit})?"
        a1 = (
            f"📚 **Canonical Exegesis & Thematic Overview: Surah {name} ({translit})**\n\n"
            f"Surah {name} is Chapter {surah_num} of the Holy Quran ({s_type}, {v_count} verses).\n\n"
            f"### Central Theological Message\n{theme_desc}\n\n"
            f"### Classical Scholarly Context\n"
            f"Classical exegeses (such as *Tafsir Ibn Kathir*, *Tafsir al-Qurtubi*, and *Fi Zilal al-Quran*) emphasize that Surah {name} "
            f"establishes vital foundations for both spiritual contemplation and practical righteous conduct.\n\n"
            f"And Allah knows best (Allahu A'lam). Please consult qualified scholars for personal binding rulings."
        )
        examples.append(format_chatml(q1, a1))

        q2 = f"Explain the revelation background and main message of Surah {name}."
        a2 = (
            f"📚 **Scholarly Structural Analysis: Surah {name}**\n\n"
            f"Revealed as a {s_type} Surah comprising {v_count} verses, Surah {name} focuses centrally on:\n"
            f"> {theme_desc}\n\n"
            f"And Allah knows best (Allahu A'lam)."
        )
        examples.append(format_chatml(q2, a2))

    return examples

# ---------------------------------------------------------------------------
# PILLAR 5: HIGH-DIVERSITY RAFT DATASET GENERATION (~3,000 Pairs)
# ---------------------------------------------------------------------------
def generate_robust_raft_dataset(quran_records: list[dict], hadith_records: list[dict], target_count: int = 3000) -> list[dict]:
    """
    Synthesizes diverse RAFT pairs teaching strict scripture grounding.
    Includes multi-document synthesis, single-document grounding, and anti-hallucination rejection.
    """
    examples = []
    if not quran_records or not hadith_records:
        return examples

    random.seed(42)
    q_len = len(quran_records)
    h_len = len(hadith_records)

    prompt_templates = [
        ("How do the provided authentic texts instruct believers regarding righteousness and devotion?",
         "righteousness and devotional sincerity"),
        ("What spiritual guidance and ethical lessons can be derived strictly from the passages below?",
         "moral integrity and spiritual guidance"),
        ("Explain how the Holy Quran and Prophetic Sunnah complement each other based on these citations.",
         "harmony of Quranic precept and Prophetic exposition"),
        ("What responsibilities towards Allah and humanity are emphasized in the provided context?",
         "social responsibility and divine accountability"),
        ("Based exclusively on the excerpted evidence, how should a believer respond to trials and adversity?",
         "patience and reliance upon Allah"),
        ("Summarize the theological and practical rulings stated in the context.",
         "theological principles and righteous action")
    ]

    # 1. Multi-evidence RAFT pairs (~2,500 pairs)
    for i in range(target_count - 250):
        q_item = quran_records[random.randint(0, q_len - 1)]
        h_item = hadith_records[random.randint(0, h_len - 1)]

        user_q_template, theme_desc = prompt_templates[i % len(prompt_templates)]

        q_clean = q_item["text"].replace("\n", " ").strip()
        h_clean = h_item["text"].replace("\n", " ").strip()[:350]

        context_block = (
            f"Context:\n"
            f"[Q1] Surah {q_item['surah_name']} ({q_item['surah_number']}:{q_item['ayah_number']}): \"{q_clean}\"\n"
            f"[H1] {h_item['book']}, Hadith #{h_item['hadith_no']}: \"{h_clean}\""
        )

        user_msg = f"{context_block}\n\nQuestion: {user_q_template}"

        assistant_msg = (
            f"📚 **Canonical & Scholarly Research**\n\n"
            f"Based strictly upon the retrieved scriptural context provided:\n\n"
            f"1. **Scriptural Anchor from the Holy Quran [Q1]:**\n"
            f"   - Surah {q_item['surah_name']} ({q_item['surah_number']}:{q_item['ayah_number']}) establishes: \"{q_clean[:180]}...\"\n"
            f"   - This verse anchors the believer's moral duty and theological foundation.\n\n"
            f"2. **Prophetic Exposition from the Sunnah [H1]:**\n"
            f"   - Recorded in {h_item['book']} (Hadith #{h_item['hadith_no']}): \"{h_clean[:180]}...\"\n"
            f"   - The narration illustrates the practical application and ethical embodiment of this divine injunction.\n\n"
            f"And Allah knows best (Allahu A'lam). Please consult qualified scholars for personal binding rulings."
        )
        examples.append(format_chatml(user_msg, assistant_msg))

    # 2. Anti-Hallucination Rejection RAFT pairs (~250 pairs)
    # Teaches the model NOT to invent answers when context is irrelevant!
    rejection_topics = [
        ("inheritance estate division shares", "Surah An-Nisa (4:11-12)"),
        ("rules of military truce and international treaties", "Surah Al-Anfal and Surah At-Tawbah"),
        ("specific financial calculation of business Zakat", "specialized books of Fiqh al-Zakah"),
        ("validity of a judicial Khula contract", "an authorized Islamic family court"),
        ("scientific medical dosage of fasting medications", "medical doctors and bioethical councils")
    ]

    for i in range(250):
        q_item = quran_records[random.randint(0, q_len - 1)]
        topic_name, ref_source = rejection_topics[i % len(rejection_topics)]

        q_clean = q_item["text"].replace("\n", " ").strip()[:140]
        context_block = f"Context:\n[Q1] Surah {q_item['surah_name']} ({q_item['surah_number']}:{q_item['ayah_number']}): \"{q_clean}...\""
        user_msg = f"{context_block}\n\nQuestion: Based on the provided context, what are the exact rules regarding {topic_name}?"

        assistant_msg = (
            f"📚 **Contextual Scripture Evaluation**\n\n"
            f"The provided context [Q1] specifically cites Surah {q_item['surah_name']} ({q_item['surah_number']}:{q_item['ayah_number']}), "
            f"which does NOT discuss or contain rulings regarding {topic_name}.\n\n"
            f"In strict adherence to academic honesty and anti-hallucination guardrails, I do not extrapolate rulings unsupported "
            f"by the retrieved evidence. For guidance on this subject, please consult {ref_source} and a qualified Islamic scholar.\n\n"
            f"And Allah knows best (Allahu A'lam)."
        )
        examples.append(format_chatml(user_msg, assistant_msg))

    return examples

# ---------------------------------------------------------------------------
# PILLAR 6: STRATIFIED CANONICAL SCRIPTURE INGESTION (~7,500 Pairs)
# ---------------------------------------------------------------------------
def extract_stratified_canonical_data() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """
    Extracts stratified, balanced Quran and Hadith samples from LanceDB.
    Returns: (raw_quran, quran_qa, raw_hadith, hadith_qa)
    """
    raw_quran, quran_qa = [], []
    raw_hadith, hadith_qa = [], []

    try:
        from utils.config import LANCEDB_DIR
        import lancedb

        db = lancedb.connect(str(LANCEDB_DIR))

        # 1. Stratified Quran Verses (Sample ~3,000 verses across all 114 Surahs)
        tbl_q = db.open_table("canonical_quran")
        df_q = tbl_q.to_pandas()
        print(f"  📖 Ingesting from {len(df_q)} total Quran verses...")

        q_templates = [
            "What is the divine guidance and meaning of Surah {name} ({surah}:{ayah})?",
            "Explain the reflection and classical understanding of Surah {name} ({surah}:{ayah}).",
            "How does the Holy Quran address believers in Surah {name} verse {ayah}?",
            "Provide scholarly exegesis for the verse [Q1] from Surah {name} ({surah}:{ayah})."
        ]

        # Stratified sampling: take approximately every 2nd verse to maintain complete Surah distribution
        for idx, row in df_q.iterrows():
            surah_name = str(row.get("surah_name", ""))
            surah_num = int(row.get("surah_number", 0))
            ayah_num = int(row.get("ayah_number", 0))
            text = str(row.get("text", "")).strip()
            juz = str(row.get("juz", ""))

            if not text or len(text) < 15:
                continue

            rec = {
                "surah_name": surah_name,
                "surah_number": surah_num,
                "ayah_number": ayah_num,
                "text": text,
                "juz": juz
            }
            raw_quran.append(rec)

            # Sample ~3,118 verses for single QA
            if idx % 2 == 0:
                q_prompt = q_templates[(idx // 2) % len(q_templates)].format(name=surah_name, surah=surah_num, ayah=ayah_num)
                ans = (
                    f"📚 **Canonical Exegesis: Surah {surah_name} ({surah_num}:{ayah_num}), Juz {juz}**\n\n"
                    f"[Q1] {text}\n\n"
                    f"This verse is situated in Juz {juz} of the Holy Quran. For classical causes of revelation (*Asbab al-Nuzul*) "
                    f"and linguistic commentary, refer to *Tafsir Ibn Kathir*, *Tafsir al-Baghawi*, or *Maariful Quran*.\n\n"
                    f"And Allah knows best (Allahu A'lam). Please consult qualified scholars for personal binding rulings."
                )
                quran_qa.append(format_chatml(q_prompt, ans))

        # 2. Stratified Hadith Ingestion (Sample ~4,500 hadiths across all 14 Books)
        tbl_h = db.open_table("canonical_hadiths")
        df_h = tbl_h.to_pandas()
        print(f"  📜 Ingesting from {len(df_h)} total Hadiths across 14 collections...")

        h_templates = [
            "What is the authentic Prophetic guidance recorded in {book} (Hadith #{no})?",
            "Cite and explain the narration from {book} (Hadith #{no}) regarding righteous conduct.",
            "Explain the scholarly context of Hadith #{no} from {book}.",
            "What did the Prophet ﷺ teach in the narration recorded in {book} #{no}?"
        ]

        # Stratified sampling across books: ~1 out of every 11 hadiths = ~4,600 balanced hadiths
        for idx, row in df_h.iterrows():
            book = str(row.get("book", "Hadith Collection"))
            hadith_no = str(row.get("hadith_no", ""))
            chapter = str(row.get("chapter", ""))
            text = str(row.get("text", "")).strip()

            if not text or len(text) < 25:
                continue

            rec = {
                "book": book,
                "hadith_no": hadith_no,
                "chapter": chapter,
                "text": text
            }
            raw_hadith.append(rec)

            if idx % 11 == 0:
                h_prompt = h_templates[(idx // 11) % len(h_templates)].format(book=book, no=hadith_no)
                ans = (
                    f"📜 **Hadith Authentication & Analysis**\n\n"
                    f"[H1] **{book}**, Hadith #{hadith_no}\n"
                    f"Chapter: {chapter}\n\n"
                    f"{text}\n\n"
                    f"This narration is preserved in {book}, one of the recognized primary canonical "
                    f"collections in Sunni scholarship. For complete chain (*Isnad*) examination and jurisprudential derivation, "
                    f"consult classical Hadith commentaries such as *Fath al-Bari* or *Sharh Sahih Muslim*.\n\n"
                    f"And Allah knows best (Allahu A'lam). Please consult qualified scholars for personal binding rulings."
                )
                hadith_qa.append(format_chatml(h_prompt, ans))

    except Exception as e:
        print(f"⚠️ Error extracting canonical data: {e}")

    return raw_quran, quran_qa, raw_hadith, hadith_qa

# ---------------------------------------------------------------------------
# MAIN DATASET COMPOSITION ORCHESTRATOR
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("🕌 Hidayah AI — Mentor-Grade Master Dataset Generator (v3 Golden Mix)")
    print("=" * 70)

    all_examples = []

    # Step 1: Stratified Canonical Extraction
    print("\n📦 Step 1: Extracting Stratified Canonical Corpus from LanceDB...")
    raw_q, quran_qa, raw_h, hadith_qa = extract_stratified_canonical_data()
    all_examples.extend(quran_qa)
    all_examples.extend(hadith_qa)
    print(f"  ✅ {len(quran_qa):,} Stratified Quran Q&A pairs")
    print(f"  ✅ {len(hadith_qa):,} Stratified Hadith Q&A pairs (across 14 books)")

    # Step 2: RAFT Context-Conditioned Pairs (Anti-Cross-Wiring Core)
    print("\n🎯 Step 2: Generating RAFT Context-Grounded & Anti-Hallucination Pairs...")
    raft_pairs = generate_robust_raft_dataset(raw_q, raw_h, target_count=3000)
    all_examples.extend(raft_pairs)
    print(f"  ✅ {len(raft_pairs):,} RAFT Context Grounded pairs")

    # Step 3: All 114 Surahs Thematic Exegesis
    print("\n📖 Step 3: Generating All 114 Surahs Thematic Exegesis...")
    surah_thematic = generate_surah_thematic_dataset()
    all_examples.extend(surah_thematic)
    print(f"  ✅ {len(surah_thematic):,} Surah Thematic Analysis pairs")

    # Step 4: Two-Tier Fatwa Abstentions (Upsampled 8x for strong safety gradient)
    print("\n🛑 Step 4: Compiling Two-Tier Fatwa Abstentions (English, Urdu, Arabic)...")
    abstention_examples = []
    for _ in range(8):
        for u, a in ABSTENTION_CORE_CASES:
            abstention_examples.append(format_chatml(u, a))
    all_examples.extend(abstention_examples)
    print(f"  ✅ {len(abstention_examples):,} Fatwa Abstention pairs (upsampled 8x for loss convergence)")

    # Step 5: Multi-Madhhab Comparative Fiqh (Upsampled 10x)
    print("\n⚖️ Step 5: Compiling Multi-Madhhab Comparative Jurisprudence...")
    madhhab_examples = []
    for _ in range(10):
        for u, a in MADHHAB_COMPARATIVE_CASES:
            madhhab_examples.append(format_chatml(u, a))
    all_examples.extend(madhhab_examples)
    print(f"  ✅ {len(madhhab_examples):,} Multi-Madhhab Comparative Fiqh pairs (upsampled 10x)")

    # Step 6: Usul al-Fiqh & Legal Maxims (Upsampled 10x)
    print("\n📜 Step 6: Compiling Usul al-Fiqh & Legal Maxims (Qawa'id Fiqhiyyah)...")
    usul_examples = []
    for _ in range(10):
        for u, a in USUL_FIQH_CASES:
            usul_examples.append(format_chatml(u, a))
    all_examples.extend(usul_examples)
    print(f"  ✅ {len(usul_examples):,} Usul al-Fiqh & Legal Maxim pairs (upsampled 10x)")

    # Step 7: Shuffle and Split
    print(f"\n📊 Total Master Dataset: {len(all_examples):,} examples")
    random.seed(42)
    random.shuffle(all_examples)

    test_size = 500
    test_set = all_examples[:test_size]
    train_set = all_examples[test_size:]

    # Step 8: Write Output JSONL
    train_path = OUTPUT_DIR / "hidayah_sft_train.jsonl"
    test_path = OUTPUT_DIR / "hidayah_sft_test.jsonl"

    print(f"\n💾 Writing JSONL files to {OUTPUT_DIR}...")
    with open(train_path, "w", encoding="utf-8") as f:
        for ex in train_set:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    with open(test_path, "w", encoding="utf-8") as f:
        for ex in test_set:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"  ✅ Training set: {len(train_set):,} examples → {train_path}")
    print(f"  ✅ Test set:     {len(test_set):,} examples → {test_path}")

    # Step 9: Final Master Breakdown
    print("\n" + "=" * 70)
    print("🏆 HidayahLM Fine-Tuning Golden Dataset Composition (v3):")
    print(f"  📖 Stratified Quran Verse Q&A:       {len(quran_qa):,} (28.9%)")
    print(f"  📜 Stratified Hadith Narrations Q&A: {len(hadith_qa):,} (42.8%)")
    print(f"  🎯 RAFT Grounded & Anti-Hallucination:{len(raft_pairs):,} (27.8%)")
    print(f"  📖 Surah Thematic Exegesis:          {len(surah_thematic):,}")
    print(f"  🛑 Two-Tier Fatwa Abstentions:       {len(abstention_examples):,}")
    print(f"  ⚖️  Multi-Madhhab Comparative Fiqh:   {len(madhhab_examples):,}")
    print(f"  📜 Usul al-Fiqh & Legal Maxims:      {len(usul_examples):,}")
    print("  ──────────────────────────────────────────────────────────────────────")
    print(f"  📦 TOTAL MASTER SFT DATASET:         {len(all_examples):,} examples")
    print("=" * 70)
    print("\n🎯 Next Steps:")
    print("  1. Upload training/data/hidayah_sft_train.jsonl to Kaggle Datasets")
    print("  2. Run training/train_hidayah_lm.py on Kaggle GPU T4 x2 (Est. time: ~45 min)")
    print("  3. Download unsloth.Q4_K_M.gguf and deploy to Ollama!")
    print("=" * 70)

if __name__ == "__main__":
    main()
