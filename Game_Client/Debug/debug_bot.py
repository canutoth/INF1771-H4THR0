# DEBUG DO BOT

class BotDebugManager:
    def __init__(self):
        self.debug_enabled = False
        self.filter_enabled = True
        self.seen = {}           

    # -------- CONTROLE --------
    def toggle_debug(self):
        self.debug_enabled = not self.debug_enabled

    def toggle_filter(self):
        self.filter_enabled = not self.filter_enabled
        if self.filter_enabled:
            self.seen.clear()

    # -------- FILTRO --------
    def should_show_message(self, message, category):
        if category == "OBS" and ("['none']" in message or "observations: none" in message.lower()):
            return False
        if not self.debug_enabled:
            return False
        if not self.filter_enabled:        
            return True
        if message in self.seen.get(category, set()):
            return False
        self.seen.setdefault(category, set()).add(message)
        return True

    def print_debug(self, message, category="INFO"):
        if self.should_show_message(message, category):
            print(f"# {message}")

    
    # ---------- SAÍDA ----------
    def print_debug(self, message, category="INFO"):
        if self.should_show_message(message, category):
            print(f"# {message}")

    # ---------- LOGS ----------
    def log_decision(self, decision):
        if decision:
            self.print_debug(f"Decisão: {decision}", "DECISION")

    def log_status_update(self, x, y, direction, state, score, energy):
        self.print_debug(f"Status: pos=({x},{y}) dir={direction} state={state} score={score} energy={energy}", "STATUS")

    def log_game_command(self, command):
        self.print_debug(f"Comando: {command}", "SERVER")

    def log_connection_status(self, connected, host=None, port=None):
        msg = f"Conectado: {host}:{port}" if connected else "Desconectado"
        self.print_debug(msg, "CONN")

    def log_timer_info(self, game_status, time_str):
        self.print_debug(f"Timer – status={game_status} time={time_str}", "TIMER")

    def log_player_update(self, pid, name, action="update"):
        self.print_debug(f"Player {pid} {action}: {name}", "PLAYER")

    def log_game_status_change(self, new_status):
        self.print_debug(f"Game status → {new_status}", "GAME")

    def log_observation(self, obs):
        self.print_debug(f"Observations: {obs}", "OBS")

    def log_combat(self, event_type, target):
        self.print_debug(f"Combat {event_type} with {target}", "COMBAT")

    def log_error(self, err_type, msg):
        self.print_debug(f"ERROR {err_type}: {msg}", "ERROR")