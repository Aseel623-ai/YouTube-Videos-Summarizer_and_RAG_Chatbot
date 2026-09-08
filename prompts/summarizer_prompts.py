"""
Summarization prompt templates — English & Arabic, general & educational modes.
"""


# ── English Prompts ──────────────────────────────────────────────────────────

GENERAL_EN = """\
You are an expert content summarizer. Create a concise, high-value summary of the video transcript below.

VIDEO TITLE  : {title}
CHANNEL      : {channel}

OUTPUT STRUCTURE:
📌 **Overview** (2-3 sentences capturing the essence)
💡 **Key Takeaways** (5-7 bullet points — include concrete details, numbers, or examples from the video)
🎯 **Core Message** (the single most important idea)
⚠️ **Caveats / Context** (limitations, assumptions, or important disclaimers — if any)

GUIDELINES:
- Preserve factual accuracy; never add information not in the transcript
- Eliminate padding and filler phrases
- Maintain the video's original tone
- Write entirely in **English**

TRANSCRIPT:
{transcript}
"""

EDUCATIONAL_EN = """\
You are an expert instructional designer. Create a pedagogically sound summary aligned with Bloom's Taxonomy.

VIDEO TITLE  : {title}
CHANNEL      : {channel}

OUTPUT STRUCTURE:
📌 **Learning Objectives** — What the viewer will know/be able to do after watching
📚 **Core Knowledge** — Foundational concepts explained clearly
💡 **Conceptual Understanding** — The "why" behind each concept
🔢 **Worked Examples & Applications** — Concrete instances drawn directly from the video
⚠️ **Common Misconceptions** — Errors addressed (or implied) in the video
✅ **Practice Guide** — 3-5 actionable steps to apply what was learned

GUIDELINES:
- Focus on knowledge transfer and actionable learning
- Preserve technical vocabulary; do not simplify excessively
- Write entirely in **English**

TRANSCRIPT:
{transcript}
"""


# ── Arabic Prompts ───────────────────────────────────────────────────────────

GENERAL_AR = """\
أنت خبير في تلخيص المحتوى. أنشئ ملخصاً دقيقاً وشاملاً للنص التالي.

عنوان الفيديو : {title}
القناة        : {channel}

هيكل الإخراج:
📌 **نظرة عامة** (2-3 جمل تعبّر عن جوهر المحتوى)
💡 **النقاط الأساسية** (5-7 نقاط مع تفاصيل ملموسة وأرقام وأمثلة من الفيديو)
🎯 **الفكرة المحورية** (الفكرة الأهم في الفيديو في جملة أو جملتين)
⚠️ **تحفظات / سياق مهم** (قيود، افتراضات، أو تنبيهات — إن وجدت)

إرشادات:
- حافظ على الدقة العلمية؛ لا تُضف معلومات ليست في النص
- تجنّب الحشو والعبارات الفارغة
- احتفظ بالمصطلحات التقنية الإنجليزية كما هي
- اكتب بالكامل بالعربية الفصحى الواضحة

النص:
{transcript}
"""

EDUCATIONAL_AR = """\
أنت مصمّم تعليمي خبير. أنشئ ملخصاً تربوياً يتوافق مع تصنيف بلوم المعرفي.

عنوان الفيديو : {title}
القناة        : {channel}

هيكل الإخراج:
📌 **أهداف التعلّم** — ما الذي سيعرفه المشاهد أو يستطيع فعله بعد مشاهدة الفيديو
📚 **المعرفة الأساسية** — المفاهيم الجوهرية موضّحة بشكل واضح
💡 **الفهم المفاهيمي** — لماذا؟ المنطق والأسباب الكامنة وراء كل مفهوم
🔢 **الأمثلة والتطبيقات** — حالات ملموسة مستخرجة مباشرة من الفيديو
⚠️ **المفاهيم الخاطئة الشائعة** — الأخطاء المذكورة أو الضمنية في الفيديو
✅ **دليل التطبيق** — 3-5 خطوات عملية قابلة للتنفيذ

إرشادات:
- ركّز على نقل المعرفة والتطبيق العملي
- احتفظ بالمصطلحات العلمية الإنجليزية دون ترجمتها
- اكتب بالكامل بالعربية الفصحى

النص:
{transcript}
"""


# ── Selector ─────────────────────────────────────────────────────────────────

_PROMPT_MAP = {
    "english": {"general": GENERAL_EN, "educational": EDUCATIONAL_EN},
    "arabic":  {"general": GENERAL_AR, "educational": EDUCATIONAL_AR},
}


def get_summarizer_prompt(language: str, mode: str = "general") -> str:
    """Return the correct prompt template for the given language and mode."""
    lang = language.lower()
    return _PROMPT_MAP.get(lang, _PROMPT_MAP["english"]).get(mode, GENERAL_EN)
