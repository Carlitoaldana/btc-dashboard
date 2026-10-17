"""ALPHA PULSE BTC — secure entry point. Original app.py remains unchanged."""
import os
import runpy
from pathlib import Path
import requests
import streamlit as st

st.set_page_config(page_title="ALPHA PULSE BTC", page_icon="🔐",
                   layout="centered", initial_sidebar_state="collapsed")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()
TIMEOUT = 12

st.markdown("""<style>
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important}
.stApp{background:radial-gradient(circle at 50% 0%,#123a3b 0%,#07131b 38%,#04090e 100%);color:#edf8f7}
.block-container{max-width:450px!important;padding:38px 20px 30px!important}
.brand{text-align:center;margin:22px 0 28px}.brand-icon{width:92px;height:92px;margin:0 auto 12px;border:2px solid #00ddb8;border-radius:24px;display:flex;align-items:center;justify-content:center;font-size:42px;font-weight:950;color:#00e0bb;box-shadow:0 0 27px #00caaa33;background:#061a20}
.brand-title{font-size:29px;line-height:1.06;font-weight:950;letter-spacing:1px}.brand-title span{color:#00dfb5}
.brand-sub{font-size:11px;color:#92b7b5;letter-spacing:2px;margin-top:8px}
h2{text-align:center;font-size:22px!important}
.stTextInput input{background:#0b1e25!important;color:#fff!important;border:1px solid #206158!important;border-radius:11px!important}
[data-testid="stFormSubmitButton"] button,.stButton>button[kind="primary"]{background:#00bc9c!important;color:#041914!important;border:0!important;border-radius:12px!important;font-weight:900!important;width:100%}
.stButton>button{border-color:#206158}
.stTabs [data-baseweb="tab"]{color:#a3b9b9!important}
.stTabs [aria-selected="true"]{color:#00e0bb!important}
</style>""", unsafe_allow_html=True)

def brand():
    st.markdown("""<div class="brand"><div class="brand-icon">₿↗</div>
    <div class="brand-title">ALPHA PULSE <span>BTC</span></div>
    <div class="brand-sub">PRIVATE BTC SIGNAL PORTAL</div></div>""",
    unsafe_allow_html=True)

