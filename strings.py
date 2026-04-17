# strings.py
# Amharic translations for the Telegram Rental Bot

WELCOME_MSG = (
    "✨ <b>እንኳን ወደ አከራይና ተከራይ ቦት በደህና መጡ!</b> ✨\n\n"
    "🏠 ይህ ቦት በኢትዮጵያ ውስጥ ቤት ለማከራየት የሚፈልጉ አካላትን እና ቤት የሚፈልጉ ሰዎችን በቀላሉ ያገናኛል።\n\n"
    "👇 <i>እባክዎን ከታች ካሉት አማራጮች አንዱን ይምረጡ፦</i>"
)

ROLE_OWNER = "አከራይ ነኝ (ቤት አለኝ)"
ROLE_SEEKER = "ተከራይ ነኝ (ቤት ፈላጊ)"

# Owner Flow
OWNER_MENU_MSG = "ምን ማድረግ ይፈልጋሉ?"
OWNER_ADD_NEW = "አዲስ ቤት መመዝገብ መጀመር"
OWNER_MANAGE = "የተመዘገቡ ቤቶቼን ማየት"
OWNER_NO_LISTINGS = "ምንም የተመዘገበ ቤት የሎትም።"
OWNER_UNLIST_BTN = "❌ ዝርዝሩን አጥፋ/ለሌላ ተከራይቷል"
OWNER_UNLIST_CONFIRM = "ዝርዝሩ በተሳካ ሁኔታ ተነስቷል።"

OWNER_START = "እባክዎን የቤቱን አይነት ወይም አጭር መግለጫ ይጻፉ (ለምሳሌ፦ ባለ 2 ክፍል ኮንዶሚኒየም)"
OWNER_ASK_CITY = "ቤቱ በየትኛው ከተማ ወይም ክልል ነው የሚገኘው?"
OWNER_ASK_LOCATION = "ቤቱ በዚች ከተማ ውስጥ የት አካባቢ/ሰፈር ነው? (ለምሳሌ፦ ቦሌ፣ መገናኛ፣ 02፣ ...)"
OWNER_ASK_PRICE = "የወር ኪራይ ስንት ነው? (በቁጥር ብቻ ይጻፉ ለምሳሌ፦ 3500)"
OWNER_ASK_PHOTO = "እባክዎን እስከ 4 የቤቱን ፎቶዎችን ይላኩ (ደረጃውን ለመዝለል /skip ወይም 'ዝለል' ይጫኑ)"
PHOTO_UPLOADED = "{count}/4 ፎቶ ተልኳል። ተጨማሪ መላክ ይችላሉ ወይም ሲጨርሱ 'ጨርሻለሁ' ይበሉ።"
DONE = "ጨርሻለሁ"
OWNER_ASK_CONTACT = "እባክዎን ስልክ ቁጥርዎን ያስገቡ"
OWNER_ASK_PAYMENT = (
    "🙏 <b>የቤቱ ምዝገባ ሊጠናቀቅ ጥቂት ቀርቶታል!</b>\n\n"
    "ቤቱ በቦቱ ላይ ሆኖ ለተከራዮች እንዲታይ የአገልግሎት ክፍያ (<b>4%</b>) መክፈል ይኖርብዎታል (2% እርሶ ቀሪዉን 2% ቤቶን ከሚከራይ ሰዉ የሚቀበሉ ይሆናል)\n\n"
    "💰 <b>የክፍያ መጠን፦ {fee} ብር</b>\n"
    "👤 <b>ስም፦ ሳምሶን ማሬ</b>\n"
    # "📞 <b>የቴሌቢር ቁጥር፦ 0985605005</b>\n\n"
    "   <b>የኢትዮጵያ ንግድ ባንክ አካዉንት ቁጥር፦ 1000174738533</b>\n\n"
    # "👇 <i>ክፍያውን ከፈጸሙ በኋላ፣ ከቴሌቢር የደረስዎትን የትራንዛክሽን ቁጥር (Transaction ID) እባክዎን እዚህ ይላኩ፦</i>"
    "👇 <i>ክፍያውን ከፈጸሙ በኋላ፣ ከኢትዮጵያ ንግድ ባንክ የደረስዎትን የትራንዛክሽን ቁጥር (Transaction ID) እባክዎን እዚህ ይላኩ፦</i>"
)
PAYMENT_GUIDE = "እባክዎን ከኢትዮጵያ ንግድ ባንክ የደረስዎትን የትራንዛክሽን ቁጥር (Transaction ID) በትክክል ያስገቡ።"
OWNER_PAYMENT_PENDING = "ክፍያዎ በተሳካ ሁኔታ ተመዝግቧል! ✅ አስተዳዳሪው ሲያጸድቀው ቤቱ በቦቱ ላይ ይወጣል። እናመሰግናለን።"
OWNER_PAYMENT_SUCCESS = "እንኳን ደስ አለዎት! 🎉 የቤትዎ ዝርዝር በአስተዳዳሪው ጸድቆ ለተከራዮች ክፍት ሆኗል።"
OWNER_SUCCESS = "ቤቱ በተሳካ ሁኔታ ተመዝግቧል! ✅"

