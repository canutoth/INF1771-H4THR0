from Map.Position import Position
from MapKnowledge import MapKnowledge               # MAPA
from Debug.debug_game_ai import GameAIDebugManager  # DEBUG
from StateMachine import GameStateMachine           # STATEMACHINE

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

    def __init__(self, scoreboard_knowledge=None):
        self.debug_manager = GameAIDebugManager() # DEBUG
        self.map_knowledge = MapKnowledge() # MAPA
        self.debug_manager.set_map_knowledge(self.map_knowledge) # DEBUG/MAPA
        self.scoreboard_knowledge = scoreboard_knowledge # SCOREBOARD
        self.state_machine = GameStateMachine()  
        self.memory = [None] # Memória do bot, guarda status a cada tick
        self.gold_collected_last_tick = False

        # auxiliar STATEMACHINE
        self._enemy_dist: int | None = None
        self._last_steps_ts = -999
        self._last_hit_ts = -999

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
        self.memory.append(self._capture_status()) # Captura o status atual do bot
    
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
            print("Gold collected last tick, updating map knowledge.")  # DEBUG
            self.gold_collected_last_tick = False
            # Diferença de score entre tick atual e penúltimo na memória
            prev_score = self.memory[self.game_time_ticks-1]['score']
            diff = self.score - prev_score

            if diff < 500:
                # BlueLight#1 para variação de até 500 (anel)
                self.map_knowledge.update(self.player.x, self.player.y, self.dir, ['blueLight#1'])  # MAPA
            elif diff < 1000:
                # BlueLight#2 para variação entre 500 e 1000 (moeda)
                self.map_knowledge.update(self.player.x, self.player.y, self.dir, ['blueLight#2'])  # MAPA

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
        return self.state_machine.next_action(self)


    # ----------------- Helper API usada pela FSM -----------------

    # --- triggers ---
    def see_enemy(self) -> bool:       return self._enemy_dist is not None
    def enemy_dist(self) -> int:       return self._enemy_dist or 99
    def hear_steps(self) -> bool:      return (self.game_time_ticks - self._last_steps_ts) <= 1
    def take_hit(self) -> bool:      return (self.game_time_ticks - self._last_hit_ts) <= 1

    # --- pick-up override ---
    def _check_item_override(self) -> str:
        # Verifica se há ouro na posição atual e se pode ser pego
        if (self.map_knowledge.is_gold_here(self.player.x, self.player.y) and 
            self.map_knowledge.can_pick_item(self.player.x, self.player.y)):
            self.map_knowledge.register_item_picked(self.player.x, self.player.y) # Registra que o item foi pego
            self.gold_collected_last_tick = True # Variável helper para informar a state machine o tipo de ouro

            return "pegar_ouro"
        
        # Verifica se há poção na posição atual e se pode ser pega
        if (self.map_knowledge.is_potion_here(self.player.x, self.player.y) and
            self.energy < 100 and
            self.map_knowledge.can_pick_item(self.player.x, self.player.y)):
            self.map_knowledge.register_item_picked(self.player.x, self.player.y) # Registra que o item foi pego
            return "pegar_powerup"
        
        return ""
