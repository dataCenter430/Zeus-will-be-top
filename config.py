"""Central configuration: site knowledge, playbooks, constants."""
from __future__ import annotations
from urllib.parse import urlsplit

# ---------------------------------------------------------------------------
# Port → project mapping (IWA sandbox)
# ---------------------------------------------------------------------------
PORT_TO_PROJECT: dict[int, str] = {
    8000: "autocinema",
    8001: "autobooks",
    8002: "autozone",
    8003: "autodining",
    8004: "autocrm",
    8005: "automail",
    8006: "autodelivery",
    8007: "autolodge",
    8008: "autoconnect",
    8009: "autowork",
    8010: "autocalendar",
    8011: "autolist",
    8012: "autodrive",
    8013: "autohealth",
    8014: "autostats",
    8015: "autodiscord",
}


def detect_website(url: str) -> str | None:
    port = urlsplit(url).port
    return PORT_TO_PROJECT.get(port) if port else None


# ---------------------------------------------------------------------------
# Selector priority (stable → fragile)
# ---------------------------------------------------------------------------
SELECTOR_PRIORITY: list[str] = [
    "id", "data-testid", "href", "aria-label", "name",
    "placeholder", "title", "text",
]

# ---------------------------------------------------------------------------
# LLM defaults
# ---------------------------------------------------------------------------
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 350
PAGE_IR_MAX_TOKENS = 1400
PAGE_IR_CHAR_LIMIT = PAGE_IR_MAX_TOKENS * 4

# ---------------------------------------------------------------------------
# Agent limits
# ---------------------------------------------------------------------------
AGENT_MAX_STEPS = 10
MAX_TASK_STATES = 8

# ---------------------------------------------------------------------------
# Per-website hints (detailed UI structure per site)
# ---------------------------------------------------------------------------
WEBSITE_HINTS: dict[str, str] = {
    "autocinema": (
        "SITE: Movie/film database. NAV: Films list, Login/Register, Admin panel (when logged in). "
        "Film cards show title, year, genre, director, duration. "
        "Click film -> detail page with Watch Trailer button, Add to Watchlist button, Share button, Comments section. "
        "Admin: Add Film, Edit Film, Delete Film (requires login with 'user '/'Passw0rd!'). "
        "Registration: username='newuser ', email='newuser @gmail.com', password='Passw0rd!'."
    ),
    "autobooks": (
        "SITE: Book store. NAV: Books, Cart icon, Login/Register. "
        "Books have title, author, genres, year, page_count, rating, price. "
        "Login/Register with placeholder credentials (' '/' '). "
        "Book detail: Add to Cart, Add to Wishlist, Open Preview buttons. "
        "Admin: Add Book, Edit Book, Delete Book. Cart icon top-right."
    ),
    "autozone": (
        "SITE: E-commerce store. NAV: Products grid, Category sidebar/filter, Cart icon, Wishlist. "
        "Products have name, brand, price, description, rating. "
        "Category filter on left sidebar (click to filter by category). "
        "Product card: Add to Cart, Add to Wishlist, Share buttons. "
        "Cart page: shows items, total, Proceed to Checkout button. "
        "Carousel sections: scroll left/right buttons on carousel cards."
    ),
    "autodining": (
        "SITE: Restaurant reservation/booking. NAV: Restaurants, About, Help/FAQ, Contact. "
        "Main page: search bar, country selector dropdown, date/time pickers, people/guest count. "
        "Guest dropdown: click on people/guest count to open dropdown and select number. "
        "Restaurant cards: click to view details. "
        "Help/FAQ page: expandable FAQ items. "
        "About page: feature cards (Trusted reviews, etc.). "
        "Contact form: name, email, message, subject fields."
    ),
    "autocrm": (
        "SITE: Legal case management + calendar. NAV: Dashboard, Matters, Clients, Calendar. "
        "Matters list: sortable columns. Add New Matter button. "
        "Clients list: Add New Client button (name, email, status, matters). "
        "Calendar: Add event button, date/time/label/event_type fields. "
        "Settings: Change user name option. "
        "Sort by column: click column header or sort button."
    ),
    "automail": (
        "SITE: Webmail client. NAV: Inbox, Drafts, Sent, Spam, Templates folder tabs. "
        "Email list: shows from_email, subject, date, is_starred, is_important flags. "
        "Actions per email: Star, Archive, Mark as Spam, Delete, Forward, Reply. "
        "Select email: checkbox. Select all: top checkbox. Clear selection: deselect all. "
        "Important: click flag/important icon. "
        "Templates tab: list of templates with template_name, subject, to fields. "
        "Template actions: Select (use it), Send, Save as Draft. "
        "Pagination: Next/Previous page arrows at bottom of email list."
    ),
    "autodelivery": (
        "SITE: Food delivery app. NAV: Restaurants list, Cart, Orders. "
        "Restaurant cards: name, cuisine, rating, description. Click to view restaurant detail. "
        "Restaurant detail: menu items with size, price, quantity selector. Add to cart. "
        "Cart page: shows items with preferences (dietary), size, quantity, price, restaurant name. "
        "Cart: Dropoff preference selector (Hand it to me / Leave at door / Text when arriving). "
        "Delivery priority: Normal/Priority/Scheduled option. "
        "Checkout: proceed to checkout button. "
        "Pagination: next/previous page for restaurant list. "
        "View all restaurants: click All Restaurants or similar nav link."
    ),
    "autolodge": (
        "SITE: Hotel/lodging booking (Airbnb-style). Shows listing cards. "
        "Listing card/detail: title, host_name, location, price/night, rating, reviews count, amenities list, guests. "
        "Guest selector: +/- buttons or dropdown to set number of guests. "
        "Actions: Reserve/Book Now -> payment form, Add to Wishlist, Submit Review. "
        "Payment form fields: card_number, expiration (MM/YY), cvv, zipcode, country. "
        "Payment methods: Credit card, PayPal, Bank transfer. "
        "Search: search bar for hotel name/location. "
        "Filters: rating, region/country, price range. "
        "Review form: rating stars + text area."
    ),
    "autoconnect": (
        "SITE: Professional network (LinkedIn-style). NAV: Feed, Jobs, People, Company Pages. "
        "Feed: posts with text, author, Like/Comment buttons. Comment: text field + submit. "
        "Jobs section: job listings with title, company, location, Apply button. "
        "My Applications: list with status (Pending/Accepted/Rejected), Withdraw/Cancel button. "
        "Company Pages: Follow/Unfollow button on each page. "
        "People/Users: search bar for users. "
        "Profile: Edit profile (bio, skills, photo). "
        "Back to Jobs: breadcrumb or Back button from job detail."
    ),
    "autowork": (
        "SITE: Freelancer hiring platform. NAV: Jobs, Hires, Experts/Browse. "
        "Expert/Consultant cards: name, role, country, rating, price. "
        "Expert actions: Hire Now button, Hire Later button, View Profile. "
        "Hire Later page: list of saved experts with Remove button. "
        "Job Posting: Post a Job / + button -> form with title, description, rate_from, rate_to, project size. "
        "Job posting form: title field, description, rate range, project size (Small/Medium/Large). "
        "Close job posting window: X/Cancel button on job posting modal. "
        "Search skills: search bar for skills. "
        "NAV: Jobs link, Hires link in navbar. "
        "Hiring Team: section showing team members."
    ),
    "autocalendar": (
        "SITE: Calendar app (Google Calendar-style). "
        "View buttons: Day, 5-day (work week), Week, Month -- click to switch view. "
        "Left sidebar: list of calendars with + button to add new calendar. "
        "Add New Calendar modal: name + description fields. "
        "Events: click on time slot or + button to add event. "
        "Event form: title, date, time, visibility (Public/Private/Default), reminders (minutes), "
        "meeting_link, attendees (email), all_day toggle, recurrence, calendar, description, busy. "
        "Event actions: Edit, Delete. "
        "Attendees: add attendee email field in event edit form."
    ),
    "autolist": (
        "SITE: Task management (Trello/Monday-style). "
        "Tasks list: each task has name, description, date, priority (1=High/2=Medium/3=Low), status. "
        "Add Task button: + or 'Add Task' button to create new task. "
        "Task actions: Edit (pencil icon) -> modal, Delete (trash icon) -> confirm. "
        "Edit task modal: name, description, date, priority fields. "
        "Team tab/section: list of team members with name, role. "
        "Add member: search by name and add. "
        "Assign role: dropdown next to member name."
    ),
    "autodrive": (
        "SITE: Ride-sharing app (Uber-style). "
        "Main page: Location (pickup) input + Destination input fields. "
        "Available rides: list with ride_name, price, estimated time, scheduled. "
        "Reserve button on each ride card. "
        "Date picker: select trip date (calendar widget). "
        "Time picker: select trip time. "
        "Search location: type in the search/destination input box. "
        "Reservation history: list of upcoming/past rides with Cancel button. "
        "Cancel: click Cancel on a specific reservation. "
        "Next pickup: shows scheduled pickup details."
    ),
    "autohealth": (
        "SITE: Medical/healthcare platform. NAV: Doctors, Appointments, Medical Records/Analysis. "
        "Doctor cards: doctor_name, speciality, rating, consultation_fee, language. "
        "Doctor card actions: View Profile, Book Appointment, Contact Doctor. "
        "Doctor profile detail: full info, education section. "
        "Appointment form: doctor_name, speciality, date, time fields. "
        "Quick appointment form: speciality, patient_name, patient_email. "
        "Medical Records/Analysis: searchable list with record_title, doctor_name, record_type, date. "
        "Search: filter fields for doctor_name, speciality, record_title, etc. "
        "Contact doctor form: opens when Contact button clicked on doctor card."
    ),
    "autostats": (
        "SITE: Bittensor analytics. Subnet cards: favorite with star/heart icon. "
        "WALLET: 'Connect Wallet' button in header → modal → select wallet type (Polkadot.js/MetaMask). "
        "BLOCKS: Blocks section in nav → table of blocks with hash, number, timestamp, transactions. "
        "NAV: Subnets, Validators, Miners, Dashboard, Blocks. "
        "Subnet fields: subnet_name, subnet_id, description, emission, registration_cost. "
        "Validator/Miner: name, stake, rank, trust, emission. Export: download button."
    ),
    "autodiscord": (
        "SITE: Discord-style chat application. LEFT SIDEBAR: server list (icons), channel list per server. "
        "Channel types: text channels (#), voice channels (speaker icon). "
        "Voice channel: Join button, Mute/Unmute toggle button, Deafen/Undeafen toggle button. "
        "Mute button: microphone icon in voice controls bar at bottom of channel sidebar or in voice panel. "
        "When muted, mute icon shows slash-through; click to unmute (set muted=False). "
        "When unmuted, click to mute (set muted=True). "
        "MAIN PANEL: message list with author, timestamp, content. "
        "Message actions: Edit, Delete, Pin, React (emoji picker). "
        "Message input: text field at bottom of main panel. "
        "Server management: server name dropdown -> Server Settings. "
        "User search: search bar in member list or top bar. "
        "Channel actions: Create Channel (+), Delete Channel, Edit Channel in server settings."
    ),
}