# Seeker Flow
SEEKER_MENU_MSG = "ምን ማድረግ ይፈልጋሉ?"
SEEKER_VIEW_ALL = "ሁሉንም ቤቶች እይ"
SEEKER_SEARCH = "በአካባቢ ፈልግ"
# SEEKER_AI_SEARCH = "AI ብልህ ፍለጋ 🤖"
SEEKER_AI_SEARCH = "በAI ፈልግ 🤖"
SEEKER_ASK_CITY = "ቤቱን በየትኛው ከተማ ወይም ክልል መፈለግ ይፈልጋሉ?"
SEEKER_ASK_SEARCH = "የሚፈልጉትን አካባቢ/ሰፈር ስም ይጻፉ (ለምሳሌ፦ ቦሌ፣ መገናኛ፣ ...)"
AI_SEARCH_PROMPT = "የሚፈልጉትን ቤት በዝርዝር ይግለጹልኝ (ለምሳሌ፦ 'አዲስ አበባ ቦሌ አካባቢ ባለ 2 ክፍል ኮንዶሚኒየም ፈልግልኝ')"
AI_PROCESSING = "በመፈለግ ላይ ነኝ... ⏳"
SEEKER_NO_LISTINGS = "ምንም የተመዘገበ ቤት አልተገኘም።"
SEEKER_NO_MATCH = "በዚህ አካባቢ የተመዘገበ ቤት አልተገኘም።"

# Listing Template
LISTING_TEMPLATE = (
    "🏠 {title}\n"
    "📍 ከተማ፦ {city}\n"
    "📍 ሰፈር፦ {location}\n"
    "💰 ኪራይ፦ {price} ብር\n"
    "📞 ስልክ፦ {contact}\n"
    "📅 የተመዘገበበት፦ {date}"
)

# Admin
ADMIN_DELETE = "🗑️ ዝርዝሩን ሰርዝ (Admin)"
ADMIN_DELETE_CONFIRM = "ዝርዝሩ በተሳካ ሁኔታ ተሰርዟል።"
ADMIN_TITLE = "--- የአስተዳዳሪ ክፍል ---"
ADMIN_APPROVE_REQ = "🆕 አዲስ ክፍያ ተመዝግቧል!\n\nባለቤት፦ {owner}\nርዕስ፦ {title}\nዋጋ፦ {price} ብር\nክፍያ (4%)፦ {fee} ብር\nTxID፦ {txid}"
ADMIN_APPROVE = "✅ አጽድቅ"
ADMIN_REJECT = "❌ ውድቅ አድርግ"
ADMIN_APPROVE_CONFIRM = "ዝርዝሩ ጸድቋል! ለተከራዮች የቀረበ ነው።"
ADMIN_BROADCAST_PROMPT = "📢 እባክዎን ለሁሉም ተጠቃሚዎች የሚላከውን መልእክት ይጻፉ።"
ADMIN_BROADCAST_DONE = "✅ መልእክቱ ለ {count} ተጠቃሚዎች ተልኳል።"
ADMIN_STATS = (
    "📊 <b>― የአስተዳዳሪ ዳሽቦርድ ―</b>\n\n"
    "👥 ጠቅላላ ተጠቃሚዎች፦ <b>{total}</b>\n"
    "🏠 ንቁ ዝርዝሮች፦ <b>{active}</b>\n"
    "⏳ ሊጸድቁ እየጠበቁ ያሉ፦ <b>{pending}</b>\n"
    "👤 አከራዮች (ግምት)፦ <b>{owners}</b>\n"
    "👤 ተከራዮች (ግምት)፦ <b>{seekers}</b>"
)
ADMIN_ONLY = "❌ ይህ ትዕዛዝ ለአስተዳዳሪዎች ብቻ ነው።"
ADMIN_PENDING_TITLE = "⏳ <b>ከክፍያ ጋር የቀረቡ ቤቶች፦</b>"
ADMIN_NO_PENDING = "✅ ምንም የሚጠበቁ ክፍያዎች የሉም።"

