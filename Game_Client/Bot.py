# IMPORTS
from threading import Timer
from GameAI import GameAI
import Socket.HandleClient
from Socket.HandleClient import HandleClient
from dto.PlayerInfo import PlayerInfo
from dto.ScoreBoard import ScoreBoard
from Debug.debug_bot import BotDebugManager  # DEBUG
import time
import datetime
import re

# CLASSE PRINCIPAL DO BOT
# RECEBE INFORMAÇÕES DO SERVIDOR, TRADUZ PRA GAME AI PROCESSAR E RETORNA DECISÕES DA GAME AI AO SERVIDOR 
class Bot():
    # ==================== CONFIGURAÇÕES DO BOT ====================
    botcolor = (90, 50, 168)       # Cor do bot (RGB)
    name = "h4thr0_example"         # Nome do bot
    host = "atari.icad.puc-rio.br" # Endereço do servidor
    port = 8888                    # Porta do servidor

    # ==================== VARIÁVEIS DE ESTADO ====================
    client = None           # Cliente de conexão com o servidor
    gameAi = None           # Instância da IA do bot
    timer1 = None           # Timer para execução periódica
    running = True          # Controle de execução do bot
    thread_interval = 0.1   # Intervalo do timer (em segundos) 
    debug_manager = None    # DEBUG

    # Listas e variáveis para armazenar informações do jogo
    playerList = {}           # Dicionário de jogadores
    shotList = []             # Lista de tiros
    scoreList = []            # Lista de placar
    time = 0                  # Tempo de jogo (segundos)
    gameStatus = ""           # Status atual do jogo
    sscoreList = ""           # String formatada do placar
    msg = []                  # Mensagens recebidas
    msgSeconds = 0            # Temporizador de mensagens
    gamestatus_interval = 0   # Intervalo para atualização de status do jogo
    sayHello = 0              # Controle de saudação inicial

    # ==================== CONSTRUTOR ====================
    # Inicializa o bot, conecta ao servidor e configura os handlers
    def __init__(self):
        # ==DEBUG==
        self.debug_manager = BotDebugManager() # Inicializar sistema de debug especializado para Bot
        
        self.client = HandleClient()
        self.gameAi = GameAI() # =======================================>>>>> INSTANCIA GAME AI
        self.timer1 = Timer(self.thread_interval, self.timer1_Tick)
        self.client.append_cmd_handler(self.ReceiveCommand)
        self.client.append_chg_handler(self.SocketStatusChange)
        while(not self.client.connect(self.host, self.port)):
            print("Conexão falhou... Tentando conectar em 5 segundos...")
            time.sleep(5)
        self.timer1.start()
    
    # Converte string de cor para tupla RGB
    def convertFromString(self, c):
        p = re.split(',|]', c)
        A = int(p[0][(p[0].find('=') + 1):])
        R = int(p[1][(p[1].find('=') + 1):])
        G = int(p[2][(p[2].find('=') + 1):])
        B = int(p[3][(p[3].find('=') + 1):])
        return (R, G, B)

    # ==================== RECEBIMENTO DE COMANDOS ====================
    # Recebe comandos do servidor e repassa para a GameAI ou atualiza o estado do bot
    def ReceiveCommand(self, cmd):
        if len(cmd) > 0:
            try:          
                ######################################################        
                if cmd[0] ==  "o":
                    if len(cmd) > 1:
                        if cmd[1].strip() == "":
                            self.gameAi.GetObservationsClean() # =======================================>>>>> LIMPA OBSERVAÇÕES
                        else:
                            o = []
                            if cmd[1].find(",") > -1:
                                os = cmd[1].split(',')
                                for i in range(0,len(os)):
                                    o.append(os[i])
                            else:
                                o.append(cmd[1])
                            self.gameAi.GetObservations(o)  # =======================================>>>>> ENVIA OBSERVAÇÕES (geral, menos hit e damage)
                        self.debug_manager.log_observation(cmd) # DEBUG
                    else:
                        self.gameAi.GetObservationsClean()  # =======================================>>>>> LIMPA OBSERVAÇÕES
                        self.debug_manager.log_observation(cmd) # DEBUG
                ######################################################        
                elif cmd[0] ==  "s":
                    if len(cmd) > 1:
                        self.gameAi.SetStatus(int(cmd[1]), int(cmd[2]), cmd[3], cmd[4], int(cmd[5]), int(cmd[6]))  # =======================================>>>>> ENVIA STATUS
                        self.debug_manager.log_status(cmd) # DEBUG
                ######################################################        
                elif cmd[0] == "player":
                    if len(cmd) == 8:
                        if int(cmd[1]) not in self.playerList:
                            self.playerList.append(int(cmd[1]), 
                                PlayerInfo(
                                    int(cmd[1]),
                                    cmd[2],
                                    int(cmd[3]),
                                    int(cmd[4]),
                                    int(cmd[5]),
                                    int(cmd[6]),
                                    self.convertFromString(cmd[7])))
                        else:
                            self.playerList[int(cmd[1])] = PlayerInfo(
                                int(cmd[1]),
                                cmd[2],
                                int(cmd[3]),
                                int(cmd[4]),
                                int(cmd[5]),
                                int(cmd[6]),
                                self.convertFromString(cmd[7]))
                        self.debug_manager.log_player(cmd) # DEBUG
                ######################################################        
                elif cmd[0] == "g":
                    if len(cmd) == 3:
                        if self.gameStatus != cmd[1]:
                            self.playerList.clear()
                        if self.gameStatus != cmd[1]:
                            self.client.sendRequestUserStatus()
                            self.client.sendRequestObservation()
                        elif self.time > int(cmd[2]):
                            self.client.sendRequestUserStatus()
                        self.gameStatus = cmd[1]
                        self.time = int(cmd[2])
                        self.debug_manager.log_game(cmd) # DEBUG    
                ######################################################        
                elif cmd[0] == "u":
                    if len(cmd) > 1:
                        for i in range(1, len(cmd)):
                            a = cmd[i].split('#')
                            if len(a) == 4:
                                self.scoreList.append(
                                    ScoreBoard(
                                    a[0],
                                    (a[1] == "connected"),
                                    int(a[2]),
                                    int(a[3]), (0, 0, 0)))
                            elif len(a) == 5:
                                self.scoreList.append(
                                    ScoreBoard(
                                    a[0],
                                    (a[1] == "connected"),
                                    int(a[2]),
                                    int(a[3]), self.convertFromString(a[4])))
                        self.sscoreList = ""
                        for sb in self.scoreList:
                            self.sscoreList += sb.name + "\n"
                            self.sscoreList += ("connected" if sb.connected else "offline") + "\n"
                            self.sscoreList += str(sb.energy) + "\n"
                            self.sscoreList += str(sb.score) + "\n"
                            self.sscoreList += "---\n"
                        self.scoreList.clear()
                ######################################################        
                elif cmd[0] == "notification":
                    if len(cmd) > 1:
                        if len(self.msg) == 0:
                            self.msgSeconds = 0
                        self.msg.append(cmd[1])
                        self.debug_manager.log_notification(cmd) # DEBUG
                ######################################################        
                elif cmd[0] == "hello":
                    if len(cmd) > 1:
                        if len(self.msg) == 0:
                            self.msgSeconds = 0
                        self.msg.append(cmd[1] + " has entered the game!")
                        self.debug_manager.log_player_event(cmd) # DEBUG
                ######################################################        
                elif cmd[0] == "goodbye":
                    if len(cmd) > 1:
                        if len(self.msg) == 0:
                            self.msgSeconds = 0
                        self.msg.append(cmd[1] + " has left the game!")
                        self.debug_manager.log_player_event(cmd) # DEBUG
                ######################################################        
                elif cmd[0] == "changename":
                    if len(cmd) > 1:
                        if len(self.msg) == 0:
                            self.msgSeconds = 0
                        self.msg.append(cmd[1] + " is now known as " + cmd[2] + ".")
                        self.debug_manager.log_player_event(cmd) # DEBUG
                ######################################################        
                elif cmd[0] == "h":
                    if len(cmd) > 1:
                        o = []
                        o.append("hit")
                        self.gameAi.GetObservations(o) # =======================================>>>>> ENVIA OBSERVAÇÕES (BOT DEU DANO EM ALGUÉM)
                        self.msg.append("you hit " + cmd[1])
                        self.debug_manager.log_combat(cmd) # DEBUG
                ######################################################        
                elif cmd[0] == "d":
                    if len(cmd) > 1:
                        o = []
                        o.append("damage")
                        self.gameAi.GetObservations(o) # =======================================>>>>> ENVIA OBSERVAÇÕES (BOT TOMOU DANO)
                        self.msg.append(cmd[1] + " hit you")
                        self.debug_manager.log_combat(cmd) # DEBUG
                ######################################################
            except Exception as ex:
                self.debug_manager.log_error(type(ex).__name__, str(ex))

    # Manda mensagem para outros usuários
    def sendMsg(self, msg):
        if len(msg.strip()) > 0:
            self.client.sendSay(msg)

    # Pega o tempo atual do jogo como string
    def GetTime(self):
        return str(datetime.timedelta(seconds=self.time))
    
    # Manda decisão ao servidor
    def sendDecision(self, decision):
        self.debug_manager.log_decision(decision) # DEBUG

        # d sendTurnRight(); – virar a direita 90º
        if decision == "virar_direita":
            self.client.sendTurnRight()

        # a sendTurnLeft(); – virar a esquerda 90º
        elif decision == "virar_esquerda":
            self.client.sendTurnLeft()

        # w sendForward(); – anda para frente
        elif decision == "andar":
            self.client.sendForward()

        # e sendShoot(); – atirar
        elif decision ==  "atacar":
            self.client.sendShoot()

        # t sendGetItem(); – pegar item
        elif decision ==  "pegar_ouro":
            self.client.sendGetItem()

        # t sendGetItem(); – pegar item
        elif decision == "pegar_anel":
            self.client.sendGetItem()

        # t sendGetItem(); – pegar item
        elif decision == "pegar_powerup":
            self.client.sendGetItem()

        # s sendBackward(); – anda de ré
        elif decision ==  "andar_re":
            self.client.sendBackward()
   
    # Executa uma decisão da GameAI
    def DoDecision(self):
        
        decision = self.gameAi.GetDecision()
        self.sendDecision(decision)
        self.client.sendRequestUserStatus()
        self.client.sendRequestObservation()

    # Função chamada periodicamente pelo timer para atualizar o status do jogo, processar mensagens e tomar decisões
    def timer1_Tick(self):
        # Configuração inicial de conexão
        if self.client.connected and self.sayHello == 0:
            self.sayHello = 1
            self.client.sendName(self.name)
            if hasattr(self, 'botcolor'):
                self.client.sendRGB(self.botcolor[0], self.botcolor[1], self.botcolor[2])
        
        # Atualiza contadores e solicita status
        self.msgSeconds += self.timer1.interval * 1000
        self.client.sendRequestGameStatus()

        # Logs, scoreboard e timer periódicos (5 segundos)
        should_reset_timer = self.msgSeconds >= 5000
        if should_reset_timer:
            self.debug_manager.log_timer_info(self.gameStatus, self.GetTime()) # DEBUG
            self.debug_manager.log_full_scoreboard(self.sscoreList if self.sscoreList.strip() else '') # DEBUG
            self.client.sendRequestScoreboard()
            if len(self.msg) > 0:
                self.msg.clear()
            self.msgSeconds = 0
            
        # Decisão da IA (durante jogo)
        if self.gameStatus == "Game":
            self.DoDecision()

        # Engatilha próximo timer
        if self.running:
            self.timer1 = Timer(self.thread_interval, self.timer1_Tick)
            self.timer1.start()


    # Handler para mudanças de status da conexão
    def SocketStatusChange(self):
        if self.client.connected:
            self.debug_manager.log_connection_status(True, self.host, self.port) # DEBUG
            if self.sayHello == 0:
                self.sayHello = 1
                self.client.sendName(self.name)
                if hasattr(self, 'botcolor'):
                    self.client.sendRGB(self.botcolor[0],self.botcolor[1],self.botcolor[2]) 
            self.client.sendRequestGameStatus()
            self.client.sendRequestUserStatus()
            self.client.sendRequestObservation()
        else:
            self.debug_manager.log_connection_status(False) # DEBUG
            if self.running:
                self.sayHello = 0
                self.debug_manager.log_reconnecting() # DEBUG
                while(not self.client.connect(self.host, self.port)):
                    self.debug_manager.log_reconnect_failed() # DEBUG
                    time.sleep(5)
