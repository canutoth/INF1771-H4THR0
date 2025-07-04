import random
from Map.Position import Position
from enum import Enum
from typing import List, Dict

from Debug.debug_game_ai import GameAIDebugManager  # Sistema de debug especializado

# CLASSE PRINCIPAL DA GAME AI
# RECEBE INFORMAÇOES DE BOT.PY, AS PROCESSA E RETORNA DECISÕES
class GameAI():

    # Variáveis relevantes do bot
    player = Position()
    state = "ready"
    dir = "north"
    score = 0
    energy = 0
    
    # ========== SISTEMA DE DEBUG ESPECIALIZADO ==========
    debug_manager = None  # Gerenciador de debug específico para GameAI
    
    def __init__(self):
        """Inicializa o sistema de debug especializado"""
        self.debug_manager = GameAIDebugManager()

    # STATUS DO BOT
    # Recebe a mensagem do servidor com o status do bot e atualiza as variáveis internas do bot
    # Exemplo de mensagem recebida: ['s', '50', '8', 'north', 'game', '-220', '100']
    # Parâmetros:
    # 1 - s: comando de status
    # 2 - 50: posição x do jogador no mapa
    # 3 - 8: posição y do jogador no mapa
    # 4 - north: direção que o jogador está olhando (north, south, east, west)
    # 5 - game: estado do jogador (ex: 'game', 'dead')
    # 6 - -220: pontuação atual do jogador
    # 7 - 100: energia atual do jogador
    def SetStatus(self, x: int, y: int, dir: str, state: str, score: int, energy: int):
        self.SetPlayerPosition(x, y)
        self.dir = dir.lower()
        self.state = state
        self.score = score
        self.energy = energy
        
        # DEBUG
        self.debug_manager.log_status(x, y, dir, state, score, energy)

    # Retorna lista de posições adjacentes observáveis (cima, baixo, esquerda, direita) em relação à posição atual do jogador 
    # Não recebe nada de posição, usa o conhecimeto prévio da posição atual do jogador para retornar as posições adjacentes
    def GetCurrentObservableAdjacentPositions(self) -> List[Position]:
        return self.GetObservableAdjacentPositions(self.player) # Chama função abaixo
    
    # Recebe uma posição e retorna as posições vizinhas ortogonais (não diagonais)
    # Exemplo: para pos = (3, 7), retorna [(2,7), (4,7), (3,6), (3,8)]
    def GetObservableAdjacentPositions(self, pos):
        ret = []
        ret.append(Position(pos.x - 1, pos.y))  # esquerda
        ret.append(Position(pos.x + 1, pos.y))  # direita
        ret.append(Position(pos.x, pos.y - 1))  # cima
        ret.append(Position(pos.x, pos.y + 1))  # baixo
        return ret

    # Retorna todas as posições adjacentes (incluindo diagonais) 
    # Exemplo: para pos = (3, 7), retorna [(2,6), (2,7), (2,8), (3,6), (3,8), (4,6), (4,7), (4,8)]
    def GetAllAdjacentPositions(self):
        ret = []
        ret.append(Position(self.player.x - 1, self.player.y - 1))
        ret.append(Position(self.player.x, self.player.y - 1))
        ret.append(Position(self.player.x + 1, self.player.y - 1))
        ret.append(Position(self.player.x - 1, self.player.y))
        ret.append(Position(self.player.x + 1, self.player.y))
        ret.append(Position(self.player.x - 1, self.player.y + 1))
        ret.append(Position(self.player.x, self.player.y + 1))
        ret.append(Position(self.player.x + 1, self.player.y + 1))
        return ret

    # Calcula e retorna a posição que o bot estaria se andasse uma quantidade de casas (steps) para frente, na direção em que está olhando.
    # Exemplo: se o bot está em (5,5) olhando para 'east' e steps=3, retorna (8,5)
    def NextPositionAhead(self, steps):
        ret = None
        if self.dir == "north":
            ret = Position(self.player.x, self.player.y - steps)  # Anda para cima
        elif self.dir == "east":
            ret = Position(self.player.x + steps, self.player.y)  # Anda para a direita
        elif self.dir == "south":
            ret = Position(self.player.x, self.player.y + steps)  # Anda para baixo
        elif self.dir == "west":
            ret = Position(self.player.x - steps, self.player.y)  # Anda para a esquerda
        return ret

    # Calcula e retorna a próxima posição do bot, considerando que ele andará 1 passo na direção em que está olhando.
    # Exemplo: se o bot está em (2,3) olhando para 'north', retorna (2,2)
    def NextPosition(self) -> Position:
        return self.NextPositionAhead(1) # Chama a função que calcula a próxima posição com 1 passo

    # Retorna a posição do jogador 
    def GetPlayerPosition(self):
        return Position(self.player.x, self.player.y)

    # Muda a variável posição do jogador
    def SetPlayerPosition(self, x: int, y: int):
        self.player.x = x
        self.player.y = y

    # OBSERVAÇÕES DO BOT
    # Não implementada
    # Exemplo de mensagem recebida: ['o', 'blocked']
    # Parâmetros:
    # 1 - o: comando de observção
    # 2 - blocked: observação recebida pelo bot
    # Nesse caso quando recebemos 'h' ou 'd' separadamente para damage ou hit (olhar bot.py)
    # Obs BAFFA:
     # IMPLEMENTAR
        # como sua solucao vai tratar as observacoes?
        # como seu bot vai memorizar os lugares por onde passou?
        # aqui, recebe-se as observacoes dos sensores para as
        # coordenadas atuais do player
    def GetObservations(self, o):

        # DEBUG 
        self.debug_manager.log_observation(o)
    
        for s in o:
        
            # Ao caminhar contra uma parede o agente sente um impacto. As laterais do labirinto são paredes, o mapa também pode conter outras posições bloqueadas
            # blocked: último movimento não foi feito. Destino está bloqueado
            if s == "blocked": # 
                pass

            # Em coordenadas adjacentes aos inimigos, exceto diagonal, o agente ouve um som de passos.
            # steps: há um inimigo próximo há até 2 passos de distância de manhatan
            elif s == "steps":
                pass
            
            # Em coordenadas adjacentes a um poço/obstáculo, exceto diagonal, o agente sente uma brisa.
            # breeze: há uma brisa (buraco) adjacente (1 passo em distância de manhatan)
            elif s == "breeze":
                pass

            # Em coordenadas adjacentes ao inimigo que teletransporta, exceto diagonal, o agente percebe um flash
            # flash: há um clarão (teletransporte) adjacente (1 passo em distância de manhatan)
            elif s == "flash":
                pass

            # Em coordenadas onde existem itens o agente percebe o brilho de uma luz, Bluelight = tesouro
            # blueLight: há uma luz azul fraca (tesouro) na posição do jogador
            elif s == "blueLight":
                pass

            # Em coordenadas onde existem itens o agente percebe o brilho de uma luz, Redlight = powerup
            # redLight: há uma luz vermelha fraca (powerup) na posição do jogador
            elif s == "redLight":
                pass

            # Em coordenadas onde existem itens o agente percebe o brilho de uma luz, Greenlight = veneno (não será utilizado nos mapas do trabalho)
            # greenLight: há uma luz verde fraca (veneno) na posição do jogador
            elif s == "greenLight":
                pass

            # Em coordenadas onde existem itens o agente percebe o brilho de uma luz, Weaklight = indefinido
            # weaklight: há uma luz fraca não identificável na posição do jogador
            elif s == "weakLight":
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
            elif s.startswith("enemy#"):
                try:
                    steps = int(s.replace("enemy#", ""))
                except:
                    pass


    # Função para limpar as observações do bot
    # Não implementada
    # Obs BAFFA:
     # IMPLEMENTAR
        # como "apagar/esquecer" as observacoes?
        # devemos apagar as atuais para poder receber novas
        # se nao apagarmos, as novas se misturam com as anteriores
    def GetObservationsClean(self):
        # DEBUG 
        self.debug_manager.log_observation(['nenhum'])
        pass

    # DECISÃO DO BOT
    # Não implementada
    # Obs BAFFA:
     # IMPLEMENTAR
        # Qual a decisão do seu bot?

        # A cada ciclo, o bot segue os passos:
        # 1- Solicita observações
        # 2- Ao receber observações:
        # 2.1 - chama "GetObservationsClean()" para apagar as anteriores
        # 2.2 - chama "GetObservations(_)" passando as novas observacoes
        # 3- chama "GetDecision()" para perguntar o que deve fazer agora
        # 4- envia decisão ao servidor
        # 5- após ação enviada, reinicia voltando ao passo 1
    def GetDecision(self) -> str:
        # ---------- CONTROLE MANUAL ----------
        if self.debug_manager.manual_mode:
            manual_decision = self.debug_manager.get_manual_decision()
            if manual_decision:            # há comando na fila, executa
                return manual_decision
            return ""                      # sem comando, não faz nada
        # ---------- CONTROLE MANUAL ----------
        
        # Lógica automática original (decisão aleatória):
        n = random.randint(0,7)

        # Log da decisão aleatória (DEBUG)
        self.debug_manager.decision_explanation(n, 8)

        # Vira a direita
        # Cada ação executada possui o custo de -1 (andar, virar para a esquerda, direita, etc)
        if n == 0:
            decision = "virar_direita"
        
        # Vira a esquerda
        # Cada ação executada possui o custo de -1 (andar, virar para a esquerda, direita, etc)
        elif n == 1:
            decision = "virar_esquerda"
        
        # Anda para frente
        # Cada ação executada possui o custo de -1 (andar, virar para a esquerda, direita, etc)
        elif n == 2:
            decision = "andar"
        
        # Dá um tiro
        # Atirar = -10
        # Matar um inimigo = +1000
        elif n == 3:
            decision = "atacar"
        
        # Tenta pegar um item (nesse caso pressupoe que haja um ouro na posição do jogador)
        # Pegar = -5 + ganho do item (a tentativa mesmo que não tenha nada)
        # Moedas de ouro (+1000)
        elif n == 4:
            decision = "pegar_ouro"

        # Tenta pegar um item (nesse caso pressupoe que haja um anel na posição do jogador)
        # Pegar = -5 + ganho do item (a tentativa mesmo que não tenha nada)
        # Anéis de ouro (+500)
        elif n == 5:
            decision = "pegar_anel"
        
        # Tenta pegar um item (nesse caso pressupoe que haja um powerup na posição do jogador)
        # Pegar = -5 + ganho do item (a tentativa mesmo que não tenha nada)
        # Poções (power up +10, +20 ou +50 - energia)
        elif n == 6:
            decision = "pegar_powerup"
        
        # Anda para trás
        # Cada ação executada possui o custo de -1 (andar, virar para a esquerda, direita, etc)
        elif n == 7:
            decision = "andar_re"
        else:
            decision = ""
        
        # Log da decisão automática
        if decision:
            self.debug_manager.log_decision(decision)
        
        return decision

