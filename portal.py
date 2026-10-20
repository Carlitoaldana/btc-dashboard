"""ALPHA PULSE BTC — secure entry point. Original app.py remains unchanged."""

import os
import runpy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import streamlit as st
from PIL import Image


# Logo
_logo_candidates = sorted(Path(__file__).parent.glob("2649B951*"))

try:
    _page_icon = Image.open(_logo_candidates[0]) if _logo_candidates else "🔐"
except (OSError, ValueError):
    _page_icon = "🔐"

st.set_page_config(
    page_title="ALPHA PULSE BTC",
    page_icon=_page_icon,
    layout="centered",
    initial_sidebar_state="collapsed",
)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()
TIMEOUT = 12


# Diseño original
st.markdown(
    """
<style>
#MainMenu,footer,header,
[data-testid="stToolbar"],
[data-testid="stDecoration"]{
    display:none!important
}

.stApp{
    background:radial-gradient(
        circle at 50% 0%,
        #123a3b 0%,
        #07131b 38%,
        #04090e 100%
    );
    color:#edf8f7
}

.block-container{
    max-width:450px!important;
    padding:38px 20px 30px!important
}

.brand{
    text-align:center;
    margin:22px 0 28px
}

.brand-icon{
    width:92px;
    height:92px;
    margin:0 auto 12px;
    border:2px solid #00ddb8;
    border-radius:24px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:42px;
    font-weight:950;
    color:#00e0bb;
    box-shadow:0 0 27px #00caaa33;
    background:#061a20
}

.brand-title{
    font-size:29px;
    line-height:1.06;
    font-weight:950;
    letter-spacing:1px
}

.brand-title span{
    color:#00dfb5
}

.brand-sub{
    font-size:11px;
    color:#92b7b5;
    letter-spacing:2px;
    margin-top:8px
}

h2{
    text-align:center;
    font-size:22px!important;
    color:#edf8f7!important
}

.stTextInput label,
.stTextInput label p,
.stTextInput [data-testid="stWidgetLabel"]{
    color:#edf8f7!important
}

.stTextInput input{
    background:#0b1e25!important;
    color:#fff!important;
    border:1px solid #206158!important;
    border-radius:11px!important
}

.stTextInput input::placeholder{
    color:#b7c9ca!important;
    opacity:1!important
}

.stTabs [data-baseweb="tab"],
.stTabs [data-baseweb="tab"] *,
.stTabs button[role="tab"],
.stTabs button[role="tab"] *{
    color:#edf8f7!important;
    opacity:1!important
}

.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] *{
    color:#00e0bb!important
}

.stTabs [data-baseweb="tab-highlight"]{
    background-color:#00e0bb!important
}

[data-testid="stRadio"] label,
[data-testid="stRadio"] label *,
[data-testid="stRadio"] p,
[data-testid="stRadio"] span{
    color:#edf8f7!important;
    opacity:1!important
}

[data-testid="stRadio"] [role="radiogroup"]{
    gap:0.8rem
}

.stButton>button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stDownloadButton"] button{
    background:#00bc9c!important;
    color:#041914!important;
    border:1px solid #00dfb5!important;
    border-radius:12px!important;
    font-weight:900!important
}

.stButton>button[kind="secondary"]{
    background:#0b1e25!important;
    color:#ffffff!important;
    border:1px solid #00bc9c!important
}

.stButton>button p,
.stButton>button span,
[data-testid="stFormSubmitButton"] button *,
[data-testid="stDownloadButton"] button *{
    color:inherit!important;
    opacity:1!important
}

.stButton>button:hover{
    background:#00d4b0!important;
    color:#041914!important
}

.stButton>button[kind="secondary"]:hover{
    background:#123a3b!important;
    color:#ffffff!important
}

.stMarkdown,
.stMarkdown p,
.stCaption,
.stCaption *,
[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stWidgetLabel"]{
    color:#edf8f7
}

[data-testid="stAlert"] a{
    color:#70b7ff!important
}
</style>
""",
    unsafe_allow_html=True,
)


