"""UI strings in the learner's language.

Keys are stable identifiers; values are per-language text. A missing
translation falls back to English, and a missing key returns the key itself
so a gap is visible on screen instead of crashing a page.
"""

from __future__ import annotations

from core import config

UI_STRINGS: dict[str, dict[str, str]] = {
    "tagline": {
        "en-IN": "Learn in the language you think in.",
        "hi-IN": "जिस भाषा में सोचते हैं, उसी में सीखिए।",
        "bn-IN": "আপনি যে ভাষায় চিন্তা করেন, সেই ভাষাতেই শিখুন।",
        "ta-IN": "நீங்கள் எந்த மொழியில் சிந்திக்கிறீர்களோ, அதே மொழியிலேயே கற்றுக்கொள்ளுங்கள்.",
        "te-IN": "మీరు ఏ భాషలో ఆలోచిస్తారో అదే భాషలో నేర్చుకోండి.",
    },
    "choose_language": {
        "en-IN": "Choose your language",
        "hi-IN": "अपनी भाषा चुनिए",
        "bn-IN": "আপনার ভাষা বেছে নিন",
        "ta-IN": "உங்கள் மொழியைத் தேர்ந்தெடுங்கள்",
        "te-IN": "మీ భాషను ఎంచుకోండి",
    },
    "hero_sub": {
        "en-IN": "Read, ask, and be assessed in your mother tongue.",
        "hi-IN": "अपनी मातृभाषा में पढ़िए, पूछिए और मूल्यांकन दीजिए।",
        "bn-IN": "মাতৃভাষায় পড়ুন, প্রশ্ন করুন এবং মূল্যায়নের মুখোমুখি হোন।",
        "ta-IN": "உங்கள் தாய்மொழியிலேயே படியுங்கள், கேளுங்கள், மற்றும் மதிப்பீடு பெறுங்கள்.",
        "te-IN": "మీ మాతృభాషలోనే చదవండి, అడగండి, అంచనా వేయించుకోండి.",
    },
    "telemetry_line": {
        "en-IN": "Everything you tap is measured, so a teacher can see what works.",
        "hi-IN": "आपका हर टैप दर्ज होता है, ताकि शिक्षक देख सकें क्या काम कर रहा है।",
        "bn-IN": "আপনি যা কিছুতে ট্যাপ করবেন তা মাপা হয়, যাতে একজন শিক্ষক বুঝতে পারেন কোনটি কাজ করছে।",
        "ta-IN": "நீங்கள் தொடும் அனைத்தும் அளவிடப்படுகிறது, எனவே எது வேலை செய்கிறது என்பதை ஒரு ஆசிரியர் பார்க்க முடியும்.",
        "te-IN": "మీరు నొక్కే ప్రతిదీ కొలుస్తారు, కాబట్టి ఏది బాగా పనిచేస్తుందో ఉపాధ్యాయుడు చూడగలరు.",
    },
    "built_for": {
        "en-IN": "Built for CDS208",
        "hi-IN": "CDS208 के लिए बनाया गया",
        "bn-IN": "CDS208-এর জন্য তৈরি করা হয়েছে",
        "ta-IN": "CDS208-க்காக உருவாக்கப்பட்டது",
        "te-IN": "CDS208 కోసం రూపొందించబడింది",
    },
    "card_reader": {
        "en-IN": "The lesson reader",
        "hi-IN": "पाठ वाचक",
        "bn-IN": "পাঠ পড়ার অংশ",
        "ta-IN": "பாடம் படிப்பவர்",
        "te-IN": "లెసన్ రీడర్",
    },
    "card_translate": {
        "en-IN": "Live translation",
        "hi-IN": "तुरंत अनुवाद",
        "bn-IN": "লাইভ ট্রান্সলেশন",
        "ta-IN": "நேரடி மொழிபெயர்ப்பு",
        "te-IN": "లైవ్ ట్రాన్స్‌లేషన్",
    },
    "card_tutor": {
        "en-IN": "The AI tutor",
        "hi-IN": "एआई शिक्षक",
        "bn-IN": "এআই টিউটর",
        "ta-IN": "AI ஆசிரியர்",
        "te-IN": "AI ట్యూటర్",
    },
    "card_progress": {
        "en-IN": "My progress",
        "hi-IN": "मेरी प्रगति",
        "bn-IN": "আমার অগ্রগতি",
        "ta-IN": "என் முன்னேற்றம்",
        "te-IN": "నా ప్రోగ్రెస్",
    },
    "card_analytics": {
        "en-IN": "Analytics",
        "hi-IN": "विश्लेषण",
        "bn-IN": "অ্যানালিটিক্স",
        "ta-IN": "பகுப்பாய்வு",
        "te-IN": "అనలిటిక్స్",
    },
    "mock_mode": {
        "en-IN": "Mock mode",
        "hi-IN": "मॉक मोड",
        "bn-IN": "মক মোড",
        "ta-IN": "போலி முறை",
        "te-IN": "మాక్ మోడ్",
    },
    "later_phase": {
        "en-IN": "Coming in a later phase",
        "hi-IN": "अगले चरण में आएगा",
        "bn-IN": "পরবর্তী ধাপে আসছে",
        "ta-IN": "பிற்காலத்தில் வரவுள்ளது",
        "te-IN": "తర్వాతి దశలో రాబోతోంది",
    },
    "nav_home": {
        "en-IN": "Home",
        "hi-IN": "मुख्य पृष्ठ",
        "bn-IN": "হোম",
        "ta-IN": "முகப்பு",
        "te-IN": "హోమ్",
    },
}


def t(key: str, lang: str | None = None) -> str:
    """Translate a UI key into ``lang``, falling back to English, then the key."""
    entry = UI_STRINGS.get(key)
    if entry is None:
        return key
    code = lang or config.DEFAULT_LANG
    return entry.get(code) or entry.get(config.DEFAULT_LANG) or key


def coverage() -> dict[str, int]:
    """How many keys each language has — surfaced as a Phase 5 QA check."""
    return {
        code: sum(1 for entry in UI_STRINGS.values() if code in entry)
        for code in config.LANG_CODES
    }
