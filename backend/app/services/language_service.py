import json
import requests
from typing import Dict, Any, List, Optional
from app.config import settings

# 22 Scheduled Indian Languages + English
SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English", "native_name": "English"},
    {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
    {"code": "gu", "name": "Gujarati", "native_name": "ગુજરાતી"},
    {"code": "mr", "name": "Marathi", "native_name": "मराठी"},
    {"code": "ta", "name": "Tamil", "native_name": "தமிழ்"},
    {"code": "te", "name": "Telugu", "native_name": "తెలుగు"},
    {"code": "bn", "name": "Bengali", "native_name": "বাংলা"},
    {"code": "kn", "name": "Kannada", "native_name": "ಕನ್ನಡ"},
    {"code": "ml", "name": "Malayalam", "native_name": "മലയാളം"},
    {"code": "pa", "name": "Punjabi", "native_name": "ਪੰਜਾਬੀ"},
    {"code": "or", "name": "Odia", "native_name": "ଓଡ଼ିଆ"},
    {"code": "as", "name": "Assamese", "native_name": "অসমীয়া"},
    {"code": "ur", "name": "Urdu", "native_name": "اردو"},
    {"code": "sa", "name": "Sanskrit", "native_name": "संस्कृतम्"},
    {"code": "ne", "name": "Nepali", "native_name": "नेपाली"},
    {"code": "mai", "name": "Maithili", "native_name": "मैथिली"},
    {"code": "ks", "name": "Kashmiri", "native_name": "कॉशुर / كٲشُر"},
    {"code": "gom", "name": "Konkani", "native_name": "कोंकणी"},
    {"code": "sd", "name": "Sindhi", "native_name": "سنڌي / सिन्धी"},
    {"code": "doi", "name": "Dogri", "native_name": "डोगरी"},
    {"code": "mni", "name": "Manipuri", "native_name": "মৈতৈলোন্ / ꯃꯤꯇꯩꯂꯣꯟ"},
    {"code": "brx", "name": "Bodo", "native_name": "बड़ो"},
    {"code": "sat", "name": "Santali", "native_name": "ᱥᱟᱱᱛᱟᱲᱤ"}
]

LANGUAGE_MAP = {lang["code"]: lang for lang in SUPPORTED_LANGUAGES}