def brand():
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">₿↗</div>
            <div class="brand-title">
                ALPHA PULSE <span>BTC</span>
            </div>
            <div class="brand-sub">
                PRIVATE BTC SIGNAL PORTAL
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def api(method, path, *, bearer=None, payload=None, params=None):
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }

    headers["Authorization"] = (
        "Bearer " + (bearer or SUPABASE_ANON_KEY)
    )

    response = requests.request(
        method,
        SUPABASE_URL + path,
        headers=headers,
        json=payload,
        params=params,
        timeout=TIMEOUT,
    )

    try:
        data = response.json()
    except ValueError:
        data = {}

    if not response.ok:
        if isinstance(data, dict):
            reason = (
                data.get("msg")
                or data.get("error_description")
                or data.get("message")
                or data.get("error")
            )
        else:
            reason = None

        raise RuntimeError(
            str(reason or "Operación no disponible")[:250]
        )

    return data


def parse_expiry(value):
    if not value:
        return None

    dt = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    if dt.tzinfo:
        return dt

    return dt.replace(tzinfo=timezone.utc)


def access_active(row, now=None):
    if not row or not row.get("approved"):
        return False

    expiry = parse_expiry(row.get("expires_at"))

    return (
        expiry is None
        or expiry > (now or datetime.now(timezone.utc))
    )


def extend_expiry(value, days, now=None):
    now = now or datetime.now(timezone.utc)

    previous = parse_expiry(value)

    if previous and previous > now:
        base = previous
    else:
        base = now

    return (
        base + timedelta(days=days)
    ).isoformat()


def verify_session():
    token = st.session_state.get("alpha_access_token")
    refresh = st.session_state.get("alpha_refresh_token")

    if not token:
        return None

    try:
        user = api(
            "GET",
            "/auth/v1/user",
            bearer=token,
        )

    except Exception:
        if not refresh:
            st.session_state.pop(
                "alpha_access_token", None
            )
            return None

        try:
            session = api(
                "POST",
                "/auth/v1/token",
                params={
                    "grant_type": "refresh_token"
                },
                payload={
                    "refresh_token": refresh
                },
            )

            token = session["access_token"]

            st.session_state[
                "alpha_access_token"
            ] = token

            st.session_state[
                "alpha_refresh_token"
            ] = session.get("refresh_token")

            user = api(
                "GET",
                "/auth/v1/user",
                bearer=token,
            )

        except Exception:
            st.session_state.pop(
                "alpha_access_token", None
            )

            st.session_state.pop(
                "alpha_refresh_token", None
            )

            return None

    user_id = user.get("id")

    if not user_id:
        return None

    rows = api(
        "GET",
        "/rest/v1/portal_access",
        bearer=token,
        params={
            "select": "approved,expires_at",
            "id": "eq." + str(user_id),
            "limit": "1",
        },
    )

    admins = api(
        "GET",
        "/rest/v1/portal_admins",
        bearer=token,
        params={
            "select": "id",
            "id": "eq." + str(user_id),
            "limit": "1",
        },
    )

    approved = bool(
        rows
        and (
            access_active(rows[0])
            or (
                bool(admins)
                and bool(rows[0].get("approved"))
            )
        )
    )

    return {
        "id": user_id,
        "email": user.get("email", ""),
        "approved": approved,
        "is_admin": bool(admins),
    }


def logout():
    token = st.session_state.pop(
        "alpha_access_token", None
    )

    st.session_state.pop(
        "alpha_refresh_token", None
    )

    if token:
        try:
            api(
                "POST",
                "/auth/v1/logout",
                bearer=token,
            )
        except Exception:
            pass

    st.rerun()


