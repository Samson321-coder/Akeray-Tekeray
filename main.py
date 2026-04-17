import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

import strings
import database
import watermark

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot_debug.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id_str) for id_str in os.getenv("ADMIN_IDS", "").split(",") if id_str]

# Initialize Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_gemini_model(model_name="gemini-1.5-flash-latest"):
    """Safely initialize a generative model."""
    try:
        return genai.GenerativeModel(model_name)
    except Exception as e:
        logger.error(f"Failed to initialize model {model_name}: {e}")
        return None

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Default model
    model = get_gemini_model("gemini-2.5-flash")
else:
    model = None
    logger.warning("GEMINI_API_KEY not found in environment variables.")

# Conversation States
CHOOSING_ROLE, OWNER_TITLE, OWNER_CITY, OWNER_LOCATION, OWNER_PRICE, OWNER_PHOTO, OWNER_CONTACT, OWNER_PAYMENT, SEEKER_MENU, SEARCH_CITY, SEARCH_QUERY, ADMIN_BROADCAST, AI_SEARCH, OWNER_MENU = range(14)

def get_main_keyboard():
    keyboard = [
        [strings.ROLE_OWNER],
        [strings.ROLE_SEEKER],
        [strings.HELP_BTN]
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received start command from {update.effective_user.id}")
    user = update.effective_user
    database.add_user(user.id, user.username)
    
    # Check if user is admin
    if user.id in ADMIN_IDS:
        database.add_user(user.id, user.username, role='admin')
        await update.message.reply_text(strings.ADMIN_TITLE)

    await update.message.reply_text(
        strings.WELCOME_MSG,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )
    return CHOOSING_ROLE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        strings.CANCEL_MSG, reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def timeout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Called when a conversation times out due to inactivity."""
    if update and update.effective_message:
        await update.effective_message.reply_text(
            strings.TIMEOUT_MSG, reply_markup=get_main_keyboard()
        )
    return ConversationHandler.END

# Landlord Flow
async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[strings.OWNER_ADD_NEW], [strings.OWNER_MANAGE], [strings.BACK]]
    await update.message.reply_text(
        strings.OWNER_MENU_MSG, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return OWNER_MENU

async def owner_add_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        strings.OWNER_START, reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True)
    )
    return OWNER_TITLE

async def owner_manage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    listings = database.get_listings_by_owner(user_id)
    
    if not listings:
        await update.message.reply_text(strings.OWNER_NO_LISTINGS)
        return OWNER_MENU
        
    context.user_data['current_listings'] = listings
    context.user_data['is_for_owner'] = True
    await send_listing_page(update, context, 0)
    return OWNER_MENU

async def owner_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["title"] = update.message.text
    keyboard = []
    # Major Cities
    for i in range(0, len(strings.MAJOR_CITIES), 3):
        row = strings.MAJOR_CITIES[i:i+3]
        keyboard.append(row)
    # Add "Regions" button
    keyboard.append(["ክልሎች (Regions) 🌍"])
    keyboard.append([strings.BACK, strings.CANCEL])
    
    await update.message.reply_text(
        strings.OWNER_ASK_CITY,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return OWNER_CITY

async def owner_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == strings.BACK:
        return await owner_add_new(update, context)
    
    if "Regions" in text or "ክልሎች" in text:
        keyboard = []
        for i in range(0, len(strings.ETHIOPIAN_REGIONS), 2):
            row = strings.ETHIOPIAN_REGIONS[i:i+2]
            keyboard.append(row)
        keyboard.append([strings.BACK])
        await update.message.reply_text("እባክዎን ክልል ይምረጡ፦", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return OWNER_CITY

    context.user_data["city"] = text
    await update.message.reply_text(
        strings.OWNER_ASK_LOCATION,
        reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True)
    )
    return OWNER_LOCATION

async def owner_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["location"] = update.message.text
    await update.message.reply_text(strings.OWNER_ASK_PRICE)
    return OWNER_PRICE

async def owner_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import re
    price_text = update.message.text.strip()
    # Strip currency symbols and whitespace, keep digits and decimal point
    cleaned = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
    try:
        price_val = float(cleaned)
        if price_val <= 0:
            raise ValueError
        context.user_data["price"] = cleaned
        await update.message.reply_text(strings.OWNER_ASK_PHOTO)
        return OWNER_PHOTO
    except (ValueError, TypeError):
        await update.message.reply_text(strings.PRICE_INVALID)
        return OWNER_PRICE

async def owner_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "photos" not in context.user_data:
        context.user_data["photos"] = []
    
    if update.message.photo:
        # Download photo and apply watermark
        try:
            photo_file = await update.message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            watermarked = watermark.apply_watermark(bytes(photo_bytes))
            # Send and immediately get the new file_id
            sent = await update.message.reply_photo(photo=watermarked, caption="✅ ፎቶ ተቀብሏል (watermarked)")
            photo_id = sent.photo[-1].file_id
        except Exception as e:
            logger.warning(f"Watermark failed, using original: {e}")
            photo_id = update.message.photo[-1].file_id
        
        context.user_data["photos"].append(photo_id)
    
    count = len(context.user_data["photos"])
    
    if count >= 4:
        await update.message.reply_text(strings.OWNER_ASK_CONTACT, reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True))
        return OWNER_CONTACT
    
    keyboard = [[strings.DONE], [strings.CANCEL]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        strings.PHOTO_UPLOADED.format(count=count),
        reply_markup=reply_markup
    )
    return OWNER_PHOTO

async def owner_skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["photos"] = []
    await update.message.reply_text(strings.OWNER_ASK_CONTACT, reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True))
    return OWNER_CONTACT

async def owner_done_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "photos" not in context.user_data or not context.user_data["photos"]:
        context.user_data["photos"] = []
        
    await update.message.reply_text(strings.OWNER_ASK_CONTACT, reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True))
    return OWNER_CONTACT

async def owner_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text
    user_id = update.effective_user.id
    
    # Calculate 4% fee
    try:
        price_str = context.user_data["price"].replace(",", "").replace(" ", "")
        # Remove any non-numeric characters except decimal point
        import re
        price_str = re.sub(r'[^\d.]', '', price_str)
        price = float(price_str)
        fee = price * 0.04
    except:
        fee = 0 # Fallback
    
    context.user_data["fee"] = fee
    
    # Join photo IDs with comma
    photos_str = ",".join(context.user_data.get("photos", [])) if context.user_data.get("photos") else None
    
    listing_id = database.add_listing(
        user_id,
        context.user_data["title"],
        context.user_data.get("city", "ዲላ"),
        context.user_data["location"],
        context.user_data["price"],
        photos_str,
        context.user_data["contact"],
        fee_amount=fee
    )
    context.user_data["listing_id"] = listing_id
    
    await update.message.reply_text(
        strings.OWNER_ASK_PAYMENT.format(fee=f"{fee:,.2f}"),
        reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True),
        parse_mode='HTML'
    )
    return OWNER_PAYMENT

async def owner_submit_txid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txid = update.message.text
    listing_id = context.user_data["listing_id"]
    database.update_listing_txid(listing_id, txid)
    
    # Notify Admin
    owner = update.effective_user.username or update.effective_user.first_name
    admin_msg = strings.ADMIN_APPROVE_REQ.format(
        owner=owner,
        title=context.user_data["title"],
        price=context.user_data["price"],
        fee=f"{context.user_data['fee']:,.2f}",
        txid=txid
    )
    
    keyboard = [
        [
            InlineKeyboardButton(strings.ADMIN_APPROVE, callback_data=f"approve_{listing_id}"),
            InlineKeyboardButton(strings.ADMIN_REJECT, callback_data=f"reject_{listing_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=admin_msg, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    await update.message.reply_text(strings.OWNER_PAYMENT_PENDING, reply_markup=get_main_keyboard())
    return CHOOSING_ROLE

# Seeker Flow
async def seeker_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[strings.SEEKER_VIEW_ALL], [strings.SEEKER_SEARCH, strings.SEEKER_AI_SEARCH], [strings.BACK]]
    await update.message.reply_text(
        strings.SEEKER_MENU_MSG, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SEEKER_MENU

async def seeker_ai_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not model:
        await update.message.reply_text("AI features are currently unavailable.")
        return SEEKER_MENU
    
    await update.message.reply_text(strings.AI_SEARCH_PROMPT)
    return AI_SEARCH

async def handle_ai_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    if not model:
        await update.message.reply_text("AI features are currently unavailable.")
        return SEEKER_MENU

    processing_msg = await update.message.reply_text(strings.AI_PROCESSING)
    
    # Get all active listings to give context to Gemini
    listings = database.get_all_listings()
    
    context_text = "Here are the available house listings:\n"
    for item in listings:
        # id, owner_id, title, city, location, price, photo_file_id, contact_phone, created_at
        context_text += f"- Title: {item[2]}, City: {item[3]}, Location: {item[4]}, Price: {item[5]}, Contact: {item[7]}\n"
    
    prompt = f"""
    You are a helpful house hunting assistant for the 'Akeray Tekeray' bot in Ethiopia. 
    User Question: "{query}"
    
    {context_text}
    
    Based on the listings above, please:
    1. Identify the most relevant houses for the user.
    2. Respond in Amharic.
    3. If you find matches, summarize them and tell the user they can see the full details below or search for the specific location.
    4. If no houses match, suggest the closest alternatives or tell them to try a different search.
    5. ONLY talk about house hunting. Do not answer questions about other topics.
    """
    
    try:
        # List of models to try in order of preference
        models_to_try = [
            "gemini-2.5-flash", 
            "gemini-2.0-flash", 
            "gemini-1.5-flash",
            "gemini-flash-latest", 
            "gemini-pro-latest",
            "gemini-1.5-pro"
        ]
        
        response = None
        last_error = ""

        for m_name in models_to_try:
            try:
                temp_model = genai.GenerativeModel(m_name)
                response = temp_model.generate_content(prompt)
                if response:
                    logger.info(f"Successfully used model: {m_name}")
                    break
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Model {m_name} failed: {e}")
                continue

        if not response:
            raise Exception(f"All models failed. Last error: {last_error}")

        await processing_msg.delete()
        
        # Safe response extraction
        if response and response.candidates:
            candidate = response.candidates[0]
            if candidate.finish_reason != 1: # 1 = STOP
                logger.warning(f"Gemini stopped early: {candidate.finish_reason}")
            
            if candidate.content and candidate.content.parts:
                text = response.text
                await update.message.reply_text(text)
            else:
                logger.warning(f"Gemini returned no content. Finish reason: {candidate.finish_reason}")
                await update.message.reply_text("ይቅርታ፣ ጥያቄዎን ማቀነባበር አልቻልኩም። እባክዎን ጥያቄዎን ቀየር አድርገው ይሞክሩ።")
        else:
            logger.warning(f"Gemini returned no response for query: {query}")
            await update.message.reply_text("ይቅርታ፣ ምንም መልስ አልተገኘም። እባክዎን እንደገና ይሞክሩ።")
            
    except Exception as e:
        logger.error(f"Gemini Error for query '{query}': {e}", exc_info=True)
        try:
            await processing_msg.edit_text(f"Sorry, I encountered an error: {str(e)[:50]}... Please try again later.")
        except:
            await update.message.reply_text("Sorry, I encountered an error while processing your request.")
    
    return SEEKER_MENU

async def view_all_listings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    listings = database.get_all_listings()
    if not listings:
        await update.message.reply_text(strings.SEEKER_NO_LISTINGS)
        return SEEKER_MENU
    
    context.user_data['current_listings'] = listings
    context.user_data['is_for_owner'] = False
    await send_listing_page(update, context, 0)
    return SEEKER_MENU

async def search_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for i in range(0, len(strings.MAJOR_CITIES), 3):
        row = strings.MAJOR_CITIES[i:i+3]
        keyboard.append(row)
    keyboard.append(["ክልሎች (Regions) 🌍"])
    keyboard.append([strings.BACK])
    
    await update.message.reply_text(
        strings.SEEKER_ASK_CITY,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SEARCH_CITY

async def search_city_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == strings.BACK:
        return await seeker_start(update, context)
    
    if "Regions" in text or "ክልሎች" in text:
        keyboard = []
        for i in range(0, len(strings.ETHIOPIAN_REGIONS), 2):
            row = strings.ETHIOPIAN_REGIONS[i:i+2]
            keyboard.append(row)
        keyboard.append([strings.BACK])
        await update.message.reply_text("እባክዎን የሚፈልጉትን ክልል ይምረጡ፦", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return SEARCH_CITY
        
    context.user_data["search_city"] = text
    await update.message.reply_text(
        strings.SEEKER_ASK_SEARCH,
        reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True)
    )
    return SEARCH_QUERY

async def execute_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    city = context.user_data.get("search_city")
    listings = database.search_listings(query, city=city)
    if not listings:
        await update.message.reply_text(strings.SEEKER_NO_MATCH)
        return SEEKER_MENU
    
    context.user_data['current_listings'] = listings
    context.user_data['is_for_owner'] = False
    await send_listing_page(update, context, 0)
    return SEEKER_MENU

async def send_listing_page(update: Update, context: ContextTypes.DEFAULT_TYPE, current_idx: int):
    listings = context.user_data.get('current_listings', [])
    
    # If listings are missing (e.g. after bot restart), reload from DB
    if not listings:
        listings = database.get_all_listings()
        context.user_data['current_listings'] = listings
        context.user_data['is_for_owner'] = False
        logger.info(f"DEBUG: Reloaded {len(listings)} listings from DB for pagination")
    
    if not listings or current_idx < 0 or current_idx >= len(listings):
        return

    for_owner = context.user_data.get('is_for_owner', False)
    is_admin = update.effective_user.id in ADMIN_IDS
    viewer_id = update.effective_user.id
    item = listings[current_idx]
    listing_id = item[0]
    
    from telegram import InputMediaPhoto
    
    status_msg = ""
    if for_owner:
        status_map = {'pending': '⏳ Pending', 'paid': '✅ Active', 'rented': '🔒 Unlisted'}
        status_text = status_map.get(item[9], item[9]) if len(item) > 9 else "Unknown"
        tx_info = f"\n🎫 TXID: {item[11]}" if len(item) > 11 and item[11] else ""
        status_msg = f"\n📊 Status: {status_text}{tx_info}"
    
    # Show rating
    avg_rating, rating_count = database.get_avg_rating(listing_id)
    rating_line = f"\n{strings.RATING_DISPLAY.format(avg=avg_rating, count=rating_count)}" if avg_rating else ""
    
    # Page indicator
    page_indicator = f"\n\n📄 {current_idx + 1}/{len(listings)}"
        
    text = strings.LISTING_TEMPLATE.format(
        title=item[2],
        city=item[3],
        location=item[4],
        price=item[5],
        contact=item[7],
        date=item[8]
    ) + status_msg + rating_line + page_indicator
    
    nav_row = []
    if current_idx > 0:
        nav_row.append(InlineKeyboardButton(strings.BTN_PREV, callback_data=f"page_{current_idx-1}"))
    if current_idx < len(listings) - 1:
        nav_row.append(InlineKeyboardButton(strings.BTN_NEXT, callback_data=f"page_{current_idx+1}"))
    
    keyboard = []
    if nav_row:
        keyboard.append(nav_row)
    
    # Rating buttons (1-5 stars) — only for seekers viewing active listings
    if not for_owner and not is_admin:
        keyboard.append([
            InlineKeyboardButton(f"{i}⭐", callback_data=f"rate_{listing_id}_{i}")
            for i in range(1, 6)
        ])
        
    if is_admin:
        keyboard.append([InlineKeyboardButton(strings.ADMIN_DELETE, callback_data=f"delete_{item[0]}")])
        
    if for_owner and (len(item) <= 8 or item[8] != 'rented'):
        keyboard.append([InlineKeyboardButton(strings.OWNER_UNLIST_BTN, callback_data=f"unlist_{item[0]}")])
        
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    photo_ids = item[5].split(",") if item[5] else []
    
    # Send new message
    # Use context.bot directly to avoid issues if the original message was deleted
    chat_id = update.effective_chat.id
    func = context.bot.send_photo
    func_text = context.bot.send_message
    func_media_group = context.bot.send_media_group
    
    # Common arguments for sending
    send_args = {"chat_id": chat_id}

    if len(photo_ids) > 1:
        media = [InputMediaPhoto(media=photo_ids[0], caption=text, parse_mode='HTML')]
        for pid in photo_ids[1:]:
            media.append(InputMediaPhoto(media=pid))
        
        sent_messages = await func_media_group(media=media, **send_args)
        context.user_data['last_media_group_ids'] = [m.message_id for m in sent_messages]
        
        if keyboard:
            await func_text(text="መቆጣጠሪያ (Controls):", reply_markup=reply_markup, **send_args)
    elif len(photo_ids) == 1:
        context.user_data['last_media_group_ids'] = []
        await func(photo=photo_ids[0], caption=text, reply_markup=reply_markup, parse_mode='HTML', **send_args)
    else:
        context.user_data['last_media_group_ids'] = []
        await func_text(text=text, reply_markup=reply_markup, parse_mode='HTML', **send_args)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    log_msg = f"DEBUG: Callback query received: {query.data} from {update.effective_user.id}"
    logger.info(log_msg)
    print(log_msg) # Direct terminal output
    await query.answer()
    
    if query.data.startswith("page_"):
        idx = int(query.data.split("_")[1])
        try:
            # Delete media group messages if they exist
            last_media_ids = context.user_data.get('last_media_group_ids', [])
            for mid in last_media_ids:
                try:
                    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=mid)
                except:
                    pass
            context.user_data['last_media_group_ids'] = []
            
            await query.message.delete()
        except:
            pass
        await send_listing_page(update, context, idx)

    elif query.data.startswith("delete_"):
        if update.effective_user.id not in ADMIN_IDS:
            return
            
        listing_id = query.data.split("_")[1]
        database.delete_listing(listing_id)
        if query.message.photo:
            await query.edit_message_caption(caption=f"{query.message.caption}\n\n❌ {strings.ADMIN_DELETE_CONFIRM}")
        else:
            await query.edit_message_text(text=f"{query.message.text}\n\n❌ {strings.ADMIN_DELETE_CONFIRM}")

    elif query.data.startswith("unlist_"):
        listing_id = int(query.data.split("_")[1])
        listing = database.get_listing_by_id(listing_id)
        if not listing or listing[1] != update.effective_user.id:
            return
            
        database.unlist_listing(listing_id)
        if query.message.photo:
            await query.edit_message_caption(caption=f"{query.message.caption}\n\n{strings.OWNER_UNLIST_CONFIRM}")
        else:
            await query.edit_message_text(text=f"{query.message.text}\n\n{strings.OWNER_UNLIST_CONFIRM}")

    elif query.data.startswith("approve_"):
        if update.effective_user.id not in ADMIN_IDS:
            return
            
        listing_id = int(query.data.split("_")[1])
        database.approve_listing(listing_id)
        
        # Notify owner
        listing = database.get_listing_by_id(listing_id)
        if listing:
            owner_id = listing[1]
            try:
                await context.bot.send_message(chat_id=owner_id, text=strings.OWNER_PAYMENT_SUCCESS)
            except:
                pass
        
        await query.edit_message_text(text=f"{query.message.text}\n\n✅ {strings.ADMIN_APPROVE_CONFIRM}")

    elif query.data.startswith("rate_"):
        parts = query.data.split("_")
        listing_id = int(parts[1])
        stars = int(parts[2])
        reviewer_id = update.effective_user.id
        database.add_rating(listing_id, reviewer_id, stars)
        await query.answer(strings.RATING_SAVED, show_alert=True)

        await query.edit_message_text(text=f"{query.message.text}\n\n❌ {strings.CANCEL_MSG}")

    elif query.data.startswith("reject_"):
        if update.effective_user.id not in ADMIN_IDS:
            return
        listing_id = query.data.split("_")[1]
        database.delete_listing(listing_id)
        await query.edit_message_text(text=f"{query.message.text}\n\n❌ {strings.CANCEL_MSG}")

    elif query.data.startswith("verify_available_"):
        listing_id = int(query.data.split("_")[2])
        database.refresh_listing_date(listing_id)
        database.update_last_checked(listing_id)
        await query.edit_message_text(text=f"{query.message.text}\n\n{strings.STATUS_CHECK_SUCCESS}")

    elif query.data.startswith("verify_rented_"):
        listing_id = int(query.data.split("_")[2])
        database.unlist_listing(listing_id)
        await query.edit_message_text(text=f"{query.message.text}\n\n{strings.OWNER_UNLIST_CONFIRM}")


# Admin Features
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(strings.ADMIN_ONLY)
        return
    
    users = database.get_all_users()
    total = database.get_total_user_count()
    active = database.get_active_listing_count()
    pending = database.get_pending_listing_count()
    roles = [u[2] for u in users]
    owners_count = roles.count('owner') + roles.count('admin')
    seekers_count = total - owners_count
    
    await update.message.reply_text(
        strings.ADMIN_STATS.format(
            total=total, active=active, pending=pending,
            owners=owners_count, seekers=seekers_count
        ),
        parse_mode='HTML'
    )

async def admin_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all listings waiting for admin approval."""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(strings.ADMIN_ONLY)
        return
    
    pending_listings = database.get_pending_listings_with_txid()
    
    if not pending_listings:
        await update.message.reply_text(strings.ADMIN_NO_PENDING)
        return
    
    await update.message.reply_text(strings.ADMIN_PENDING_TITLE, parse_mode='HTML')
    
    context.user_data['current_listings'] = pending_listings
    context.user_data['is_for_owner'] = True # Use owner view style to show status/txid
    await send_listing_page(update, context, 0)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        strings.HELP_MSG, 
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(strings.ADMIN_ONLY)
        return ConversationHandler.END
    
    await update.message.reply_text(strings.ADMIN_BROADCAST_PROMPT, reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True))
    return ADMIN_BROADCAST

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return ConversationHandler.END
    
    msg_text = update.message.text
    if msg_text == strings.CANCEL:
        return await cancel(update, context)
        
    users = database.get_all_users()
    count = 0
    for user in users:
        try:
            # user[0] is telegram_id
            await context.bot.send_message(chat_id=user[0], text=msg_text)
            count += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user[0]}: {e}")
            
    await update.message.reply_text(strings.ADMIN_BROADCAST_DONE.format(count=count), reply_markup=get_main_keyboard())
    return CHOOSING_ROLE

