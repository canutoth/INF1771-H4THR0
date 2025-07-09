from Map.Position import Position
from MapKnowledge import MapKnowledge               # MAPA
from Debug.debug_game_ai import GameAIDebugManager  # DEBUG
from StateMachine import GameStateMachine           # STATEMACHINE
import random

# CLASSE DA GAME AI
# RECEBE INFORMAÇOES DE BOT.PY, AS PROCESSA E RETORNA DECISÕES
class GameAI():

    # Variáveis relevantes do bot
    player = Position()
    state = "ready"
    state_machine_mode = "exploration"  
    dir = "north"
    score = 0
    energy = 0
    game_time_seconds = 0  # tempo de jogo em segundos
    game_time_ticks = 0  # ticks de partida, 10 ticks = 1 segundo de partida. Dura 5 minutos (300 segundos = 30.000 ticks)
    
    map_knowledge = None # MAPA
    debug_manager = None  # DEBUG
    scoreboard_knowledge = None  # SCOREBOARD
    bot = None  # BOT

    def __init__(self, bot = None ,scoreboard_knowledge=None):
        self.bot = bot # BOT
        self.debug_manager = GameAIDebugManager() # DEBUG
        self.map_knowledge = MapKnowledge(bot, self) # MAPA
        self.debug_manager.set_map_knowledge(self.map_knowledge) # DEBUG/MAPA
        self.scoreboard_knowledge = scoreboard_knowledge # SCOREBOARD
        self.state_machine = GameStateMachine()  
        self.memory = [None] # Memória do bot, guarda status a cada tick
        self.gold_collected_last_tick = False
        self.last_gold_pos = None  # Posição do ouro coletado na última vez

        # auxiliar STATEMACHINE
        self._enemy_dist: int | None = None
        self._last_steps_ts = -999
        self._last_hit_ts = -999
        self._last_time_score_earned = -999  # Último tick em que houve ganho de pontos

        # PathFinder reutilizável
        from PathFinder import create_path_finder
        self.path_finder = create_path_finder(self.map_knowledge)
    
    # STATUS DO BOT
    def SetStatus(self, x: int, y: int, dir: str, state: str, score: int, energy: int):
        self.SetPlayerPosition(x, y)
        self.dir = dir.lower()
        self.state = state
        self.score = score
        self.energy = energy
        self.debug_manager.log_status(x, y, dir, state, score, energy) #DEBUG
    
    # Método para capturar o status do bot (histórico)
    def _capture_status(self):
        return {
            "tick":           self.game_time_ticks,
            "x":              self.player.x,
            "y":              self.player.y,
            "dir":            self.dir,
            "state":          self.state,
            "score":          self.score,
            "energy":         self.energy
        }
    
    # Método para atualizar o tempo de jogo
    def SetGameTime(self, time: int):
        self.game_time_seconds = time

    # Método para incrementar os ticks a cada ciclo real
    def IncrementTick(self):
        self.game_time_ticks += 1 # Atualiza o número de ticks
        self.map_knowledge.update_respawn_timers() # Atualiza timers de respawn de itens
        self._check_score_gain() # Verifica se houve ganho de pontos comparando com o tick anterior
        self.memory.append(self._capture_status()) # Captura o status atual do bot

    # Método para verificar ganho de pontos entre ticks
    def _check_score_gain(self):
        # Se há pelo menos um tick anterior na memória
        if len(self.memory) > 1 and self.memory[-1] is not None:
            previous_score = self.memory[-1]['score']
            current_score = self.score
            
            # Se houve ganho de pontos
            if current_score > previous_score:
                self._last_time_score_earned = self.game_time_ticks
                self.debug_manager.log_observation([f"score_gained: {current_score - previous_score} points at tick {self.game_time_ticks}"])
    
    # Retorna a posição relativa ao jogador: "frente", "atras", "esquerda" ou "direita", em x passos
    def NextPositionRelative(self, steps, direction):
        dir_map = {
            "north": {"frente": ( 0, -1), "atras": ( 0,  1), "esquerda": (-1,  0), "direita": ( 1,  0)},
            "east":  {"frente": ( 1,  0), "atras": (-1,  0), "esquerda": ( 0, -1), "direita": ( 0,  1)},
            "south": {"frente": ( 0,  1), "atras": ( 0, -1), "esquerda": ( 1,  0), "direita": (-1,  0)},
            "west":  {"frente": (-1,  0), "atras": ( 1,  0), "esquerda": ( 0,  1), "direita": ( 0, -1)},
        }
        offsets = dir_map[self.dir].get(direction)
        dx, dy = offsets
        return (self.player.x + dx*steps, self.player.y + dy*steps)


    # Retorna a posição do jogador 
    def GetPlayerPosition(self):
        return Position(self.player.x, self.player.y)

    # Muda a variável posição do jogador
    def SetPlayerPosition(self, x: int, y: int):
        self.player.x = x
        self.player.y = y

    # OBSERVAÇÕES DO BOT
    def GetObservations(self, o):
        self.debug_manager.log_observation(o) #DEBUG
        self.map_knowledge.update(self.player.x, self.player.y, self.dir, o) # MAPA

        # Reseta a distância do inimigo no início de cada observação
        self._enemy_dist = None    

        if self.gold_collected_last_tick:
            self.gold_collected_last_tick = False
            gold_pos = self.last_gold_pos # Recupera a posição onde o ouro foi coletado
            prev_score = self.memory[self.game_time_ticks-1]['score']
            diff = self.score - prev_score

            if diff < 500:
                # BlueLight#1 para variação de até 500 (anel)
                self.map_knowledge.update(gold_pos[0], gold_pos[1], self.dir, ['blueLight#1'])  # MAPA
            elif diff < 1000:
                # BlueLight#2 para variação entre 500 e 1000 (moeda)
                self.map_knowledge.update(gold_pos[0], gold_pos[1], self.dir, ['blueLight#2'])  # MAPA

            self.last_gold_pos = None  # Limpa a posição do ouro coletado

        for s in o:
            # steps: há um inimigo próximo há até 2 passos de distância de manhatan
            if s == "steps": # Quando está ao lado
                self._last_steps_ts = self.game_time_ticks
            # Quando o tiro de um inimigo acerta o agente, ele é notificado
            # damage: o jogador levou um dano
            elif s == "damage":
                pass
            # Quando um inimigo recebe um dano, o agente que disparou o tiro é notificado
            # hit: o jogador acertou um tiro
            elif s == "hit":
                self._last_hit_ts = self.game_time_ticks

            # enemy: detectado inimigo em até 10 passos na direção o qual o jogador está olhando. Normalmente apresentado como “enemy#xx”, onde xx é o número de passos.
            elif s.startswith("enemy#"): # Quando está a frente
                try:
                    self._enemy_dist = int(s.split("#")[1])
                except ValueError:
                    pass

    # Função para limpar as observações do bot
    def GetObservationsClean(self):
        # Reseta a distância do inimigo quando não há observações
        self._enemy_dist = None
        self.debug_manager.log_observation(['nenhum']) # DEBUG
        self.map_knowledge.update(self.player.x, self.player.y, self.dir, ['nenhum']) # MAPA
        pass

    # DECISÃO DO BOT
    def GetDecision(self) -> str:
    
        # ---------- CONTROLE MANUAL (DEBUG) ----------  
        if self.debug_manager.manual_mode:
            md = self.debug_manager.get_manual_decision()
            return md if md else ""
        # ---------- CONTROLE MANUAL (DEBUG) ----------
        
        # 1) Regra prioritária: pegar ouro/poção embaixo dos pés
        pickup = self._check_item_override()
        if pickup:
            return pickup
        
        # 2) Delega à FSM simplificada
        action = self.state_machine.next_action(self)
        if action == "andar":
            # Re-Verificação de segurança antes de andar
            next_pos = self.NextPositionRelative(1, "frente")
            # Verifica se a próxima posição é segura (novamente, por segurança)
            if self.map_knowledge.is_free(next_pos[0], next_pos[1]):
                return "andar"
            else:
                # Se não for seguro, limpa a navegação da FSM
                self.state_machine._clear_navigation()
                # Tenta virar (fallback)
                return "virar_esquerda" if random.random() < 0.5 else "virar_direita" # Gira
        return action if action else ""


    # ----------------- Helper API usada pela FSM -----------------

    # --- triggers ---
    def see_enemy(self):          return self._enemy_dist is not None # Se há inimigo na frente
    def enemy_dist(self):         return self._enemy_dist or 99 # Distância do inimigo, ou 99 se não houver inimigo
    def hear_steps(self):         return (self.game_time_ticks - self._last_steps_ts) <= 1 # Se o bot ouviu passos recentemente (dentro de 1 tick)
    def take_hit(self):           return (self.game_time_ticks - self._last_hit_ts) <= 1 # Se o bot levou dano recentemente (dentro de 1 tick)
    def get_last_score_gain_tick(self): return self._last_time_score_earned # Último tick em que houve ganho de pontos
    def scored_recently(self, ticks_threshold=10): return (self.game_time_ticks - self._last_time_score_earned) <= ticks_threshold # Se o bot ganhou pontos recentemente (dentro de ticks_threshold ticks)
    def energy_leq(self, value: int) -> bool: return self.energy <= value  # Retorna True se a energia do robô é igual ou menor que o valor passado
    def have_potion(self): return self.map_knowledge.get_best_item("pocao") # Retorna Tuple[bool, Optional[Tuple[int, int]]] com True se há poçao disponível, ou False se não há e retorna a posição da melhor poçao disponível
    def have_gold(self): return self.map_knowledge.get_best_item("ouro") # Retorna Tuple[bool, Optional[Tuple[int, int]]] com True se há ouro disponível, ou False se não há e retorna a posição do melhor ouro disponível
    def gold_spawning_soon(self): 
        # Pega informações sobre items em cooldown
        respawn_info = self.map_knowledge.get_respawn_info()
        
        # Se não há items em cooldown, retorna (False, None)
        if not respawn_info:
            return False, None
        
        # Filtra as posições onde há ouro e que estão prestes a ressurgir (<2s)
        candidatos: list[tuple[tuple[int,int], int, int]] = []
        for (x, y), ticks_rem in respawn_info.items():
            if not self.map_knowledge.is_gold_here(x, y):
                continue

            est = self.path_finder.time_estimated_to_go(
                self.player.x, self.player.y, self.dir, x, y
            )
            if ticks_rem - est <= 20: # Se o tempo restante é menor ou igual a 2 segundos (20 ticks)
                reward = self.map_knowledge.get_item_reward(x, y) 
                # (posição, tempo_restante – viagem, recompensa)
                candidatos.append(((x, y), ticks_rem - est, reward))

        if not candidatos:
            return False, None # Não há ouro prestes a ressurgir

        # Ordena: maior recompensa primeiro; em empate, menor tempo_restante
        candidatos.sort(key=lambda c: (-c[2], c[1]))
        melhor_pos = candidatos[0][0]
        return True, melhor_pos
   
    def potion_spawning_soon(self):
        # Sem utilidade se já estamos com energia cheia
        if self.energy >= 100:
            return False, None

        respawn_info = self.map_knowledge.get_respawn_info()
        if not respawn_info:
            return False, None

        candidates: list[tuple[tuple[int, int], int]] = []
        for (x, y), ticks_left in respawn_info.items():
            if not self.map_knowledge.is_potion_here(x, y):
                continue

            travel = self.path_finder.time_estimated_to_go(
                self.player.x, self.player.y, self.dir, x, y
            )

            # Só interessa se reaparecerá até 2 s depois que chegarmos
            if ticks_left - travel <= 20:
                # (pos, ticks_restantes – viagem)
                candidates.append(((x, y), ticks_left - travel))

        if not candidates:
            return False, None

        # Prioriza a que volta primeiro (menor diff ticks_left – travel)
        candidates.sort(key=lambda c: c[1])
        best_pos = candidates[0][0]

        # Descarta se distância Manhattan > 10 (regra de negócio)   
        dist = abs(best_pos[0] - self.player.x) + abs(best_pos[1] - self.player.y)
        if dist > 10:
            return False, None

        return True, best_pos
    
    # --- pick-up override ---
    def _check_item_override(self) -> str:
        # Verifica se há ouro na posição atual e se pode ser pego
        if (self.map_knowledge.is_gold_here(self.player.x, self.player.y) and 
            self.map_knowledge.can_pick_item(self.player.x, self.player.y)):
            self.map_knowledge.register_item_picked(self.player.x, self.player.y) # Registra que o item foi pego
            self.gold_collected_last_tick = True # Variável helper para informar a state machine o tipo de ouro
            self.last_gold_pos = (self.player.x, self.player.y)  # Salva a posição do ouro coletado

            return "pegar_ouro"
        
        # Verifica se há poção na posição atual e se pode ser pega
        if (self.map_knowledge.is_potion_here(self.player.x, self.player.y) and
            self.energy < 100 and
            self.map_knowledge.can_pick_item(self.player.x, self.player.y)):
            self.map_knowledge.register_item_picked(self.player.x, self.player.y) # Registra que o item foi pego
            return "pegar_powerup"
        
        return ""