def admin_panel(current):
    token = st.session_state[
        "alpha_access_token"
    ]

    st.subheader("Administrar accesos")

    search = st.text_input(
        "Buscar cliente por correo",
        placeholder="Escribe un email...",
    )

    try:
        rows = api(
            "GET",
            "/rest/v1/portal_access",
            bearer=token,
            params={
                "select": (
                    "id,email,approved,expires_at"
                ),
                "order": "email.asc",
            },
        )

    except Exception:
        st.error(
            "No se pudo cargar la lista de usuarios."
        )
        return

    filtered = [
        row
        for row in rows
        if search.strip().lower()
        in str(
            row.get("email") or ""
        ).lower()
    ]

    if not filtered:
        st.info(
            "No hay usuarios que coincidan "
            "con la búsqueda."
        )

    now = datetime.now(timezone.utc)

    for row in filtered:
        label = (
            row.get("email")
            or row["id"]
        )

        approved = bool(
            row.get("approved")
        )

        expiry = parse_expiry(
            row.get("expires_at")
        )

        active = access_active(
            row, now
        )

        if approved and expiry is None:
            status = "De por vida"

        elif active:
            remaining = max(
                1,
                (
                    expiry
                    - now
                    + timedelta(days=1)
                    - timedelta(microseconds=1)
                ).days,
            )

            status = (
                f"Activo · {remaining} "
                "días restantes"
            )

        elif approved and expiry:
            status = "Vencido"

        else:
            status = "Pendiente o revocado"

        with st.expander(
            f"{label} — {status}"
        ):
            if expiry:
                st.write(
                    "Vence: "
                    + expiry.astimezone(
                        timezone.utc
                    ).strftime(
                        "%d/%m/%Y %H:%M UTC"
                    )
                )

            else:
                st.write(
                    "Sin fecha de vencimiento"
                )

            if row["id"] == current["id"]:
                st.caption(
                    "Cuenta administradora. "
                    "No se modifica desde aquí."
                )
                continue

            plan = st.selectbox(
                "Plan",
                [
                    "30 días — $20",
                    "60 días — $40",
                    "90 días — $60",
                    "De por vida",
                ],
                key="plan_" + row["id"],
            )

            days = {
                "30 días — $20": 30,
                "60 días — $40": 60,
                "90 días — $60": 90,
            }.get(plan)

            if not approved or (
                expiry and not active
            ):
                if st.button(
                    "Aprobar acceso",
                    key="approve_" + row["id"],
                ):
                    payload = {
                        "approved": True,
                        "expires_at": (
                            extend_expiry(
                                row.get("expires_at"),
                                days,
                            )
                            if days
                            else None
                        ),
                    }

                    try:
                        api(
                            "PATCH",
                            "/rest/v1/portal_access",
                            bearer=token,
                            params={
                                "id": "eq." + row["id"]
                            },
                            payload=payload,
                        )

                        st.rerun()

                    except Exception:
                        st.error(
                            "No se pudo aprobar "
                            "el acceso. Revisa los "
                            "permisos de Supabase."
                        )

            elif expiry is not None:
                if st.button(
                    "Renovar / ampliar",
                    key="renew_" + row["id"],
                ):
                    payload = {
                        "expires_at": (
                            extend_expiry(
                                row.get("expires_at"),
                                days,
                            )
                            if days
                            else None
                        )
                    }

                    try:
                        api(
                            "PATCH",
                            "/rest/v1/portal_access",
                            bearer=token,
                            params={
                                "id": "eq." + row["id"]
                            },
                            payload=payload,
                        )

                        st.rerun()

                    except Exception:
                        st.error(
                            "No se pudo renovar. "
                            "Revisa los permisos "
                            "de Supabase."
                        )

            else:
                st.caption(
                    "Este usuario ya tiene "
                    "acceso de por vida."
                )

            if approved and st.button(
                "Revocar acceso",
                key="revoke_" + row["id"],
            ):
                try:
                    api(
                        "PATCH",
                        "/rest/v1/portal_access",
                        bearer=token,
                        params={
                            "id": "eq." + row["id"]
                        },
                        payload={
                            "approved": False
                        },
                    )

                    st.rerun()

                except Exception:
                    st.error(
                        "No se pudo revocar "
                        "el acceso."
                    )


