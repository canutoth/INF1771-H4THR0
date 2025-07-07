from Map.Position import Position
from MapKnowledge import MapKnowledge               # MAPA
from Debug.debug_game_ai import GameAIDebugManager  # DEBUG
from StateMachine import ExplorationDecision, AttackDecision, SurvivalDecision, ItsAboutTimeDecision  

# CLASSE DA GAME AI
# RECEBE INFORMAÇOES DE BOT.PY, AS PROCESSA E RETORNA DECISÕES
class GameAI():

    # Variáveis relevantes do bot
    player = Position()
    state = "ready"
    dir = "north"
    score = 0
    energy = 0
    game_time = 0  # Tempo de jogo em segundos
    
    map_knowledge = None # MAPA
    debug_manager = None  # DEBUG
    scoreboard_knowledge = None  # SCOREBOARD

    def __init__(self, scoreboard_knowledge=None):
        self.debug_manager = GameAIDebugManager() # DEBUG
        self.map_knowledge = MapKnowledge() # MAPA
        self.debug_manager.set_map_knowledge(self.map_knowledge) # DEBUG/MAPA
        self.scoreboard_knowledge = scoreboard_knowledge # SCOREBOARD

    # STATUS DO BOT
    # Recebe a mensagem do servidor com o status do bot e atualiza as variáveis internas do bot
    def SetStatus(self, x: int, y: int, dir: str, state: str, score: int, energy: int):
        self.SetPlayerPosition(x, y)
        self.dir = dir.lower()
        self.state = state
        self.score = score
        self.energy = energy
        self.debug_manager.log_status(x, y, dir, state, score, energy) #DEBUG
    
    # Método para atualizar o tempo de jogo
    def SetGameTime(self, time: int):
        self.game_time = time

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
        for s in o:
            # steps: há um inimigo próximo há até 2 passos de distância de manhatan
            if s == "steps": # Quando está ao lado
                pass
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
                    steps = int(s.replace("enemy#", ""))
                except:
                    pass

    # Função para limpar as observações do bot
    def GetObservationsClean(self):
       
        self.debug_manager.log_observation(['nenhum']) # DEBUG
        self.map_knowledge.update(self.player.x, self.player.y, self.dir, ['nenhum']) # MAPA
        pass

    # DECISÃO DO BOT
    def GetDecision(self) -> str:
    
        # ---------- CONTROLE MANUAL (DEBUG) ----------
        
        if self.debug_manager.manual_mode:
            manual_decision = self.debug_manager.get_manual_decision()
            if manual_decision:            # há comando na fila, executa
                return manual_decision
            return ""                      # sem comando, não faz nada
        # ---------- CONTROLE MANUAL (DEBUG) ----------

        if self.game_time >= 285: 
            return ItsAboutTimeDecision()
        elif self.energy < 30:
            self.state = "sobrevivencia"
        else:
            self.state = "exploracao"


        if self.state == "sobrevivencia":
            return SurvivalDecision()
        elif self.state == "exploracao":
            return ExplorationDecision() # se quiser testar substitui por aleatorio()
        elif self.state == "ataque":
            return AttackDecision()
        else:
            return ""


