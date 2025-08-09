Here’s a README.md you can copy into your project root so GitHub shows all the instructions clearly:


---

# People Helping Each Other 💰🌐

A fully functional donation tracking web application built with **Flask (Python)**.  
Users can **register**, **login**, **logout**, **view their personal dashboard**, and **provide/request donations** in **PiCoin**, with real-time PHP conversion.  

The site features:
- **Pi Network sole donation address**:  
  `MALYJFJ5SVD45FBWN2GT4IW67SEZ3IBOFSBSPUFCWV427NBNLG3PWAAAAAAAAIR37PBGG`  
  *(Copy button available in the UI)*  
- Provide/request donation buttons with amount entry and PHP equivalent in real-time.
- Dashboard graph showing:
  - Provided donations
  - Requested donations
  - Compound earnings (+30% per month)
- Pending status display until approved.
- Admin approval by editing a code in `donations.txt` and adding `/` before it.
- All data stored in simple `.txt` files, human-readable in Notepad/WordPad.

---

## 📂 Project Structure

DonationSite/ │ ├── app.py                  # Main Flask backend ├── templates/              # HTML files (Jinja2 templates) │   ├── base.html │   ├── login.html │   ├── register.html │   ├── dashboard.html │ ├── static/ │   ├── css/ │   │   └── style.css       # Business-style theme + animations │   ├── js/ │   │   └── script.js       # Copy button, API fetch for PiCoin price │ ├── users.txt               # Stores user login data ├── donations.txt           # Stores provided/requested donations + status ├── transactions.txt        # Logs all transactions └── README.md               # This file

---

## 🚀 How to Run Locally

### 1️⃣ Install Python
Make sure Python 3.8+ is installed:  
[Download Python](https://www.python.org/downloads/)

### 2️⃣ Install Dependencies
Open a terminal in the project folder and run:
```bash
pip install flask requests werkzeug

3️⃣ Run the Server

python app.py

The app will be available at:

http://127.0.0.1:5000


---

🛠 Admin Approval Process

When a user provides or requests a donation, a code is generated (e.g., REQ12345).
To approve:

1. Open donations.txt


2. Find the line with the request


3. Add / before the code (e.g., /REQ12345)


4. Save the file


5. The dashboard will automatically update for the user.




---

💹 Real-Time PiCoin Conversion

The PHP value of PiCoin is fetched in real-time via the CoinGecko API.


---

📤 Deploy to GitHub

1. Create a new repository on GitHub.


2. On your local machine, open the project folder in a terminal:



git init
git add .
git commit -m "Initial commit - Pi Network Donation Site"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main

3. Your project will now be visible on GitHub.




---

📜 License

This project is open-source and free to use.


---

💡 Note: This site does NOT process Pi transactions automatically — it only tracks and records them for your reference.

---

I can now prepare **all the actual code files** exactly matching this README so you can run it immediately and push to GitHub.  
Do you want me to give you **everything in one complete code block** so you can copy-paste into your folders?

