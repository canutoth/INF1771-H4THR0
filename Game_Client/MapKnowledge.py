# MapKnowledge.py
# Mantém conhecimento incremental sobre o labirinto (59 x 34)

from typing import List, Tuple

class MapKnowledge:
    """Guarda e atualiza informações do labirinto.
    Cada célula contém:
        [0] seguro:      -1 (não), 0 (desconhecido), 1 (sim)
        [1] passável:    -1 (não), 0 (desconhecido), 1 (sim)
        [2] percepção:    0-6 conforme tabela
        [3] n_passagens:  contador de passagens pelo bloco
        [4] qtd_potion:   energia recuperada pela poção (0 se indef.)
    """
    #Tamanho do mapa, vai de (0,0) [esquerda superior] a (58,33) [direita inferior]
    WIDTH, HEIGHT = 59, 34

    # Índices auxiliares
    IDX_SAFE, IDX_WALK, IDX_PERCEPT, IDX_VISITS, IDX_PWR = range(5)

    # Percepções   
    PERCEPT = {
        "bloqueado":     0,
        "poço":          1,  
        "teleporter":    2,
        "ouro":          3,
        "anel":          4,
        "moeda":         5,
        "poçao":         6
    }

    # Vetores de deslocamento para pegar a célula à frente
    DIR_VEC = {
        "north": ( 0, -1),
        "east":  ( 1,  0),
        "south": ( 0,  1),
        "west":  (-1,  0)
    }

    def __init__(self):
        default = [0, 0, 0, 0, 0, 0]  # valores iniciais
        self.map: List[List[List[int]]] = [
            [default[:] for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)
        ]
        
        # Controle de print automático
        self.auto_print = False
        self.last_x = None
        self.last_y = None
        self.last_direction = None

    # --------------- API principal ---------------
    def update(self, x: int, y: int, direction: str, observations: List[str]) -> None:
        if not self._inside(x, y):
            return

        # Verifica se deve fazer print automático
        self._check_auto_print(x, y, direction)
        
        # Atualiza posição e direção atuais
        self.last_x = x
        self.last_y = y
        self.last_direction = direction

        cell = self.map[x][y]

        # -------- marca passagem pelo bloco atual --------
        cell[self.IDX_VISITS] += 1
        if cell[self.IDX_SAFE] == 0:
            cell[self.IDX_SAFE] = 1
        if cell[self.IDX_WALK] == 0:
            cell[self.IDX_WALK] = 1

        # flags p/ saber se há brisa ou flash entre as observações
        has_breeze = False
        has_flash  = False

        # -------- Processa cada observação individual --------
        for obs in observations:
            # BLOQUEIO
            if obs == "blocked":
                nx, ny = self._front(x, y, direction)
                if self._inside(nx, ny):
                    tgt = self.map[nx][ny]
                    tgt[self.IDX_SAFE]     =  1
                    tgt[self.IDX_WALK]     = -1
                    tgt[self.IDX_PERCEPT]  = self.PERCEPT["bloqueado"]

            # ITENS
            elif obs.startswith("blueLight"):
                if "#" in obs:
                    typ = obs.split("#", 1)[1]
                    if typ == "1":
                        cell[self.IDX_PERCEPT] = self.PERCEPT["anel"]
                    elif typ == "2":
                        cell[self.IDX_PERCEPT] = self.PERCEPT["moeda"]
                else:
                    cell[self.IDX_PERCEPT] = self.PERCEPT["ouro"]

            elif obs.startswith("redLight"):
                cell[self.IDX_PERCEPT] = self.PERCEPT["poçao"]
                if "#" in obs:
                    cell[self.IDX_PWR] = int(obs.split("#", 1)[1])

            # PERCEPÇÕES ADJACENTES
            elif obs == "breeze":
                has_breeze = True
                self._mark_adjacent(x, y, self.PERCEPT["poço"])
            elif obs == "flash":
                has_flash = True
                self._mark_adjacent(x, y, self.PERCEPT["teleporter"])

        # -------- se NÃO houver breeze nem flash, vizinhos são seguros --------
        if not has_breeze and not has_flash:
            self._mark_adjacent_safe(x, y)



    # --------------- Métodos auxiliares internos ---------------

    # Verifica se as coordenadas estão dentro dos limites do mapa (true/false)
    def _inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    # Retorna a célula à frente do agente
    def _front(self, x: int, y: int, direction: str) -> Tuple[int, int]:
        dx, dy = self.DIR_VEC.get(direction.lower(), (0, 0))
        return x + dx, y + dy

    # Marca as células adjacentes com a percepção dada
    def _mark_adjacent(self, x: int, y: int, percept_code: int) -> None:
        for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
            nx, ny = x + dx, y + dy
            if not self._inside(nx, ny):
                continue  # não sobrescreve se fora do mapa

            cell = self.map[nx][ny]
           
            if cell[self.IDX_SAFE] == 1:
                continue  # não sobrescreve se já for considerado seguro

            cell[self.IDX_PERCEPT] = percept_code 

    # Marca vizinhos como seguros, limpando marcas de poço/teleporter
    def _mark_adjacent_safe(self, x: int, y: int) -> None:
        for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
            nx, ny = x + dx, y + dy
            if not self._inside(nx, ny):
                continue
            cell = self.map[nx][ny]
            # Define como seguro e passável
            cell[self.IDX_SAFE] = 1
            if cell[self.IDX_WALK] == 0:
                cell[self.IDX_WALK] = 1
            # Remove marcações de poço ou teleporter, se houver
            if cell[self.IDX_PERCEPT] in (self.PERCEPT["poço"], self.PERCEPT["teleporter"]):
                cell[self.IDX_PERCEPT] = 0


    #--------------- [DEBUG] ---------------

    # Ativa ou desativa o print automático do mapa
    def set_auto_print(self, enabled: bool) -> None:
        self.auto_print = enabled

    # Verifica se deve fazer print automático e executa
    def _check_auto_print(self, x: int, y: int, direction: str) -> None:
        if self.auto_print and (self.last_x != x or self.last_y != y or self.last_direction != direction):
            if self.last_x is not None:  # Não printa na primeira execução
                print("\n# =============================================== MAPA DO CONHECIMENTO ================================================")
                self.print_map(x, y, direction)
                print("# =====================================================================================================================\n")

    def print_map(self, player_x: int = None, player_y: int = None, player_direction: str = None) -> None:
        colors = {
            'yellow':  '\033[33m',
            'blue':    '\033[34m',
            'red':     '\033[31m',
            'cyan':    '\033[36m',
            'gray':    '\033[90m',
            'purple':  '\033[35m',
            'black':   '\033[30m',
            'white':   '\033[37m',
            'green':   '\033[32m',
            'reset':   '\033[0m'
        }

        # Símbolos de direção para o jogador
        direction_symbols = {
            "north": "↑",
            "east":  "→", 
            "south": "↓",
            "west":  "←"
        }

        # Legenda horizontal
        legenda = (
            f"{colors['red']}X{colors['reset']}=Bloq. "
            f"{colors['purple']}°{colors['reset']}=Poço "
            f"{colors['cyan']}/{colors['reset']}=Telep. "
            f"{colors['yellow']}A{colors['reset']}=Anel "
            f"{colors['yellow']}M{colors['reset']}=Moeda "
            f"{colors['yellow']}O{colors['reset']}=Ouro "
            f"{colors['blue']}P{colors['reset']}=Poção "
            f"{colors['white']}*{colors['reset']}=Visit. "
            f"{colors['green']}↑→↓←{colors['reset']}=Player "
            f"{colors['black']}?{colors['reset']}=Desconh."
        )
        print(legenda)

        for y in range(self.HEIGHT):
            line = ""
            for x in range(self.WIDTH):
                cell   = self.map[x][y]
                visits = cell[self.IDX_VISITS]
                perc   = cell[self.IDX_PERCEPT]
                walk   = cell[self.IDX_WALK]

                # Verifica se é a posição atual do jogador
                if player_x == x and player_y == y and player_direction:
                    symbol = direction_symbols.get(player_direction.lower(), "?")
                    ch, color = f"{symbol} ", 'green'
                # 1) bloqueado
                elif walk == -1:
                    ch, color = "X ", 'red' 
                # 2) poço
                elif perc == self.PERCEPT["poço"]:
                    ch, color = "° ", 'purple'  
                # 3) teleporter
                elif perc == self.PERCEPT["teleporter"]:
                    ch, color = "/ ", 'cyan'  
                # 4) anel
                elif perc == self.PERCEPT["anel"]:
                    ch, color = "A ", 'yellow'
                # 5) moeda
                elif perc == self.PERCEPT["moeda"]:
                    ch, color = "M ", 'yellow'
                # 6) ouro
                elif perc == self.PERCEPT["ouro"]:
                    ch, color = "O ", 'yellow'
                # 7) poção
                elif perc == self.PERCEPT["poçao"]:
                    ch, color = "P ", 'blue'
                # 8) visitado sem percepção
                elif visits > 0:
                    ch, color = "* ", 'white'
                # 9) não visitado
                else:
                    ch, color = "? ", 'black'

                line += colors[color] + ch + colors['reset']
            print(line)

