def auto_process(ticker, round_signal, target, seconds_left, live_price):
    if not st.session_state.auto_paper_enabled or not ticker or ticker == "--":
        return

    auto_settle_previous(ticker)

    state = round_signal.get("round_state")

    if (
        state
        and state.get("first_direction")
        and ticker not in st.session_state.auto_paper_entries
    ):
        px = state.get("first_signal_price")

        if (
            px is not None
            and target is not None
            and not (
                seconds_left is not None
                and seconds_left <= NEW_ENTRY_LOCK
            )
        ):
            amount = int(
                st.session_state.auto_paper_amount
            )

            contracts = max(
                1,
                int(amount // float(px))
            )

            st.session_state.auto_paper_entries[ticker] = {
                "ticker": ticker,
                "direction": state["first_direction"],
                "amount": amount,
                "entry_price": float(px),
                "contracts": contracts,
                "paper_cost": contracts * float(px),
                "target": float(target),
                "status": "OPEN",
                "last_seen_btc": live_price,
                "result": None
            }

    trade = st.session_state.auto_paper_entries.get(ticker)

    if (
        trade
        and trade["status"] == "OPEN"
        and live_price is not None
    ):
        trade["last_seen_btc"] = float(live_price)

    st.session_state.auto_previous_ticker = ticker
