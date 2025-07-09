# DEBUG DA GAME AI 

class GameAIDebugManager:
    def __init__(self):
        self.debug_enabled = False
        self.manual_mode = False
        self.command_queue = []
        self.ui            = None
        self._cache_status = None
        self._cache_obs    = ""
        self.map_knowledge = None  

    # ligação UI
    def bind_ui(self, ui):
        self.ui = ui
        if self._cache_status:
            ui.update_status(*self._cache_status)
        if self._cache_obs:
            ui.update_observation(self._cache_obs.split(", "))

    def set_map_knowledge(self, map_knowledge):
        self.map_knowledge = map_knowledge

    # Get auto print state from map knowledge
    def get_auto_print_state(self):
        if self.map_knowledge:
            return self.map_knowledge.auto_print
        return False

    # Toggle auto print in map knowledge
    def toggle_auto_print(self):
        if self.map_knowledge:
            self.map_knowledge.set_auto_print(not self.map_knowledge.auto_print)

    # Print map using map knowledge
    def print_map(self):
        if self.map_knowledge:
            self.map_knowledge.print_map()

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
    def decision_explanation(self, idx, total):
        if not self.manual_mode:               
            self._log(f"Escolha randômica: {idx}/{total - 1}")
    
    # Debug detalhado das decisões da State Machine
    def log_state_machine_decision(self, game_ai, current_state, action, reasoning=""):
        if not self.debug_enabled:
            return
            
        # Informações básicas do estado atual
        self._log(f"=== DECISÃO DA STATE MACHINE ===")
        self._log(f"Estado atual: {current_state}")
        self._log(f"Ação escolhida: {action}")
        self._log(f"Tick atual: {game_ai.game_time_ticks}")
        self._log(f"Posição: ({game_ai.player.x}, {game_ai.player.y}) facing {game_ai.dir}")
        
        # Informações do contexto do jogo
        self._log(f"Status do jogador:")
        self._log(f"  - Energia: {game_ai.energy}")
        self._log(f"  - Score: {game_ai.score}")
        self._log(f"  - Estado do jogo: {game_ai.state}")
        
        # Informações de percepção
        self._log(f"Percepções:")
        self._log(f"  - Vê inimigo: {game_ai.see_enemy()} (dist: {game_ai.enemy_dist() if game_ai.see_enemy() else 'N/A'})")
        self._log(f"  - Ouve passos: {game_ai.hear_steps()}")
        self._log(f"  - Levou dano: {game_ai.take_hit()}")
        
        # Informações sobre ouro
        gold_info = game_ai.gold_spawning_soon()
        self._log(f"  - Ouro próximo ao respawn: {gold_info[0]} {f'em {gold_info[1]}' if gold_info[0] else ''}")
        
        # Reasoning adicional se fornecido
        if reasoning:
            self._log(f"Motivo: {reasoning}")
        
        self._log(f"================================")
    
    # Debug das transições de estado
    def log_state_transition(self, old_state, new_state, reason=""):
        if not self.debug_enabled:
            return
            
        self._log(f">>> TRANSIÇÃO DE ESTADO: {old_state} → {new_state}")
        if reason:
            self._log(f"    Motivo: {reason}")
    
    # Debug do sistema de navegação
    def log_navigation_info(self, game_ai, target=None, path=None, path_length=0):
        if not self.debug_enabled:
            return
            
        self._log(f"--- NAVEGAÇÃO ---")
        if target:
            self._log(f"Destino: {target}")
            manhattan_dist = abs(game_ai.player.x - target[0]) + abs(game_ai.player.y - target[1])
            self._log(f"Distância Manhattan: {manhattan_dist}")
        
        if path:
            self._log(f"Caminho atual: {path[:5]}{'...' if len(path) > 5 else ''}")
            self._log(f"Passos restantes: {len(path)}")
        elif path_length > 0:
            self._log(f"Passos no caminho: {path_length}")
        
        self._log(f"----------------")
    
    # Debug das condições de combate
    def log_combat_info(self, game_ai, attack_sequence=None, attack_count=0, cooldown_until=0):
        if not self.debug_enabled:
            return
            
        self._log(f"--- COMBATE ---")
        if game_ai.see_enemy():
            self._log(f"Inimigo detectado a {game_ai.enemy_dist()} passos")
        
        if attack_sequence:
            self._log(f"Sequência de ataque: {attack_sequence}")
        
        if attack_count > 0:
            self._log(f"Ataques consecutivos: {attack_count}")
        
        if cooldown_until > game_ai.game_time_ticks:
            remaining = cooldown_until - game_ai.game_time_ticks
            self._log(f"Cooldown de ataque: {remaining} ticks restantes")
        
        self._log(f"---------------")
    
    # Debug das ações de evasão
    def log_evade_info(self, evade_sequence=None, last_evade_axis=0, axis_names=None):
        if not self.debug_enabled:
            return
            
        self._log(f"--- EVASÃO ---")
        if evade_sequence:
            self._log(f"Sequência de evasão: {evade_sequence}")
        
        if axis_names and last_evade_axis in axis_names:
            self._log(f"Último eixo de evasão: {axis_names[last_evade_axis]}")
        
        self._log(f"--------------")
    
    # Debug de busca por itens
    def log_item_search_info(self, item_type, target_position=None, estimated_time=None):
        if not self.debug_enabled:
            return
            
        self._log(f"--- BUSCA POR {item_type.upper()} ---")
        if target_position:
            self._log(f"Posição do item: {target_position}")
        
        if estimated_time is not None:
            self._log(f"Tempo estimado para chegar: {estimated_time} ticks")
        
        self._log(f"---------------------------")
    
    # Debug geral de exploração
    def log_exploration_info(self, exploration_type="", target=None, percentage_chance=0):
        if not self.debug_enabled:
            return
            
        self._log(f"--- EXPLORAÇÃO ---")
        if exploration_type:
            self._log(f"Tipo de exploração: {exploration_type}")
        
        if target:
            self._log(f"Alvo escolhido: {target}")
        
        if percentage_chance > 0:
            self._log(f"Chance utilizada: {percentage_chance}%")
        
        self._log(f"------------------")
    
    # Debug de coleta de itens
    def log_item_pickup(self, item_type, position, reward=0):
        if not self.debug_enabled:
            return
            
        self._log(f"*** ITEM COLETADO ***")
        self._log(f"Tipo: {item_type}")
        self._log(f"Posição: {position}")
        if reward > 0:
            self._log(f"Recompensa: {reward} pontos")
        self._log(f"*********************")
    
    # Debug de eventos gerais do jogo
    def log_game_event(self, event_type, details=""):
        if not self.debug_enabled:
            return
            
        self._log(f"[EVENTO] {event_type}")
        if details:
            self._log(f"Detalhes: {details}")
    
    # Debug de erro ou situação inesperada
    def log_error_or_warning(self, message, error_type="WARNING"):
        if not self.debug_enabled:
            return
            
        self._log(f"[{error_type}] {message}")
    
    # Debug resumido da decisão (versão mais concisa)
    def log_decision_summary(self, state, action, key_factors=""):
        if not self.debug_enabled:
            return
            
        summary = f"{state} → {action}"
        if key_factors:
            summary += f" ({key_factors})"
        self._log(f"[DECISÃO] {summary}")