# ---------------------------------------------------------------------------
# Task playbooks (130+ step-by-step guides per task type)
# ---------------------------------------------------------------------------
TASK_PLAYBOOKS: dict[str, str] = {
    "REGISTRATION": "PLAYBOOK: 1) Find and click Register/Sign Up link in navbar or on homepage. 2) On the registration form page: type <signup_username> into username field, type <signup_email> into email field. 3) Type <signup_password> into password field (and confirm password field if present). 4) Click Submit/Register button. Use placeholder tokens exactly as shown.",
    "LOGIN": "PLAYBOOK: 1) Navigate to login page. 2) Type username into username/email field EXACTLY as given. 3) Type password into password field EXACTLY as given. 4) Click login/sign-in submit button.",
    "LOGIN_THEN_LOGOUT": "PLAYBOOK: 1) Navigate to login page. 2) Type username exactly. 3) Type password exactly. 4) Click login submit. 5) After login, find logout/sign-out button (often in nav/profile menu). 6) Click logout.",
    "LOGIN_THEN_LIST_ACTION": "PLAYBOOK: 1) Login (navigate to login, fill credentials, submit). 2) Search or browse to find the specific item matching the criteria. 3) Navigate to that item's detail page. 4) Click the add-to-watchlist/reading-list/cart button, or remove button.",
    "LOGIN_THEN_COMMENT": "PLAYBOOK: 1) Login (navigate to login, fill credentials, submit). 2) Find and navigate to the specific item. 3) Find the comment/review form on the detail page. 4) Type the comment text. 5) Submit.",
    "LOGIN_THEN_ADD_ITEM": "PLAYBOOK: 1) Login (navigate to login, fill credentials, submit). 2) Navigate to admin or add-item page (look for Admin/Add Film/Add Book in nav). 3) Fill ALL fields with EXACT values from task. 4) Submit.",
    "LOGIN_THEN_EDIT_ITEM": "PLAYBOOK: 1) Login. 2) Navigate to item list page (admin or main list). 3) Find the specific item matching the search/filter criteria. 4) Click Edit. 5) Update the specified fields EXACTLY. 6) Submit.",
    "LOGIN_THEN_DELETE_ITEM": "PLAYBOOK: 1) Login. 2) Navigate to item list. 3) Find the specific item. 4) Click Delete. 5) Confirm deletion if prompted.",
    "LOGIN_THEN_EDIT_PROFILE": "PLAYBOOK: 1) Login. 2) Navigate to profile/account/settings page. 3) Update the specified fields EXACTLY. 4) Save.",
    "LOGIN_THEN_PURCHASE": "PLAYBOOK: 1) Login. 2) Find the item and add to cart. 3) Navigate to cart/checkout. 4) Complete checkout form. 5) Submit order.",
    "SEARCH_ITEM": "PLAYBOOK: 1) Find the search bar on the page. 2) Type the search query EXACTLY as given in the task. 3) Submit search (press Enter or click search button). Do NOT modify the search query.",
    "FILTER_ITEM": "PLAYBOOK: 1) Find filter controls on the page. 2) Select/type the filter criteria EXACTLY as specified. 3) Apply the filter.",
    "NAVIGATE_DETAIL": "PLAYBOOK: 1) Browse or search for items. 2) Use list_cards or list_links tool to find item matching ALL criteria. 3) Click/navigate to that item's detail page. If you need to filter by criteria, use search or filter controls first.",
    "SHARE_ITEM": "PLAYBOOK: 1) Navigate to the specific item detail page. 2) Find the Share button/icon. 3) Click it.",
    "WATCH_TRAILER": "PLAYBOOK: 1) Navigate to the specific film/movie detail page. 2) Find the Watch Trailer or play button. 3) Click it.",
    "FILM_DETAIL": "PLAYBOOK: 1) On AutoCinema, browse the movie list. 2) Find a movie matching ALL TASK_CONSTRAINTS. 3) Click on that movie to open its detail page.",
    "SEARCH_FILM": "PLAYBOOK: 1) On AutoCinema, find the search bar. 2) Type a movie title that is NOT the excluded term. 3) Submit the search.",
    "OPEN_PREVIEW": "PLAYBOOK: 1) Navigate to the specific book detail page. 2) Find the Open Preview button. 3) Click it.",
    "ADD_BOOK": "PLAYBOOK: 1) On AutoBooks, login first if credentials provided. 2) Find the Add Book button/link. 3) Fill in the book form. 4) Submit the form.",
    "ADD_COMMENT_BOOK": "PLAYBOOK: 1) On AutoBooks, find the book whose name CONTAINS the specified title. 2) Open that book's detail page. 3) Find the comments section. 4) Fill in commenter name and message. 5) Submit the comment.",
    "ADD_TO_CART": "PLAYBOOK: 1) Find and navigate to the specific book/item. 2) Click Add to Cart button.",
    "REMOVE_FROM_CART": "PLAYBOOK: 1) Navigate to the cart page. 2) Find the specific item in cart. 3) Click Remove/Delete.",
    "VIEW_CART": "PLAYBOOK: 1) Navigate to the cart page (look for Cart icon in nav).",
    "PURCHASE": "PLAYBOOK: 1) Add the item to cart. 2) Navigate to cart. 3) Click checkout/purchase button. 4) Fill out purchase form. 5) Submit.",
    "CONTACT": "PLAYBOOK: 1) Navigate to the Contact page. 2) Fill in name, email, message fields with EXACT values. 3) Submit the form.",
    "ADD_COMMENT": "PLAYBOOK: 1) Navigate to the specific item detail page. 2) Find the comment/review form. 3) Type the comment EXACTLY as specified. 4) Submit.",
    "LIST_ACTION": "PLAYBOOK: 1) Navigate to the item detail page. 2) Find the watchlist/reading-list button. 3) Click add or remove.",
    "SEARCH_LOCATION": "PLAYBOOK: 1) Find the search/destination input field. 2) Click it to focus. 3) Type the destination EXACTLY as given. 4) Click the matching result. 5) Submit/confirm if needed.",
    "RESERVE_RIDE": "PLAYBOOK: 1) Browse available rides. 2) Use list_cards to see all rides. 3) Find the ride matching ALL TASK_CONSTRAINTS. 4) Click Reserve on the matching ride.",
    "CANCEL_RESERVATION": "PLAYBOOK: 1) Navigate to reservations/upcoming trips page. 2) Find the reservation matching ALL constraints: location CONTAINS value, destination NOT CONTAIN excluded value (skip if destination matches), ride_name equals, scheduled time equals. 3) Click Cancel or the reservation row. 4) Confirm cancellation if prompted.",
    "SELECT_DATE": "PLAYBOOK: 1) Find the date picker/calendar widget. 2) Click it to open. 3) Select a date satisfying TASK_CONSTRAINTS. 4) Confirm the selection.",
    "SELECT_TIME": "PLAYBOOK: 1) Find the time picker/dropdown. 2) Click to open. 3) Select a time satisfying the constraint. 4) Confirm.",
    "NEXT_PICKUP": "PLAYBOOK: 1) Look for Next Pickup or scheduled rides section. 2) Use list_cards to see all pickups. 3) Compare each card's date/time against CONSTRAINTS (<=, >= etc). 4) Click Show Details on the matching pickup.",
    "STAR_AN_EMAIL": "PLAYBOOK: 1) Browse the inbox email list. 2) Find the email matching ALL constraints. 3) Click the Star icon on that email row.",
    "ARCHIVE_EMAIL": "PLAYBOOK: 1) Browse the inbox. 2) Find email matching constraints. 3) Click on that email. 4) Find Archive button. Click it.",
    "DELETE_EMAIL": "PLAYBOOK: 1) Find the email matching constraints. 2) Click the Delete/Trash icon on that email row.",
    "ADD_LABEL": "PLAYBOOK: 1) Find the email matching ALL TASK_CONSTRAINTS. 2) Open that email or select it. 3) Find the Label option. 4) Select a label that is NOT the excluded label_name.",
    "FORWARD_EMAIL": "PLAYBOOK: 1) Find the email matching constraints. 2) Click to open. 3) Click Forward button. 4) Fill in To field if needed. 5) Send.",
    "MARK_EMAIL_AS_IMPORTANT": "PLAYBOOK: 1) Find the email matching constraints. 2) Click the Important/Flag icon on that email.",
    "EDIT_DRAFT_EMAIL": "PLAYBOOK: 1) Navigate to Drafts folder. 2) Find draft matching constraints. 3) Click to open/edit the draft.",
    "EMAILS_NEXT_PAGE": "PLAYBOOK: 1) Look at the bottom of the email list for pagination. 2) Click the Next arrow/button.",
    "EMAILS_PREV_PAGE": "PLAYBOOK: 1) Look for Previous arrow at bottom of email list. 2) Click it.",
    "CLEAR_SELECTION": "PLAYBOOK: 1) Look for a Clear Selection button or uncheck Select All checkbox. 2) Click it.",
    "TEMPLATE_SENT": "PLAYBOOK: 1) Navigate to Templates section. 2) Find template matching constraints. 3) Click Send or Use Template.",
    "TEMPLATE_SAVED_DRAFT": "PLAYBOOK: 1) Navigate to Templates section. 2) Find template matching constraints. 3) Click Save as Draft.",
    "TEMPLATE_SELECTED": "PLAYBOOK: 1) Navigate to Templates section. 2) Find the template matching constraints. 3) Click Select or Use.",
    "SELECT_WEEK": "PLAYBOOK: 1) Find the view switcher buttons. 2) Click Week button.",
    "SELECT_MONTH": "PLAYBOOK: 1) Find view buttons. 2) Click Month button.",
    "SELECT_DAY": "PLAYBOOK: 1) Find view buttons. 2) Click Day button.",
    "SELECT_FIVE_DAYS": "PLAYBOOK: 1) Find view buttons. 2) Click 5-day or Work Week button.",
    "ADD_NEW_CALENDAR": "PLAYBOOK: 1) Find the + or Add Calendar button in the left sidebar. 2) Click it to open the modal.",
    "CREATE_CALENDAR": "PLAYBOOK: 1) Click the + button next to Other calendars. 2) Fill in name and description satisfying constraints. 3) Click Create/Save.",
    "EVENT_ADD_ATTENDEE": "PLAYBOOK: 1) Find an event on the calendar. 2) Click on it to open. 3) Click Edit. 4) Find Add Attendee field. 5) Type email satisfying constraints. 6) Save.",
    "DELETE_ADDED_EVENT": "PLAYBOOK: 1) Browse calendar events. 2) Find the event matching ALL constraints. 3) Click on it. 4) Click Delete. 5) Confirm.",
    "CANCEL_ADD_EVENT": "PLAYBOOK: 1) Find the event matching constraints. 2) Click on it. 3) Click Cancel/Delete. 4) Confirm.",
    "NEW_CALENDAR_EVENT_ADDED": "PLAYBOOK: 1) Click the + or Add Event button. 2) Fill in the event form satisfying ALL constraints. 3) Save the event.",
    "ADD_EVENT": "PLAYBOOK: 1) Click + or on a time slot. 2) Fill ALL fields from TASK_CONSTRAINTS. 3) Save.",
    "VIEW_PENDING_EVENTS": "PLAYBOOK: 1) Switch to a view showing upcoming events. 2) Find events matching constraint. 3) Navigate to or click on that event.",
    "AUTOLIST_TEAM_MEMBERS_ADDED": "PLAYBOOK: 1) Navigate to Team section. 2) Click Add Member. 3) Search for a member satisfying constraints. 4) Add them.",
    "AUTOLIST_TEAM_ROLE_ASSIGNED": "PLAYBOOK: 1) Go to Team section. 2) Find a member satisfying constraints. 3) Click their role dropdown. 4) Select the required role.",
    "AUTOLIST_EDIT_TASK_MODAL_OPENED": "PLAYBOOK: 1) Browse task list. 2) Find task matching ALL constraints. 3) Click the Edit/Pencil icon to open the edit modal.",
    "AUTOLIST_ADD_TASK_CLICKED": "PLAYBOOK: 1) Find the Add Task button. 2) Click it.",
    "AUTOLIST_TASK_ADDED": "PLAYBOOK: 1) Click the Add Task button to open form. 2) Fill fields satisfying ALL TASK_CONSTRAINTS. 3) Click Save/Submit.",
    "AUTOLIST_DELETE_TASK": "PLAYBOOK: 1) Navigate to Tasks section. 2) Find the task matching ALL TASK_CONSTRAINTS. 3) Click Delete button. 4) Confirm deletion.",
    "CONFIRM_AND_PAY": "PLAYBOOK: 1) Browse listings. Find matching ALL TASK_CONSTRAINTS. 2) Click Book Now. 3) Fill payment form with EXACT values. 4) Submit.",
    "VIEW_DOCTOR_PROFILE": "PLAYBOOK: 1) Browse doctor list. 2) Find doctor matching ALL constraints. 3) Click to view profile.",
    "SEARCH_DOCTORS": "PLAYBOOK: 1) Find search/filter fields for doctors. 2) Enter search criteria matching constraints. 3) Submit search.",
    "SEARCH_MEDICAL_ANALYSIS": "PLAYBOOK: 1) Navigate to Medical Records/Analysis. 2) Use search/filter fields. 3) Submit/search.",
    "VIEW_MEDICAL_ANALYSIS": "PLAYBOOK: 1) Navigate to Medical Records. 2) Find the record matching constraints. 3) Click to view details.",
    "OPEN_APPOINTMENT_FORM": "PLAYBOOK: 1) Browse doctor cards. 2) Find doctor matching ALL constraints. 3) Click Book Appointment. 4) Fill in date and time. 5) Open/submit.",
    "OPEN_CONTACT_DOCTOR_FORM": "PLAYBOOK: 1) Find doctor matching ALL constraints. 2) Click Contact Doctor button.",
    "CONTACT_DOCTOR": "PLAYBOOK: 1) Find doctor matching constraints. 2) Click Contact. 3) Fill the contact form. 4) Submit.",
    "SEARCH_APPOINTMENT": "PLAYBOOK: 1) Navigate to Appointments section (click Appointments in navbar). 2) Look for search/filter input fields: doctor_name, specialty, date, patient_name, status. 3) Enter EXACT values from TASK_CONSTRAINTS into matching filter fields. 4) Click Search or Apply Filter button. 5) The matching appointments appear in the table below.",
    "REQUEST_QUICK_APPOINTMENT": "PLAYBOOK: 1) Find Quick Appointment button. 2) Fill form satisfying constraints. 3) Submit.",
    "VIEW_DOCTOR_EDUCATION": "PLAYBOOK: 1) Browse doctors list. 2) Find doctor matching ALL constraints. 3) Click on doctor's card. 4) Find Education tab/section. 5) Click it.",
    "COMMENT_ON_POST": "PLAYBOOK: 1) Find a post in the feed. 2) Click the Comment button. 3) Type the EXACT comment text. 4) Submit.",
    "FOLLOW_PAGE": "PLAYBOOK: 1) Find the company page matching constraints. 2) Click the Follow button.",
    "UNFOLLOW_PAGE": "PLAYBOOK: 1) Find the company page. 2) Click Unfollow.",
    "CANCEL_APPLICATION": "PLAYBOOK: 1) Navigate to My Applications or Jobs. 2) Find the application matching constraints. 3) Click Withdraw/Cancel.",
    "SEARCH_USERS": "PLAYBOOK: 1) Find the user search bar. 2) Type the query. 3) Submit.",
    "BACK_TO_ALL_JOBS": "PLAYBOOK: 1) Navigate to Jobs section. 2) Find a job satisfying constraints. 3) Click on it. 4) Find and click Back to all jobs link.",
    "EDIT_PROFILE_BIO": "PLAYBOOK: 1) Navigate to Profile/Settings. 2) Find Bio field. 3) Set bio to EXACT value. 4) Save.",
    "HIRE_BTN_CLICKED": "PLAYBOOK: 1) Browse expert/consultant list. 2) Find expert matching ALL constraints. 3) Click Hire Now.",
    "HIRE_LATER": "PLAYBOOK: 1) Browse expert list. 2) Find expert matching constraints. 3) Click Hire Later.",
    "HIRE_LATER_REMOVED": "PLAYBOOK: 1) Navigate to Hire Later page (find 'Hire Later' link in navbar or hires section). 2) Find the expert whose role equals and name equals the constraints. 3) Click Remove or Delete button next to that expert.",
    "SELECT_HIRING_TEAM": "PLAYBOOK: 1) Find the Hiring Team section. 2) Find member matching constraints. 3) Click to view.",
    "CHOOSE_PROJECT_SIZE": "PLAYBOOK: 1) Find the project size selector. 2) Choose a size NOT the excluded one.",
    "CLOSE_POST_A_JOB_WINDOW": "PLAYBOOK: 1) Open the job posting form. 2) Fill in rate_from/rate_to. 3) Close the window (X/Cancel).",
    "NAVBAR_JOBS_CLICK": "PLAYBOOK: 1) Find Jobs link in the navbar. 2) Click it.",
    "NAVBAR_HIRES_CLICK": "PLAYBOOK: 1) Find Hires link in the navbar. 2) Click it.",
    "SEARCH_SKILL": "PLAYBOOK: 1) Find the skill search bar. 2) Type the query. 3) Submit.",
    "EDIT_PROFILE_LOCATION": "PLAYBOOK: 1) Navigate to Profile/Settings. 2) Find Location field. 3) Enter value satisfying constraints. 4) Save.",
    "EDIT_PROFILE_EMAIL": "PLAYBOOK: 1) Navigate to Profile/Settings/Account. 2) Find Email field. 3) Enter value satisfying constraints. 4) Save.",
    "BOOKING_CONFIRM": "PLAYBOOK: 1) Browse listings. Find matching ALL TASK_CONSTRAINTS. 2) Set guests count. 3) Click Book Now/Reserve. 4) Fill payment form. 5) Submit/Confirm.",
    "RESERVE_HOTEL": "PLAYBOOK: 1) Browse hotel listings. 2) Find hotel matching ALL constraints. 3) Set guests if needed. 4) Click Reserve/Book Now.",
    "SEARCH_HOTEL": "PLAYBOOK: 1) Find the hotel search bar. 2) Type the search term. 3) Submit.",
    "PAYMENT_METHOD_SELECTED": "PLAYBOOK: 1) Find hotel matching constraints. 2) Click to book. 3) Select a payment method satisfying constraints.",
    "EDIT_NUMBER_OF_GUESTS": "PLAYBOOK: 1) Find the booking/listing matching ALL constraints (may have many: rating, location, host_name, title, price, reviews). 2) Click on it to open the detail or booking page. 3) Find the guest count selector (+/- buttons or dropdown). 4) Set the guest count to the value specified in the task (e.g. 'Set total guests to 2'). 5) Save or update the booking.",
    "SUBMIT_REVIEW": "PLAYBOOK: 1) Find listing matching constraints. 2) Click Write Review. 3) Set rating. 4) Type review text. 5) Submit.",
    "ADD_TO_WISHLIST_HOTEL": "PLAYBOOK: 1) Find hotel matching constraints. 2) Click Add to Wishlist/heart icon.",
    "APPLY_FILTERS": "PLAYBOOK: 1) Find filter controls. 2) Set region/rating/price as specified. 3) Apply the filter.",
    "PEOPLE_DROPDOWN_OPENED": "PLAYBOOK: 1) Find the people/guest selector. 2) Click to open the dropdown. 3) Select the number satisfying the constraint.",
    "COUNTRY_SELECTED": "PLAYBOOK: 1) Find the country/destination dropdown. 2) Set other filters per constraints. 3) Open dropdown. 4) Select the specified country.",
    "RESTAURANT_NEXT_PAGE": "PLAYBOOK: 1) Look for pagination at bottom. 2) Click the Next button.",
    "RESTAURANT_PREV_PAGE": "PLAYBOOK: 1) Look for pagination. 2) Click Previous button.",
    "SEARCH_DELIVERY_RESTAURANT": "PLAYBOOK: 1) Find the restaurant search bar. 2) Type query satisfying constraints. 3) Submit.",
    "DROPOFF_PREFERENCE": "PLAYBOOK: 1) Find order matching constraints. 2) Find the dropoff preference selector. 3) Select an option satisfying constraints.",
    "DELIVERY_PRIORITY_SELECTED": "PLAYBOOK: 1) Find order matching constraints. 2) Find delivery priority selector. 3) Select a priority satisfying constraints.",
    "VIEW_DELIVERY_RESTAURANT": "PLAYBOOK: 1) Browse restaurant list. 2) Find restaurant matching constraints. 3) Click on it.",
    "VIEW_ALL_RESTAURANTS": "PLAYBOOK: 1) Click All Restaurants or equivalent link/tab.",
    "OPEN_CHECKOUT_PAGE": "PLAYBOOK: 1) Find order matching constraints. 2) Navigate to checkout.",
    "SEARCH_RESTAURANT": "PLAYBOOK: 1) Find the restaurant search bar. 2) Type EXACT query. 3) Submit search.",
    "VIEW_RESTAURANT": "PLAYBOOK: 1) Browse restaurant listing cards. 2) Find restaurant matching ALL constraints. 3) Click on it to open detail page.",
    "HELP_FAQ_TOGGLED": "PLAYBOOK: 1) Navigate to Help/FAQ page. 2) Find FAQ item NOT containing excluded text. 3) Click to expand.",
    "HELP_VIEWED": "PLAYBOOK: 1) Find Help or FAQ link in navigation. 2) Click it.",
    "ABOUT_FEATURE_CLICK": "PLAYBOOK: 1) Navigate to About page. 2) Find the feature card matching text. 3) Click on it.",
    "CONTACT_FORM_SUBMIT": "PLAYBOOK: 1) Navigate to Contact page. 2) Fill form satisfying constraints. 3) Submit.",
    "CATEGORY_FILTER": "PLAYBOOK: 1) Find the category filter. 2) Click the category matching the specified value.",
    "VIEW_WISHLIST": "PLAYBOOK: 1) Find the Wishlist link/icon. 2) Click to view saved items.",
    "PROCEED_TO_CHECKOUT": "PLAYBOOK: 1) Go to cart. 2) Click Proceed to Checkout.",
    "ORDER_COMPLETED": "PLAYBOOK: 1) Find item matching constraints. 2) Navigate to it. 3) Complete purchase/order.",
    "CAROUSEL_SCROLL": "PLAYBOOK: 1) Find carousel section NOT the excluded one. 2) Click the scroll button.",
    "SHARE_PRODUCT": "PLAYBOOK: 1) Find product matching constraints. 2) Click Share button.",
    "ADD_CLIENT": "PLAYBOOK: 1) Navigate to Clients section. 2) Click Add New Client. 3) Fill form satisfying constraints. 4) Save.",
    "ADD_NEW_MATTER": "PLAYBOOK: 1) Navigate to Matters section. 2) Click Add New Matter. 3) Fill form. 4) Save.",
    "SORT_MATTER_BY_CREATED_AT": "PLAYBOOK: 1) Navigate to Matters list. 2) Find the created_at column header. 3) Click it to sort.",
    "CHANGE_USER_NAME": "PLAYBOOK: 1) Navigate to Settings or Profile. 2) Find the user name field. 3) Set it to the specified value. 4) Save.",
    "WRITE_JOB_TITLE": "PLAYBOOK: 1) Look for Post a Job or + button. 2) Click it. 3) Type the EXACT job title from TASK_CREDENTIALS. 4) Do NOT click submit.",
    "ENTER_DESTINATION": "PLAYBOOK: 1) Find the destination input field. 2) Click to focus. 3) Clear if pre-filled. 4) Type a valid destination DIFFERENT from the NOT constraint. 5) Confirm.",
    "ENTER_LOCATION": "PLAYBOOK: 1) Find the location/pickup input field. 2) Click to focus. 3) Type the EXACT location from TASK_CONSTRAINTS. 4) Click matching autocomplete suggestion. 5) Confirm.",
    "SEARCH_RIDE": "PLAYBOOK: 1) On AutoRide, find the ride search/filter interface. 2) Apply filters or scroll to find ride matching ALL constraints. 3) Click on matching ride.",
    "MARK_AS_SPAM": "PLAYBOOK: 1) Browse the inbox. 2) Find email matching ALL constraints. 3) Click on it or select it. 4) Find Mark as Spam button. 5) Click it.",
    "MARK_AS_UNREAD": "PLAYBOOK: 1) Browse the inbox email list. 2) Find email matching ALL constraints. 3) Click or use menu. 4) Click Mark as Unread.",
    "VIEW_EMAIL": "PLAYBOOK: 1) Browse the email list. 2) Find the email matching constraint. 3) Click to open and view.",
    "THEME_CHANGED": "PLAYBOOK: 1) Find Settings/Preferences. 2) Look for Theme/Appearance settings. 3) Select Dark theme. 4) Save/Apply.",
    "COLLAPSE_MENU": "PLAYBOOK: 1) Browse restaurants. 2) Find matching restaurant. 3) Click to expand. 4) Find collapse button. 5) Click it.",
    "CONTACT_CARD_CLICK": "PLAYBOOK: 1) Find contact cards. 2) Find the card NOT containing excluded value. 3) Click on it.",
    "SCROLL_VIEW": "PLAYBOOK: 1) Find scrollable section NOT containing excluded name. 2) Scroll in specified direction.",
    "HELP_CATEGORY_SELECTED": "PLAYBOOK: 1) Navigate to Help page. 2) Find category matching constraint. 3) Click on it.",
    "HELP_PAGE_VIEW": "PLAYBOOK: 1) Find Help/FAQ link in navigation/footer. 2) Click it.",
    "QUANTITY_CHANGED": "PLAYBOOK: 1) Navigate to cart. 2) Find item matching constraints. 3) Set quantity to satisfy constraint. 4) Confirm.",
    "ITEM_INCREMENTED": "PLAYBOOK: 1) Navigate to cart. 2) Find item quantity control. 3) Increment to target value. 4) Confirm.",
    "VIEW_DETAIL": "PLAYBOOK: 1) Browse product listing. 2) Find product matching ALL constraints. 3) Click to open detail page.",
    "SAVE_POST": "PLAYBOOK: 1) Browse feed/posts. 2) Find post matching constraints. 3) Click Save/Bookmark.",
    "HOME_NAVBAR": "PLAYBOOK: 1) Find navigation bar. 2) Click Home tab/link.",
    "VIEW_HIDDEN_POSTS": "PLAYBOOK: 1) Go to profile or settings. 2) Find Hidden Posts section. 3) Navigate to it.",
    "SEARCH_JOBS": "PLAYBOOK: 1) Find Jobs section. 2) Find search input. 3) Type query satisfying constraints. 4) Submit.",
    "APPLY_FOR_JOB": "PLAYBOOK: 1) Browse job listings. 2) Find job matching ALL constraints. 3) Click to open. 4) Click Apply.",
    "SEARCH_SUBMIT": "PLAYBOOK: 1) Find search input. 2) Type query from TASK_CONSTRAINTS. 3) Submit.",
    "EVENT_WIZARD_OPEN": "PLAYBOOK: 1) Find Add Event button. 2) Click it to open wizard. 3) If title field appears, type title satisfying constraints.",
    "CELL_CLICKED": "PLAYBOOK: 1) Switch to 5 days view. 2) Find a cell matching date/time constraints. 3) Click on that cell.",
    "EVENT_REMOVE_ATTENDEE": "PLAYBOOK: 1) Find an event. 2) Click to open. 3) Find attendees list. 4) Find attendee NOT matching excluded email. 5) Click Remove.",
    "SELECT_TODAY": "PLAYBOOK: 1) Find the focus-today button. 2) Click it.",
    "AUTOLIST_SELECT_TASK_PRIORITY": "PLAYBOOK: 1) Find task with priority NOT the excluded value. 2) Click priority selector. 3) Select High or target value. 4) Save.",
    "AUTOLIST_CANCEL_TASK_CREATION": "PLAYBOOK: 1) Click Add Task. 2) Fill fields as specified. 3) Click Cancel/Discard instead of Submit.",
    "AUTOLIST_TEAM_CREATED": "PLAYBOOK: 1) Navigate to Teams section. 2) Click Create Team. 3) Fill fields satisfying constraints. 4) Save.",
    "AUTOLIST_COMPLETE_TASK": "PLAYBOOK: 1) Find task list. 2) For NOT constraints (name NOT X, description NOT CONTAIN Y): skip any task where that field matches the excluded value. 3) For positive constraints (priority equals, date >=): require those to match. 4) Click the checkbox or Complete button on the task satisfying ALL constraints.",
    "AUTOLIST_SELECT_DATE_FOR_TASK": "PLAYBOOK: 1) Find task. 2) Click Edit or date field. 3) Select date satisfying constraint. 4) Confirm.",
    "DELETE_BOOK": "PLAYBOOK: 1) Login with credentials. 2) Navigate to your books. 3) Find matching book. 4) Click Delete. 5) Confirm.",
    "EDIT_BOOK": "PLAYBOOK: 1) Login. 2) Find book matching constraints. 3) Click Edit. 4) Modify fields. 5) Save.",
    "REMOVE_FROM_READING_LIST": "PLAYBOOK: 1) Login. 2) Navigate to Reading List. 3) Find book satisfying constraints. 4) Click Remove.",
    "CONTACT_BOOK": "PLAYBOOK: 1) Navigate to Contact page. 2) Fill form satisfying constraints. 3) Submit.",
    "REGISTRATION_BOOK": "PLAYBOOK: 1) Navigate to Register page. 2) Fill in username, email, password. 3) Submit.",
    "BOOK_DETAIL": "PLAYBOOK: 1) Browse books list. 2) Find book matching ALL constraints. 3) Click to open detail page.",
    "FILTER_BOOK": "PLAYBOOK: 1) Find filter/genre panel. 2) Select genre matching constraint. 3) Apply filter.",
    "SEARCH_BOOK": "PLAYBOOK: 1) Find search bar. 2) Type exact query. 3) Submit.",
    "VIEW_CART_BOOK": "PLAYBOOK: 1) Login if needed. 2) Click Cart icon or navigate to /cart. 3) View contents.",
    "LOGIN_BOOK": "PLAYBOOK: 1) Click Login. 2) Type username and password. 3) Click Login button.",
    "LOGOUT_BOOK": "PLAYBOOK: 1) Login first. 2) Find logout option. 3) Click Logout.",
    "ADD_TO_WATCHLIST": "PLAYBOOK: 1) Login if required. 2) Browse films. 3) Find film matching constraints. 4) Click to open detail. 5) Click Add to Watchlist.",
    "REMOVE_FROM_WATCHLIST": "PLAYBOOK: 1) Login. 2) Navigate to watchlist. 3) Find item. 4) Click Remove.",
    "SHARE_MOVIE": "PLAYBOOK: 1) Browse films. 2) Find film matching constraints. 3) Click to open detail. 4) Click Share.",
    "CHECKOUT_STARTED": "PLAYBOOK: 1) Browse products. 2) Find product matching constraints. 3) Click Buy Now.",
    "ABOUT_PAGE_VIEW": "PLAYBOOK: 1) Find About link. 2) Click it.",
    "DATE_DROPDOWN_OPENED": "PLAYBOOK: 1) Find date selector. 2) Click to open. 3) Select date satisfying constraint. 4) Confirm.",
    "TIME_DROPDOWN_OPENED": "PLAYBOOK: 1) Find time selection dropdown. 2) Click to open. 3) Select time matching constraint. 4) Confirm.",
    "BILLING_SEARCH": "PLAYBOOK: 1) Navigate to Billing section. 2) Find search/filter inputs. 3) Enter query. 4) Select date_filter satisfying constraints. 5) Apply.",
    "LOG_EDITED": "PLAYBOOK: 1) Navigate to Logs/Time entries. 2) Find log entry matching constraints. 3) Click Edit. 4) Make change. 5) Save.",
    "ARCHIVE_MATTER": "PLAYBOOK: 1) Navigate to Matters. 2) Find matter satisfying constraints. 3) Click Archive. 4) Confirm.",
    "VIEW_CLIENT_DETAILS": "PLAYBOOK: 1) Navigate to Clients. 2) Find client matching constraints. 3) Click to open details.",
    "VIEW_MATTER_DETAILS": "PLAYBOOK: 1) Navigate to Matters. 2) Find matter matching constraints. 3) Click to open details.",
    "SEND_EMAIL": "PLAYBOOK: 1) Click Compose/New Email. 2) Fill To, Subject, Body satisfying constraints. 3) Click Send.",
    "SEARCH_EMAIL": "PLAYBOOK: 1) Find Search bar. 2) Type query. 3) Submit.",
    "DELETE_REVIEW": "PLAYBOOK: 1) Find restaurant matching constraints. 2) Open it. 3) Find review matching constraints. 4) Click Delete. 5) Confirm.",
    "RESTAURANT_FILTER": "PLAYBOOK: 1) Find cuisine filter. 2) Apply filter satisfying constraints.",
    "ADD_TO_CART_MENU_ITEM": "PLAYBOOK: 1) Browse restaurants. 2) Find restaurant. 3) Find menu item matching constraints. 4) Add to cart.",
    "ADD_TO_CART_MODAL_OPEN": "PLAYBOOK: 1) Find restaurant matching constraints. 2) Click to view menu. 3) Find menu item matching price constraint. 4) Click to open add-to-cart modal.",
    "QUICK_ORDER_STARTED": "PLAYBOOK: 1) Find Quick Order button on any restaurant card. 2) Click it.",
    "FAQ_OPENED": "PLAYBOOK: 1) Navigate to FAQ page. 2) Find FAQ item matching constraint. 3) Click to expand.",
    "MESSAGE_HOST": "PLAYBOOK: 1) Find hotel matching ALL constraints. 2) Click to open. 3) Find Message Host button. 4) Type message. 5) Send.",
    "EDIT_CHECK_IN_OUT_DATES": "PLAYBOOK: 1) Find listing matching constraints. 2) Open booking form. 3) Modify dates. 4) Save.",
    "WISHLIST_OPENED": "PLAYBOOK: 1) Find Wishlist/Saved Hotels icon. 2) Click to open.",
    "REMOVE_FROM_WISHLIST": "PLAYBOOK: 1) Navigate to Wishlist (click Wishlist/Saved link). 2) Scan each hotel card. 3) For NOT constraints (title NOT contain, host NOT equal): skip any card where that field matches the excluded value. 4) For positive constraints (price equals, guests >=): require those to match. 5) Click Remove or the heart/bookmark icon on the matching hotel.",
    "JOBS_NAVBAR": "PLAYBOOK: 1) Find Jobs tab in navbar. 2) Click it.",
    "EDIT_PROFILE": "PLAYBOOK: 1) Find user matching constraints. 2) Navigate to Profile. 3) Click Edit Profile. 4) Update fields. 5) Save.",
    "POST_STATUS": "PLAYBOOK: 1) On the feed/home page, find the status input textarea (placeholder: 'What's on your mind?' or 'Write a post'). 2) Click on the textarea to focus it. 3) Type post content: if content 'NOT equals X' constraint, type any text that is NOT X. 4) After typing, look for 'Post' or 'Share' button. 5) Click Post to publish. If textarea not visible, scroll up to find it.",
    "REMOVE_POST": "PLAYBOOK: 1) Find post satisfying constraints. 2) Click 3-dot menu. 3) Click Remove/Delete. 4) Confirm.",
    "EDIT_PROFILE_TITLE": "PLAYBOOK: 1) Navigate to profile settings. 2) Find title field. 3) Click Edit, clear, type new value. 4) Save.",
    "POST_A_JOB": "PLAYBOOK: 1) Find Post a Job button. 2) Click it.",
    "NAVBAR_EXPERTS_CLICK": "PLAYBOOK: 1) Find Experts link in navbar. 2) Click it.",
    "ADD_SKILL": "PLAYBOOK: 1) Navigate to Skills section. 2) Find Add Skill button. 3) Type skill name satisfying constraints. 4) Save.",
    "SUBMIT_JOB": "PLAYBOOK: 1) Navigate to Post a Job. 2) Fill title, rate_from, rate_to satisfying constraints. 3) Submit.",
    "HIRE_LATER_START": "PLAYBOOK: 1) Navigate to Hire Later page. 2) Find expert matching constraints. 3) Click Start Hiring.",
    "EDIT_ABOUT": "PLAYBOOK: 1) Navigate to profile. 2) Find About/Bio section. 3) Click Edit. 4) Update text satisfying constraints. 5) Save.",
    "SELECT_CALENDAR": "PLAYBOOK: 1) Find calendar list/sidebar. 2) Find calendar matching constraints. 3) Click to select it.",
    "UNSELECT_CALENDAR": "PLAYBOOK: 1) Find calendar list. 2) Find calendar matching constraints. 3) Click to unselect it.",
    "DOCTOR_CONTACTED_SUCCESSFULLY": "PLAYBOOK: 1) Find doctor matching ALL constraints. 2) Open Contact Doctor form. 3) Fill form satisfying constraints. 4) Submit.",
    "VIEW_DOCTOR_AVAILABILITY": "PLAYBOOK: 1) Browse doctors list. 2) Find doctor matching constraints. 3) Click profile. 4) Navigate to Availability tab.",
    "SEARCH_MATTER": "PLAYBOOK: 1) Find Matters search bar. 2) Type query satisfying constraints. 3) Submit.",
    "FILTER_CLIENTS": "PLAYBOOK: 1) On Clients page, find filter/search. 2) Apply filters satisfying constraints. 3) Show filtered list.",
    "FILTER_MATTER_STATUS": "PLAYBOOK: 1) On Matters page, find status filter. 2) Filter by status matching constraint. 3) Apply.",
    "DOCUMENT_DELETED": "PLAYBOOK: 1) Navigate to Documents. 2) Find document matching ALL constraints. 3) Click to view or delete as task requires.",
    "REVIEW_SUBMITTED": "PLAYBOOK: 1) Find restaurant matching constraints. 2) Open it. 3) Find Write Review button. 4) Fill rating and review text. 5) Submit.",
    "BACK_TO_ALL_RESTAURANTS": "PLAYBOOK: 1) Navigate to restaurant matching constraints. 2) Open detail page. 3) Find Back button. 4) Click it.",
    "ADDRESS_ADDED": "PLAYBOOK: 1) Find delivery address section. 2) Click Add Address. 3) Type exact address. 4) Fill additional fields. 5) Save.",
    "SHARE_HOTEL": "PLAYBOOK: 1) Scroll through hotel cards. 2) For NOT constraints (host_name, title, location): skip any card where that field matches the excluded value. 3) For positive constraints (price, rating, guests, amenities): find matching card. 4) Click that hotel to open details. 5) Find Share button/link. 6) Type the email from constraints exactly. 7) Send/Submit.",
    "POPULAR_HOTELS_VIEWED": "PLAYBOOK: 1) Find Popular Hotels section. 2) Apply rating filter if available. 3) Click to view.",
    "TRIP_DETAILS": "PLAYBOOK: 1) View trips list. 2) Find trip matching ALL constraints. 3) Click to view details.",
    "SELECT_CAR": "PLAYBOOK: 1) Find ride matching constraints. 2) Click to open. 3) Select car option.",
    "SEARCH_DESTINATION": "PLAYBOOK: 1) Find destination search bar. 2) Type a destination NOT the excluded value. 3) Submit.",
    "REFILL_PRESCRIPTION": "PLAYBOOK: 1) Navigate to Prescriptions. 2) Find prescription matching constraints. 3) Click Refill. 4) Confirm.",
    "VIEW_PRESCRIPTION": "PLAYBOOK: 1) Navigate to Prescriptions. 2) Find prescription matching constraints. 3) Click to view details.",
    "FILTER_DOCTOR_REVIEWS": "PLAYBOOK: 1) Navigate to Reviews/Doctors. 2) Find filter. 3) Set filter matching constraints. 4) Apply.",
    "QUICK_REORDER": "PLAYBOOK: 1) Find Recent Orders section. 2) Find order satisfying constraints. 3) Click Reorder.",
    "EDIT_CART_ITEM": "PLAYBOOK: 1) Navigate to Cart. 2) Find item matching constraints. 3) Click Edit.",
    "DELETE_MATTER": "PLAYBOOK: 1) Navigate to Matters. 2) Find matter matching constraints. 3) Click Delete. 4) Confirm.",
    "CREATE_LABEL": "PLAYBOOK: 1) Find Labels section. 2) Click + or Create Label. 3) Type name satisfying constraints. 4) Save.",
    "DELETE_TASK": "PLAYBOOK: 1) Navigate to task list. 2) Find task matching ALL constraints. 3) Click Delete. 4) Confirm.",
    "CREATE_TASK": "PLAYBOOK: 1) Find New Task/Add Task button. 2) Fill fields with EXACT values. 3) Save/Submit.",
    "EDIT_TASK": "PLAYBOOK: 1) Find task matching constraints. 2) Click Edit. 3) Update fields. 4) Save.",
    "COMPLETE_TASK": "PLAYBOOK: 1) Find task matching constraints. 2) Click Complete/Done/Checkmark.",
    "JOB_POSTING": "PLAYBOOK: 1) Find Post a Job button. 2) Click it. 3) Type EXACT job title. 4) Submit.",
    # ---- AutoDiscord playbooks ----
    "TOGGLE_MUTE": "PLAYBOOK: 1) Look for voice channel controls at bottom of sidebar or voice panel. 2) Find the Mute/Unmute button (microphone icon). 3) Click it to toggle mute state. If task says muted='False', ensure you UNMUTE (click mute button when currently muted).",
    "TOGGLE_DEAFEN": "PLAYBOOK: 1) Find voice controls. 2) Find Deafen button (headphone icon). 3) Click to toggle.",
    "JOIN_VOICE_CHANNEL": "PLAYBOOK: 1) Find voice channel in channel list (speaker icon). 2) Click on the voice channel name to join.",
    "LEAVE_VOICE_CHANNEL": "PLAYBOOK: 1) Find Disconnect button in voice controls. 2) Click it.",
    "SEND_CHANNEL_MESSAGE": "PLAYBOOK: 1) Navigate to the correct channel. 2) Find message input at bottom. 3) Type message. 4) Submit (Enter or Send).",
    "CREATE_CHANNEL": "PLAYBOOK: 1) Find + button next to channel category. 2) Click it. 3) Fill channel name. 4) Select type (text/voice). 5) Create.",
    "DELETE_CHANNEL": "PLAYBOOK: 1) Find channel matching constraints. 2) Right-click or open settings. 3) Delete Channel. 4) Confirm.",
    "CREATE_SERVER": "PLAYBOOK: 1) Find + button in server list. 2) Click Create Server. 3) Fill server name. 4) Create.",
    "SWITCH_SERVER": "PLAYBOOK: 1) Find server icon in left sidebar. 2) Click on it.",
    "SWITCH_CHANNEL": "PLAYBOOK: 1) Find channel matching constraints in channel list. 2) Click on it.",
    "PIN_MESSAGE": "PLAYBOOK: 1) Find message matching constraints. 2) Hover or right-click. 3) Click Pin/Unpin.",
    "EDIT_MESSAGE": "PLAYBOOK: 1) Find message matching constraints. 2) Click Edit. 3) Modify text. 4) Save.",
    "DELETE_MESSAGE": "PLAYBOOK: 1) Find message matching constraints. 2) Click Delete. 3) Confirm.",
    "REACT_MESSAGE": "PLAYBOOK: 1) Find message matching constraints. 2) Click Add Reaction. 3) Select emoji. 4) Confirm.",
    "SEARCH_USER": "PLAYBOOK: 1) Find user search in member list or top bar. 2) Type search query. 3) Submit.",
    "INVITE_USER": "PLAYBOOK: 1) Find Invite button or member settings. 2) Enter username/email. 3) Send invite.",
    "CHANGE_NICKNAME": "PLAYBOOK: 1) Find profile or server settings. 2) Find nickname field. 3) Change to value satisfying constraints. 4) Save.",
    "SERVER_SETTINGS": "PLAYBOOK: 1) Click server name dropdown. 2) Click Server Settings.",
    # ---- AutoStats playbooks ----
    "FAVORITE_SUBNET": "PLAYBOOK: 1) Use list_cards tool to inspect all subnet cards. 2) For each subnet: check ALL constraints simultaneously - skip if any NOT constraint matches, require all positive (equals/contains/>/< ) constraints to match. 3) Exactly one subnet will match all constraints. 4) Click the Star or Heart (favorite) icon on that specific subnet card. Do NOT click View Details - click the star/heart icon.",
    "UNFAVORITE_SUBNET": "PLAYBOOK: 1) Browse subnet list. 2) Find subnet matching constraints. 3) Click to unfavorite (toggle star/heart off).",
    "VIEW_SUBNET_DETAILS": "PLAYBOOK: 1) Browse subnet list. 2) Find subnet matching constraints. 3) Click to view details.",
    "FILTER_SUBNET": "PLAYBOOK: 1) Find search/filter controls. 2) Apply filters satisfying constraints. 3) View results.",
    "VIEW_VALIDATOR_DETAILS": "PLAYBOOK: 1) Navigate to Validators section. 2) Find validator matching constraints. 3) Click to view.",
    "VIEW_MINER_DETAILS": "PLAYBOOK: 1) Navigate to Miners section. 2) Find miner matching constraints. 3) Click to view.",
    "SELECT_DATE_RANGE": "PLAYBOOK: 1) Find date range selector. 2) Set range satisfying constraints. 3) Apply.",
    "EXPORT_DATA": "PLAYBOOK: 1) Find Export/Download button. 2) Click it. 3) Select format if prompted.",
    "VIEW_DASHBOARD": "PLAYBOOK: 1) Find Dashboard link in navigation. 2) Click it.",
    "DISCONNECT_WALLET": "PLAYBOOK: 1) Navigate to Settings or Wallet/Account section. 2) Find the wallet matching the wallet_name constraint. 3) Click Disconnect button. 4) Confirm if prompted.",
    "CONNECT_WALLET": "PLAYBOOK: 1) Look for 'Connect Wallet' button in the header/navbar. 2) Click it to open the wallet connection modal. 3) A modal/dialog appears with wallet options. 4) Click on a wallet option satisfying the wallet_name constraint (e.g. Polkadot.js, MetaMask, SubWallet). 5) Confirm the connection.",
    "VIEW_BLOCK": "PLAYBOOK: 1) Find 'Blocks' link in the navigation. 2) Click it to navigate to the Blocks section. 3) A table of blocks appears. 4) Find the block matching ALL CONSTRAINTS (block_number equals, hash equals, timestamp, transactions count). 5) Click on the matching block row to view details.",
    # ---- New task types from failure analysis ----
    "VIEW_HOTEL_DETAIL": "PLAYBOOK: 1) If currently on a hotel detail page, click Back or 'All Hotels' link first to return to the list. 2) Scroll through hotel cards. 3) For NOT constraints: skip any card where that field matches the excluded value. 4) Match ALL positive constraints (title, price, amenities, host_name, etc.) - the title/price/amenities may require clicking into each hotel to verify. 5) Click View Details or the hotel card title.",
    "REORDER": "PLAYBOOK: 1) Navigate to Orders or Order History section. 2) Find the past order containing the item matching constraints (item name, restaurant). 3) Click Reorder button on that order.",
    "OPEN_SETTINGS": "PLAYBOOK: 1) Look for Settings link in: profile/avatar dropdown menu, gear icon in navbar, or account menu. 2) Click it to open Settings page.",
    "ADD_REMINDER": "PLAYBOOK: 1) Browse events on the calendar. 2) Find the event where the current reminder value satisfies the constraint (e.g. minutes > 14 means find an event whose reminder is currently > 14). 3) Click the event to open it. 4) Find the Reminders field. 5) Add a reminder value satisfying the constraint. 6) Save the event.",
    "OPEN_DM": "PLAYBOOK: 1) Find Direct Messages link or icon in the left sidebar or navigation bar. 2) Click it.",
    "CLEAR_CART": "PLAYBOOK: 1) Navigate to Cart or Shopping Cart. 2) Find items matching constraints (item name, price). 3) Remove items one by one up to the maximum quantity limit specified. 4) Confirm each removal.",
    "PLACE_ORDER": "PLAYBOOK: 1) Navigate to restaurant matching constraints. 2) Find menu item matching ALL constraints (name, price; NOT equals quantity: pick any other). 3) Add to cart. 4) Checkout. 5) Fill phone, address exactly. 6) Set mode (pickup/delivery). 7) Add preferences (contains: type text with substring). 8) Place order.",
    "BOOK_APPOINTMENT": "PLAYBOOK: 1) Browse Doctors list. 2) Skip any doctor where name/speciality matches a NOT constraint. 3) Click Book Appointment on the matching doctor. 4) Fill form fields: date/time/phone/insurance exactly as given; for NOT constraints on patient_name/email/reason pick any value that is NOT the excluded one. 5) Submit the form.",
    "ADD_EXPERIENCE": "PLAYBOOK: 1) Navigate to Profile or Edit Profile page. 2) Find Experience section. 3) Click Add Experience or + button. 4) Fill form: company=exact value, title=any value NOT matching excluded title, location=exact value, description=any text containing the specified substring. 5) Save/Submit.",
    "BACK_TO_ALL_JOBS": "PLAYBOOK: 1) Find and click Back, All Jobs, or Jobs breadcrumb link to return to job list. 2) Scroll through jobs. 3) For NOT constraints: skip any job where that field matches the excluded value. 4) Find job matching ALL constraints (title, company, location). 5) Click to view details.",
    "ABOUT_FEATURE_CLICK": "PLAYBOOK: 1) Navigate to About page (look for About link in navbar). 2) Find feature cards/sections. 3) Click on the feature whose text CONTAINS the specified value.",
    "GENERAL": "PLAYBOOK: Analyze the task carefully, identify the key action required, and execute the most direct path. Use TASK_CONSTRAINTS to find the correct item and fill forms.",
}

# ---------------------------------------------------------------------------
# Search input IDs per website (for search shortcuts)
# ---------------------------------------------------------------------------
SEARCH_INPUT_IDS: dict[str, str] = {
    "automail": "mail-search",
    "autocinema": "input",
    "autodining": "search-field",
    "autodelivery": "food-search",
    "autobooks": "input",
    "autozone": "input",
    "autoconnect": "input",
    "autohealth": "input",
}

# ---------------------------------------------------------------------------
# Known element IDs for quick-click shortcuts
# ---------------------------------------------------------------------------
QUICK_CLICK_IDS: dict[str, str] = {
    "focus_today": "focus-today",
    "new_event": "new-event-cta",
    "add_team": "add-team-btn",
    "wishlist": "favorite-action",
    "spotlight_movie": "spotlight-view-details-btn",
    "featured_book": "featured-book-view-details-btn-1",
    "featured_product": "view-details",
    "nav_about": "nav-about",
}
