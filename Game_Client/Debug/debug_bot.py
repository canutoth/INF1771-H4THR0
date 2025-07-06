# DEBUG DO BOT

class BotDebugManager:
    def __init__(self):
        self.debug_enabled = False
        self.filter_enabled = True
        self.raw_enabled = False
        self.last_message = {}
        self.disabled = {}         

    # -------- CONTROLE --------
    def toggle_debug(self):
        self.debug_enabled = not self.debug_enabled

    def toggle_filter(self):
        self.filter_enabled = not self.filter_enabled
        if self.filter_enabled:
            self.last_message.clear()

    def toggle_raw(self):
        self.raw_enabled = not self.raw_enabled

    # -------- FILTRO --------
    def should_show_message(self, message, category):
       
        # 1) se o filtro estiver *desativado*, mostra sempre
        if not self.filter_enabled:
            return True
        
        # 2) categoria silenciada?
        if category in self.disabled:
            return False
        
         # 3) se for igual à última mensagem dessa categoria, suprime
        last = self.last_message.get(category)
        if last == message:
            return False
        
        # 4) caso contrário, registra e mostra
        self.last_message[category] = message
        return True

    # ---------- SAÍDA ----------
    def print_debug(self, message, category, cmd):

        if not self.debug_enabled:
            return
        
        if self.raw_enabled == True:
            print(f"[RAW][{category}] -> {cmd}")

        if self.should_show_message(message, category):
            print(f"[{category}] -> {message}")

    # ---------- LOGS ----------

    def log_observation(self, cmd):
        obs_list = [] if len(cmd) < 2 or cmd[1].strip() == "" else cmd[1].split(',')
        obs_str  = ", ".join(obs_list) if obs_list else "nenhuma"
        self.print_debug(f"Observações recebidas: {obs_str}", "OBS", cmd)

    def log_player(self, cmd):
        pid, name = cmd[1], cmd[2]
        self.print_debug(f"Atualização de player #{pid} → {name}", "PLAYER", cmd)

    def log_game(self, cmd):
        status, secs = cmd[1], int(cmd[2])
        mm, ss = divmod(secs, 60)
        self.print_debug(f"Estado do jogo: {status} (t={mm:02d}:{ss:02d})", "GAME", cmd)

    def log_notification(self, cmd):
        self.print_debug(f"Servidor: {cmd[1]}", "NOTIFICATION", cmd)

    def log_message(self, cmd):
        self.print_debug(cmd[1], "MESSAGE", cmd)

    def log_player_event(self, cmd):
        if cmd[0] == "hello":
            self.print_debug(f"{cmd[1]} entrou no jogo", "PLAYER", cmd)
        elif cmd[0] == "goodbye":
            self.print_debug(f"{cmd[1]} saiu do jogo", "PLAYER", cmd)
        elif cmd[0] == "changename":
            self.print_debug(f"{cmd[1]} agora é {cmd[2]}", "PLAYER", cmd)

    def log_combat(self, cmd):
        if cmd[0] == "h":
            self.print_debug(f"Atingiu {cmd[1]}", "COMBAT", cmd)
        elif cmd[0] == "d":
            self.print_debug(f"Recebeu dano de {cmd[1]}", "COMBAT", cmd)

    def log_error(self, exc):
        self.print_debug(f"{type(exc).__name__}: {exc}", "ERROR", exc)

    def log_decision(self, decision):
        cmd = ["decision", decision]
        msg = f"Decisão: executar '{decision}'"
        self.print_debug(msg, "DECISION", cmd)

    def log_timer_info(self, status, time_str):
        self.print_debug(
            f"Timer tick -> estado={status}, tempo={time_str}",
            "TIMER",
            (status, time_str)
        )

    def log_full_scoreboard(self, board_str):
        # Espera uma string formatada como no sscoreList: nome, status, energia, score, ---\n
        lines = [l for l in board_str.strip().split('\n') if l and l != '---']
        players = []
        for i in range(0, len(lines), 4):
            try:
                name = lines[i]
                status = lines[i+1]
                energy = lines[i+2]
                score = lines[i+3]
                players.append(f"{name} | {status} | E:{energy} | S:{score}")
            except Exception:
                continue
        if players:
            msg = "SCOREBOARD (nome | status | E:energia | S:score):\n" + "\n".join(players)
        else:
            msg = "SCOREBOARD vazio."
        self.print_debug(msg, "SCOREBOARD", board_str)

    def log_chat_line(self, text):
        self.print_debug(text, "MESSAGE", text)

    def log_connection_status(self, connected, host=None, port=None):
 
        if connected:
            msg = f"Conectado ao servidor em {host}:{port}"
            cmd = ["connection", "connected", host, str(port)]
        else:
            msg = "Desconectado do servidor"
            cmd = ["connection", "disconnected"]

        self.print_debug(msg, "CONN", cmd)

    def log_reconnecting(self):
        self.print_debug("Iniciando tentativa de reconexão...", "CONNEC", "Iniciando tentativa de reconexão...")

    def log_reconnect_failed(self):
        self.print_debug("Falha na conexão, tentando de novo em 5s...", "CONNEC", "Falha na conexão, tentando de novo em 5s...")
    