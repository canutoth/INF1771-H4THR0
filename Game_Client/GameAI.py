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

        # auxiliar STATEMACHINE
        self._enemy_dist: int | None = None
        self._last_steps_ts = -999
        self._look_mode = False
        self._look_turns = 0

    # STATUS DO BOT
    def SetStatus(self, x: int, y: int, dir: str, state: str, score: int, energy: int):
        self.SetPlayerPosition(x, y)
        self.dir = dir.lower()
        self.state = state
        self.score = score
        self.energy = energy
        self.debug_manager.log_status(x, y, dir, state, score, energy) #DEBUG
    
    # Método para atualizar o tempo de jogo
    def SetGameTime(self, time: int):
        self.game_time_seconds = time

    # Método para incrementar os ticks a cada ciclo real
    def IncrementTick(self):
        self.game_time_ticks += 1
        # Atualiza timers de respawn de itens
        self.map_knowledge.update_respawn_timers()

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
        # Será preenchida apenas se houver observação "enemy#"
        self._enemy_dist = None    
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
                pass

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

    # --- look-mode control ---
    def start_look_mode(self):         self._look_mode, self._look_turns = True, 0
    def look_mode_active(self) -> bool:return self._look_mode
    def look_step_done(self) -> bool:
        self._look_turns += 1
        if self._look_turns >= 3 or (self.game_time_ticks - self._last_steps_ts) > 50:  # 3 giros ou 5s (50 ticks)
            self._look_mode = False
            return True
        return False

    # --- pick-up override ---
    def _check_item_override(self) -> str:
        # Verifica se há ouro na posição atual e se pode ser pego
        if (self.map_knowledge.is_gold_here(self.player.x, self.player.y) and 
            self.map_knowledge.can_pick_item(self.player.x, self.player.y)):
            # Registra que o item foi pego
            self.map_knowledge.register_item_picked(self.player.x, self.player.y)
            return "pegar_ouro"
        
        # Verifica se há poção na posição atual e se pode ser pega
        if (self.map_knowledge.is_potion_here(self.player.x, self.player.y) and
            self.energy < 100 and
            self.map_knowledge.can_pick_item(self.player.x, self.player.y)):
            # Registra que o item foi pego
            self.map_knowledge.register_item_picked(self.player.x, self.player.y)
            return "pegar_powerup"
        
        return ""
