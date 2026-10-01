import os, re, sqlite3, hashlib, hmac
from pathlib import Path
import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "hath_users.db"

def _db():
    conn=sqlite3.connect(DB_PATH); conn.execute("CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP, login_count INTEGER DEFAULT 0, last_login TEXT)"); conn.commit(); return conn

def _hash(password): return hashlib.pbkdf2_hmac("sha256", password.encode(), os.getenv("HATH_PASSWORD_SALT","hath-hackers-local-salt").encode(), 240000).hex()

def _valid_email(email): return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@gmail\.com", email.strip(), re.I))

def login_screen():
    st.markdown('<div class="login-card"><div class="login-brand">HATH HACKERS</div><h1>AI Data Intelligence</h1><p>Your private workspace for analysis, insights and reporting.</p></div>', unsafe_allow_html=True)
    tab1,tab2=st.tabs(["Sign in","Create account"] )
    with tab1:
        with st.form("login_form"):
            email=st.text_input("Gmail address",placeholder="name@gmail.com")
            password=st.text_input("Password",type="password")
            submit=st.form_submit_button("Sign in",use_container_width=True,type="primary")
        if submit:
            if not _valid_email(email): st.error("Use a valid @gmail.com address.")
            else:
                conn=_db(); row=conn.execute("SELECT password_hash FROM users WHERE email=?",(email.strip().lower(),)).fetchone()
                if row and hmac.compare_digest(row[0],_hash(password)):
                    conn.execute("UPDATE users SET login_count=login_count+1,last_login=CURRENT_TIMESTAMP WHERE email=?",(email.strip().lower(),)); conn.commit(); conn.close()
                    st.session_state.user={"email":email.strip().lower()}; st.rerun()
                else: conn.close(); st.error("Incorrect Gmail address or password, or create an account first.")
    with tab2:
        with st.form("register_form"):
            email2=st.text_input("Gmail address",key="reg_email",placeholder="name@gmail.com")
            p1=st.text_input("Create password",type="password",key="reg_password")
            p2=st.text_input("Confirm password",type="password",key="reg_confirm")
            submit2=st.form_submit_button("Create account",use_container_width=True)
        if submit2:
            if not _valid_email(email2): st.error("Registration is limited to @gmail.com addresses.")
            elif len(p1)<8: st.error("Use at least 8 characters for your password.")
            elif p1!=p2: st.error("Passwords do not match.")
            else:
                try:
                    conn=_db(); conn.execute("INSERT INTO users(email,password_hash) VALUES (?,?)",(email2.strip().lower(),_hash(p1))); conn.commit(); conn.close(); st.success("Account created. Sign in to continue.")
                except sqlite3.IntegrityError: st.error("An account already exists for this Gmail address.")

def user_metrics():
    conn=_db(); total=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]; logins=conn.execute("SELECT COALESCE(SUM(login_count),0) FROM users").fetchone()[0]; recent=conn.execute("SELECT email,last_login,login_count FROM users ORDER BY last_login DESC LIMIT 10").fetchall(); conn.close(); return total,logins,recent