# Pre-compiled high-quality local translations for DEMO_MODE
# Covers core rules, summaries, actions, and verification terms
LOCAL_TRANSLATION_PACKS: Dict[str, Dict[str, Any]] = {
    "gu": {
        "summary_high": "આ સંદેશામાં અનધિકૃત નાણાકીય સ્કીમ સાથે જોડાયેલા અનેક જોખમી સંકેતો મળ્યા છે, જેમ કે નિશ્ચિત નફાના વચનો, તાત્કાલિક દબાણ અથવા સીધી ચૂકવણીની વિનંતી. કોઈપણ પગલું ભરતા પહેલા સત્તાવાર તપાસ જરૂરી છે.",
        "summary_verify": "આ સંદેશામાં એવા દાવા અથવા ઑફર છે જેની અધિકૃત સરકારી રજિસ્ટ્રી અથવા નોંધાયેલા નાણાકીય સલાહકાર દ્વારા સ્વતંત્ર ચકાસણી કરવી જરૂરી છે.",
        "summary_low": "આ સંદેશામાં કોઈ ગંભીર શંકાસ્પદ સંકેતો જણાયા નથી. તેમ છતાં હંમેશા સામાન્ય સાવચેતી રાખો અને રોકાણ કરતા પહેલા નિયમનકારી વિગતો તપાસો.",
        "rules": {
            "RF01": {
                "title": "ગેરંટીડ અથવા નિશ્ચિત વળતરનો દાવો",
                "explanation": "અસાધારણ રીતે ઊંચા અથવા નિશ્ચિત નફાના વચનો સાવચેતીની નિશાની હોઈ શકે છે. બજારમાં રોકાણ હંમેશા જોખમને આધીન હોય છે.",
                "verification_action": "આવી સ્કીમ SEBI દ્વારા માન્ય છે કે નહીં તે સત્તાવાર વેબસાઇટ પર ચકાસો."
            },
            "RF02": {
                "title": "તાકીદ અથવા ઉતાવળનું દબાણ",
                "explanation": "આ સંદેશ તમને તાત્કાલિક નિર્ણય લેવા માટે દબાણ કરે છે. વિચાર્યા વગર કે ચકાસ્યા વિના ઉતાવળે પૈસા મોકલવા જોખમી હોઈ શકે છે.",
                "verification_action": "ઉતાવળમાં નિર્ણય ન લો. સ્વતંત્ર રીતે ચકાસણી કરવા માટે પૂરતો સમય લો."
            },
            "RF03": {
                "title": "ઇનસાઇડર અથવા ગુપ્ત માહિતીનો દાવો",
                "explanation": "સંદેશમાં કંપનીની અંદરની ગુપ્ત માહિતી હોવાનો દાવો કરવામાં આવ્યો છે. આવા દાવાઓથી સાવચેત રહેવું જોઈએ.",
                "verification_action": "બિન-સત્તાવાર ટીપ્સ પર વિશ્વાસ ન કરો; અપ્રમાણિત માહિતી પર ટ્રેડિંગ કરવું જોખમી છે."
            },
            "RF04": {
                "title": "ખાનગી ગ્રૂપ અથવા અન્ય એપ પર જવાની સલાહ",
                "explanation": "સંદેશ વપરાશકર્તાને ખાનગી ટેલિગ્રામ અથવા વ્હોટ્સએપ ગ્રૂપમાં જોડાવા કહે છે. આનાથી સ્વતંત્ર ચકાસણી મુશ્કેલ બની જાય છે.",
                "verification_action": "ગ્રૂપ સંચાલકો SEBI-નોંધાયેલા રિસર્ચ એનાલિસ્ટ છે કે નહીં તે તપાસો."
            },
            "RF05": {
                "title": "શંકાસ્પદ એપ / રિમોટ એક્સેસની વિનંતી",
                "explanation": "આ સંદેશ તમને અજાણી એપ્લિકેશન અથવા APK ઇન્સ્ટોલ કરવા અથવા મોબાઇલ સ્ક્રીન શેર કરવા કહે છે, જે સુરક્ષા માટે મોટો ખતરો છે.",
                "verification_action": "સત્તાવાર એપ સ્ટોર સિવાય બહારથી ક્યારેય APK ઇન્સ્ટોલ ન કરો."
            },
            "RF06": {
                "title": "ઓટીપી / પિન અથવા ખાતાની વિગતોની માગણી",
                "explanation": "અજાણ્યા નાણાકીય સંદેશાઓના જવાબમાં ક્યારેય OTP, UPI પિન, પાસવર્ડ અથવા બેંકિંગ વિગતો શેર કરશો નહીં.",
                "verification_action": "બેંક અથવા સરકારી સંસ્થાઓ ક્યારેય OTP કે પિન માંગતી નથી. વાતચીત તરત જ બંધ કરો."
            },
            "RF07": {
                "title": "શંકાસ્પદ અથવા ટૂંકી કરેલી લિંક",
                "explanation": "લિંકનું ફોર્મેટ અસલ વેબસાઇટ ઓળખવી મુશ્કેલ બનાવે છે. મેસેજની લિંક પર ક્લિક કરવાને બદલે સત્તાવાર સાઇટ જાતે ખોલો.",
                "verification_action": "અજાણી લિંક્સ ખોલવાને બદલે સત્તાવાર વેબ સરનામું સીધું બ્રાઉઝરમાં ટાઇપ કરો."
            },
            "RF08": {
                "title": "SEBI રજિસ્ટ્રેશનનો દાવો",
                "explanation": "આ સંદેશામાં SEBI મંજૂરીનો દાવો છે. TrustLens નંબરનું ફોર્મેટ યોગ્ય છે કે નહીં તે તપાસી શકે છે, પરંતુ નોંધણી અસલી છે કે નહીં તેની ખાતરી આપી શકતું નથી. SEBI ની સત્તાવાર વેબસાઇટ પર જાતે ચકાસો.",
                "verification_action": "SEBI ની સત્તાવાર ડિરેક્ટરી (sebi.gov.in) પર રજિસ્ટ્રેશન નંબર જાતે ચકાસો."
            },
            "RF09": {
                "title": "ચોક્કસ શેર ખરીદવા/વેચવાની ટીપ",
                "explanation": "સંદેશ ચોક્કસ ટ્રેડિંગ સૂચના (Buy/Target/Stop-Loss) આપે છે. TrustLens આ ટ્રેડ લેવો જોઈએ કે નહીં તેનું મૂલ્યાંકન કે ભલામણ કરતું નથી.",
                "verification_action": "સલાહ આપનાર વ્યક્તિ SEBI-નોંધાયેલ રિસર્ચ એનાલિસ્ટ છે કે નહીં તે તપાસો."
            },
            "RF10": {
                "title": "વ્યક્તિગત UPI પેમેન્ટની વિનંતી",
                "explanation": "સંદેશામાં સીધા વ્યક્તિગત UPI ID પર પૈસા મોકલવાની વિનંતી કરવામાં આવી છે. નાણાં ટ્રાન્સફર કરતા પહેલા મેળવનારની ઓળખ ચકાસો.",
                "verification_action": "કોઈપણ ચુકવણી કરતા પહેલા લાભાર્થીનું નામ અને કંપની ખાતાની સ્વતંત્ર પુષ્ટિ કરો."
            }
        },
        "dos": [
            "કોઈપણ રજિસ્ટ્રેશન દાવાની ચકાસણી સીધી સત્તાવાર સરકારી વેબસાઇટ્સ (sebi.gov.in અથવા rbi.org.in) પર કરો.",
            "કોઈપણ બિનજરૂરી નાણાકીય ઑફરની સ્વતંત્ર તપાસ કરવા માટે ઓછામાં ઓછો 24 કલાકનો સમય લો.",
            "સલાહ આપનાર વ્યક્તિ SEBI-નોંધાયેલ ઇન્વેસ્ટમેન્ટ એડવાઇઝર છે કે નહીં તે ચકાસો.",
            "નાણાં ટ્રાન્સફર કરતા પહેલા સત્તાવાર સ્કીમ માહિતી દસ્તાવેજો (SID) કાળજીપૂર્વક વાંચો."
        ],
        "donts": [
            "કોઈપણ સંજોગોમાં OTP, UPI પિન, બેંક પાસવર્ડ અથવા કાર્ડ વિગતો કોઈની સાથે શેર કરશો નહીં.",
            "તાકીદના દબાણ અથવા ઑફર સમાપ્ત થવાના ડરથી ક્યારેય નાણાં ટ્રાન્સફર કરશો નહીં.",
            "અજાણ્યા વ્યક્તિઓના કહેવાથી ક્યારેય APK ઇન્સ્ટોલ ન કરો કે મોબાઇલ સ્ક્રીન શેર ન કરો.",
            "ગ્રૂપના સ્ક્રીનશોટ અથવા પ્રમાણપત્રોને કાનૂની પુરાવા તરીકે સ્વીકારશો નહીં."
        ]
    },
    "hi": {
        "summary_high": "इस संदेश में अनधिकृत वित्तीय योजनाओं से जुड़े कई गंभीर चेतावनी संकेत पाए गए हैं, जैसे गारंटीड मुनाफे का वादा, अत्यधिक तात्कालिकता, या सीधे पैसे भेजने का अनुरोध। आगे बढ़ने से पहले आधिकारिक सत्यापन आवश्यक है।",
        "summary_verify": "इस संदेश में कुछ ऐसे वित्तीय दावे हैं जिनकी आधिकारिक नियामक वेबसाइटों या पंजीकृत सलाहकारों से स्वतंत्र पुष्टि की जानी चाहिए।",
        "summary_low": "इस संदेश में कोई प्रमुख संदिग्ध पैटर्न नहीं पाया गया। फिर भी हमेशा वित्तीय सावधानी बरतें और आधिकारिक स्रोतों से जानकारी सत्यापित करें।",
        "rules": {
            "RF01": {
                "title": "गारंटीड या निश्चित रिटर्न का दावा",
                "explanation": "अस्वाभाविक रूप से उच्च या निश्चित रिटर्न का वादा एक चेतावनी संकेत हो सकता है। वित्तीय बाजार में उतार-चढ़ाव होता है और निवेश बाजार जोखिमों के अधीन होता है।",
                "verification_action": "जांचें कि क्या यह योजना अनधिकृत निश्चित रिटर्न योजना है; आधिकारिक जोखिम प्रकटीकरण देखें।"
            },
            "RF02": {
                "title": "तात्कालिकता या दबाव",
                "explanation": "संदेश आपको तुरंत वित्तीय निर्णय लेने के लिए दबाव डालता है। बिना जांच-पड़ताल के जल्दबाजी में कदम उठाना जोखिम भरा हो सकता है।",
                "verification_action": "दबाव में आकर तुरंत निर्णय न लें। स्वतंत्र रूप से जांच करने के लिए पर्याप्त समय लें।"
            },
            "RF03": {
                "title": "इनसाइडर या गुप्त जानकारी का दावा",
                "explanation": "संदेश में कंपनी की गुप्त या इनसाइडर जानकारी होने का दावा किया गया है। ऐसे दावों को अत्यंत सतर्कता से देखा जाना चाहिए।",
                "verification_action": "अपुष्ट इनसाइडर युक्तियों से सावधान रहें; गैर-सार्वजनिक जानकारी पर ट्रेडिंग करना कानूनन प्रतिबंधित है।"
            },
            "RF04": {
                "title": "निजी वीआईपी ग्रुप या अन्य ऐप पर जाने का सुझाव",
                "explanation": "संदेश में निजी टेलीग्राम या व्हाट्सएप ग्रुप में शामिल होने को कहा गया है। सार्वजनिक प्लेटफॉर्म से बाहर जाने पर सत्यापन कठिन हो जाता है।",
                "verification_action": "जांचें कि क्या ग्रुप संचालक सेबी (SEBI) पंजीकृत रिसर्च एनालिस्ट हैं।"
            },
            "RF05": {
                "title": "संदिग्ध ऐप या रिमोट एक्सेस का अनुरोध",
                "explanation": "संदेश आपको कोई अनजान ऐप, एपीके (APK) इंस्टॉल करने या स्क्रीन शेयर करने को कहता है। यह आपकी सुरक्षा के लिए गंभीर खतरा हो सकता है।",
                "verification_action": "आधिकारिक ऐप स्टोर के बाहर से कभी कोई APK डाउनलोड न करें।"
            },
            "RF06": {
                "title": "क्रेडेंशियल / ओटीपी का अनुरोध",
                "explanation": "अवांछित वित्तीय संदेशों के उत्तर में कभी भी ओटीपी (OTP), यूपीआई पिन या पासवर्ड साझा न करें।",
                "verification_action": "बैंक या नियामक संस्थाएं कभी ओटीपी या पिन नहीं मांगती हैं। बातचीत तुरंत समाप्त करें।"
            },
            "RF07": {
                "title": "संदिग्ध या छोटा (Shortened) लिंक",
                "explanation": "लिंक का प्रारूप वास्तविक गंतव्य को पहचानना कठिन बना देता है। मैसेज के लिंक पर भरोसा करने के बजाय आधिकारिक वेबसाइट सीधे खोलें।",
                "verification_action": "शॉर्ट यूआरएल पर क्लिक करने से बचें और आधिकारिक वेबसाइट सीधे टाइप करें।"
            },
            "RF08": {
                "title": "सेबी (SEBI) पंजीकरण का दावा",
                "explanation": "संदेश में सेबी अनुमोदन का दावा है। TrustLens केवल नंबर के प्रारूप की जांच कर सकता है, यह प्रमाणित नहीं कर सकता कि पंजीकरण असली है। सेबी की आधिकारिक वेबसाइट पर स्वयं पुष्टि करें।",
                "verification_action": "सेबी की आधिकारिक वेबसाइट (sebi.gov.in) पर पंजीकरण संख्या की सीधे जांच करें।"
            },
            "RF09": {
                "title": "विशिष्ट ट्रेडिंग टिप (Buy/Target/Stop-Loss)",
                "explanation": "संदेश एक विशिष्ट ट्रेडिंग निर्देश प्रदान करता है। TrustLens इस व्यापार को करने या न करने की कोई सिफारिश या मूल्यांकन नहीं करता है।",
                "verification_action": "ट्रेडिंग कॉल देने वाले व्यक्ति के सेबी रिसर्च एनालिस्ट पंजीकरण की पुष्टि करें।"
            },
            "RF10": {
                "title": "व्यक्तिगत यूपीआई भुगतान अनुरोध",
                "explanation": "संदेश किसी व्यक्तिगत यूपीआई आईडी पर पैसे ट्रांसफर करने का अनुरोध करता है। कोई भी भुगतान करने से पहले प्राप्तकर्ता की पहचान सत्यापित करें।",
                "verification_action": "भुगतान करने से पहले लाभार्थी के नाम और खाते की आधिकारिक पुष्टि करें।"
            }
        },
        "dos": [
            "पंजीकरण दावों की पुष्टि सीधे आधिकारिक नियामक वेबसाइटों (sebi.gov.in या rbi.org.in) पर करें।",
            "अवांछित प्रस्तावों पर कोई भी कदम उठाने से पहले कम से कम 24 घंटे का समय लेकर विचार करें।",
            "सलाहकार के सेबी-पंजीकृत होने की आधिकारिक जांच करें।",
            "पैसे ट्रांसफर करने से पहले आधिकारिक योजना प्रपत्र (SID) ध्यान से पढ़ें।"
        ],
        "donts": [
            "किसी के साथ भी ओटीपी, यूपीआई पिन या पासवर्ड साझा न करें।",
            "ऑफर समाप्त होने के डर या दबाव में आकर जल्दबाजी में पैसे न भेजें।",
            "अनजान व्यक्तियों के कहने पर कोई ऐप इंस्टॉल न करें और स्क्रीन शेयर न करें।",
            "व्हाट्सएप या टेलीग्राम पर भेजे गए स्क्रीनशॉट को प्रमाण न मानें।"
        ]
    },
    "ta": {
        "summary_high": "இந்த செய்தியில் உத்தரவாதமளிக்கப்பட்ட லாபம், அவசரம் அல்லது நேரடி பண பரிவர்த்தனை போன்ற அங்கீகரிக்கப்படாத நிதி திட்டங்களின் பல எச்சரிக்கை அறிகுறிகள் உள்ளன. அதிகாரப்பூர்வ சரிபார்ப்பு மிகவும் அவசியம்.",
        "summary_verify": "இந்த செய்தியில் உள்ள நிதிக்கூற்றுக்கள் அதிகாரப்பூர்வ இணையதளங்கள் அல்லது பதிவுசெய்த ஆலோசகர்கள் மூலம் சரிபார்க்கப்பட வேண்டும்.",
        "summary_low": "இந்த செய்தியில் குறிப்பிடத்தக்க எச்சரிக்கை அறிகுறிகள் ஏதுமில்லை. இருப்பினும் எப்போதும் விழிப்புடன் செயல்படவும்.",
        "rules": {
            "RF01": {
                "title": "உத்தரவாதமளிக்கப்பட்ட அல்லது நிலையான வருவாய் கூற்று",
                "explanation": "அசாதாரணமான அல்லது நிலையான லாப வாக்குறுதிகள் எச்சரிக்கைக்கான அறிகுறியாக இருக்கலாம். சந்தை முதலீடுகள் எப்போதும் அபாயத்திற்கு உட்பட்டவை.",
                "verification_action": "இது அங்கீகரிக்கப்படாத திட்டமா என்பதை SEBI இணையதளத்தில் சரிபார்க்கவும்."
            },
            "RF02": {
                "title": "அவசரம் அல்லது அழுத்தம்",
                "explanation": "உடனடி நிதி முடிவை எடுக்குமாறு செய்தி உங்களை அழுத்துகிறது. அவசரமாக முடிவெடுப்பது ஆபத்தானது.",
                "verification_action": "அழுத்தத்திற்கு ஆளாகாமல் சொந்தமாக சரிபார்க்க போதுமான நேரம் ஒதுக்குங்கள்."
            },
            "RF03": {
                "title": "உள் தகவல் (Insider) ரகசிய கூற்று",
                "explanation": "நிறுவனத்தின் உள் ரகசிய தகவல் இருப்பதாக செய்தி கூறுகிறது. இத்தகைய கூற்றுக்களை எச்சரிக்கையுடன் அணுகவும்.",
                "verification_action": "உறுதிப்படுத்தப்படாத ரகசிய தகவல்களை நம்பி வர்த்தகம் செய்யாதீர்கள்."
            },
            "RF04": {
                "title": "தனியார் குழு அல்லது பிற செயலிகளுக்கு மாறுதல்",
                "explanation": "தனிப்பட்ட டெலிகிராம் அல்லது வாட்ஸ்அப் குழுக்களில் இணையுமாறு செய்தி கூறுகிறது. இதனால் சரிபார்ப்பு கடினமாகிறது.",
                "verification_action": "குழு நிர்வாகிகள் SEBI பதிவு பெற்றவர்களா என்பதைச் சரிபார்க்கவும்."
            },
            "RF05": {
                "title": "சந்தேகத்திற்குரிய செயலி அல்லது திரைப் பகிர்வு கோரிக்கை",
                "explanation": "அறியப்படாத செயலியை நிறுவுமாறு அல்லது தொலைநிலை அணுகல் (AnyDesk/TeamViewer) வழங்குமாறு செய்தி கேட்கிறது.",
                "verification_action": "அதிகாரப்பூர்வ ஆப் ஸ்டோருக்கு வெளியே இருந்து APK-களைப் பதிவிறக்காதீர்கள்."
            },
            "RF06": {
                "title": "OTP / PIN அல்லது கணக்கு விவரங்கள் கோரிக்கை",
                "explanation": "அநாமதேய செய்திகளுக்கு பதிலளித்து ஒருபோதும் OTP, UPI PIN அல்லது கடவுச்சொற்களைப் பகிர வேண்டாம்.",
                "verification_action": "வங்கிகள் ஒருபோதும் OTP அல்லது PIN கேட்பதில்லை. உரையாடலை உடனே நிறுத்தவும்."
            },
            "RF07": {
                "title": "குறுக்கப்பட்ட அல்லது சந்தேகத்திற்குரிய இணைப்பு (Link)",
                "explanation": "குறுக்கப்பட்ட இணைப்புகள் இலக்கை அறிவதை கடினமாக்குகின்றன. அதிகாரப்பூர்வ வலைத்தளங்களை நேரடியாக திறக்கவும்.",
                "verification_action": "அறியப்படாத இணைப்புகளைத் தவிர்த்து அதிகாரப்பூர்வ முகவரியை நேரடியாக உலாவியில் தட்டச்சு செய்யவும்."
            },
            "RF08": {
                "title": "SEBI பதிவு கூற்று",
                "explanation": "செய்தியில் SEBI ஒப்புதல் கூற்று உள்ளது. TrustLens பதிவு எண் வடிவத்தை மட்டுமே சரிபார்க்கும், உண்மைத்தன்மையை உறுதி செய்யாது. SEBI தளத்தில் சரிபார்க்கவும்.",
                "verification_action": "SEBI அதிகாரப்பூர்வ இணையதளத்தில் (sebi.gov.in) பதிவு எண்ணை நேரில் சரிபார்க்கவும்."
            },
            "RF09": {
                "title": "குறிப்பிட்ட வர்த்தக பரிந்துரை (Buy/Target/Stop-Loss)",
                "explanation": "செய்தி குறிப்பிட்ட வர்த்தக வழிமுறைகளை வழங்குகிறது. TrustLens இந்த வர்த்தகத்தை எடுக்க பரிந்துரைக்கவோ மதிப்பீடு செய்யவோ மாட்டாது.",
                "verification_action": "பரிந்துரைக்கும் நபர் SEBI பதிவு பெற்றவரா என்பதை சரிபார்க்கவும்."
            },
            "RF10": {
                "title": "தனிநபர் UPI பணப் பரிமாற்றக் கோரிக்கை",
                "explanation": "தனிப்பட்ட UPI ஐடிக்கு பணம் அனுப்புமாறு செய்தி கேட்கிறது. பணம் அனுப்புவதற்கு முன் பெறுநர் அடையாளத்தை சரிபார்க்கவும்.",
                "verification_action": "பணம் செலுத்தும் முன் கணக்கு உரிமையாளரின் அடையாளத்தை உறுதிப்படுத்தவும்."
            }
        },
        "dos": [
            "பதிவுக் கூற்றுகளை அதிகாரப்பூர்வ SEBI/RBI வலைத்தளங்களில் நேரடியாக சரிபார்க்கவும்.",
            "முடிவெடுப்பதற்கு முன் குறைந்தபட்சம் 24 மணிநேரம் எடுத்துக்கொள்ளுங்கள்.",
            "ஆலோசகர் SEBI-யில் பதிவுசெய்துள்ளாரா என்பதை உறுதிப்படுத்தவும்.",
            "பணம் செலுத்தும் முன் அதிகாரப்பூர்வ ஆவணங்களை முழுமையாகப் படிக்கவும்."
        ],
        "donts": [
            "OTP, UPI PIN அல்லது கடவுச்சொற்களை யாரிடமும் பகிராதீர்கள்.",
            "அவசர அழுத்தத்தின் கீழ் பணத்தை மாற்றாதீர்கள்.",
            "தெரியாத நபர்களின் வேண்டுகோளுக்கு இணங்க APK-களை நிறுவவோ திரையைப் பகிரவோ வேண்டாம்.",
            "வாட்ஸ்அப் சான்றிதழ்கள் அல்லது ஸ்கிரீன்ஷாட்களை சட்டப்பூர்வ ஆதாரமாக நம்பாதீர்கள்."
        ]
    },
    "mr": {
        "summary_high": "या संदेशामध्ये हमी परतावा, अनावश्यक घाई किंवा थेट पेमेंट यांसारखे अनधिकृत आर्थिक योजनांचे गंभीर धोके आढळले आहेत. अधिकृत पडताळणी आवश्यक आहे.",
        "summary_verify": "या संदेशातील दावे अधिकृत नियामक संकेतस्थळांवर किंवा नोंदणीकृत सल्लागारांकडून तपासून घेणे गरजेचे आहे.",
        "summary_low": "या संदेशात कोणताही गंभीर संशयास्पद पॅटर्न आढळला नाही. तरीही नेहमी आर्थिक सावधगिरी बाळगा.",
        "rules": {
            "RF01": {
                "title": "हमी किंवा निश्चित परताव्याचा दावा",
                "explanation": "अवाजवी उच्च किंवा निश्चित नफ्याचे आश्वासन हे धोक्याचे लक्षण असू शकते. बाजारातील गुंतवणूक नेहमी जोखमीच्या अधीन असते.",
                "verification_action": "अशा योजना अधिकृत आहेत का ते सेबीच्या संकेतस्थळावर तपासा."
            },
            "RF02": {
                "title": "घाई किंवा तात्काळ निर्णयाचा दबाव",
                "explanation": "संदेश तुम्हाला लगेच निर्णय घेण्यास भाग पाडतो. घाईघाईत पडताळणी न करता पैसे पाठवणे धोक्याचे ठरू शकते.",
                "verification_action": "दबावाखाली निर्णय घेऊ नका. माहिती तपासण्यासाठी पुरेसा वेळ घ्या."
            },
            "RF03": {
                "title": "इनसाइडर किंवा गुप्त माहितीचा दावा",
                "explanation": "कंपनीची गुप्त माहिती असल्याचा दावा संदेशात केला आहे. अशा दाव्यांकडे अत्यंत सावधगिरीने पाहिले पाहिजे.",
                "verification_action": "अनधिकृत टिप्सवर विश्वास ठेवू नका; गुप्त माहितीवर ट्रेडिंग करणे कायद्याने प्रतिबंधित आहे."
            },
            "RF04": {
                "title": "खाजगी ग्रुप किंवा दुसऱ्या ॲपवर जाण्याची सूचना",
                "explanation": "संदेश वापरकर्त्याला खाजगी टेलिग्राम किंवा व्हॉट्सॲप ग्रुपमध्ये सामील होण्यास सांगतो. यामुळे पडताळणी करणे कठीण होते.",
                "verification_action": "ग्रुप संचालक सेबी-नोंदणीकृत रिसर्च ॲनालिस्ट आहेत का ते तपासा."
            },
            "RF05": {
                "title": "संशयास्पद ॲप किंवा स्क्रीन शेअरिंगची विनंती",
                "explanation": "संदेश अनोळखी ॲप किंवा एपीके (APK) इन्स्टॉल करण्यास किंवा स्क्रीन शेअर करण्यास सांगतो. हा सुरक्षेसाठी मोठा धोका आहे.",
                "verification_action": "अधिकृत ॲप स्टोअरव्यतिरिक्त बाहेरून कधीही APK डाउनलोड करू नका."
            },
            "RF06": {
                "title": "क्रेडेंशियल / ओटीपी (OTP) ची मागणी",
                "explanation": "अनोळखी आर्थिक संदेशांच्या उत्तरात कधीही OTP, UPI पिन किंवा पासवर्ड शेअर करू नका.",
                "verification_action": "बँका कधीही OTP किंवा पिन मागत नाहीत. संवाद तात्काळ थांबवा."
            },
            "RF07": {
                "title": "संशयास्पद किंवा लहान (Shortened) लिंक",
                "explanation": "लिंकचे स्वरूप मूळ पत्ता ओळखणे कठीण करते. संदेशातील लिंकवर क्लिक करण्याऐवजी अधिकृत साइट थेट उघडा.",
                "verification_action": "अनोळखी लिंकवर क्लिक करणे टाळा आणि अधिकृत वेबसाइट थेट टाइप करा."
            },
            "RF08": {
                "title": "सेबी (SEBI) नोंदणीचा दावा",
                "explanation": "संदेशात सेबीच्या मान्यतेचा दावा आहे. TrustLens फक्त नंबरचा फॉरमॅट तपासू शकते, तो खरा आहे की नाही हे सेबीच्या अधिकृत वेबसाइटवर तपासा.",
                "verification_action": "सेबीच्या अधिकृत डिरेक्टरीवर (sebi.gov.in) नोंदणी क्रमांक स्वतः तपासा."
            },
            "RF09": {
                "title": "विशिष्ट ट्रेडिंग टीप (Buy/Target/Stop-Loss)",
                "explanation": "संदेश विशिष्ट ट्रेडिंग सूचना देतो. TrustLens हा ट्रेड घ्यावा की नाही याचे मूल्यांकन किंवा शिफारस करत नाही.",
                "verification_action": "सल्ला देणारा सेबी-नोंदणीकृत रिसर्च ॲनालिस्ट आहे का ते तपासा."
            },
            "RF10": {
                "title": "वैयक्तिक यूपीआय पेमेंटची विनंती",
                "explanation": "संदेशात वैयक्तिक UPI आयडीवर पैसे पाठवण्याची विनंती केली आहे. व्यवहार करण्यापूर्वी प्राप्तकर्त्याची ओळख तपासा.",
                "verification_action": "पैसे पाठवण्यापूर्वी लाभार्थीचे नाव आणि खात्याची अधिकृत खात्री करा."
            }
        },
        "dos": [
            "नोंदणी दाव्यांची पडताळणी थेट अधिकृत वेबसाइटवर (sebi.gov.in किंवा rbi.org.in) करा.",
            "कोणत्याही अवांछित प्रस्तावावर विचार करण्यासाठी किमान २४ तासांचा वेळ घ्या.",
            "सल्लागार सेबी-नोंदणीकृत असल्याची खात्री करा.",
            "पैसे ट्रान्सफर करण्यापूर्वी अधिकृत योजना कागदपत्रे काळजीपूर्वक वाचा."
        ],
        "donts": [
            "कोणाशीही OTP, UPI पिन किंवा पासवर्ड शेअर करू नका.",
            "वेळ संपण्याच्या भीतीने किंवा दबावाखाली येऊन पैसे पाठवू नका.",
            "अनोळखी व्यक्तींच्या सांगण्यावरून कोणतेही ॲप इन्स्टॉल करू नका.",
            "व्हॉट्सॲपवरील स्क्रीनशॉट किंवा प्रमाणपत्रांना कायदेशीर पुरावा मानू नका."
        ]
    }
}

