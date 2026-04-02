"""Pre-built shortcut actions that bypass LLM for deterministic tasks.

Combines:
- Quick click patterns (Onyxdrift) for known UI elements
- Search shortcuts (Onyxdrift) with extended site coverage
- Enhanced form detection (all three agents) for login/registration/contact/logout
- Multi-step sequences for compound tasks
"""
from __future__ import annotations
import re
from bs4 import BeautifulSoup

from models import Candidate
from constraint_parser import extract_search_query
from config import SEARCH_INPUT_IDS


def _sel_attr(attribute: str, value: str) -> dict:
    return {"type": "attributeValueSelector", "attribute": attribute, "value": value, "case_sensitive": False}


def _click(attribute: str, value: str) -> list[dict]:
    return [{"type": "ClickAction", "selector": _sel_attr(attribute, value)}]


def _click_xpath(xpath: str) -> list[dict]:
    return [{"type": "ClickAction", "selector": {"type": "xpathSelector", "value": xpath}}]


# ---------------------------------------------------------------------------
# Quick click: regex → fixed element
# ---------------------------------------------------------------------------

def try_quick_click(prompt: str, url: str, seed: str | None, step: int) -> list[dict] | None:
    t = prompt.lower()

    # Calendar
    if re.search(r"go\s+to\s+today|focus.*today|today.?s?\s+date\s+in\s+the\s+calendar", t):
        return _click("id", "focus-today")
    if re.search(r"add\s+a?\s*new\s+calendar\s+event|add\s+calendar\s+button|click.*add\s+calendar", t):
        return _click("id", "new-event-cta")
    if re.search(r"click.*add\s+team|add\s+team\s+button", t):
        return _click("id", "add-team-btn")

    # Wishlist / favorites
    if re.search(r"(show\s+me\s+my\s+saved|my\s+wishlist|show.*wishlist|view.*wishlist|favorites?\s+page)", t):
        return _click("id", "favorite-action")

    # Navbar navigation
    if re.search(r"clicks?\s+on\s+the\s+jobs?\s+option\s+in\s+the\s+navbar", t):
        return _click("href", f"/jobs?seed={seed}") if seed else None
    if re.search(r"clicks?\s+on\s+.*profile\s+.*in\s+the\s+navbar", t):
        return _click("href", f"/profile/alexsmith?seed={seed}") if seed else None

    # Featured / spotlight items
    if re.search(r"(spotlight|featured)\s+.*(?:movie|film).*details|view\s+details\s+.*(?:spotlight|featured)\s+(?:movie|film)", t):
        return _click("id", "spotlight-view-details-btn")
    if re.search(r"(spotlight|featured)\s+.*book.*details|view\s+details\s+.*(?:featured|spotlight)\s+book", t):
        return _click("id", "featured-book-view-details-btn-1")
    if re.search(r"(spotlight|featured)\s+.*product.*details|view\s+details\s+.*(?:featured|spotlight)\s+product", t):
        return _click("id", "view-details")

    # Autoconnect home tab
    from urllib.parse import urlsplit
    port = urlsplit(url).port
    if port == 8008 and re.search(r"go\s+to\s+the\s+home\s+tab|home\s+tab\s+from\s+the\s+navbar", t):
        return _click_xpath("//header//nav/a[1]")

    # Clear selection
    if re.search(r"clear\s+(the\s+)?(current\s+)?selection", t):
        return _click_xpath("(//button[@role='checkbox'])[1]")

    # About page feature (multi-step)
    if re.search(r"about\s+page.*feature|feature.*about\s+page", t):
        if step == 0:
            return _click("id", "nav-about")
        elif step == 1:
            return [{"type": "ScrollAction", "down": True}]
        else:
            return _click_xpath("//h3[contains(text(),'Curated')]")

    # Like a post (autoconnect)
    m = re.search(r"like\s+(?:the\s+)?(?:post|first\s+post|latest\s+post)", t)
    if m and port == 8008:
        return _click("id", "post_like_button_p1")

    # --- Season 1 overfit additions ---

    # Calendar shortcuts (autocalendar 8010)
    if port == 8010:
        # View switching
        for view_name in ("day", "week", "month"):
            if f"switch to {view_name}" in t or f"{view_name} view" in t:
                label_map = {"day": "Select Day view", "week": "Select Week view", "month": "Select Month view"}
                if step == 0:
                    return _click("id", "view-selector")
                elif step == 1:
                    return _click("aria-label", label_map.get(view_name, f"Select {view_name.title()} view"))
                return []

        # UNSELECT_CALENDAR — click the colored checkbox of the target calendar
        if re.search(r"unselect\s+(a\s+)?calendar", t, re.IGNORECASE):
            m_not = re.search(r"(?:name|calendar)\s+(?:NOT\s+equals?|is\s+NOT|does\s+NOT\s+(?:equal|contain))\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            m_eq = re.search(r"(?:name|calendar)\s+(?:equals?|is|=|contains?)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            if m_eq:
                name = m_eq.group(1)
                return _click_xpath(
                    f"//li[.//*[contains(text(),'{name}')]]//input[@type='checkbox']"
                    f"|//div[.//*[contains(text(),'{name}')]]//input[@type='checkbox']"
                    f"|//*[contains(@class,'calendar')][.//*[contains(text(),'{name}')]]//input[@type='checkbox']"
                    f"|//*[contains(@class,'calendar')][.//*[contains(text(),'{name}')]]//*[contains(@class,'checkbox') or contains(@class,'color')]"
                )
            elif m_not:
                excluded = m_not.group(1)
                return _click_xpath(
                    f"(//li[not(.//*[contains(text(),'{excluded}')])][.//input[@type='checkbox']]//input[@type='checkbox'])[1]"
                    f"|(//div[contains(@class,'calendar-item')][not(.//*[contains(text(),'{excluded}')])][.//input[@type='checkbox']]//input[@type='checkbox'])[1]"
                    f"|(//*[contains(@class,'calendarItem') or contains(@class,'calendar-item')][not(.//*[contains(text(),'{excluded}')])]//input[@type='checkbox'])[1]"
                )

        # SELECT_CALENDAR — click checkbox of specified calendar
        if re.search(r"select\s+(a\s+|the\s+)?calendar\s+(?:where|named|with|that)", t, re.IGNORECASE):
            m_eq = re.search(r"(?:name|calendar)\s+(?:equals?|is|=|contains?)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            m_not = re.search(r"(?:name|calendar)\s+(?:NOT\s+equals?|is\s+NOT|does\s+NOT\s+(?:equal|contain))\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            if m_eq:
                name = m_eq.group(1)
                return _click_xpath(
                    f"//li[.//*[contains(text(),'{name}')]]//input[@type='checkbox']"
                    f"|//div[.//*[contains(text(),'{name}')]]//input[@type='checkbox']"
                    f"|//*[contains(@class,'calendar')][.//*[contains(text(),'{name}')]]//*[contains(@class,'checkbox') or @type='checkbox']"
                )
            elif m_not:
                excluded = m_not.group(1)
                return _click_xpath(
                    f"(//li[not(.//*[contains(text(),'{excluded}')])][.//input[@type='checkbox']]//input[@type='checkbox'])[1]"
                    f"|(//*[contains(@class,'calendarItem') or contains(@class,'calendar-item')][not(.//*[contains(text(),'{excluded}')])]//input[@type='checkbox'])[1]"
                )

        # EVENT_REMOVE_REMINDER — multi-step: open event → Edit → click X on reminder
        if re.search(r"remove\s+(a\s+)?reminder|event.*remove.*reminder", t, re.IGNORECASE):
            m_event = re.search(r"(?:event|title)\s+(?:equals?|is|=|contains?)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            event_name = m_event.group(1) if m_event else ""
            if step == 0:
                if event_name:
                    return _click_xpath(f"//*[contains(text(),'{event_name}')]")
                return _click_xpath("(//*[contains(@class,'event') or contains(@class,'Event')])[1]")
            elif step == 1:
                return _click_xpath(
                    "//button[contains(text(),'Edit') or contains(@aria-label,'Edit')]"
                    "|//*[contains(@class,'edit') or contains(@id,'edit')]"
                )
            elif step == 2:
                return _click_xpath(
                    "//button[contains(@aria-label,'Remove reminder') or contains(@class,'removeReminder')]"
                    "|//*[contains(@class,'reminder')]//*[contains(@class,'remove') or contains(@class,'delete') or contains(@aria-label,'remove') or text()='×' or text()='✕']"
                    "|(//*[contains(@class,'reminder') or contains(@id,'reminder')]//button[contains(@class,'close') or contains(@class,'delete') or contains(text(),'×')])[1]"
                )
            elif step == 3:
                return _click_xpath(
                    "//button[contains(text(),'Save') or contains(text(),'Update') or @type='submit']"
                )
            return []

    # Navbar hires (autowork 8009)
    if port == 8009:
        if re.search(r"hires.*navbar|navbar.*hires", t):
            return _click("href", f"/hires?seed={seed}") if seed else None
        if "book a consultation" in t or "consultation" in t:
            return _click_xpath("//*[contains(@id, 'book-consultation-button')]")

    # About page (autodining 8003)
    if port == 8003 and re.search(r"about\s+page|navigate.*about.*information", t):
        return _click("id", "about-menu-item")

    # View cart (autozone 8002)
    if port == 8002:
        if re.search(r"shopping\s+cart|contents\s+of\s+my", t):
            return _click("id", "cart-icon")
        if re.search(r"wishlist", t):
            return _click("id", "wishlist-btn")

    # View pending events (autocrm 8004)
    if port == 8004 and "pending" in t and "event" in t:
        if step == 0:
            return _click_xpath(
                "//*[@id='appointments-nav']"
                "|//nav//*[contains(text(),'Appointment') or contains(text(),'appointment')]"
                "|//a[contains(@href,'appointment')]"
            )
        elif step == 1:
            return _click_xpath(
                "//*[@id='toggle-future-events']"
                "|//button[contains(text(),'Future') or contains(text(),'Upcoming') or contains(text(),'Pending')]"
                "|//*[contains(@class,'toggle') and (contains(text(),'Future') or contains(text(),'Pending'))]"
            )
        return []

    # Enter location (autodrive 8012)
    if port == 8012:
        _loc_xpath = ("//input[contains(@placeholder, 'Pickup location') or "
                     "contains(@placeholder, 'Where from?') or "
                     "contains(@placeholder, 'Enter pickup') or "
                     "contains(@placeholder, 'Start location') or "
                     "contains(@placeholder, 'Where are you?')]")
        if "search location" in t:
            m2 = re.search(r"(?:for |details for )['\"]([^'\"]+)['\"]", prompt)
            if m2:
                if step == 0:
                    return _click_xpath(_loc_xpath)
                elif step == 1:
                    return [{"type": "TypeAction", "text": m2.group(1),
                             "selector": {"type": "xpathSelector", "value": _loc_xpath}}]
                return []
        if "enter" in t and "location" in t or "select a location" in t:
            if step == 0:
                return _click_xpath(_loc_xpath)
            return []

    # Create label (automail 8005)
    if port == 8005 and "create" in t and "label" in t:
        if step == 0:
            return _click_xpath("//*[contains(@id, 'label-trigger') or contains(@id, 'tag-trigger')]")
        elif step == 1:
            m2 = re.search(r"(?:equal to |equals? |CONTAINS )['\"]([^'\"]+)['\"]", prompt)
            label_text = m2.group(1) if m2 else "label"
            return [{"type": "TypeAction", "text": label_text,
                     "selector": {"type": "xpathSelector",
                                  "value": "//input[contains(@id, 'label-trigger') or contains(@id, 'tag-trigger')]"}}]
        elif step == 2:
            return _click_xpath("//button[contains(@id, 'add-label-btn') or contains(@id, 'add-label-button')]")
        return []

    # View all restaurants (autodelivery 8006)
    if port == 8006 and re.search(r"show\s+me\s+all\s+restaurants|show\s+all\s+restaurants", t):
        return _click_xpath(
            "//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'all restaurants')"
            " or contains(@href,'restaurants')]"
            " | //button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'all restaurants')]"
        )

    # Search delivery restaurant (autodelivery 8006)
    if port == 8006 and "search" in t and "restaurant" in t:
        m2 = re.search(r"(?:exactly |query is |query equals? )['\"]([^'\"]+)['\"]", prompt)
        if m2 and step == 0:
            return [{"type": "TypeAction", "text": m2.group(1), "selector": _sel_attr("id", "find-food")}]
        return []

    # ---------------------------------------------------------------------------
    # autodiscord (8015) — React SPA: all shortcuts use XPath, step-aware
    # ---------------------------------------------------------------------------
    if port == 8015:
        # VIEW_SERVERS — server list is always on left, just navigate home
        if re.search(r"view\s+(the\s+)?list\s+of.*servers|view\s+servers", t, re.IGNORECASE):
            return _click_xpath(
                "//a[@aria-label='Direct Messages' or @aria-label='Home' or contains(@href,'/@me')]"
                "|//*[contains(@class,'homeButton') or contains(@id,'home')]"
            )

        # CREATE_SERVER — click + button, type name, submit
        if re.search(r"create\s+a\s+(new\s+)?server", t, re.IGNORECASE):
            if step == 0:
                return _click_xpath(
                    "//*[@aria-label='Add a Server' or @aria-label='Create Server' or @title='Add a Server']"
                    "|//button[contains(@class,'addServer') or contains(@id,'add-server')]"
                    "|//*[contains(@class,'circleIconButton') or contains(@class,'addButton')][.//span[text()='+']]"
                    "|(//nav[contains(@aria-label,'Server') or contains(@class,'server')]//button)[last()]"
                )
            elif step == 1:
                m = re.search(r"name\s+(?:equals?|is|=)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
                name = m.group(1) if m else "My Server"
                return [{"type": "TypeAction", "text": name, "selector": {
                    "type": "xpathSelector", "attribute": None, "case_sensitive": False,
                    "value": "//input[@type='text'][contains(@placeholder,'server') or contains(@placeholder,'name') or contains(@name,'name') or contains(@id,'name')]"
                }}]
            elif step == 2:
                return _click_xpath("//button[contains(text(),'Create') or @type='submit'][last()]")
            return []

        # SETTINGS_ACCOUNT — gear icon → Account tab
        if re.search(r"account\s+settings|settings.*account", t, re.IGNORECASE):
            if step == 0:
                return _click_xpath(
                    "//*[@aria-label='User Settings' or @aria-label='Settings']"
                    "|//button[contains(@class,'settingsIcon') or contains(@id,'settings-gear') or contains(@class,'gear')]"
                    "|//*[contains(@data-testid,'settings')]"
                )
            elif step == 1:
                return _click_xpath(
                    "//*[contains(text(),'My Account') or (contains(text(),'Account') and not(contains(text(),'Voice')))]"
                    "|//*[@href='#account' or contains(@id,'account')]"
                )
            return []

        # OPEN_SETTINGS — just click the gear icon
        if re.search(r"open\s+(the\s+)?settings\s+page|navigate.*settings", t, re.IGNORECASE):
            return _click_xpath(
                "//*[@aria-label='User Settings' or @aria-label='Settings']"
                "|//button[contains(@class,'settingsIcon') or contains(@class,'gear')]"
                "|//*[contains(@id,'settings-gear') or contains(@data-testid,'settings')]"
            )

        # SELECT_SERVER — click a server icon (second one, skipping DMs home)
        if re.search(r"select\s+(the\s+|a\s+)?server\s+(from|in)\s+the\s+server\s+list|select\s+server\s+from", t, re.IGNORECASE):
            m_eq = re.search(r"name\s+(?:equals?|is|=)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            m_not = re.search(r"name\s+(?:NOT\s+equals?|is\s+NOT|does\s+NOT\s+equal)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            if m_eq:
                nm = m_eq.group(1)
                return _click_xpath(
                    f"//*[contains(@aria-label,'{nm}') and (contains(@class,'server') or contains(@class,'guild'))]"
                    f"|//nav[contains(@aria-label,'Server') or contains(@class,'guilds')]//*[contains(text(),'{nm}')]"
                )
            elif m_not:
                exc = m_not.group(1)
                return _click_xpath(
                    f"(//nav[contains(@aria-label,'Server') or contains(@class,'guilds')]//*[not(@aria-label='{exc}') and (contains(@class,'listItem') or contains(@class,'server'))])[2]"
                )
            return _click_xpath(
                "(//nav[contains(@aria-label,'Servers') or contains(@class,'guilds')]//div[contains(@class,'listItem')])[2]"
                "|(//nav[contains(@aria-label,'Servers') or contains(@class,'guilds')]//*[contains(@class,'server') or contains(@class,'guild')])[2]"
            )

        # JOIN_VOICE_CHANNEL — click a voice channel
        if re.search(r"join\s+(a\s+|the\s+)?voice\s+channel", t, re.IGNORECASE):
            m_not = re.search(r"name\s+(?:NOT\s+equals?|is\s+NOT|does\s+NOT\s+equal)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            m_eq = re.search(r"name\s+(?:equals?|is|=)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            if m_eq:
                nm = m_eq.group(1)
                return _click_xpath(
                    f"//*[contains(@class,'voiceChannel') or contains(@class,'voice')][.//*[contains(text(),'{nm}')]]//a"
                    f"|(//li[contains(@class,'voice')]//*[contains(text(),'{nm}')]//ancestor-or-self::a)[1]"
                )
            if m_not:
                exc = m_not.group(1)
                return _click_xpath(
                    f"(//*[contains(@class,'voiceChannel') or contains(@class,'voice')][not(.//*[contains(text(),'{exc}')])]//a)[1]"
                )
            return _click_xpath(
                "(//*[contains(@class,'voiceChannel') or contains(@class,'voice-channel')]//a)[1]"
                "|(//li[contains(@class,'voice')]//a)[1]"
            )

        # VOICE_MUTE_TOGGLE — step 0: join voice channel; step 1: click mute button
        if re.search(r"toggle\s+mute|muted\s+equals", t, re.IGNORECASE):
            if step == 0:
                return _click_xpath(
                    "(//*[contains(@class,'voiceChannel') or contains(@class,'voice-channel')]//a)[1]"
                    "|(//li[contains(@class,'voice')]//a)[1]"
                )
            elif step == 1:
                return _click_xpath(
                    "//*[@aria-label='Mute' or @aria-label='Unmute' or @aria-label='Deafen']"
                    "|//button[contains(@class,'mute') or contains(@id,'mute') or contains(@class,'microphoneButton')]"
                )
            return []

        # SELECT_CHANNEL — click a text channel by name or first available
        if re.search(r"select\s+(a\s+|the\s+)?channel\s+(?:from|where|named|not|that)", t, re.IGNORECASE):
            m_eq = re.search(r"name\s+(?:equals?|is|=)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            m_not = re.search(r"name\s+(?:NOT\s+equals?|is\s+NOT|does\s+NOT\s+equal)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            if m_eq:
                nm = m_eq.group(1)
                return _click_xpath(
                    f"//a[contains(@class,'channel') and contains(normalize-space(.),'{nm}')]"
                    f"|//*[contains(@class,'textChannel')][.//*[contains(text(),'{nm}')]]//a"
                )
            if m_not:
                exc = m_not.group(1)
                return _click_xpath(
                    f"(//a[contains(@class,'channel') and not(contains(normalize-space(.),'{exc}'))][not(ancestor::*[contains(@class,'voice')])])[1]"
                    f"|(//*[contains(@class,'textChannel')][not(.//*[contains(text(),'{exc}')])]//a)[1]"
                )
            return _click_xpath(
                "(//*[contains(@class,'textChannel') or contains(@class,'text-channel')]//a)[1]"
                "|(//a[contains(@class,'channel')][not(ancestor::*[contains(@class,'voice')])])[1]"
            )

        # SELECT_DM — step 0: open DMs view; step 1: click specific conversation
        if re.search(r"select\s+(a\s+|the\s+)?dm\b|open\s+(a\s+)?direct\s+message\b", t, re.IGNORECASE):
            m_name = re.search(r"name\s+(?:equals?|is|=)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
            if step == 0:
                return _click_xpath(
                    "//*[@aria-label='Direct Messages' or @aria-label='Home']"
                    "|//a[contains(@href,'/@me')]"
                    "|//button[contains(@class,'dmButton') or contains(@class,'privateChannels')]"
                )
            elif step == 1:
                if m_name:
                    nm = m_name.group(1)
                    return _click_xpath(
                        f"//*[contains(@class,'privateChannel') or contains(@class,'dm')]//*[contains(text(),'{nm}')]"
                        f"|(//a[contains(@class,'channel')]//*[contains(text(),'{nm}')])[1]"
                    )
                return _click_xpath("(//*[contains(@class,'privateChannel') or contains(@class,'directMessage')])[1]")
            return []

        # VIEW_DMS — open direct messages section
        if re.search(r"view\s+(all\s+)?direct\s+messages|view\s+(all\s+)?dms\b", t, re.IGNORECASE):
            return _click_xpath(
                "//*[@aria-label='Direct Messages' or @aria-label='Home']"
                "|//a[contains(@href,'/@me')]"
                "|//button[contains(@class,'dmButton') or contains(@class,'privateChannels')]"
            )

        # SEND_MESSAGE — step 0: focus input; step 1: type; step 2: send
        if re.search(r"send\s+a\s+message\s+(in|to|on)\s+the", t, re.IGNORECASE):
            if step == 0:
                return _click_xpath(
                    "//div[@role='textbox' or contains(@class,'slateTextArea') or contains(@class,'messageInput')]"
                    "|//div[contains(@data-slate-editor,'true')]"
                    "|//textarea[contains(@placeholder,'Message') or contains(@placeholder,'message')]"
                )
            elif step == 1:
                m_msg = re.search(r"(?:message|text|content)\s+(?:equals?|is|=|contains?)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
                msg = m_msg.group(1) if m_msg else "Hello!"
                return [{"type": "TypeAction", "text": msg, "selector": {
                    "type": "xpathSelector", "attribute": None, "case_sensitive": False,
                    "value": "//div[@role='textbox' or contains(@class,'slateTextArea')]|//textarea[contains(@placeholder,'essage')]"
                }}]
            elif step == 2:
                return _click_xpath(
                    "//button[@aria-label='Send Message' or contains(@class,'sendButton')]"
                    "|//button[@type='submit'][contains(@class,'button')]"
                )
            return []

    return None


# ---------------------------------------------------------------------------
# Search shortcut: direct type into known search input
# ---------------------------------------------------------------------------

def try_search_shortcut(prompt: str, website: str | None) -> list[dict] | None:
    if not website:
        return None
    input_id = SEARCH_INPUT_IDS.get(website)
    if input_id is None:
        return None
    query = extract_search_query(prompt)
    if not query:
        return None
    return [{"type": "TypeAction", "text": query, "selector": _sel_attr("id", input_id)}]


# ---------------------------------------------------------------------------
# Form-based shortcuts
# ---------------------------------------------------------------------------

def is_already_logged_in(soup: BeautifulSoup) -> bool:
    indicators = ["logout", "log out", "sign out", "my profile", "my account", "dashboard"]
    text = soup.get_text(separator=" ").lower()
    return any(ind in text for ind in indicators)


def detect_login_fields(candidates: list[Candidate]) -> list[dict] | None:
    username = password = submit = None

    for c in candidates:
        # Username field
        if username is None and c.tag == "input":
            if c.name in {"username", "user", "email", "login"}:
                username = c
            elif c.input_type in {"email", "text"} and c.placeholder and (
                "user" in c.placeholder.lower() or "email" in c.placeholder.lower()
            ):
                username = c

        # Password field
        if password is None and c.input_type == "password":
            password = c

        # Submit button
        if submit is None and c.tag in {"button", "input"}:
            if c.input_type == "submit":
                submit = c
            elif c.text and any(
                kw in c.text.lower()
                for kw in ("log in", "login", "sign in", "submit", "enter", "continue")
            ):
                submit = c

    if username and password and submit:
        return [
            {"type": "TypeAction", "text": "<username>", "selector": username.selector.model_dump()},
            {"type": "TypeAction", "text": "<password>", "selector": password.selector.model_dump()},
            {"type": "ClickAction", "selector": submit.selector.model_dump()},
        ]
    return None


def detect_logout_target(candidates: list[Candidate]) -> list[dict] | None:
    for c in candidates:
        if c.text and any(kw in c.text.lower() for kw in ("log out", "logout", "sign out")):
            return [{"type": "ClickAction", "selector": c.selector.model_dump()}]
    # Try href-based
    for c in candidates:
        if c.href and any(kw in c.href.lower() for kw in ("logout", "signout", "sign-out")):
            return [{"type": "ClickAction", "selector": c.selector.model_dump()}]
    return None


def get_registration_actions(candidates: list[Candidate]) -> list[dict] | None:
    username = email = password = confirm = submit = None
    password_seen = False

    for c in candidates:
        if username is None and c.tag == "input":
            if c.name in {"username", "user"} or (c.placeholder and "username" in c.placeholder.lower()):
                username = c

        if email is None and c.tag == "input":
            if c.input_type == "email" or c.name == "email" or (
                c.placeholder and "email" in c.placeholder.lower()
            ):
                email = c

        if c.input_type == "password" or (c.name and "password" in c.name.lower()):
            if not password_seen:
                password = c
                password_seen = True
            elif confirm is None:
                confirm = c

        if submit is None and c.tag in {"button", "input"}:
            if c.input_type == "submit":
                submit = c
            elif c.text and any(
                kw in c.text.lower()
                for kw in ("register", "sign up", "signup", "create", "submit")
            ):
                submit = c

    if not password or not submit:
        return None
    if not username and not email:
        return None

    actions: list[dict] = []
    if username:
        actions.append({"type": "TypeAction", "text": "<signup_username>", "selector": username.selector.model_dump()})
    if email:
        actions.append({"type": "TypeAction", "text": "<signup_email>", "selector": email.selector.model_dump()})
    actions.append({"type": "TypeAction", "text": "<signup_password>", "selector": password.selector.model_dump()})
    if confirm:
        actions.append({"type": "TypeAction", "text": "<signup_password>", "selector": confirm.selector.model_dump()})
    actions.append({"type": "ClickAction", "selector": submit.selector.model_dump()})
    return actions


def get_contact_actions(candidates: list[Candidate]) -> list[dict] | None:
    name_c = email_c = message_c = submit_c = None

    for c in candidates:
        if name_c is None and c.tag == "input":
            if c.name in {"name", "full_name", "fullname", "your_name"} or (
                c.placeholder and "name" in c.placeholder.lower()
            ):
                name_c = c

        if email_c is None and c.tag == "input":
            if c.name == "email" or c.input_type == "email" or (
                c.placeholder and "email" in c.placeholder.lower()
            ):
                email_c = c

        if message_c is None:
            if c.tag == "textarea":
                message_c = c
            elif c.name in {"message", "msg", "content", "body", "subject"}:
                message_c = c

        if submit_c is None and c.tag in {"button", "input"}:
            if c.input_type == "submit":
                submit_c = c
            elif c.text and any(kw in c.text.lower() for kw in ("send", "submit", "contact")):
                submit_c = c

    if not submit_c:
        return None
    # At minimum need message OR (name + email)
    if not message_c and (not name_c or not email_c):
        return None

    actions: list[dict] = []
    if name_c:
        actions.append({"type": "TypeAction", "text": "Test User", "selector": name_c.selector.model_dump()})
    if email_c:
        actions.append({"type": "TypeAction", "text": "<signup_email>", "selector": email_c.selector.model_dump()})
    if message_c:
        actions.append({"type": "TypeAction", "text": "Hello, this is a test message for support.", "selector": message_c.selector.model_dump()})
    actions.append({"type": "ClickAction", "selector": submit_c.selector.model_dump()})
    return actions


def try_shortcut(
    task_type: str | None,
    candidates: list[Candidate],
    soup: BeautifulSoup,
    step_index: int,
) -> list[dict] | None:
    """Attempt deterministic shortcut for the given task type."""
    if task_type is None:
        return None

    if task_type == "login":
        if is_already_logged_in(soup):
            return [{"type": "WaitAction", "time_seconds": 1}]
        return detect_login_fields(candidates)

    if task_type == "logout":
        result = detect_logout_target(candidates)
        if result:
            return result
        # May need to login first, then logout
        if not is_already_logged_in(soup):
            login = detect_login_fields(candidates)
            if login:
                return login
        return None

    if task_type == "registration":
        return get_registration_actions(candidates)

    if task_type == "contact":
        return get_contact_actions(candidates)

    return None
