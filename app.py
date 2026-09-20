def auto_process(ticker, round_signal, target, seconds_left, live_price):
    if (
        not st.session_state.auto_paper_enabled
        or not ticker
        or ticker == "--"
    ):
        return

    # Primero resuelve la ronda anterior
    auto_settle_previous(ticker)

    state = round_signal.get("round_state")

    # Si ya entró en este ticker, NO vuelve a entrar
    if ticker in st.session_state.auto_paper_entries:
        trade = st.session_state.auto_paper_entries[ticker]

        if (
            trade["status"] == "OPEN"
            and live_price is not None
        ):
            trade["last_seen_btc"] = float(live_price)

        st.session_state.auto_previous_ticker = ticker
        return

    # Todavía no hay señal
    if not state:
        st.session_state.auto_previous_ticker = ticker
        return

    direction = state.get("active_direction")

    if direction not in ("UP", "DOWN"):
        st.session_state.auto_previous_ticker = ticker
        return

    # No entrar demasiado tarde
    if (
        seconds_left is None
        or seconds_left <= NEW_ENTRY_LOCK
    ):
        st.session_state.auto_previous_ticker = ticker
        return

    # Necesitamos target
    if target is None:
        st.session_state.auto_previous_ticker = ticker
        return

    # Precio ACTUAL del contrato
    if direction == "UP":
        px = get_yes_ask(market)
    else:
        px = get_no_ask(market)

    if px is None:
        st.session_state.auto_previous_ticker = ticker
        return

    px = float(px)

    # =====================================================
    # FILTRO DE MEJOR ENTRADA
    # =====================================================

    score = float(sig["final_score"])
    mom3 = float(sig["mom3"])
    mom5 = float(sig["mom5"])
    distance = sig["distance"]

    # 1. Señal suficientemente fuerte
    if direction == "UP":
        strong_signal = (
            score >= 4.75
            and mom3 > 0
            and mom5 >= 0
        )
    else:
        strong_signal = (
            score <= -4.75
            and mom3 < 0
            and mom5 <= 0
        )

    # 2. No comprar contratos demasiado caros
    good_price = (
        0.25 <= px <= 0.65
    )

    # 3. BTC debe estar apoyando la dirección
    if distance is None:
        target_support = False

    elif direction == "UP":
        target_support = distance > -35

    else:
        target_support = distance < 35

    # 4. Evitar una entrada con warning de reversión
    no_reversal_warning = not round_signal.get(
        "reversal",
        False
    )

    # =====================================================
    # ENTRAR SOLAMENTE SI TODO CUADRA
    # =====================================================

    best_entry = (
        strong_signal
        and good_price
        and target_support
        and no_reversal_warning
    )

    if best_entry:

        amount = int(
            st.session_state.auto_paper_amount
        )

        contracts = max(
            1,
            int(amount // px)
        )

        st.session_state.auto_paper_entries[ticker] = {
            "ticker": ticker,
            "direction": direction,
            "amount": amount,
            "entry_price": px,
            "contracts": contracts,
            "paper_cost": contracts * px,
            "target": float(target),
            "status": "OPEN",
            "last_seen_btc": live_price,
            "result": None
        }

    st.session_state.auto_previous_ticker = ticker
