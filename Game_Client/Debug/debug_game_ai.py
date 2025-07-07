# DEBUG DA GAME AI 

class GameAIDebugManager:
    def __init__(self):
        self.debug_enabled = False
        self.manual_mode = False
        self.command_queue = []
        self.ui            = None
        self._cache_status = None
        self._cache_obs    = ""
        self.map_knowledge = None  # Referência para o MapKnowledge

    # ligação UI
    def bind_ui(self, ui):
        self.ui = ui
        if self._cache_status:
            ui.update_status(*self._cache_status)
        if self._cache_obs:
            ui.update_observation(self._cache_obs.split(", "))

    # Configurar referência para o MapKnowledge
    def set_map_knowledge(self, map_knowledge):
        self.map_knowledge = map_knowledge

    # ---------- CONTROLES ----------
    def toggle_debug(self):
        self.debug_enabled = not self.debug_enabled

    def toggle_manual(self):
        self.manual_mode = not self.manual_mode
        self.command_queue.clear()

    def toggle_auto_print(self):
        if self.map_knowledge:
            current_state = getattr(self.map_knowledge, 'auto_print', False)
            self.map_knowledge.set_auto_print(not current_state)
            if self.debug_enabled:
                print(f"# AUTO PRINT: {'ativado' if not current_state else 'desativado'}")

    def get_auto_print_state(self):
        if self.map_knowledge:
            return getattr(self.map_knowledge, 'auto_print', False)
        return False

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

    # Função para solicitar print do mapa
    def print_map(self):
        if self.map_knowledge:
            print("\n# =============================================== MAPA DO CONHECIMENTO ================================================")
            self.map_knowledge.print_map()
            print("# =====================================================================================================================\n")
        else:
            print("# ERRO: MapKnowledge não está configurado")

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