# Common
BACK = "ተመለስ ⬅️"
CANCEL = "አቋርጥ ❌"
SKIP = "ዝለል"
CANCEL_MSG = "ክዋኔው ተሰርዟል።"
BTN_NEXT = "ቀጣይ ➡️" # Next
BTN_PREV = "⬅️ ወደኋላ" # Previous
HELP_BTN = "መመሪያ/እርዳታ ℹ️"
TIMEOUT_MSG = "⏳ ጊዜው ስላለቀ ክዋኔው ተቋርጧል። እባክዎን እንደገና ይሞክሩ። /start"

# Price Validation
PRICE_INVALID = "❌ ያስገቡት ቁጥር ትክክል አይደለም። እባክዎን የወር ኪራዩን በቁጥር ብቻ ያስገቡ (ለምሳሌ፦ 3500)"

# Ratings
RATING_BTN = "⭐ ይስጡ"
RATING_PROMPT = "ለዚህ ቤት ምን ያህል ኮከብ ይሰጣሉ?"
RATING_SAVED = "✅ ምስጋና! ደረጃዎ ተመዝግቧል።"
RATING_DISPLAY = "⭐ አማካይ ደረጃ፦ {avg}/5 ({count} ሰዎች)"

# Help
HELP_MSG = (
    "📖 <b>የቦቱ አጠቃቀም መመሪያ</b>\n\n"
    "<b>🏠 ለቤት ባለቤቶች (አከራዮች):</b>\n"
    "• /start → 'አከራይ ነኝ' ይምረጡ\n"
    "• የቤቱን አይነት ወይም አጭር መግለጫ፣ አካባቢ፣ ዋጋ፣ እስከ 4 የቤቱን ፎቶዎች እና ስልክ ያስገቡ\n"
    "የአገልግሎት ክፍያ 4% ነው (2% እርሶ ቀሪዉን 2% ቤቶን ከሚከራይ ሰዉ የሚቀበሉ ይሆናል)\n\n"
    "• ቤቱ የአስተዳዳሪው ክፍያዎን ካረጋገጠ በኋላ ለተከራዮች ይቀርባል\n\n"
    "<b>🔍 ለቤት ፈላጊዎች (ተከራይ):</b>\n"
    "• /start → 'ተከራይ ነኝ' ይምረጡ\n"
    "• ከተማ ይምረጡ እና ሁሉንም ቤቶች ይመልከቱ ወይም ይፈልጉ\n"
    "• ቤቱ ከተመቸዎት፣ ባለቤቱን በስልክ ደውለው ያናግሩ\n\n"
    "<b>📌 ሌሎች ትዕዛዞች:</b>\n"
    "• /cancel - ወቅታዊ ክዋኔ ለማቋረጥ\n"
    "• /help - ይህን ገጽ ለማሳየት"
)

# Cities and Regions
ETHIOPIAN_REGIONS = [
    "አዲስ አበባ", "ኦሮሚያ", "አማራ", "ሲዳማ", "ደቡብ ኢትዮጵያ",
    "ማዕከላዊ ኢትዮጵያ", "ትግራይ", "ሶማሌ", "አፋር", "ቤኒሻንጉል ጉሙዝ",
    "ጋምቤላ", "ሀረሪ", "ድሬ ዳዋ", "ደቡብ ምዕራብ ኢትዮጵያ"
]

MAJOR_CITIES = [
    "አዲስ አበባ", "ዲላ", "ሀዋሳ", "አዳማ", "ባህር ዳር", "ጎንደር",
    "መቀሌ", "ድሬ ዳዋ", "ጅማ", "ደሴ", "ጅጅጋ", "ሻሸመኔ", "አርባ ምንጭ"
]

# Status Checks
STATUS_CHECK_MSG = "🏠 <b>ሰላም!</b> በቦታችን ላይ ያስመዘገቡት ቤት '{title}' አሁንም ለተከራዮች ክፍት ነው? እባክዎን ከታች ካሉት አማራጮች አንዱን ይጫኑ።"
STATUS_CONFIRM_STILL_AVAILABLE = "✅ አሁንም አለ"
STATUS_CONFIRM_RENTED = "❌ ለሌላ ተከራይቷል"
STATUS_CHECK_SUCCESS = "እናመሰግናለን! 🙏 የቤትዎ ዝርዝር ለተከራዮች ክፍት ሆኖ እንዲቆይ ተደርጓል።"