def api(method, path, *, bearer=None, payload=None, params=None):
    headers = {"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}
    headers["Authorization"] = "Bearer " + (bearer or SUPABASE_ANON_KEY)
    response = requests.request(method, SUPABASE_URL + path, headers=headers,
                                json=payload, params=params, timeout=TIMEOUT)
    try:
        data = response.json()
    except ValueError:
        data = {}
    if not response.ok:
        if isinstance(data, dict):
            reason = (data.get("msg") or data.get("error_description") or
                      data.get("message") or data.get("error"))
        else:
            reason = None
        raise RuntimeError(str(reason or "Operación no disponible")[:250])
    return data

def verify_session():
    token = st.session_state.get("alpha_access_token")
    refresh = st.session_state.get("alpha_refresh_token")
    if not token:
        return None
    try:
        user = api("GET", "/auth/v1/user", bearer=token)
    except Exception:
        if not refresh:
            st.session_state.pop("alpha_access_token", None)
            return None
        try:
            session = api("POST", "/auth/v1/token",
                          params={"grant_type": "refresh_token"},
                          payload={"refresh_token": refresh})
            token = session["access_token"]
            st.session_state["alpha_access_token"] = token
            st.session_state["alpha_refresh_token"] = session.get("refresh_token")
            user = api("GET", "/auth/v1/user", bearer=token)
        except Exception:
            st.session_state.pop("alpha_access_token", None)
            st.session_state.pop("alpha_refresh_token", None)
            return None
    user_id = user.get("id")
    if not user_id:
        return None
    rows = api("GET", "/rest/v1/portal_access", bearer=token,
               params={"select": "approved", "id": "eq." + str(user_id),
                       "limit": "1"})
    admins = api("GET", "/rest/v1/portal_admins", bearer=token,
                 params={"select": "id", "id": "eq." + str(user_id),
                         "limit": "1"})
    return {"id": user_id, "email": user.get("email", ""),
            "approved": bool(rows and rows[0].get("approved")),
            "is_admin": bool(admins)}

def logout():
    token = st.session_state.pop("alpha_access_token", None)
    st.session_state.pop("alpha_refresh_token", None)
    if token:
        try:
            api("POST", "/auth/v1/logout", bearer=token)
        except Exception:
            pass
    st.rerun()

def admin_panel(current):
    # Only a verified admin can reach this panel. Supabase RLS independently
    # enforces the same rule on every read and update.
    token = st.session_state["alpha_access_token"]
    st.subheader("Administrar accesos")
    try:
        rows = api("GET", "/rest/v1/portal_access", bearer=token,
                   params={"select": "id,email,approved", "order": "email.asc"})
    except Exception:
        st.error("No se pudo cargar la lista de usuarios.")
        return
    if not rows:
        st.info("Todavía no hay usuarios registrados.")
    for row in rows:
        label = row.get("email") or row["id"]
        approved = bool(row["approved"])
        st.write(f"**{label}** — {'Aprobado' if approved else 'Pendiente o revocado'}")
        if row["id"] == current["id"]:
            st.caption("Cuenta administradora (no se puede revocar aquí).")
            continue
        action = "Revocar acceso" if approved else "Aprobar acceso"
        if st.button(action, key="access_" + row["id"]):
            try:
                api("PATCH", "/rest/v1/portal_access", bearer=token,
                    params={"id": "eq." + row["id"]},
                    payload={"approved": not approved})
                st.rerun()
            except Exception:
                st.error("No se pudo cambiar el acceso. Inténtalo nuevamente.")

if not SUPABASE_URL.startswith("https://") or not SUPABASE_ANON_KEY:
    brand()
    st.error("Falta configurar SUPABASE_URL y SUPABASE_ANON_KEY en Render → Environment.")
    st.stop()
try:
    current = verify_session()
except Exception:
    brand()
    st.error("No se pudo verificar el acceso. Reintenta en unos segundos.")
    st.stop()

if current is None:
    brand()
    login_tab, register_tab = st.tabs(["Sign In", "Create Account"])
    with login_tab:
        with st.form("alpha_login"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
        if submit:
            try:
                session = api("POST", "/auth/v1/token",
                              params={"grant_type": "password"},
                              payload={"email": email.strip(), "password": password})
                st.session_state["alpha_access_token"] = session["access_token"]
                st.session_state["alpha_refresh_token"] = session.get("refresh_token")
                st.rerun()
            except Exception:
                st.error("No se pudo iniciar sesión. Comprueba tus datos y confirma tu correo.")
    with register_tab:
        with st.form("alpha_register"):
            email_new = st.text_input("Email", key="register_email")
            password_new = st.text_input("Password (mínimo 8 caracteres)",
                                         type="password", key="register_password")
            submit_new = st.form_submit_button("Create Account", use_container_width=True)
        if submit_new:
            if len(password_new) < 8:
                st.error("La contraseña debe tener al menos 8 caracteres.")
            else:
                try:
                    api("POST", "/auth/v1/signup",
                        payload={"email": email_new.strip(),
                                 "password": password_new})
                    st.success("Solicitud recibida. Confirma tu correo si te llega un mensaje. Después espera la aprobación.")
                except Exception:
                    st.error("No se pudo registrar. Revisa el correo y vuelve a intentarlo.")
    st.stop()

if not current["approved"]:
    brand()
    st.info("Cuenta registrada. Esperando la autorización del administrador de ALPHA PULSE BTC.")
    if st.button("Cerrar sesión"):
        logout()
    st.stop()

if current["is_admin"]:
    # Separate admin page: regular bot view remains unchanged.
    mode = st.radio("Vista", ["Señales BTC", "Administrar usuarios"],
                    horizontal=True, label_visibility="collapsed")
    if mode == "Administrar usuarios":
        brand()
        admin_panel(current)
        if st.button("Cerrar sesión"):
            logout()
        st.stop()

# Existing bot executes only after authenticated approval.
original = Path(__file__).with_name("app.py")
if not original.exists():
    st.error("El archivo app.py del bot no está presente.")
    st.stop()
st.query_params.clear()
old_set_page_config = st.set_page_config
try:
    st.set_page_config = lambda *args, **kwargs: None
    runpy.run_path(str(original), run_name="__main__")
finally:
    st.set_page_config = old_set_page_config
