"""
Hidayah AI — Builder for the 99 Names of Allah (Asma-ul-Husna) Canonical Dataset
Generates data/names_of_allah.json with full Tashkeel, transliteration, meanings,
theological categories, Quranic citations, and audio endpoints.
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT_DIR / "data" / "names_of_allah.json"

NAMES_RAW = [
    (1, "الرَّحْمَٰنُ", "Ar-Rahmaan", "The Entirely Merciful", "بہت رحم فرمانے والا", "ر-ح-م", "Mercy & Compassion", "رحمت اور شفقت",
     "The One who has vast and encompassing mercy for all of creation in this world.",
     "وہ ذات جس کی رحمت تمام کائنات اور ہر مخلوق کو گھیرے ہوئے ہے۔",
     [{"surah": 1, "ayah": 3, "text": "الرَّحْمَٰنِ الرَّحِيمِ", "translation": "The Entirely Merciful, the Especially Merciful"},
      {"surah": 55, "ayah": 1, "text": "الرَّحْمَٰنُ", "translation": "The Most Merciful"}]),
      
    (2, "الرَّحِيمُ", "Ar-Raheem", "The Especially Merciful", "نہایت مہربان", "ر-ح-م", "Mercy & Compassion", "رحمت اور شفقت",
     "The One who bestows particular and enduring mercy upon the believers.",
     "وہ ذات جو مومنین پر خصوصی اور دائمی فضل و کرم فرمانے والی ہے۔",
     [{"surah": 1, "ayah": 3, "text": "الرَّحْمَٰنِ الرَّحِيمِ", "translation": "The Entirely Merciful, the Especially Merciful"},
      {"surah": 2, "ayah": 143, "text": "إِنَّ اللَّهَ بِالنَّاسِ لَرَءُوفٌ رَّحِيمٌ", "translation": "Indeed, Allah is full of kindness and mercy to mankind."}]),

    (3, "المَلِكُ", "Al-Malik", "The Sovereign / The King", "حقیقی بادشاہ", "م-ل-ك", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Absolute Owner and Supreme Ruler over the heavens and the earth.",
     "تمام کائنات کا حقیقی اور مطلق مالک و حکمران۔",
     [{"surah": 59, "ayah": 23, "text": "هُوَ اللَّهُ الَّذِي لَا إِلَٰهَ إِلَّا هُوَ الْمَلِكُ", "translation": "He is Allah, other than whom there is no deity, the Sovereign."}]),

    (4, "القُدُّوسُ", "Al-Quddoos", "The Pure / The Most Sacred", "نہایت پاک", "ق-د-س", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One who is purely transcendent above all imperfections, deficiencies, or shortcomings.",
     "وہ ذات جو ہر عیب، نقص اور کمزوری سے بالکل پاک و منزہ ہے۔",
     [{"surah": 59, "ayah": 23, "text": "الْمَلِكُ الْقُدُّوسُ السَّلَامُ", "translation": "The Sovereign, the Pure, the Perfection."}]),

    (5, "السَّلَامُ", "As-Salaam", "The Source of Peace", "سلامتی دینے والا", "س-ل-م", "Protection & Peace", "حفاظت اور سلامتی",
     "The Flawless Source of peace, safety, and security for all existence.",
     "وہ ذات جو خود ہر آفت سے محفوظ اور دوسروں کو امن و سلامتی عطا کرنے والی ہے۔",
     [{"surah": 59, "ayah": 23, "text": "الْقُدُّوسُ السَّلَامُ الْمُؤْمِنُ", "translation": "The Pure, the Source of Peace, the Bestower of Faith."}]),

    (6, "المُؤْمِنُ", "Al-Mu'min", "The Bestower of Faith & Security", "امن و ایمان دینے والا", "أ-م-ن", "Protection & Peace", "حفاظت اور سلامتی",
     "The One who confirms the truth of His promises and grants peace and sanctuary to believers.",
     "وہ ذات جو دلوں کو ایمان کی روشنی بخشتی ہے اور خوف سے امن عطا فرماتی ہے۔",
     [{"surah": 59, "ayah": 23, "text": "السَّلَامُ الْمُؤْمِنُ الْمُهَيْمِنُ", "translation": "The Source of Peace, the Bestower of Faith, the Overseer."}]),

    (7, "المُهَيْمِنُ", "Al-Muhaymin", "The Guardian & Overseer", "نگہبان و محافظ", "ه-ي-م-ن", "Protection & Peace", "حفاظت اور سلامتی",
     "The Supreme Guardian who watches over, controls, and preserves all affairs.",
     "وہ ذات جو تمام مخلوقات کی نگران، شاہد اور ان کے احوال کی محافظ ہے۔",
     [{"surah": 59, "ayah": 23, "text": "الْمُؤْمِنُ الْمُهَيْمِنُ الْعَزِيزُ", "translation": "The Bestower of Faith, the Overseer, the Exalted in Might."}]),

    (8, "العَزِيزُ", "Al-Azeez", "The All-Mighty / Invincible", "سب پر غالب اور زبردست", "ع-ز-ز", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Omnipotent and Irresistible One who cannot be overcome by any force.",
     "وہ غالب اور صاحبِ عزت ذات جس پر کوئی غالب نہیں آ سکتا۔",
     [{"surah": 59, "ayah": 23, "text": "الْعَزِيزُ الْجَبَّارُ الْمُتَكَبِّرُ", "translation": "The Exalted in Might, the Compeller, the Superior."}]),

    (9, "الجَبَّارُ", "Al-Jabbaar", "The Compeller / Restorer", "سب پر زبردست اور بگڑے کام سنوارنے والا", "ج-ب-ر", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One who mends broken hearts, rights hardships, and enforces His divine will.",
     "وہ ذات جس کی مشیت ہر چیز پر نافذ ہے اور جو ٹوٹے ہوئے دلوں کو سنوارتی ہے۔",
     [{"surah": 59, "ayah": 23, "text": "الْجَبَّارُ الْمُتَكَبِّرُ", "translation": "The Compeller, the Superior."}]),

    (10, "المُتَكَبِّرُ", "Al-Mutakabbir", "The Supreme in Greatness", "بزرگی و بڑائی والا", "ك-ب-ر", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One who alone possesses absolute majesty, beyond all created conception.",
     "وہ ذات جس کے لیے ہی حقیقی عظمت اور کبریائی زیبا ہے۔",
     [{"surah": 59, "ayah": 23, "text": "الْمُتَكَبِّرُ سُبْحَانَ اللَّهِ عَمَّا يُشْرِكُونَ", "translation": "The Supreme. Exalted is Allah above whatever they associate with Him."}]),

    (11, "الخَالِقُ", "Al-Khaaliq", "The Creator", "پیدا فرمانے والا", "خ-ل-ق", "Creation & Sustenance", "تخلیق اور رزق",
     "The One who brings things into existence from nothingness according to precise design.",
     "وہ ذات جو کائنات اور اس کی ہر چیز کو عدم سے وجود میں لانے والی ہے۔",
     [{"surah": 59, "ayah": 24, "text": "هُوَ اللَّهُ الْخَالِقُ الْبَارِئُ الْمُصَوِّرُ", "translation": "He is Allah, the Creator, the Inventor, the Fashioner."}]),

    (12, "البَارِئُ", "Al-Baari'", "The Originator / Maker", "عدم سے وجود بخشنے والا", "ب-ر-أ", "Creation & Sustenance", "تخلیق اور رزق",
     "The One who initiates creation with distinct individuality and impeccable harmony.",
     "وہ ذات جو بغیر کسی نمونے کے مخلوق کو بالکل درست اور متناسب پیدا فرماتی ہے۔",
     [{"surah": 59, "ayah": 24, "text": "الْخَالِقُ الْبَارِئُ الْمُصَوِّرُ", "translation": "The Creator, the Inventor, the Fashioner."}]),

    (13, "المُصَوِّرُ", "Al-Musawwir", "The Bestower of Forms / Fashioner", "صورتیں بنانے والا", "ص-و-ر", "Creation & Sustenance", "تخلیق اور رزق",
     "The Divine Sculptor who shapes and distinguishes each entity with a unique form.",
     "وہ ذات جو ہر مخلوق کو اس کی مناسب اور مخصوص شکل و صورت عطا فرماتی ہے۔",
     [{"surah": 59, "ayah": 24, "text": "الْبَارِئُ الْمُصَوِّرُ لَهُ الْأَسْمَاءُ الْحُسْنَىٰ", "translation": "The Inventor, the Fashioner; to Him belong the best names."}]),

    (14, "الغَفَّارُ", "Al-Ghaffaar", "The Continual Forgiver", "بہت زیادہ بخشنے والا", "غ-ف-ر", "Forgiveness & Clemency", "مغفرت اور حلم",
     "The One who repeatedly shields and covers the sins and faults of His servants.",
     "وہ ذات جو بار بار توبہ کرنے والوں کے گناہوں کو معاف فرماتی اور پردہ ڈالتی ہے۔",
     [{"surah": 20, "ayah": 82, "text": "وَإِنِّي لَغَفَّارٌ لِّمَن تَابَ وَآمَنَ", "translation": "And indeed, I am the Perpetual Forgiver of whoever repents and believes."}]),

    (15, "القَهَّارُ", "Al-Qahhaar", "The All-Dominant / Subduer", "سب کو اپنے قابو میں رکھنے والا", "ق-ه-ر", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Irresistible Conqueror to whom all things submit in utter humility.",
     "وہ ذات جس کی قدرت کے آگے تمام کائنات مغلوب اور سرنگوں ہے۔",
     [{"surah": 12, "ayah": 39, "text": "أَأَرْبَابٌ مُّتَفَرِّقُونَ خَيْرٌ أَمِ اللَّهُ الْوَاحِدُ الْقَهَّارُ", "translation": "Are separate lords better or Allah, the One, the Prevailing?"}]),

    (16, "الوَهَّابُ", "Al-Wahhaab", "The Supreme Bestower", "بے غرض بخشش کرنے والا", "و-ه-ب", "Mercy & Compassion", "رحمت اور شفقت",
     "The One who gives bounties abundantly and endlessly without expecting anything in return.",
     "وہ ذات جو کسی غرض یا بدلے کے بغیر کثرت سے عطیات و انعامات بخشنے والی ہے۔",
     [{"surah": 3, "ayah": 8, "text": "إِنَّكَ أَنتَ الْوَهَّابُ", "translation": "Indeed, You are the Bestower."}]),

    (17, "الرَّزَّاقُ", "Ar-Razzaaq", "The Supreme Provider", "سب کو روزی دینے والا", "ر-ز-ق", "Creation & Sustenance", "تخلیق اور رزق",
     "The One who sustains and provides both physical and spiritual nourishment to all living beings.",
     "وہ ذات جو کائنات کے ہر جاندار کی روزی اور روحانی خوراک کی ضامن ہے۔",
     [{"surah": 51, "ayah": 58, "text": "إِنَّ اللَّهَ هُوَ الرَّزَّاقُ ذُو الْقُوَّةِ الْمَتِينُ", "translation": "Indeed, it is Allah who is the Continual Provider, the firm possessor of strength."}]),

    (18, "الفَتَّاحُ", "Al-Fattaah", "The Supreme Opener / Decider", "بند دروازے کھولنے والا اور فیصلہ کن", "ف-ت-ح", "Justice & Truth", "عدل اور حق",
     "The One who opens the doors of mercy, sustenance, and wisdom, and judges between His servants with truth.",
     "وہ ذات جو رحمت و نصرت کے تمام دروازے کھولتی اور حق و باطل کا کامل فیصلہ کرتی ہے۔",
     [{"surah": 34, "ayah": 26, "text": "قُلْ يَجْمَعُ بَيْنَنَا رَبُّنَا ثُمَّ يَفْتَحُ بَيْنَنَا بِالْحَقِّ وَهُوَ الْفَتَّاحُ الْعَلِيمُ", "translation": "Say, 'Our Lord will bring us together; then He will judge between us in truth. And He is the Knowing Judge.'"}]),

    (19, "العَلِيمُ", "Al-Aleem", "The All-Knowing", "سب کچھ جاننے والا", "ع-ل-م", "Wisdom & Knowledge", "حکمت اور علم",
     "The One whose infinite knowledge encompasses everything in the past, present, future, hidden, and manifest.",
     "وہ ذات جس کا علم غیب و شہود، ظاہر و باطن اور کائنات کی ہر حرکت پر محیط ہے۔",
     [{"surah": 2, "ayah": 29, "text": "وَهُوَ بِكُلِّ شَيْءٍ عَلِيمٌ", "translation": "And He is Knowing of all things."}]),

    (20, "القَابِضُ", "Al-Qaabid", "The Withholder / Restrainer", "تنگی کرنے والا اور سمیٹنے والا", "ق-ب-ض", "Wisdom & Knowledge", "حکمت اور علم",
     "The One who contracts sustenance, souls, or hearts according to profound wisdom and justice.",
     "وہ ذات جو حکمت کے تحت رزق اور ارواح کو روکنے اور سمیٹنے والی ہے۔",
     [{"surah": 2, "ayah": 245, "text": "وَاللَّهُ يَقْبِضُ وَيَبْسُطُ وَإِلَيْهِ تُرْجَعُونَ", "translation": "And it is Allah who withholds and grants in abundance, and to Him you will be returned."}]),

    (21, "البَاسِطُ", "Al-Baasit", "The Expander / Extender", "فراخی اور کشادگی بخشنے والا", "ب-س-ط", "Mercy & Compassion", "رحمت اور شفقت",
     "The One who expands sustenance, joy, and mercy to whomsoever He wills.",
     "وہ ذات جو اپنے فضل و کرم سے دلوں اور روزی میں وسعت و کشادگی پیدا کرتی ہے۔",
     [{"surah": 2, "ayah": 245, "text": "وَاللَّهُ يَقْبِضُ وَيَبْسُطُ", "translation": "And it is Allah who withholds and grants in abundance."}]),

    (22, "الخَافِضُ", "Al-Khaafid", "The Abaser / Humbler", "پست کرنے والا", "خ-ف-ض", "Justice & Truth", "عدل اور حق",
     "The One who lowers the arrogant, the unjust, and the transgressors.",
     "وہ ذات جو سرکشوں اور ظالموں کو ان کے غرور کی سزا کے طور پر ذلیل و پست فرماتی ہے۔",
     [{"surah": 56, "ayah": 3, "text": "خَافِضَةٌ رَّافِعَةٌ", "translation": "Bringing down [some] and elevating [others]."}]),

    (23, "الرَّافِعُ", "Ar-Raafi'", "The Exalter / Elevator", "بلندی اور عزت عطا کرنے والا", "ر-ف-ع", "Justice & Truth", "عدل اور حق",
     "The One who elevates the humble believers in rank, honour, and closeness in this world and the Hereafter.",
     "وہ ذات جو اہل ایمان اور متقین کو عزت و شرف کے اعلیٰ درجات پر فائز کرتی ہے۔",
     [{"surah": 58, "ayah": 11, "text": "يَرْفَعِ اللَّهُ الَّذِينَ آمَنُوا مِنكُمْ وَالَّذِينَ أُوتُوا الْعِلْمَ دَرَجَاتٍ", "translation": "Allah will raise those who have believed among you and those who were given knowledge, by degrees."}]),

    (24, "المُعِزُّ", "Al-Mu'izz", "The Bestower of Honour", "عزت دینے والا", "ع-ز-ز", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Giver of true esteem, nobility, and dominion to whom He pleases.",
     "وہ ذات جو جسے چاہے حقیقی وقار، سر بلندی اور عزت عطا فرماتی ہے۔",
     [{"surah": 3, "ayah": 26, "text": "تُعِزُّ مَن تَشَاءُ وَتُذِلُّ مَن تَشَاءُ", "translation": "You honor whom You will and You humble whom You will."}]),

    (25, "المُذِلُّ", "Al-Mudhill", "The Humbler of the Arrogant", "ذلت دینے والا", "ذ-ل-ل", "Justice & Truth", "عدل اور حق",
     "The One who deprives the proud and obstinate of His divine guidance, leaving them disgraced.",
     "وہ ذات جو حق کے دشمنوں اور تکبر کرنے والوں کو ذلت و رسوائی کا شکار فرماتی ہے۔",
     [{"surah": 3, "ayah": 26, "text": "تُعِزُّ مَن تَشَاءُ وَتُذِلُّ مَن تَشَاءُ بِيَدِكَ الْخَيْرُ", "translation": "You honor whom You will and You humble whom You will. In Your hand is all good."}]),

    (26, "السَّمِيعُ", "As-Samee'", "The All-Hearing", "سب کچھ سننے والا", "س-م-ع", "Wisdom & Knowledge", "حکمت اور علم",
     "The One who hears every sound, whisper, thought, and prayer throughout the universe.",
     "وہ ذات جو ہر سرگوشی، دعا اور پوشیدہ آواز کو یکساں طور پر سننے والی ہے۔",
     [{"surah": 2, "ayah": 127, "text": "إِنَّكَ أَنتَ السَّمِيعُ الْعَلِيمُ", "translation": "Indeed You are the Hearing, the Knowing."}]),

    (27, "البَصِيرُ", "Al-Baseer", "The All-Seeing", "سب کچھ دیکھنے والا", "ب-ص-ر", "Wisdom & Knowledge", "حکمت اور علم",
     "The One who perceives every hidden speck, action, and occurrence in darkness and light.",
     "وہ ذات جس کی نظر سے رات کے اندھیرے اور زمین کی تہوں میں چھپی کوئی چیز پوشیدہ نہیں۔",
     [{"surah": 42, "ayah": 11, "text": "لَيْسَ كَمِثْلِهِ شَيْءٌ وَهُوَ السَّمِيعُ الْبَصِيرُ", "translation": "There is nothing like unto Him, and He is the Hearing, the Seeing."}]),

    (28, "الحَكَمُ", "Al-Hakam", "The Supreme Arbitrator / Judge", "فیصلہ فرمانے والا حاکم", "ح-ك-م", "Justice & Truth", "عدل اور حق",
     "The Infallible Judge whose decrees cannot be challenged or overturned.",
     "وہ عادل حاکم جس کا فیصلہ قطعی اور ناگزیر ہوتا ہے اور جس پر کوئی ظلم نہیں ہوتا۔",
     [{"surah": 6, "ayah": 114, "text": "أَفَغَيْرَ اللَّهِ أَبْتَغِي حَكَمًا", "translation": "[Say], 'Then is it other than Allah I should seek as judge?'"}]),

    (29, "العَدْلُ", "Al-Adl", "The Absolutely Just", "سراپا عدل و انصاف", "ع-د-ل", "Justice & Truth", "عدل اور حق",
     "The One who is entirely righteous, free from tyranny, injustice, or inequity.",
     "وہ ذات جس کے ہر کام اور حکم میں کامل عدل اور برابری کارفرما ہے۔",
     [{"surah": 6, "ayah": 115, "text": "وَتَمَّتْ كَلِمَتُ رَبِّكَ صِدْقًا وَعَدْلًا", "translation": "And the word of your Lord has been fulfilled in truth and in justice."}]),

    (30, "اللَّطِيفُ", "Al-Lateef", "The Subtle, Kind & Gracious", "باریک بین اور لطف و کرم والا", "ل-ط-ف", "Mercy & Compassion", "رحمت اور شفقت",
     "The One who comprehends the subtlest mysteries and acts with profound, unseen gentleness.",
     "وہ ذات جو باریک ترین امور سے باخبر ہے اور نہایت لطیف انداز سے مہربانیاں فرماتی ہے۔",
     [{"surah": 6, "ayah": 103, "text": "لَّا تُدْرِكُهُ الْأَبْصَارُ وَهُوَ يُدْرِكُ الْأَبْصَارَ وَهُوَ اللَّطِيفُ الْخَبِيرُ", "translation": "Vision perceives Him not, but He perceives [all] vision; and He is the Subtle, the Acquainted."}]),

    (31, "الخَبِيرُ", "Al-Khabeer", "The All-Aware", "ہر بات سے باخبر", "خ-ب-ر", "Wisdom & Knowledge", "حکمت اور علم",
     "The One who knows the innermost realities and hidden dimensions of all things.",
     "وہ ذات جو ہر شے کے باطنی احوال اور اندرونی حقیقتوں سے مکمل باخبر ہے۔",
     [{"surah": 67, "ayah": 14, "text": "أَلَا يَعْلَمُ مَنْ خَلَقَ وَهُوَ اللَّطِيفُ الْخَبِيرُ", "translation": "Does He who created not know, while He is the Subtle, the Acquainted?"}]),

    (32, "الحَلِيمُ", "Al-Haleem", "The Most Forbearing", "بردبار اور نرم خو", "ح-ل-م", "Forgiveness & Clemency", "مغفرت اور حلم",
     "The One who does not rush to punish, giving His servants time to repent and return to Him.",
     "وہ ذات جو نافرمانی کے باوجود فوری عذاب نہیں دیتی بلکہ مہلت عطا فرماتی ہے۔",
     [{"surah": 2, "ayah": 225, "text": "وَاللَّهُ غَفُورٌ حَلِيمٌ", "translation": "And Allah is Forgiving and Forbearing."}]),

    (33, "العَظِيمُ", "Al-Azeem", "The Magnificent / Supreme", "بے پناہ عظمت والا", "ع-ظ-م", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One whose infinite greatness and majesty surpass all human comprehension.",
     "وہ ذات جس کی عظمت اور شان تمام عقلوں اور پیمانوں سے بالا تر ہے۔",
     [{"surah": 2, "ayah": 255, "text": "وَهُوَ الْعَلِيُّ الْعَظِيمُ", "translation": "And He is the Most High, the Most Great."}]),

    (34, "الغَفُورُ", "Al-Ghafoor", "The All-Forgiving", "بہت زیادہ معاف فرمانے والا", "غ-ف-ر", "Forgiveness & Clemency", "مغفرت اور حلم",
     "The One who completely forgives, wipes away, and shields sins through His boundless grace.",
     "وہ ذات جو گناہوں کو معاف فرما کر اپنے بندوں پر عفو و رحمت کی چادر ڈال دیتی ہے۔",
     [{"surah": 39, "ayah": 53, "text": "إِنَّ اللَّهَ يَغْفِرُ الذُّنُوبَ جَمِيعًا إِنَّهُ هُوَ الْغَفُورُ الرَّحِيمُ", "translation": "Indeed, Allah forgives all sins. Indeed, it is He who is the Forgiving, the Merciful."}]),

    (35, "الشَّكُورُ", "Ash-Shakoor", "The Appreciative / Rewarder", "قدردان اور بدلہ دینے والا", "ش-ك-ر", "Mercy & Compassion", "رحمت اور شفقت",
     "The One who abundantly rewards even the smallest sincere deeds of His servants.",
     "وہ ذات جو بندوں کے معمولی نیک اعمال کی بھی قدر فرماتی اور بے حساب اجر دیتی ہے۔",
     [{"surah": 35, "ayah": 30, "text": "إِنَّهُ غَفُورٌ شَكُورٌ", "translation": "Indeed, He is Forgiving and Appreciative."}]),

    (36, "العَلِيُّ", "Al-Aliyy", "The Most High / Sublimely Exalted", "سب سے بلند و بالا", "ع-ل-و", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One who is elevated above all creation in His Essence, Attributes, and Dominance.",
     "وہ ذات جو اپنی ذات، صفات اور اقتدار میں ہر چیز سے بلند تر ہے۔",
     [{"surah": 2, "ayah": 255, "text": "وَهُوَ الْعَلِيُّ الْعَظِيمُ", "translation": "And He is the Most High, the Most Great."}]),

    (37, "الكَبِيرُ", "Al-Kabeer", "The Most Great", "نہایت بڑا اور بزرگ", "ك-ب-ر", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Incomparably Grand One before Whom everything else is small and fleeting.",
     "وہ ذات جس کی بڑائی اور کبریائی کے سامنے کائنات کا ہر وجود ہیچ ہے۔",
     [{"surah": 22, "ayah": 62, "text": "وَأَنَّ اللَّهَ هُوَ الْعَلِيُّ الْكَبِيرُ", "translation": "And that Allah is the Most High, the Grand."}]),

    (38, "الحَفِيظُ", "Al-Hafeez", "The Preserver & Protector", "سب کی حفاظت فرمانے والا", "ح-ف-ظ", "Protection & Peace", "حفاظت اور سلامتی",
     "The One who safeguards the heavens, the earth, and the deeds of every soul from loss.",
     "وہ ذات جو تمام کائنات کو فنا سے بچانے اور اعمال کی حفاظت کرنے والی ہے۔",
     [{"surah": 11, "ayah": 57, "text": "إِنَّ رَبِّي عَلَىٰ كُلِّ شَيْءٍ حَفِيظٌ", "translation": "Indeed, my Lord is, over all things, Guardian."}]),

    (39, "المُقِيتُ", "Al-Muqeet", "The Sustainer & Nourisher", "سب کو قوت و خوراک دینے والا", "ق-و-ت", "Creation & Sustenance", "تخلیق اور رزق",
     "The One who creates nourishment, portions it out, and sustains life through His power.",
     "وہ ذات جو جسم اور روح دونوں کو مناسب قوت اور خوراک بہم پہنچاتی ہے۔",
     [{"surah": 4, "ayah": 85, "text": "وَكَانَ اللَّهُ عَلَىٰ كُلِّ شَيْءٍ مُّقِيتًا", "translation": "And ever is Allah, over all things, a Keeper."}]),

    (40, "الحَسِيبُ", "Al-Haseeb", "The Reckoner & Sufficient One", "کافی ہونے والا اور حساب لینے والا", "ح-س-ب", "Justice & Truth", "عدل اور حق",
     "The One who is sufficient for those who rely upon Him and will reckon all deeds on Judgment Day.",
     "وہ ذات جو بھروسہ کرنے والوں کے لیے کافی ہے اور تمام اعمال کا حساب لینے والی ہے۔",
     [{"surah": 4, "ayah": 6, "text": "وَكَفَىٰ بِاللَّهِ حَسِيبًا", "translation": "And sufficient is Allah as an Accountant."}]),

    (41, "الجَلِيلُ", "Al-Jaleel", "The Majestic & Sublime", "صاحبِ جلال و بزرگی", "ج-ل-ل", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One possessor of glory, transcendent dignity, and awe-inspiring perfection.",
     "وہ ذات جو عظمت، شکوہ اور جلال کی تمام صفات کی حامل ہے۔",
     [{"surah": 55, "ayah": 27, "text": "وَيَبْقَىٰ وَجْهُ رَبِّكَ ذُو الْجَلَالِ وَالْإِكْرَامِ", "translation": "And there will remain the Face of your Lord, Owner of Majesty and Honor."}]),

    (42, "الكَرِيمُ", "Al-Kareem", "The Most Generous & Bountiful", "نہایت سخی اور کرم فرمانے والا", "ك-ر-م", "Mercy & Compassion", "رحمت اور شفقت",
     "The Noble Giver who grants without measure, forgives with kindness, and fulfills promises.",
     "وہ ذات جو بن مانگے عطا فرماتی اور تقاضے کے بغیر فضل و احسان سے نوازتی ہے۔",
     [{"surah": 82, "ayah": 6, "text": "يَا أَيُّهَا الْإِنسَانُ مَا غَرَّكَ بِرَبِّكَ الْكَرِيمِ", "translation": "O mankind, what has deceived you concerning your Lord, the Generous."}]),

    (43, "الرَّقِيبُ", "Ar-Raqeeb", "The Watchful Observer", "ہمہ وقت نگران", "ر-ق-ب", "Protection & Peace", "حفاظت اور سلامتی",
     "The Ever-Vigilant One from Whom not a single whisper, gaze, or thought is hidden.",
     "وہ ذات جو ہر لمحہ اور ہر آن اپنے بندوں کے افعال و خیالات کی نگہبان ہے۔",
     [{"surah": 4, "ayah": 1, "text": "إِنَّ اللَّهَ كَانَ عَلَيْكُمْ رَقِيبًا", "translation": "Indeed Allah is ever, over you, an Observer."}]),

    (44, "المُجِيبُ", "Al-Mujeeb", "The Responsive / Answerer of Prayers", "دعائیں قبول فرمانے والا", "ج-و-ب", "Mercy & Compassion", "رحمت اور شفقت",
     "The One who answers the heartfelt supplications of those who call upon Him with humility.",
     "وہ ذات جو پکارنے والوں کی دعائیں سنتی اور حاجت مندوں کی فریاد رسی فرماتی ہے۔",
     [{"surah": 11, "ayah": 61, "text": "إِنَّ رَبِّي قَرِيبٌ مُّجِيبٌ", "translation": "Indeed, my Lord is near and responsive."}]),

    (45, "الوَاسِعُ", "Al-Waasi'", "The All-Encompassing / Boundless", "بے پناہ وسعت والا", "و-س-ع", "Wisdom & Knowledge", "حکمت اور علم",
     "The One whose capacity, mercy, knowledge, and sovereignty encompass all of existence.",
     "وہ ذات جس کی رحمت، مغفرت اور کائنات پر گرفت لامحدود اور بے پایاں ہے۔",
     [{"surah": 2, "ayah": 268, "text": "وَاللَّهُ وَاسِعٌ عَلِيمٌ", "translation": "And Allah is all-Encompassing and Knowing."}]),

    (46, "الحَكِيمُ", "Al-Hakeem", "The All-Wise", "کامل حکمت والا", "ح-ك-م", "Wisdom & Knowledge", "حکمت اور علم",
     "The One whose every decree, creation, and guidance is rooted in absolute, unerring wisdom.",
     "وہ ذات جس کا ہر فعل، ہر قانون اور ہر تدبیر کامل مصلحت اور دانائی پر مبنی ہے۔",
     [{"surah": 2, "ayah": 129, "text": "إِنَّكَ أَنتَ الْعَزِيزُ الْحَكِيمُ", "translation": "Indeed, You are the Exalted in Might, the Wise."}]),

    (47, "الوَدُودُ", "Al-Wadood", "The Loving / Affectionate", "محبت فرمانے والا", "و-د-د", "Mercy & Compassion", "رحمت اور شفقت",
     "The One who genuinely loves His righteous servants and is loved by their hearts.",
     "وہ ذات جو اپنے مخلص بندوں سے بے پایاں محبت رکھتی اور ان کے دلوں کو انس بخشتی ہے۔",
     [{"surah": 85, "ayah": 14, "text": "وَهُوَ الْغَفُورُ الْوَدُودُ", "translation": "And He is the Forgiving, the Affectionate."}]),

    (48, "المَجِيدُ", "Al-Majeed", "The Glorious / Most Venerable", "بزرگی اور عزت کا مالک", "م-ج-د", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One characterized by complete nobility, magnificent honor, and infinite greatness.",
     "وہ ذات جو بلند مرتبہ، بے مثال شرف اور کامل فضیلت کی مالک ہے۔",
     [{"surah": 11, "ayah": 73, "text": "إِنَّهُ حَمِيدٌ مَّجِيدٌ", "translation": "Indeed, He is Praiseworthy and Honorable."}]),

    (49, "البَاعِثُ", "Al-Baa'ith", "The Resurrector of the Dead", "مردوں کو زندہ فرمانے والا", "ب-ع-ث", "Justice & Truth", "عدل اور حق",
     "The One who will raise all souls from graves on the Day of Resurrection for judgment.",
     "وہ ذات جو قیامت کے دن تمام مخلوق کو دوبارہ زندہ کر کے میدانِ حشر میں لائے گی۔",
     [{"surah": 22, "ayah": 7, "text": "وَأَنَّ اللَّهَ يَبْعَثُ مَن فِي الْقُبُورِ", "translation": "And that Allah will resurrect those in the graves."}]),

    (50, "الشَّهِيدُ", "Ash-Shaheed", "The Universal Witness", "ہر جگہ حاضر و ناظر شاہد", "ش-ه-د", "Justice & Truth", "عدل اور حق",
     "The One to Whom nothing is unseen, witnessing all thoughts and deeds in every realm.",
     "وہ ذات جو ہر ظاہر و باطن، ہر واقعے اور ہر راز کی چشم دید گواہ ہے۔",
     [{"surah": 4, "ayah": 33, "text": "إِنَّ اللَّهَ كَانَ عَلَىٰ كُلِّ شَيْءٍ شَهِيدًا", "translation": "Indeed, Allah is ever, over all things, a Witness."}]),

    (51, "الحَقُّ", "Al-Haqq", "The Absolute Truth", "حقیقی اور برحق", "ح-ق-ق", "Justice & Truth", "عدل اور حق",
     "The Ever-Existing Reality whose being and word are unequivocally true and eternal.",
     "وہ ذات جس کا وجود سچّا، جس کا کلام برحق اور جس کے تمام وعدے یقینی ہیں۔",
     [{"surah": 22, "ayah": 6, "text": "ذَٰلِكَ بِأَنَّ اللَّهَ هُوَ الْحَقُّ", "translation": "That is because Allah is the Truth."}]),

    (52, "الوَكِيلُ", "Al-Wakeel", "The Supreme Trustee & Guardian", "سب سے بہترین کارساز", "و-ك-ل", "Protection & Peace", "حفاظت اور سلامتی",
     "The Dependable Guardian who manages all affairs flawlessly for those who trust in Him.",
     "وہ ذات جو اپنے بندوں کے معاملات کو سنوارنے والی اور سب سے قابلِ اعتماد وکیل ہے۔",
     [{"surah": 3, "ayah": 173, "text": "حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ", "translation": "Sufficient for us is Allah, and [He is] the best Disposer of affairs."}]),

    (53, "القَوِيُّ", "Al-Qawiyy", "The All-Strong", "کامل طاقت والا", "ق-و-ي", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One possessing limitless and inexhaustible strength that never tires or falters.",
     "وہ ذات جس کی قدرت و قوت بے انتہا ہے اور جسے کبھی زوال یا تھکن نہیں۔",
     [{"surah": 22, "ayah": 40, "text": "إِنَّ اللَّهَ لَقَوِيٌّ عَزِيزٌ", "translation": "Indeed, Allah is Powerful and Exalted in Might."}]),

    (54, "المَتِينُ", "Al-Mateen", "The Firm / Steadfast", "نہایت مضبوط اور مستحکم", "م-ت-ن", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Unshakeable in His might, incapable of weakness or fatigue.",
     "وہ ذات جس کی قوت میں کمال استحکام ہے اور جسے کوئی طاقت متزلزل نہیں کر سکتی۔",
     [{"surah": 51, "ayah": 58, "text": "إِنَّ اللَّهَ هُوَ الرَّزَّاقُ ذُو الْقُوَّةِ الْمَتِينُ", "translation": "Indeed, it is Allah who is the Continual Provider, the firm possessor of strength."}]),

    (55, "الوَلِيُّ", "Al-Waliyy", "The Protecting Friend / Ally", "مددگار اور ولی", "و-ل-ي", "Protection & Peace", "حفاظت اور سلامتی",
     "The Loving Protector who supports, guides, and cherishes the righteous.",
     "وہ ذات جو اہل ایمان کی حامی، مددگار اور ان کی سرپرستی فرمانے والی ہے۔",
     [{"surah": 42, "ayah": 28, "text": "وَهُوَ الْوَلِيُّ الْحَمِيدُ", "translation": "And He is the Protector, the Praiseworthy."}]),

    (56, "الحَمِيدُ", "Al-Hameed", "The All-Praiseworthy", "ہر تعریف کے لائق", "ح-م-د", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One who deserves all gratitude, adoration, and praise in every state and circumstance.",
     "وہ ذات جو اپنی ذات اور صفات کے اعتبار سے بذاتِ خود لائقِ حمد و ثناء ہے۔",
     [{"surah": 14, "ayah": 8, "text": "فَإِنَّ اللَّهَ لَغَنِيٌّ حَمِيدٌ", "translation": "Indeed Allah is Free of need and Praiseworthy."}]),

    (57, "المُحْصِي", "Al-Muhsee", "The Reckoner of All Things", "ہر چیز کو شمار میں رکھنے والا", "ح-ص-ي", "Wisdom & Knowledge", "حکمت اور علم",
     "The One who precisely counts, tracks, and records every particle and action without omission.",
     "وہ ذات جس کے احاطہ شمار میں کائنات کے تمام ذرات اور بندوں کے اعمال محفوظ ہیں۔",
     [{"surah": 72, "ayah": 28, "text": "وَأَحْصَىٰ كُلَّ شَيْءٍ عَدَدًا", "translation": "And has enumerated all things in number."}]),

    (58, "المُبْدِئُ", "Al-Mubdi'", "The Originator", "پہلی بار پیدا کرنے والا", "ب-د-أ", "Creation & Sustenance", "تخلیق اور رزق",
     "The One who initiates all creation for the first time without prior model.",
     "وہ ذات جو بغیر کسی سابقہ مادے یا نمونے کے کائنات کو عدم سے پہلی بار پیدا فرماتی ہے۔",
     [{"surah": 85, "ayah": 13, "text": "إِنَّهُ هُوَ يُبْدِئُ وَيُعِيدُ", "translation": "Indeed, it is He who originates [creation] and repeats."}]),

    (59, "المُعِيدُ", "Al-Mu'eed", "The Restorer / Re-creator", "دوبارہ پیدا فرمانے والا", "ع-و-د", "Creation & Sustenance", "تخلیق اور رزق",
     "The One who reproduces and restores creation back to life after its demise.",
     "وہ ذات جو موت اور فنا کے بعد مخلوق کو دوبارہ نئی زندگی بخشے گی۔",
     [{"surah": 85, "ayah": 13, "text": "إِنَّهُ هُوَ يُبْدِئُ وَيُعِيدُ", "translation": "Indeed, it is He who originates [creation] and repeats."}]),

    (60, "المُحْيِي", "Al-Muhyee", "The Giver of Life", "زندگی بخشنے والا", "ح-ي-ي", "Creation & Sustenance", "تخلیق اور رزق",
     "The One who breathes vitality into inanimate matter and revives dead hearts.",
     "وہ ذات جو بے جان مادے میں روح پھونکتی اور مردہ دلوں کو زندہ فرماتی ہے۔",
     [{"surah": 30, "ayah": 50, "text": "إِنَّ ذَٰلِكَ لَمُحْيِي الْمَوْتَىٰ", "translation": "Indeed, that [same one] will give life to the dead."}]),

    (61, "المُمِيتُ", "Al-Mumeet", "The Bringer of Death", "موت دینے والا", "م-و-ت", "Justice & Truth", "عدل اور حق",
     "The One who decrees the departure of souls from this world at their appointed hour.",
     "وہ ذات جو مقررہ وقت پر روح کو قبض کر کے موت کا ذائقہ چکھاتی ہے۔",
     [{"surah": 40, "ayah": 68, "text": "هُوَ الَّذِي يُحْيِي وَيُمِيتُ", "translation": "He it is who gives life and causes death."}]),

    (62, "الحَيُّ", "Al-Hayy", "The Ever-Living", "ہمیشہ زندہ رہنے والا", "ح-ي-ي", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Eternally Living One whose life has neither beginning nor end, unblemished by sleep.",
     "وہ ذات جو ازل سے ابد تک زندہ ہے اور جسے کبھی اونگھ یا موت نہیں آ سکتی۔",
     [{"surah": 2, "ayah": 255, "text": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ", "translation": "Allah - there is no deity except Him, the Ever-Living, the Sustainer of existence."}]),

    (63, "القَيُّومُ", "Al-Qayyoom", "The Self-Sustaining Sustainer", "خود قائم اور سب کو قائم رکھنے والا", "ق-و-م", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Self-Sufficient One who upholds and sustains the entire universe by His will.",
     "وہ ذات جو اپنی ذات سے خود قائم ہے اور تمام آسمانوں و زمینوں کو تھامے ہوئے ہے۔",
     [{"surah": 20, "ayah": 111, "text": "وَعَنَتِ الْوُجُوهُ لِلْحَيِّ الْقَيُّومِ", "translation": "And [all] faces will be humbled before the Ever-Living, the Sustainer of existence."}]),

    (64, "الوَاجِدُ", "Al-Waajid", "The Finder / All-Perceiving", "سب کچھ پانے والا اور بے نیاز", "و-ج-د", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One who lacks nothing, for Whom every desire and command is instantly fulfilled.",
     "وہ ذات جس سے کوئی چیز گم نہیں اور جو ہر وقت ہر نعمت کی مالک ہے۔",
     [{"surah": 93, "ayah": 7, "text": "وَوَجَدَكَ ضَالًّا فَهَدَىٰ", "translation": "And He found you lost and guided [you]."}]),

    (65, "المَاجِدُ", "Al-Maajid", "The Illustrious / Noble", "بزرگی اور فضل والا", "م-ج-د", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Glorious One whose generosity, beneficence, and high honor know no boundaries.",
     "وہ ذات جو شرف و بزرگی اور کثرتِ فضل و کرم میں بے مثال ہے۔",
     [{"surah": 85, "ayah": 15, "text": "ذُو الْعَرْشِ الْمَجِيدُ", "translation": "Honorable Owner of the Throne."}]),

    (66, "الوَاحِدُ", "Al-Waahid", "The Unique / The Indivisible", "ایک اور یکتا", "و-ح-د", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One who is singular in His essence, having no partner, peer, or equal.",
     "وہ ذات جو اپنی ذات، صفات اور حقوق میں اکیلی اور یکتا ہے۔",
     [{"surah": 2, "ayah": 163, "text": "وَإِلَٰهُكُمْ إِلَٰهٌ وَاحِدٌ", "translation": "And your god is one God."}]),

    (67, "الأَحَدُ", "Al-Ahad", "The Absolute One", "یگانہ اور بے مثل", "أ-ح-د", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Incomparably Sole Being who has never begotten, nor was begotten.",
     "وہ ذات جو اپنی بے مثل وحدانیت میں یکتا ہے اور جس کا کوئی شریک نہیں۔",
     [{"surah": 112, "ayah": 1, "text": "قُلْ هُوَ اللَّهُ أَحَدٌ", "translation": "Say, 'He is Allah, [who is] One.'"}]),

    (68, "الصَّمَدُ", "As-Samad", "The Eternal / Self-Sufficient Refuge", "بے نیاز اور سب کا سہارا", "ص-م-د", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Perfect Master upon Whom all creation relies for every need, needing nothing in return.",
     "وہ ذات جو خود سب سے بے نیاز ہے اور جس کی تمام مخلوق محتاج ہے۔",
     [{"surah": 112, "ayah": 2, "text": "اللَّهُ الصَّمَدُ", "translation": "Allah, the Eternal Refuge."}]),

    (69, "القَادِرُ", "Al-Qaadir", "The Omnipotent / Capable", "ہر چیز پر قدرت رکھنے والا", "ق-د-ر", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One who has absolute ability to originate, transform, or cease anything as He decrees.",
     "وہ ذات جو ہر ممکن کام کو کرنے پر مکمل اور غیر متزلزل قدرت رکھتی ہے۔",
     [{"surah": 6, "ayah": 65, "text": "قُلْ هُوَ الْقَادِرُ عَلَىٰ أَن يَبْعَثَ عَلَيْكُمْ عَذَابًا", "translation": "Say, 'He is the [one] Able to send upon you affliction.'"}]),

    (70, "المُقْتَدِرُ", "Al-Muqtadir", "The All-Determining / Prevailing", "مطلق اقتدار والا", "ق-د-ر", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Supreme Authority whose power is perpetually realized with total dominance.",
     "وہ ذات جس کا غلبہ و تسلط سب پر غالب ہے اور جس کے ارادے میں کوئی رکاوٹ نہیں۔",
     [{"surah": 54, "ayah": 42, "text": "فَأَخَذْنَاهُمْ أَخْذَ عَزِيزٍ مُّقْتَدِرٍ", "translation": "So We seized them with a seizure of one Exalted in Might and Perfect in Ability."}]),

    (71, "المُقَدِّمُ", "Al-Muqaddim", "The Advancer / Expediter", "آگے کرنے والا", "ق-د-م", "Justice & Truth", "عدل اور حق",
     "The One who brings forward what He wills according to perfect wisdom and decree.",
     "وہ ذات جو اپنی حکمت سے جس چیز، مرتبے یا انسان کو چاہے آگے بڑھاتی ہے۔",
     [{"surah": 50, "ayah": 28, "text": "قَالَ لَا تَخْتَصِمُوا لَدَيَّ وَقَدْ قَدَّمْتُ إِلَيْكُم بِالْوَعِيدِ", "translation": "He will say, 'Do not dispute before Me, while I had already presented to you the warning.'"}]),

    (72, "المُؤَخِّرُ", "Al-Mu'akhkhir", "The Delayer / Postponer", "پیچھے رکھنے والا اور مہلت دینے والا", "أ-خ-ر", "Justice & Truth", "عدل اور حق",
     "The One who defers things or delays consequences until their decreed appointed time.",
     "وہ ذات جو اپنی مصلحت کے تحت بعض معاملات کو پیچھے رکھتی یا مہلت عطا کرتی ہے۔",
     [{"surah": 14, "ayah": 42, "text": "إِنَّمَا يُؤَخِّرُهُمْ لِيَوْمٍ تَشْخَصُ فِيهِ الْأَبْصَارُ", "translation": "He only delays them for a Day when eyes will stare [in horror]."}]),

    (73, "الأَوَّلُ", "Al-Awwal", "The First (Without Beginning)", "سب سے پہلا ازلی", "أ-و-ل", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One before Whom nothing existed, the Beginning of all that is.",
     "وہ ذات جو ازل سے موجود ہے اور جس کے وجود کی کوئی ابتدا نہیں۔",
     [{"surah": 57, "ayah": 3, "text": "هُوَ الْأَوَّلُ وَالْآخِرُ وَالظَّاهِرُ وَالْبَاطِنُ", "translation": "He is the First and the Last, the Ascendant and the Intimate."}]),

    (74, "الآخِرُ", "Al-Aakhir", "The Last (Without End)", "سب کے بعد ابدی", "أ-خ-ر", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Everlasting One after Whom nothing will remain, existing for eternity.",
     "وہ ذات جو تمام کائنات کے فنا ہو جانے کے بعد بھی ہمیشہ باقی رہے گی۔",
     [{"surah": 57, "ayah": 3, "text": "هُوَ الْأَوَّلُ وَالْآخِرُ", "translation": "He is the First and the Last."}]),

    (75, "الظَّاهِرُ", "Az-Zaahir", "The Manifest / Ascendant", "اپنی نشانیوں سے ظاہر و غالب", "ظ-ه-ر", "Wisdom & Knowledge", "حکمت اور علم",
     "The One whose existence is overwhelmingly evident through His countless signs.",
     "وہ ذات جس کی قدرت کے جلوے اور نشانیاں کائنات کے ذرے ذرے میں عیاں ہیں۔",
     [{"surah": 57, "ayah": 3, "text": "وَالظَّاهِرُ وَالْبَاطِنُ", "translation": "The Ascendant and the Intimate."}]),

    (76, "البَاطِنُ", "Al-Baatin", "The Hidden / Intimate", "نظروں سے پوشیدہ اور اندرونی بھید جاننے والا", "ب-ط-ن", "Wisdom & Knowledge", "حکمت اور علم",
     "The One who is invisible to physical eyes, yet intimately closer than life itself.",
     "وہ ذات جو مادی نگاہوں سے پوشیدہ ہے مگر باطنی رازوں اور دلوں کے بھیدوں سے باخبر ہے۔",
     [{"surah": 57, "ayah": 3, "text": "وَالظَّاهِرُ وَالْبَاطِنُ وَهُوَ بِكُلِّ شَيْءٍ عَلِيمٌ", "translation": "And He is the Ascendant and the Intimate, and He is, of all things, Knowing."}]),

    (77, "الوَالِي", "Al-Waali", "The Supreme Governor", "کائنات کا حقیقی منتظم", "و-ل-ي", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Sole Master and Governor who administrates the entirety of cosmic affairs.",
     "وہ ذات جو تمام کائنات کے نظام اور تدبیر کو تن تنہا چلانے والی ہے۔",
     [{"surah": 13, "ayah": 11, "text": "وَمَا لَهُم مِّن دُونِهِ مِن وَالٍ", "translation": "And they have not besides Him any patron."}]),

    (78, "المُتَعَالِي", "Al-Muta'aali", "The Exalted / Transcendent", "بلند ترین اور بے عیب", "ع-ل-و", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The One who is supremely transcendent above all limitations and created attributes.",
     "وہ ذات جو ہر عیب، نقص اور مخلوق کی صفات سے بے پناہ بلند و بالا ہے۔",
     [{"surah": 13, "ayah": 9, "text": "عَالِمُ الْغَيْبِ وَالشَّهَادَةِ الْكَبِيرُ الْمُتَعَالِ", "translation": "Knower of the unseen and the witnessed, the Grand, the Exalted."}]),

    (79, "البَرُّ", "Al-Barr", "The Most Benign & Generous Source of Good", "احسان فرمانے والا اور بھلائی کا سرچشمہ", "ب-ر-ر", "Mercy & Compassion", "رحمت اور شفقت",
     "The Ever-Kind Source of all righteousness, benevolence, and compassionate grace.",
     "وہ ذات جو احسان و نیکی کی پیکر اور اپنے بندوں کے ساتھ کمال مہربانی برتنے والی ہے۔",
     [{"surah": 52, "ayah": 28, "text": "إِنَّا كُنَّا مِن قَبْلُ نَدْعُوهُ إِنَّهُ هُوَ الْبَرُّ الرَّحِيمُ", "translation": "Indeed, we used to supplicate Him before. Indeed, it is He who is the Beneficent, the Merciful."}]),

    (80, "التَّوَّابُ", "At-Tawwaab", "The Ever-Pardoning / Acceptor of Repentance", "توبہ قبول فرمانے والا", "ت-و-ب", "Forgiveness & Clemency", "مغفرت اور حلم",
     "The One who continuously inspires repentance in hearts and graciously accepts it.",
     "وہ ذات جو بار بار رجوع کرنے والے بندوں کی توبہ کو کمال عنایت سے قبول فرماتی ہے۔",
     [{"surah": 2, "ayah": 37, "text": "إِنَّهُ هُوَ التَّوَّابُ الرَّحِيمُ", "translation": "Indeed, it is He who is the Accepting of repentance, the Merciful."}]),

    (81, "المُنْتَقِمُ", "Al-Muntaqim", "The Retributor / Avenger of Injustice", "ظالموں سے بدلہ لینے والا", "ن-ق-م", "Justice & Truth", "عدل اور حق",
     "The Just One who holds tyrants, oppressors, and persistently wicked souls accountable.",
     "وہ ذات جو ظالموں، سرکشوں اور حق تلفی کرنے والوں کو انصاف کے تقاضے کے تحت عبرتناک سزا دیتی ہے۔",
     [{"surah": 32, "ayah": 22, "text": "إِنَّا مِنَ الْمُجْرِمِينَ مُنتَقِمُونَ", "translation": "Indeed We, from the criminals, will take retribution."}]),

    (82, "العَفُوُّ", "Al-Afuww", "The Supreme Effacer of Sins", "درگزر کرنے والا اور گناہ مٹانے والا", "ع-ف-و", "Forgiveness & Clemency", "مغفرت اور حلم",
     "The One who completely erases sins from records as though they had never occurred.",
     "وہ ذات جو گناہوں کو صرف بخشتی ہی نہیں بلکہ نامہ اعمال سے ان کا اثر بھی مٹا دیتی ہے۔",
     [{"surah": 4, "ayah": 99, "text": "وَكَانَ اللَّهُ عَفُوًّا غَفُورًا", "translation": "And Allah is ever Pardoning and Forgiving."}]),

    (83, "الرَّءُوفُ", "Ar-Ra'oof", "The Most Compassionate & Tender", "نہایت مہربان اور شفیق", "ر-أ-ف", "Mercy & Compassion", "رحمت اور شفقت",
     "The Tenderly Merciful One who shields His servants from undue burden and agony.",
     "وہ ذات جس کی شفقت اور نرمی بے حد ہے اور جو بندوں کو مشقت سے بچانے والی ہے۔",
     [{"surah": 2, "ayah": 207, "text": "وَاللَّهُ رَءُوفٌ بِالْعِبَادِ", "translation": "And Allah is Kind to [His] servants."}]),

    (84, "مَالِكُ المُلْكِ", "Maalik-ul-Mulk", "The Owner of All Sovereignty", "تمام کائنات کی بادشاہت کا مالک", "م-ل-ك", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Absolute Lord who dispenses rule and authority across all dimensions as He wills.",
     "وہ ذات جس کے دستِ قدرت میں تمام جہانوں کی مستقل اور حقیقی حکومت ہے۔",
     [{"surah": 3, "ayah": 26, "text": "قُلِ اللَّهُمَّ مَالِكَ الْمُلْكِ تُؤْتِي الْمُلْكَ مَن تَشَاءُ", "translation": "Say, 'O Allah, Owner of Sovereignty, You give sovereignty to whom You will.'"}]),

    (85, "ذُو الجَلَالِ وَالإِكْرَامِ", "Dhul-Jalaali-wal-Ikraam", "Possessor of Majesty & Honor", "جلال اور بخشش و کرم کا مالک", "ج-ل-ل", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Lord of Glory who is rightly feared for His majesty and adored for His boundless bounty.",
     "وہ ذات جو شایانِ تعظیم بھی ہے اور جس کے فیض و کرم کا کوئی شمار نہیں۔",
     [{"surah": 55, "ayah": 78, "text": "تَبَارَكَ اسْمُ رَبِّكَ ذِي الْجَلَالِ وَالْإِكْرَامِ", "translation": "Blessed is the name of your Lord, Owner of Majesty and Honor."}]),

    (86, "المُقْسِطُ", "Al-Muqsit", "The Equitable / Just", "انصاف کا بول بالا کرنے والا", "ق-س-ط", "Justice & Truth", "عدل اور حق",
     "The One who establishes flawless balance and vindicates the oppressed from oppressors.",
     "وہ ذات جو ہر معاملے میں کامل توازن اور عدل و انصاف قائم فرماتی ہے۔",
     [{"surah": 7, "ayah": 29, "text": "قُلْ أَمَرَ رَبِّي بِالْقِسْطِ", "translation": "Say, [O Muhammad], 'My Lord has ordered justice.'"}]),

    (87, "الجَامِعُ", "Al-Jaami'", "The Gatherer", "جمع فرمانے والا", "ج-م-ع", "Justice & Truth", "عدل اور حق",
     "The One who will assemble all humanity, generations past and present, on Judgment Day.",
     "وہ ذات جو قیامت کے عظیم الشان دن تمام اولین و آخرین کو اکٹھا فرمائے گی۔",
     [{"surah": 3, "ayah": 9, "text": "رَبَّنَا إِنَّكَ جَامِعُ النَّاسِ لِيَوْمٍ لَّا رَيْبَ فِيهِ", "translation": "Our Lord, surely You will gather the people for a Day about which there is no doubt."}]),

    (88, "الغَنِيُّ", "Al-Ghaniyy", "The Self-Sufficient / Rich Beyond Need", "بے نیاز اور غنی", "غ-ن-ي", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Entirely Self-Sufficient One who has no need of anything or anyone in all creation.",
     "وہ ذات جو ہر احتیاج اور حاجت سے پاک ہے اور تمام کائنات اس کی محتاج ہے۔",
     [{"surah": 2, "ayah": 263, "text": "وَاللَّهُ غَنِيٌّ حَلِيمٌ", "translation": "And Allah is Free of need and Forbearing."}]),

    (89, "المُغْنِي", "Al-Mughni", "The Enricher", "بے نیاز اور غنی بنانے والا", "غ-ن-ي", "Mercy & Compassion", "رحمت اور شفقت",
     "The One who enriches souls with contentment, faith, and material sufficiency.",
     "وہ ذات جو اپنے فضل سے اپنے بندوں کو محتاجی سے نکال کر غنی فرما دیتی ہے۔",
     [{"surah": 9, "ayah": 74, "text": "أَنْ أَغْنَاهُمُ اللَّهُ وَرَسُولُهُ مِن فَضْلِهِ", "translation": "That Allah and His Messenger had enriched them of His bounty."}]),

    (90, "المَانِعُ", "Al-Maani'", "The Preventer / Withholder", "روکنے والا اور حفاظت کرنے والا", "م-ن-ع", "Protection & Peace", "حفاظت اور سلامتی",
     "The Wise Protector who prevents harm from reaching His servants and withholds with wisdom.",
     "وہ ذات جو اپنے بندوں کو برائی سے بچاتی اور اپنی حکمت سے بعض چیزوں کو روک لیتی ہے۔",
     [{"surah": 67, "ayah": 21, "text": "أَمَّنْ هَٰذَا الَّذِي يَرْزُقُكُمْ إِنْ أَمْسَكَ رِزْقَهُ", "translation": "Or who is it that could provide for you if He withheld His provision?"}]),

    (91, "الضَّارُّ", "Ad-Daarr", "The Creator of What Harms (As a Trial)", "نقصان اور آزمائش پیدا کرنے والا", "ض-ر-ر", "Justice & Truth", "عدل اور حق",
     "The Sovereign One who decrees hardship and adversity as trials and tests of faith.",
     "وہ ذات جس کی قدرت و مشیت کے تحت امتحانات اور تکالیف انسانوں کی آزمائش بنتی ہیں۔",
     [{"surah": 6, "ayah": 17, "text": "وَإِن يَمْسَسْكَ اللَّهُ بِضُرٍّ فَلَا كَاشِفَ لَهُ إِلَّا هُوَ", "translation": "And if Allah should touch you with adversity, there is no remover of it except Him."}]),

    (92, "النَّافِعُ", "An-Naafi'", "The Bestower of Benefit", "نفع اور بھلائی پہنچانے والا", "ن-ف-ع", "Mercy & Compassion", "رحمت اور شفقت",
     "The Sole Originator of genuine profit, well-being, goodness, and spiritual prosperity.",
     "وہ ذات جس کے دستِ قدرت سے تمام تر خیر، نفع اور فائدے بندوں تک پہنچتے ہیں۔",
     [{"surah": 6, "ayah": 17, "text": "وَإِن يَمْسَسْكَ بِخَيْرٍ فَهُوَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ", "translation": "And if He touches you with good - then He is over all things competent."}]),

    (93, "النُّورُ", "An-Noor", "The Light", "آسمانوں اور زمین کا نور", "ن-و-ر", "Wisdom & Knowledge", "حکمت اور علم",
     "The Luminary of the heavens and the earth, who guides dark hearts into radiant truth.",
     "وہ ذات جو کائنات کو وجود کی روشنی بخشنے والی اور دلوں کو ہدایت کا نور عطا کرنے والی ہے۔",
     [{"surah": 24, "ayah": 35, "text": "اللَّهُ نُورُ السَّمَاوَاتِ وَالْأَرْضِ", "translation": "Allah is the Light of the heavens and the earth."}]),

    (94, "الهَادِي", "Al-Haadi", "The Supreme Guide", "سیدھا راستہ دکھانے والا", "ه-د-ي", "Wisdom & Knowledge", "حکمت اور علم",
     "The Divine Guide who directs lost souls to righteousness, salvation, and eternal truth.",
     "وہ ذات جو اپنے بندوں کو صراطِ مستقیم کی رہنمائی اور نیکی کی توفیق بخشتی ہے۔",
     [{"surah": 22, "ayah": 54, "text": "وَإِنَّ اللَّهَ لَهَادِ الَّذِينَ آمَنُوا إِلَىٰ صِرَاطٍ مُّسْتَقِيمٍ", "translation": "And indeed is Allah the Guide of those who have believed to a straight path."}]),

    (95, "البَدِيعُ", "Al-Badee'", "The Incomparable Originator", "بے مثال اور انوکھا پیدا فرمانے والا", "ب-د-ع", "Creation & Sustenance", "تخلیق اور رزق",
     "The Master Creator who crafts masterpieces of wonder without preceding pattern.",
     "وہ ذات جو بغیر کسی سابقہ مثال کے کائنات کو حیرت انگیز خوبصورتی کے ساتھ پیدا فرماتی ہے۔",
     [{"surah": 2, "ayah": 117, "text": "بَدِيعُ السَّمَاوَاتِ وَالْأَرْضِ", "translation": "Originator of the heavens and the earth."}]),

    (96, "البَاقِي", "Al-Baaqi", "The Everlasting", "ہمیشہ باقی رہنے والا", "ب-ق-ي", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Perpetual Being whose existence endures forever, untouched by time or cessation.",
     "وہ ذات جو تمام کائنات کے فنا ہو جانے کے بعد بھی لازوال اور ابدی رہے گی۔",
     [{"surah": 55, "ayah": 27, "text": "وَيَبْقَىٰ وَجْهُ رَبِّكَ ذُو الْجَلَالِ وَالْإِكْرَامِ", "translation": "And there will remain the Face of your Lord, Owner of Majesty and Honor."}]),

    (97, "الوَارِثُ", "Al-Waarith", "The Supreme Inheritor", "سب کا حقیقی وارث", "و-ر-ث", "Majesty & Sovereignty", "عظمت اور بادشاہت",
     "The Ultimate Heir to Whom all possessions, realms, and existence return when creation ceases.",
     "وہ ذات جس کی ملکیت میں کائنات کی تمام چیزیں اس کے عارضی مالکوں کے خاتمے کے بعد لوٹ آئیں گی۔",
     [{"surah": 15, "ayah": 23, "text": "وَإِنَّا لَنَحْنُ نُحْيِي وَنُمِيتُ وَنَحْنُ الْوَارِثُونَ", "translation": "And indeed, it is We who give life and cause death, and We are the Inheritor."}]),

    (98, "الرَّشِيدُ", "Ar-Rasheed", "The Infallible Guide to the Right Path", "صحیح تدبیر اور راہ دکھانے والا", "ر-ش-د", "Wisdom & Knowledge", "حکمت اور علم",
     "The One who directs all affairs towards their rightful end without error or hesitation.",
     "وہ ذات جس کی تدبیر اور فیصلہ بالکل درست ہوتا ہے اور جو درست سمت کی رہنمائی فرماتی ہے۔",
     [{"surah": 18, "ayah": 10, "text": "وَهَيِّئْ لَنَا مِنْ أَمْرِنَا رَشَدًا", "translation": "And facilitate for us from our affair right guidance."}]),

    (99, "الصَّبُورُ", "As-Saboor", "The Most Patient & Forbearing", "بے پناہ صبر و تحمل والا", "ص-ب-ر", "Forgiveness & Clemency", "مغفرت اور حلم",
     "The One whose sublime patience does not hasten punishment, giving ample opportunity for redemption.",
     "وہ ذات جو بندوں کی نافرمانیوں کو دیکھ کر بھی فوری عذاب میں جلدی نہیں فرماتی۔",
     [{"surah": 16, "ayah": 127, "text": "وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ", "translation": "And be patient, [O Muhammad], and your patience is not but through Allah."}]),
]

def build_dataset():
    records = []
    # Verified working high-speed CDN audio endpoints (soachishti/Asma-ul-Husna via jsDelivr)
    primary_audio_base = "https://cdn.jsdelivr.net/gh/soachishti/Asma-ul-Husna@master/audio"
    fallback_audio_base = "https://raw.githubusercontent.com/soachishti/Asma-ul-Husna/master/audio"

    for item in NAMES_RAW:
        nid, name_ar, trans, mean_en, mean_ur, root, cat, cat_ur, exp_en, exp_ur, qrefs = item
        records.append({
            "id": nid,
            "number": nid,
            "name_ar": name_ar,
            "transliteration": trans,
            "meaning_en": mean_en,
            "meaning_ur": mean_ur,
            "root_ar": root,
            "category": cat,
            "category_ur": cat_ur,
            "explanation_en": exp_en,
            "explanation_ur": exp_ur,
            "quran_references": qrefs,
            "audio_url": f"{primary_audio_base}/{nid}.mp3",
            "audio_fallback_url": f"{fallback_audio_base}/{nid}.mp3",
            "canonical_hadith_ref": "Sahih al-Bukhari 2736; Sahih Muslim 2677"
        })

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"[OK] Successfully generated {len(records)} Names of Allah in {OUTPUT_FILE}")

if __name__ == "__main__":
    build_dataset()
