# DEBUG DA GAME AI 

class GameAIDebugManager:
    def __init__(self):
        self.debug_enabled = False
        self.manual_mode = False
        self.command_queue = []
        self.ui            = None
        self._cache_status = None
        self._cache_obs    = ""

    # ligação UI
    def bind_ui(self, ui):
        self.ui = ui
        if self._cache_status:
            ui.update_status(*self._cache_status)
        if self._cache_obs:
            ui.update_observation(self._cache_obs.split(", "))

    # ---------- CONTROLES ----------
    def toggle_debug(self):
        self.debug_enabled = not self.debug_enabled

    def toggle_manual(self):
        self.manual_mode = not self.manual_mode
        self.command_queue.clear()

    def add_manual_command(self, cmd):
        if not self.manual_mode:
            return
        map_cmd = {
            "up":       "andar",
            "down":     "andar_re",
            "left":     "virar_esquerda",
            "right":    "virar_direita",
            "attack":   "atacar",
            "gold":     "pegar_ouro",
            "ring":     "pegar_anel",
            "powerup":  "pegar_powerup",
        }
        action = map_cmd.get(cmd)
        if action:
            self.command_queue.append(action)

    def get_manual_decision(self):
        if self.manual_mode and self.command_queue:
            action = self.command_queue.pop(0)
            if self.debug_enabled:
                print(f"# MANUAL: executando → {action}")
            return action
        return None

    # ---------- DEBUG ----------
    def _log(self, msg):
        if self.debug_enabled:
            print(f"# IA: {msg}")

    # ---------- LOGS ----------

    # Repassa informações de status para a UI do debug
    def log_status(self, x, y, direction, state, score, energy):
        if self.ui:
            self.ui.update_status(x, y, direction, state, score, energy)
        
    # Repassa informações de status para a UI do debug
    def log_observation(self, obs):
        if self.ui:
            self.ui.update_observation(obs)

    # Debug no terminal
    def log_decision(self, decision):
        if not self.debug_enabled:
            return
        self._log(f"Decisão: {decision}")

    # Debug no terminal
    def decision_explanation(self, idx, total):
        if not self.manual_mode:               
            self._log(f"Escolha randômica: {idx}/{total - 1}")