# Verificar configuración
if (
    not SUPABASE_URL.startswith("https://")
    or not SUPABASE_ANON_KEY
):
    brand()

    st.error(
        "Falta configurar SUPABASE_URL "
        "y SUPABASE_ANON_KEY en "
        "Render → Environment."
    )

    st.stop()


# Verificar sesión
try:
    current = verify_session()

except Exception:
    brand()

    st.error(
        "No se pudo verificar el acceso. "
        "Reintenta en unos segundos."
    )

    st.stop()


# Inicio de sesión y registro
if current is None:
    brand()

    login_tab, register_tab = st.tabs(
        [
            "Sign In",
            "Create Account",
        ]
    )

    with login_tab:
        with st.form("alpha_login"):
            email = st.text_input(
                "Email",
                key="login_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            submit = st.form_submit_button(
                "Sign In",
                use_container_width=True,
            )

        if submit:
            try:
                session = api(
                    "POST",
                    "/auth/v1/token",
                    params={
                        "grant_type": "password"
                    },
                    payload={
                        "email": email.strip(),
                        "password": password,
                    },
                )

                st.session_state[
                    "alpha_access_token"
                ] = session["access_token"]

                st.session_state[
                    "alpha_refresh_token"
                ] = session.get(
                    "refresh_token"
                )

                st.rerun()

            except Exception:
                st.error(
                    "No se pudo iniciar sesión. "
                    "Comprueba tus datos y "
                    "confirma tu correo."
                )

    with register_tab:
        with st.form("alpha_register"):
            email_new = st.text_input(
                "Email",
                key="register_email",
            )

            password_new = st.text_input(
                "Password (mínimo 8 caracteres)",
                type="password",
                key="register_password",
            )

            submit_new = st.form_submit_button(
                "Create Account",
                use_container_width=True,
            )

        if submit_new:
            if len(password_new) < 8:
                st.error(
                    "La contraseña debe tener "
                    "al menos 8 caracteres."
                )

            else:
                try:
                    api(
                        "POST",
                        "/auth/v1/signup",
                        payload={
                            "email": email_new.strip(),
                            "password": password_new,
                        },
                    )

                    st.success(
                        "Solicitud recibida. "
                        "Confirma tu correo si "
                        "te llega un mensaje. "
                        "Después espera "
                        "la aprobación."
                    )

                except Exception:
                    st.error(
                        "No se pudo registrar. "
                        "Revisa el correo y "
                        "vuelve a intentarlo."
                    )

    st.stop()


# Usuario sin acceso vigente
if not current["approved"]:
    brand()

    st.info(
        "Cuenta registrada. "
        "Esperando la autorización "
        "del administrador de "
        "ALPHA PULSE BTC."
    )

    if st.button("Cerrar sesión"):
        logout()

    st.stop()


# Panel del administrador
if current["is_admin"]:
    mode = st.radio(
        "Vista",
        [
            "Señales BTC",
            "Administrar usuarios",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    if mode == "Administrar usuarios":
        brand()

        admin_panel(current)

        if st.button("Cerrar sesión"):
            logout()

        st.stop()


# Ejecutar el bot original sin modificar app.py
original = Path(__file__).with_name(
    "app.py"
)

if not original.exists():
    st.error(
        "El archivo app.py del bot "
        "no está presente."
    )

    st.stop()

st.query_params.clear()

old_set_page_config = st.set_page_config

try:
    st.set_page_config = (
        lambda *args, **kwargs: None
    )

    runpy.run_path(
        str(original),
        run_name="__main__",
    )

finally:
    st.set_page_config = (
        old_set_page_config
    )
