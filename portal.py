"""ALPHA PULSE BTC — secure entry point.
Manual Zelle access management; original app.py and signal logic remain unchanged.
"""
import os
import runpy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import streamlit as st
from PIL import Image

logos = sorted(Path(__file__).parent.glob("2649B951*"))
try:
    page_icon = Image.open(logos[0]) if logos else "🔐"
except (OSError, ValueError):
    page_icon = "🔐"

st.set_page_config(page_title="ALPHA PULSE BTC", page_icon=page_icon,
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
h2{text-align:center;font-size:22px!important;color:#edf8f7!important}
.stTextInput label,.stTextInput label p,.stTextInput [data-testid="stWidgetLabel"]{color:#edf8f7!important}
.stTextInput input{background:#0b1e25!important;color:#fff!important;border:1px solid #206158!important;border-radius:11px!important}
.stTextInput input::placeholder{color:#b7c9ca!important;opacity:1!important}
.stTabs [data-baseweb="tab"],.stTabs [data-baseweb="tab"] *, .stTabs button[role="tab"],.stTabs button[role="tab"] *{color:#edf8f7!important;opacity:1!important}
.stTabs [aria-selected="true"],.stTabs [aria-selected="true"] *{color:#00e0bb!important}
.stTabs [data-baseweb="tab-highlight"]{background-color:#00e0bb!important}
[data-testid="stRadio"] label,[data-testid="stRadio"] label *,[data-testid="stRadio"] p,[data-testid="stRadio"] span{color:#edf8f7!important;opacity:1!important}
[data-testid="stRadio"] [role="radiogroup"]{gap:.8rem}
.stButton>button,[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button{background:#00bc9c!important;color:#041914!important;border:1px solid #00dfb5!important;border-radius:12px!important;font-weight:900!important}
.stButton>button[kind="secondary"]{background:#0b1e25!important;color:#fff!important;border:1px solid #00bc9c!important}
.stButton>button p,.stButton>button span,[data-testid="stFormSubmitButton"] button *,[data-testid="stDownloadButton"] button *{color:inherit!important;opacity:1!important}
.stButton>button:hover{background:#00d4b0!important;color:#041914!important}
.stButton>button[kind="secondary"]:hover{background:#123a3b!important;color:#fff!important}
.stMarkdown,.stMarkdown p,.stCaption,.stCaption *,[data-testid="stAlert"] p,[data-testid="stAlert"] div,[data-testid="stWidgetLabel"]{color:#edf8f7}
[data-testid="stAlert"] a{color:#70b7ff!important}
details summary,details summary p{color:#edf8f7!important}
</style>""", unsafe_allow_html=True)


def brand():
    st.markdown("""<div class="brand"><div class="brand-icon">₿↗</div>
    <div class="brand-title">ALPHA PULSE <span>BTC</span></div>
    <div class="brand-sub">PRIVATE BTC SIGNAL PORTAL</div></div>""", unsafe_allow_html=True)


def api(method, path, *, bearer=None, payload=None, params=None):
    headers = {"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json",
               "Authorization": "Bearer " + (bearer or SUPABASE_ANON_KEY)}
    response = requests.request(method, SUPABASE_URL + path, headers=headers,
                                json=payload, params=params, timeout=TIMEOUT)
    try:
        data = response.json()
    except ValueError:
        data = {}
    if not response.ok:
        reason = (data.get("msg") or data.get("error_description") or
                  data.get("message") or data.get("error")) if isinstance(data, dict) else None
        raise RuntimeError(str(reason or "Operación no disponible")[:250])
    return data


def parse_expiry(value):
    if not value:
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result if result.tzinfo else result.replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        return None


def active_expiry(value):
    expiry = parse_expiry(value)
    return expiry is None or expiry > datetime.now(timezone.utc)


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
            session = api("POST", "/auth/v1/token", params={"grant_type": "refresh_token"},
                          payload={"refresh_token": refresh})
            token = session["access_token"]
            st.session_state["alpha_access_token"] = token
            st.session_state["alpha_refresh_token"] = session.get("refresh_token")
            user = api("GET", "/auth/v1/user", bearer=token)
        except Exception:
            st.session_state.pop("alpha_access_token", None)
            st.session_state.pop("alpha_refresh_token", None)
            return None
    uid = user.get("id")
    if not uid:
        return None
    rows = api("GET", "/rest/v1/portal_access", bearer=token,
               params={"select": "approved,expires_at", "id": "eq." + str(uid), "limit": "1"})
    admins = api("GET", "/rest/v1/portal_admins", bearer=token,
                 params={"select": "id", "id": "eq." + str(uid), "limit": "1"})
    access = rows[0] if rows else {}
    approved = bool(access.get("approved"))
    expiry = access.get("expires_at")
    return {"id": uid, "email": user.get("email", ""), "approved": approved,
            "expires_at": expiry, "access_active": approved and active_expiry(expiry),
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


def date_label(value):
    dt = parse_expiry(value)
    return dt.astimezone().strftime("%m/%d/%Y") if dt else "De por vida"


def admin_panel(current):
    token = st.session_state["alpha_access_token"]
    st.subheader("Administrar accesos")
    st.caption("Confirma el pago por Zelle antes de activar o renovar.")
    try:
        rows = api("GET", "/rest/v1/portal_access", bearer=token,
                   params={"select": "id,email,approved,expires_at", "order": "email.asc"})
    except Exception:
        st.error("No se pudo cargar la lista. Revisa los permisos RLS de Supabase.")
        return

    search = st.text_input("Buscar por correo", placeholder="Escribe parte del correo…",
                           key="admin_user_search").strip().lower()
    filtered = [r for r in rows if search in (r.get("email") or "").lower()]
    st.caption(f"{len(filtered)} usuario(s)")

    if not filtered:
        st.info("No hay usuarios que coincidan con esa búsqueda.")

    for row in filtered:
        uid = row["id"]
        email = row.get("email") or uid
        approved = bool(row.get("approved"))
        expiry = row.get("expires_at")
        is_active = approved and active_expiry(expiry)
        status = ("Pendiente" if not approved else
                  "Vencido" if not is_active else
                  "Activo · vence " + date_label(expiry) if expiry else
                  "Activo · de por vida")
        with st.expander(f"{email}  ·  {status}", expanded=False):
            st.write(f"**Correo:** {email}")
            st.write(f"**Estado:** {status}")
            st.write(f"**Vencimiento:** {date_label(expiry)}")
            if expiry and parse_expiry(expiry):
                seconds = (parse_expiry(expiry) - datetime.now(timezone.utc)).total_seconds()
                st.write(f"**Días restantes:** {max(0, int((seconds + 86399) // 86400))}")
            else:
                st.write("**Días restantes:** Sin vencimiento")
            if uid == current["id"]:
                st.caption("Cuenta administradora: no se puede modificar aquí.")
                continue

            duration = st.radio("Acceso después de confirmar el pago",
                ["30 días ($20)", "60 días ($40)", "90 días ($60)", "De por vida"],
                key="duration_" + uid)
            left, right = st.columns(2)
            with left:
                if st.button("Activar / renovar", key="activate_" + uid, use_container_width=True):
                    try:
                        new_expiry = None if duration == "De por vida" else (
                            datetime.now(timezone.utc) + timedelta(days={
                                "30 días ($20)": 30, "60 días ($40)": 60, "90 días ($60)": 90
                            }[duration])).isoformat()
                        api("PATCH", "/rest/v1/portal_access", bearer=token,
                            params={"id": "eq." + uid},
                            payload={"approved": True, "expires_at": new_expiry})
                        st.success("Acceso guardado. El plazo empieza desde ahora.")
                        st.rerun()
                    except Exception:
                        st.error("No se pudo guardar. Revisa las políticas RLS.")
            with right:
                if st.button("Revocar acceso", key="revoke_" + uid, use_container_width=True):
                    try:
                        api("PATCH", "/rest/v1/portal_access", bearer=token,
                            params={"id": "eq." + uid}, payload={"approved": False})
                        st.success("Acceso revocado.")
                        st.rerun()
                    except Exception:
                        st.error("No se pudo revocar. Revisa las políticas RLS.")


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
                session = api("POST", "/auth/v1/token", params={"grant_type": "password"},
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
                        payload={"email": email_new.strip(), "password": password_new})
                    st.success("Solicitud recibida. Confirma tu correo si te llega un mensaje. Después espera la aprobación.")
                except Exception:
                    st.error("No se pudo registrar. Revisa el correo y vuelve a intentarlo.")
    st.stop()

if not current["access_active"] and not current["is_admin"]:
    brand()
    if current["approved"] and current.get("expires_at"):
        st.warning("Tu acceso ha vencido. Contacta al administrador para renovarlo.")
    else:
        st.info("Cuenta registrada. Esperando la autorización del administrador de ALPHA PULSE BTC.")
    if st.button("Cerrar sesión"):
        logout()
    st.stop()

if current["is_admin"]:
    mode = st.radio("Vista", ["Señales BTC", "Administrar usuarios"],
                    horizontal=True, label_visibility="collapsed")
    if mode == "Administrar usuarios":
        brand()
        admin_panel(current)
        if st.button("Cerrar sesión"):
            logout()
        st.stop()

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