# Automated Jobs
async def send_status_checks(context: ContextTypes.DEFAULT_TYPE):
    """Periodic job to ask owners if their listings are still available."""
    listings = database.get_listings_needing_check(days=14)
    logger.info(f"Running automated status check for {len(listings)} listings...")
    
    for item in listings:
        listing_id = item[0]
        owner_id = item[1]
        title = item[2]
        
        keyboard = [
            [
                InlineKeyboardButton(strings.STATUS_CONFIRM_STILL_AVAILABLE, callback_data=f"verify_available_{listing_id}"),
                InlineKeyboardButton(strings.STATUS_CONFIRM_RENTED, callback_data=f"verify_rented_{listing_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = strings.STATUS_CHECK_MSG.format(title=title)
        
        try:
            await context.bot.send_message(chat_id=owner_id, text=msg, reply_markup=reply_markup, parse_mode='HTML')
            database.update_last_checked(listing_id) # Mark as checked for this period
        except Exception as e:
            logger.error(f"Failed to send status check to {owner_id}: {e}")

# Health Check Server for local fallback (not used when run_webhook is active)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        return

def run_health_check_server():
    port = int(os.getenv("PORT", 7860))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health check server started on port {port}")
    server.serve_forever()

def main():
    database.init_db()
    
    async def post_init(application: Application):
        # Verify bot identity
        me = await application.bot.get_me()
        msg = f"BOT IDENTITY: Bot is running as @{me.username} (ID: {me.id})"
        logger.info(msg)
        print(msg)
        
        # Global catch-all for debugging
        async def debug_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
            d_msg = f"GLOBAL DEBUG: Received update: {update.to_dict()}"
            logger.info(d_msg)
            print(d_msg)
        
        application.add_handler(CallbackQueryHandler(debug_all), group=-1)

    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_ROLE: [
                MessageHandler(filters.Text(strings.ROLE_OWNER), owner_start),
                MessageHandler(filters.Text(strings.ROLE_SEEKER), seeker_start),
                MessageHandler(filters.Text(strings.HELP_BTN), help_command),
            ],
            # Landlord
            OWNER_MENU: [
                MessageHandler(filters.Text(strings.OWNER_ADD_NEW), owner_add_new),
                MessageHandler(filters.Text(strings.OWNER_MANAGE), owner_manage),
                MessageHandler(filters.Text(strings.BACK), start),
            ],
            OWNER_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_title)],
            OWNER_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_city)],
            OWNER_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_location)],
            OWNER_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_price)],
            OWNER_PHOTO: [
                MessageHandler(filters.PHOTO, owner_photo),
                CommandHandler("skip", owner_skip_photo),
                MessageHandler(filters.Text(strings.SKIP), owner_skip_photo),
                MessageHandler(filters.Text(strings.DONE), owner_done_photo),
            ],
            OWNER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_contact)],
            OWNER_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_submit_txid)],
            # Seeker
            SEEKER_MENU: [
                MessageHandler(filters.Text(strings.SEEKER_VIEW_ALL), view_all_listings),
                MessageHandler(filters.Text(strings.SEEKER_SEARCH), search_prompt),
                MessageHandler(filters.Text(strings.SEEKER_AI_SEARCH), seeker_ai_prompt),
                MessageHandler(filters.Text(strings.BACK), start),
            ],
            SEARCH_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), search_city_selected)],
            SEARCH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), execute_search)],
            AI_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), handle_ai_search)],
            ADMIN_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), broadcast_message)],
            # Timeout state — triggered on all states after 5 minutes of inactivity
            ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, timeout_handler)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel), 
            MessageHandler(filters.Text(strings.CANCEL), cancel),
            CommandHandler("start", start)
        ],
        conversation_timeout=900,  # 15 minutes
    )

    # Callback queries need to be registered first or in a separate group so conv_handler doesn't swallow them
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("admin", admin_stats))
    application.add_handler(CommandHandler("stats", admin_stats))
    application.add_handler(CommandHandler("admin_pending", admin_pending))
    application.add_handler(CommandHandler("pending", admin_pending))
    application.add_handler(CommandHandler("broadcast", broadcast_start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Schedule daily listings checks
    job_queue = application.job_queue
    if job_queue:
        # Expiry check at 3:00 AM
        job_queue.run_daily(lambda ctx: database.expire_old_listings(), time=__import__('datetime').time(hour=3, minute=0))
        # Status verify check at 10:00 AM
        job_queue.run_daily(send_status_checks, time=__import__('datetime').time(hour=10, minute=0))
    
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(msg="Exception while handling an update:", exc_info=context.error)
    application.add_error_handler(error_handler)
    
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.getenv("PORT", 7860))

    if WEBHOOK_URL:
        # Production: Use webhooks (faster, no polling overhead)
        logger.info(f"Starting bot in WEBHOOK mode on port {PORT}...")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
            secret_token=os.getenv("WEBHOOK_SECRET", ""),
        )
    else:
        # Local development: Use polling
        logger.info("No WEBHOOK_URL found. Starting bot in POLLING mode...")
        # Start health check server in background for local testing
        threading.Thread(target=run_health_check_server, daemon=True).start()
        
        logger.info("Bot is now polling for updates...")
        application.run_polling()

if __name__ == "__main__":
    main()
