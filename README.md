# STUDIO101 🎬

STUDIO101 is a dynamic, high-performance web application designed for a premier creative production studio. Built with a robust Django backend and a lightweight, framework-free frontend (HTML5, CSS3, Vanilla ES6 JS), it delivers a cinematic user experience without sacrificing load speeds or scalability.

---

## 📸 Key Features

* **Dynamic Service Showcases:** Dedicated management for Podcast, Photography, Music Video, and Short Film services.
* **Portfolio & Case Studies:** Filterable project showcase linked directly to core services via Django ORM relationships.
* **Live Streaming Integration:** Dedicated live streaming section featuring embedded player capabilities (YouTube Live, Facebook Live, custom RTMP providers) managed directly from the Django Admin.
* **Booking Request Pipeline:** Lightweight V1 inquiry system for studio hire, equipment reservation, and service consultations.
* **Client-Ready Admin Panel:** Fully customized Django Admin interface allowing non-technical studio operators to update content, media, and stream links.
* **Performance-First Design System:** Responsive, dark-themed UI (Burgundy `#5c0a22` & Black `#050505`) built with custom CSS design tokens—zero heavy frontend frameworks (No React/Bootstrap/Tailwind).

---

## 🛠️ Tech Stack

* **Backend:** Python 3.14+, Django 5.x
* **Database:** SQLite (Development) / PostgreSQL (Production ready)
* **Frontend:** HTML5, CSS3 (Custom Properties), Vanilla JavaScript (ES6)
* **Static Asset Management:** WhiteNoise

---

## 📂 Project Structure

```text
STUDIO_101/
├── apps/
│   ├── core/         # Home page, shared components, static pages
│   ├── services/     # Studio services & dynamic service pages
│   ├── portfolio/    # Portfolio items & project detail pages
│   ├── studio/       # Physical facility layout, equipment, & hire
│   ├── streams/      # Live streaming & video embed management
│   └── bookings/     # Client booking request pipeline
├── config/           # Django project configuration & WSGI/ASGI
├── templates/        # Modular HTML templates & components
├── static/           # CSS stylesheets, ES6 JS modules, media assets
├── .env              # Environment variables (secret)
├── .gitignore        # Git exclusion setup
├── manage.py         # Django CLI entrypoint
└── requirements.txt  # Project dependencies

🚀 Quick Start (Local Setup)
Follow these steps to set up the project locally.

1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

2. Clone the Repository
Bash
git clone [https://github.com/YOUR_USERNAME/STUDIO_101.git](https://github.com/YOUR_USERNAME/STUDIO_101.git)
cd STUDIO_101
3. Set Up Virtual Environment
Windows (CMD):

DOS
python -m venv .venv
.venv\Scripts\activate
macOS / Linux:

Bash
python3 -m venv .venv
source .venv/bin/activate
4. Install Dependencies
Bash
pip install -r requirements.txt
5. Run Migrations
Bash
python manage.py makemigrations
python manage.py migrate
6. Create Superuser (Admin Access)
Bash
python manage.py createsuperuser
7. Run Development Server
Bash
python manage.py runserver
Navigate to http://127.0.0.1:8000/ in your web browser. Access the admin dashboard at http://127.0.0.1:8000/admin/.

📺 Managing Live Streams
To display a live stream on the frontend:

Log into /admin.

Navigate to Live Streams -> Add Live Stream.

Select your provider platform (YouTube, Facebook, etc.).

Paste the iframe embed URL (e.g., https://www.youtube.com/embed/YOUR_VIDEO_ID).

Toggle Is Live and Is Active to True and save.

📄 License
This project is proprietary and built specifically for STUDIO101. All rights reserved.