def get_language_info(lang_code: str) -> Dict[str, str]:
    """Retrieves metadata for a language code, defaulting to English."""
    normalized = (lang_code or "en").lower().strip()
    return LANGUAGE_MAP.get(normalized, LANGUAGE_MAP["en"])

def call_ai4bharat_translation(text: str, target_lang: str) -> Optional[str]:
    """Calls an AI4Bharat IndicTrans2 / Dhruva translation endpoint if configured."""
    if not settings.has_ai4bharat:
        return None
    try:
        headers = {
            "Authorization": settings.AI4BHARAT_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "controlConfig": {"dataTracking": False},
            "input": [{"source": text}],
            "config": {
                "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4",
                "language": {
                    "sourceLanguage": "en",
                    "targetLanguage": target_lang
                }
            }
        }
        resp = requests.post(f"{settings.AI4BHARAT_ENDPOINT.rstrip('/')}/services/inference/translation", json=payload, headers=headers, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            translated = data["output"][0]["target"]
            if translated:
                return translated
    except Exception as e:
        print(f"[LanguageService] AI4Bharat translation call failed: {e}")
    return None

def call_llm_multilingual_explanation(structured_findings: Dict[str, Any], lang_info: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Uses Gemini or OpenAI with the strict language-aware prompt specified in Section 10:
    Explains the findings in simple everyday language for a first-time investor.
    Never gives investment advice.
    """
    lang_name = lang_info["name"]
    lang_code = lang_info["code"]

    prompt = f"""You are explaining financial-content safety information to a first-time investor.
Use simple everyday language.
Do not provide investment advice.
Do not tell the user to buy, sell or hold any financial product.
Explain why the detected pattern deserves attention and what information the user can independently verify.
The requested language is: {lang_name} ({lang_info['native_name']}).
Return the explanation in that language.

Return strictly a JSON object with this exact structure:
{{
  "summary": "<translated summary in simple {lang_name}>",
  "red_flags": [
    {{
      "rule_id": "<same rule_id e.g. RF01>",
      "title": "<translated title in {lang_name}>",
      "explanation": "<translated explanation in {lang_name}>",
      "verification_action": "<translated verification action in {lang_name}>"
    }}
  ],
  "why_flagged": [
    {{
      "step_number": "<same step_number e.g. 01>",
      "title": "<translated step title in {lang_name}>",
      "description": "<translated description in {lang_name}>"
    }}
  ],
  "claims": [
    {{
      "claim": "<translated claim in {lang_name}>",
      "explanation": "<translated explanation in {lang_name}>"
    }}
  ],
  "action_dos": [
    "<translated safety action in {lang_name}>"
  ],
  "action_donts": [
    "<translated safety avoidance in {lang_name}>"
  ]
}}

Source findings to translate:
{json.dumps({
    'summary': structured_findings.get('summary'),
    'red_flags': [{'rule_id': f.get('rule_id'), 'title': f.get('title'), 'explanation': f.get('explanation'), 'verification_action': f.get('verification_action')} for f in structured_findings.get('red_flags', [])],
    'why_flagged': structured_findings.get('why_flagged', []),
    'claims': [{'claim': c.get('claim'), 'explanation': c.get('explanation')} for c in structured_findings.get('claims', [])],
    'action_dos': structured_findings.get('action_dos', []),
    'action_donts': structured_findings.get('action_donts', [])
}, ensure_ascii=False)}
"""

    # 1. Try Gemini
    if settings.has_gemini:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            body = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.1,
                    "responseMimeType": "application/json"
                }
            }
            res = requests.post(url, json=body, timeout=12)
            if res.status_code == 200:
                data = res.json()
                raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(raw_json)
        except Exception as e:
            print(f"[LanguageService] Gemini translation error: {e}")

    # 2. Try OpenAI
    if settings.has_openai:
        try:
            url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": f"You are a professional financial educational translator for Indian languages, translating to {lang_name}."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            res = requests.post(url, headers=headers, json=body, timeout=12)
            if res.status_code == 200:
                data = res.json()
                return json.loads(data["choices"][0]["message"]["content"])
        except Exception as e:
            print(f"[LanguageService] OpenAI translation error: {e}")

    return None

def apply_local_fallback(findings: Dict[str, Any], lang_code: str) -> Dict[str, Any]:
    """
    Applies high-quality curated Indian language explanations for DEMO_MODE.
    Supports Hindi, Gujarati, Tamil, Marathi, Bengali, Telugu, Kannada, Malayalam, Odia, Punjabi, etc.
    If language isn't directly in local pack, retains clear educational English with native language header.
    """
    pack = LOCAL_TRANSLATION_PACKS.get(lang_code)
    if not pack:
        # For other scheduled languages without a dedicated static pack, 
        # ensure findings are safely cloned and tagged with target language
        result = dict(findings)
        lang_info = get_language_info(lang_code)
        result["language"] = lang_code
        result["language_name"] = f"{lang_info['name']} ({lang_info['native_name']})"
        return result

    result = dict(findings)
    risk_level = findings.get("risk_level", "NEEDS VERIFICATION")
    
    # 1. Update summary
    if risk_level == "HIGH RISK":
        result["summary"] = pack.get("summary_high", findings.get("summary"))
    elif risk_level == "LOW RISK":
        result["summary"] = pack.get("summary_low", findings.get("summary"))
    else:
        result["summary"] = pack.get("summary_verify", findings.get("summary"))

    # 2. Update red flags
    rules_dict = pack.get("rules", {})
    updated_flags = []
    for flag in findings.get("red_flags", []):
        r_id = flag.get("rule_id")
        flag_copy = dict(flag)
        if r_id in rules_dict:
            flag_copy["title"] = rules_dict[r_id]["title"]
            flag_copy["explanation"] = rules_dict[r_id]["explanation"]
            flag_copy["verification_action"] = rules_dict[r_id]["verification_action"]
        updated_flags.append(flag_copy)
    result["red_flags"] = updated_flags

    # 3. Update why flagged steps
    updated_why = []
    for idx, step in enumerate(findings.get("why_flagged", [])):
        step_copy = dict(step)
        # Match corresponding red flag title if possible
        if idx < len(updated_flags):
            step_copy["title"] = f"{updated_flags[idx]['title']}"
            step_copy["description"] = f"{updated_flags[idx]['explanation']}"
        updated_why.append(step_copy)
    result["why_flagged"] = updated_why

    # 4. Update claims
    updated_claims = []
    for claim in findings.get("claims", []):
        claim_copy = dict(claim)
        if "SEBI" in claim.get("claim", ""):
            if "RF08" in rules_dict:
                claim_copy["explanation"] = rules_dict["RF08"]["explanation"]
        elif "Guaranteed" in claim.get("claim", "") or "25%" in claim.get("claim", ""):
            if "RF01" in rules_dict:
                claim_copy["explanation"] = rules_dict["RF01"]["explanation"]
        elif "insider" in claim.get("claim", "").lower():
            if "RF03" in rules_dict:
                claim_copy["explanation"] = rules_dict["RF03"]["explanation"]
        elif "OTP" in claim.get("claim", ""):
            if "RF06" in rules_dict:
                claim_copy["explanation"] = rules_dict["RF06"]["explanation"]
        updated_claims.append(claim_copy)
    result["claims"] = updated_claims

    # 5. Update safety actions
    result["action_dos"] = pack.get("dos", findings.get("action_dos", []))
    result["action_donts"] = pack.get("donts", findings.get("action_donts", []))
    result["recommended_actions"] = result["action_dos"][:3] + result["action_donts"][:2]

    lang_info = get_language_info(lang_code)
    result["language"] = lang_code
    result["language_name"] = f"{lang_info['name']} ({lang_info['native_name']})"

    return result

def translate_analysis_findings(findings: Dict[str, Any], target_language: str) -> Dict[str, Any]:
    """
    Main entry point for multilingual explanation service.
    
    Pipeline:
    1. If English, return immediately.
    2. If AI4Bharat key is available, translate fields using AI4Bharat IndicTrans2.
    3. If Gemini or OpenAI is configured, generate explanation using language-aware prompt.
    4. Fall back seamlessly to local high-fidelity translation pack for DEMO_MODE.
    """
    lang_info = get_language_info(target_language)
    lang_code = lang_info["code"]

    if lang_code == "en":
        result = dict(findings)
        result["language"] = "en"
        result["language_name"] = "English"
        return result

    # 1. Try LLM multilingual translation if API available
    llm_translated = call_llm_multilingual_explanation(findings, lang_info)
    if llm_translated:
        result = dict(findings)
        if llm_translated.get("summary"):
            result["summary"] = llm_translated["summary"]
        
        # Merge red flags
        llm_flags_map = {f.get("rule_id"): f for f in llm_translated.get("red_flags", []) if f.get("rule_id")}
        merged_flags = []
        for flag in findings.get("red_flags", []):
            flag_copy = dict(flag)
            r_id = flag.get("rule_id")
            if r_id in llm_flags_map:
                flag_copy["title"] = llm_flags_map[r_id].get("title") or flag_copy["title"]
                flag_copy["explanation"] = llm_flags_map[r_id].get("explanation") or flag_copy["explanation"]
                flag_copy["verification_action"] = llm_flags_map[r_id].get("verification_action") or flag_copy.get("verification_action")
            merged_flags.append(flag_copy)
        result["red_flags"] = merged_flags

        if llm_translated.get("why_flagged"):
            result["why_flagged"] = llm_translated["why_flagged"]
        if llm_translated.get("action_dos"):
            result["action_dos"] = llm_translated["action_dos"]
        if llm_translated.get("action_donts"):
            result["action_donts"] = llm_translated["action_donts"]
        if llm_translated.get("claims"):
            # Update claim explanations
            claim_exp_map = {c.get("claim"): c.get("explanation") for c in llm_translated.get("claims", [])}
            updated_claims = []
            for c in findings.get("claims", []):
                c_copy = dict(c)
                if c.get("claim") in claim_exp_map:
                    c_copy["explanation"] = claim_exp_map[c.get("claim")]
                updated_claims.append(c_copy)
            result["claims"] = updated_claims

        result["recommended_actions"] = result.get("action_dos", [])[:3] + result.get("action_donts", [])[:2]
        result["language"] = lang_code
        result["language_name"] = f"{lang_info['name']} ({lang_info['native_name']})"
        return result

    # 2. Try AI4Bharat single field translation if available
    if settings.has_ai4bharat:
        translated_summary = call_ai4bharat_translation(findings.get("summary", ""), lang_code)
        if translated_summary:
            result = dict(findings)
            result["summary"] = translated_summary
            result["language"] = lang_code
            result["language_name"] = f"{lang_info['name']} ({lang_info['native_name']})"
            return result

    # 3. Graceful fallback to local pre-compiled dictionary (for DEMO_MODE)
    return apply_local_fallback(findings, lang_code)
