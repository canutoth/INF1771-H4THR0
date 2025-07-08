from typing import List, Tuple, Optional, Iterator, Dict

# CLASSE DO CONHECIMENTO DE MAPA
# GUARDA E ATUALIZA INFORMAÇÕES DO LABIRINTO
class MapKnowledge:    
    """Guarda e atualiza informações do labirinto.
    Cada célula contém:
        [0] seguro:      -1 (não), 0 (desconhecido), 1 (sim)
        [1] passável:    -1 (não), 0 (desconhecido), 1 (sim)
        [2] percepção:   bit-flags (ver PERCEPT)
        [3] n_passagens: contador de passagens pelo bloco
        [4] certeza:     0 (desconhecido), 1 (certeza absoluta)
    """
    #Tamanho do mapa, vai de (0,0) [esquerda superior] a (58,33) [direita inferior]
    WIDTH, HEIGHT = 59, 34

    # Índices auxiliares
    IDX_SAFE, IDX_WALK, IDX_PERCEPT, IDX_VISITS, IDX_CERTAIN = range(5)

    # PERCEPÇÕES (bit-flags) ----------------------------------------------------
    # trocado para flags; permite múltiplas percepções num mesmo bloco
    PERCEPT = {
        "poço":          1 << 0,   # 1
        "teleporter":    1 << 1,   # 2
        "ouro":          1 << 2,   # 4
        "anel":          1 << 3,   # 8
        "moeda":         1 << 4,   # 16
        "poçao":         1 << 5,   # 32
        "bloqueado":     1 << 6,   # 64
        "nenhum":        0,
    }
    # ------------------------------------------------------------------------

    # Vetores de deslocamento para pegar a célula à frente
    DIRECTION_VECTORS = {
        "north": ( 0, -1),
        "east":  ( 1,  0),
        "south": ( 0,  1),
        "west":  (-1,  0)
    }

    def __init__(self):
        default = [0, 0, 0, 0, 0]  # valores iniciais [safe, walk, percept, visits, certain]
        self.map: List[List[List[int]]] = [
            [default[:] for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)
        ]
        
        # Controle de print automático
        self.auto_print = False
        self.last_x = None
        self.last_y = None
        self.last_direction = None
        self.last_observations = None
        
        # Sistema de inferência de poços
        self.pseudo_pocos: List[set] = []  # Lista de conjuntos de possíveis poços
        self.pseudo_teleporters: List[set] = []  # Lista de conjuntos de possíveis teleporters
        
        # Sistema de controle de respawn de itens
        self.item_respawn_timers: Dict[Tuple[int, int], int] = {}  # {(x, y): ticks_restantes}

    # ------------------------------ [API PRINCIPAL] ------------------------------
    #    ------------------------------ [INÍCIO] ------------------------------
    # ------------------------------ [API PRINCIPAL] ------------------------------

    def update(self, x: int, y: int, direction: str, observations: List[str]) -> None:

        # Verifica se deve fazer print automático
        self._check_auto_print(x, y, direction, observations)
        
        # Atualiza posição, direção e observações atuais
        self.last_x = x
        self.last_y = y
        self.last_direction = direction
        self.last_observations = observations[:]

        # Pega a coordenada atual
        cell = self.map[x][y]

        # Marca passagem pelo bloco atual 
        cell[self.IDX_VISITS] += 1
        cell[self.IDX_SAFE] = 1
        cell[self.IDX_WALK] = 1

        # flags p/ saber se há brisa ou flash entre as observações
        has_breeze = False
        has_flash  = False

        # Processa cada observação individual 
        for obs in observations:
            # BLOQUEIO
            if obs == "blocked":
                nx, ny = self._front(x, y, direction)
                if self._inside(nx, ny):
                    tgt = self.map[nx][ny]
                    tgt[self.IDX_SAFE] =  1
                    tgt[self.IDX_WALK] = -1
                    tgt[self.IDX_PERCEPT]  |= self.PERCEPT["bloqueado"]

            # ITENS
            elif obs.startswith("blueLight"): 
                if "#" in obs:
                    typ = obs.split("#", 1)[1]
                    if typ == "1":
                        cell[self.IDX_PERCEPT] |= self.PERCEPT["anel"]
                    elif typ == "2":
                        cell[self.IDX_PERCEPT] |= self.PERCEPT["moeda"]
                else:
                    cell[self.IDX_PERCEPT] |= self.PERCEPT["ouro"]

            elif obs.startswith("redLight"):
                cell[self.IDX_PERCEPT] |= self.PERCEPT["poçao"]

            # PERCEPÇÕES ADJACENTES
            elif obs == "breeze":
                has_breeze = True
                self._mark_adjacent(x, y, self.PERCEPT["poço"])
                self._add_pseudo_pits(x, y) # adiciona possíveis poços
                self._update_inference_system(x, y, "poço") # atualiza inferência apenas para poço

            elif obs == "flash":
                has_flash = True
                self._mark_adjacent(x, y, self.PERCEPT["teleporter"])
                self._add_pseudo_teleporters(x, y) # adiciona possíveis teleporters
                self._update_inference_system(x, y, "teleporter") # atualiza inferência apenas para teleporter

        # Se NÃO houver breeze nem flash, vizinhos são seguros 
        if not has_breeze and not has_flash:
            self._mark_adjacent_safe(x, y)

    # ------------------------------ [API PRINCIPAL] ------------------------------
    #      ------------------------------ [FIM] ------------------------------
    # ------------------------------ [API PRINCIPAL] ------------------------------



    # ------------------------------ [SISTEMA DE INFERÊNCIA] ------------------------------
    #        ------------------------------ [INÍCIO] ------------------------------
    # ------------------------------ [SISTEMA DE INFERÊNCIA] ------------------------------
    
    # Adiciona um conjunto de possíveis posições de ameaças baseado na percepção
    def _add_pseudo_positions(self, x: int, y: int, target_list: List[set]) -> None:
        possible_positions = set()
        
        for nx, ny in self._get_adjacent_positions(x, y):
            # Só adiciona se não for seguro
            if self.map[nx][ny][self.IDX_SAFE] != 1:
                possible_positions.add((nx, ny))
        
        target_list.append(possible_positions)
    
    # Adiciona um conjunto de possíveis poços baseado na brisa sentida
    def _add_pseudo_pits(self, x: int, y: int) -> None:
        self._add_pseudo_positions(x, y, self.pseudo_pocos)
    
    # Adiciona um conjunto de possíveis teleporters baseado no flash sentido
    def _add_pseudo_teleporters(self, x: int, y: int) -> None:
        self._add_pseudo_positions(x, y, self.pseudo_teleporters)
    
    # Atualiza o sistema de inferência removendo células seguras e aplicando regras
    def _update_inference_system(self, player_x: int, player_y: int, perception_type: str) -> None:
        
        self._remove_safe_from_pseudo_lists(player_x, player_y, perception_type) # Remove células seguras das adjacências do jogador apenas para o tipo específico
        self._apply_non_adjacent_rule(player_x, player_y, perception_type) # Aplica regra: ameaças não são adjacentes apenas nos arredores do jogador
    
    # Remove células seguras das adjacências do jogador apenas para o tipo de percepção ativado
    def _remove_safe_from_pseudo_lists(self, player_x: int, player_y: int, perception_type: str) -> None:
        # Pega as posições adjacentes ao jogador
        adjacent_positions = set(self._get_adjacent_positions(player_x, player_y))
        
        # Trabalha apenas com o tipo de percepção que foi ativado
        if perception_type == "poço":
            target_list = self.pseudo_pocos
            percept_code = self.PERCEPT["poço"]
        elif perception_type == "teleporter":
            target_list = self.pseudo_teleporters
            percept_code = self.PERCEPT["teleporter"]
        
        # Itera pela lista de trás para frente para poder remover elementos com segurança
        for i in range(len(target_list) - 1, -1, -1):
            pseudo_set = target_list[i]
            
            # Verifica se alguma posição adjacente ao jogador está no conjunto
            positions_to_check = pseudo_set.intersection(adjacent_positions)
            
            # Remove apenas as posições adjacentes que são seguras
            to_remove = set()
            for pos in positions_to_check:
                x, y = pos
                if self.map[x][y][self.IDX_SAFE] == 1:
                    to_remove.add(pos)
            
            pseudo_set -= to_remove
            
            # Se sobrou apenas uma posição, é certeza absoluta
            if len(pseudo_set) == 1:
                pos = next(iter(pseudo_set))
                x, y = pos
                # Marca definitivamente como certeza
                if self.map[x][y][self.IDX_CERTAIN] == 0:  # só marca se ainda não for certo
                    self.map[x][y][self.IDX_PERCEPT] |= percept_code
                    self.map[x][y][self.IDX_SAFE] = -1
                    self.map[x][y][self.IDX_WALK] = -1
                    self.map[x][y][self.IDX_CERTAIN] = 1  # marca como certeza
                
                # Remove o conjunto da lista (dois coelhos numa cajadada só)
                target_list.pop(i)
            
            # Se o conjunto ficou vazio, também remove
            elif len(pseudo_set) == 0:
                target_list.pop(i)
    
    # Aplicação da regra de que ameaças não são adjacentes (poços ou teleporters)
    def _apply_non_adjacent_rule(self, player_x: int, player_y: int, perception_type: str) -> None:
        # Verifica apenas as posições adjacentes ao jogador
        adjacent_positions = self._get_adjacent_positions(player_x, player_y)
        
        # Define qual tipo de ameaça estamos procurando
        if perception_type == "poço":
            threat_percept = self.PERCEPT["poço"]
            target_list = self.pseudo_pocos
        elif perception_type == "teleporter":
            threat_percept = self.PERCEPT["teleporter"]
            target_list = self.pseudo_teleporters
        else:
            return  # Tipo não reconhecido
        
        # Encontra ameaças com certeza absoluta apenas nos arredores
        certain_threats = []
        for x, y in adjacent_positions:
            cell = self.map[x][y]
            if ((cell[self.IDX_PERCEPT] & threat_percept) and 
                cell[self.IDX_CERTAIN] == 1):
                certain_threats.append((x, y))
        
        # Remove posições adjacentes a ameaças confirmadas de todos os conjuntos
        for threat_pos in certain_threats:
            tx, ty = threat_pos
            adjacent_to_threat = set(self._get_all_adjacent_positions(tx, ty))  # Inclui diagonais
            
            # Marca todas as posições adjacentes como seguras
            for adj_x, adj_y in adjacent_to_threat:
                adj_cell = self.map[adj_x][adj_y]
                # só mexe se o vizinho tiver a MESMA ameaça
                if adj_cell[self.IDX_PERCEPT] & threat_percept:
                    adj_cell[self.IDX_SAFE] = 1  # marca como seguro
                    adj_cell[self.IDX_PERCEPT] &= ~threat_percept  # remove percepção da ameaça
            
            # Remove das listas de possíveis ameaças
            for pseudo_set in target_list:
                pseudo_set -= adjacent_to_threat
    
    # ------------------------------ [SISTEMA DE INFERÊNCIA] ------------------------------
    #        ------------------------------ [FIM] ------------------------------
    # ------------------------------ [SISTEMA DE INFERÊNCIA] ------------------------------


    
    # ------------------------------ [MÉTODOS AUXILIARES INTERNOS] ------------------------------
    #           ------------------------------ [INÍCIO] ------------------------------
    # ------------------------------ [MÉTODOS AUXILIARES INTERNOS] ------------------------------

    # Verifica se as coordenadas estão dentro dos limites do mapa (true/false)
    def _inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT
    
    # Retorna uma lista de tuplas (x, y) das células adjacentes válidas (4 direções)
    def _get_adjacent_positions(self, x: int, y: int) -> List[Tuple[int, int]]:
        adjacent = []
        for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
            nx, ny = x + dx, y + dy
            if self._inside(nx, ny):
                adjacent.append((nx, ny))
        return adjacent
    
    # Retorna uma lista de tuplas (x, y) das células adjacentes e diagonais válidas (8 direções)
    def _get_all_adjacent_positions(self, x: int, y: int) -> List[Tuple[int, int]]:
        adjacent = []
        for dx, dy in ((1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)):
            nx, ny = x + dx, y + dy
            if self._inside(nx, ny):
                adjacent.append((nx, ny))
        return adjacent

    # Retorna a célula à frente do agente
    def _front(self, x: int, y: int, direction: str) -> Tuple[int, int]:
        dx, dy = self.DIRECTION_VECTORS.get(direction.lower(), (0, 0))
        return x + dx, y + dy

    # Marca as células adjacentes com a percepção dada
    def _mark_adjacent(self, x: int, y: int, percept_code: int) -> None:
        for nx, ny in self._get_adjacent_positions(x, y):
            cell = self.map[nx][ny]
           
            if cell[self.IDX_SAFE] == 1:
                continue  # não sobrescreve se já for considerado seguro
            
            cell[self.IDX_PERCEPT] |= percept_code 

    # Marca vizinhos como seguros, limpando marcas de poço/teleporter
    def _mark_adjacent_safe(self, x: int, y: int) -> None:
        danger_flags = self.PERCEPT["poço"] | self.PERCEPT["teleporter"]
        for nx, ny in self._get_adjacent_positions(x, y):
            cell = self.map[nx][ny]
            # Define como seguro 
            cell[self.IDX_SAFE] = 1
            # Remove marcações de poço ou teleporter, se houver
            cell[self.IDX_PERCEPT] &= ~danger_flags

    # Itera sobre as células livres (seguras, não visitadas e sem percepção)
    def _iter_free_cells(
        self,
        player_x: int,
        player_y: int,
        max_manhattan: int = 0
    ) -> Iterator[Tuple[int, int, int]]:
        if max_manhattan:
            x_min = max(player_x - max_manhattan, 0)
            x_max = min(player_x + max_manhattan, self.WIDTH  - 1)
            y_min = max(player_y - max_manhattan, 0)
            y_max = min(player_y + max_manhattan, self.HEIGHT - 1)
        else:
            x_min, y_min, x_max, y_max = 0, 0, self.WIDTH - 1, self.HEIGHT - 1

        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                cell = self.map[x][y]
                if (cell[self.IDX_SAFE] == 1 and
                    cell[self.IDX_WALK] == 0 and
                    cell[self.IDX_PERCEPT] == 0):

                    dist = abs(x - player_x) + abs(y - player_y)
                    if max_manhattan and dist > max_manhattan:
                        continue
                    yield x, y, dist

    # ------------------------------ [MÉTODOS AUXILIARES INTERNOS] ------------------------------
    #           ------------------------------ [FIM] ------------------------------
    # ------------------------------ [MÉTODOS AUXILIARES INTERNOS] ------------------------------



    # ------------------------------ [MÉTODOS AUXILIARES EXTERNOS] ------------------------------
    #           ------------------------------ [INÍCIO] ------------------------------
    # ------------------------------ [MÉTODOS AUXILIARES EXTERNOS] ------------------------------

    # Retorna o mapa de conhecimento completo com 1s (andável) e 0s (não andável), para A*
    def get_safe_map(self) -> List[List[int]]:
        safe_map = []
        for x in range(self.WIDTH):
            column = []
            for y in range(self.HEIGHT):
                cell = self.map[x][y]
                is_passable = (cell[self.IDX_SAFE] == 1 and cell[self.IDX_WALK] != -1) # Seguro e não bloqueado
                column.append(1 if is_passable else 0)
            safe_map.append(column)
        return safe_map

    # Retorna as coordenadas livres (seguras, não visitadas e sem percepção) no mapa
    # Aceita parametro opcional max_manhattan para limitar a distância de Manhattan
    def get_free_coordinates(
        self,
        player_x: int,
        player_y: int,
        max_manhattan: int = 0
    ) -> List[Tuple[int, int]]:
        return [(x, y) for x, y, _ in
                self._iter_free_cells(player_x, player_y, max_manhattan)]

    # Retorna a coordenada livre mais próxima do jogador, considerando a distância de Manhattan
    def get_free_coordinate_nearest(
        self,
        player_x: int,
        player_y: int,
        max_manhattan: int = 0
    ) -> Optional[Tuple[int, int]]:
        best = min(
            self._iter_free_cells(player_x, player_y, max_manhattan),
            key=lambda t: t[2],
            default=None
        )
        return (best[0], best[1]) if best else None

    # Retorna coordenadas conhecidas (seguras e walkable) dentro da distância Manhattan especificada
    def get_known_coordinates(
        self,
        player_x: int,
        player_y: int,
        max_manhattan: int = 0
    ) -> List[Tuple[int, int]]:
        known_coords = []
        
        # Define os limites da busca
        if max_manhattan > 0:
            x_min = max(player_x - max_manhattan, 0)
            x_max = min(player_x + max_manhattan, self.WIDTH - 1)
            y_min = max(player_y - max_manhattan, 0)
            y_max = min(player_y + max_manhattan, self.HEIGHT - 1)
        else:
            x_min, y_min, x_max, y_max = 0, 0, self.WIDTH - 1, self.HEIGHT - 1

        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                # Verifica se está dentro da distância Manhattan
                if max_manhattan > 0:
                    manhattan_dist = abs(x - player_x) + abs(y - player_y)
                    if manhattan_dist > max_manhattan:
                        continue
                
                cell = self.map[x][y]
                # Coordenada conhecida: segura e walkable (visitada ou confirmada)
                if (cell[self.IDX_SAFE] == 1 and 
                    cell[self.IDX_WALK] == 1 and 
                    (x != player_x or y != player_y)):  # Exclui posição atual
                    known_coords.append((x, y))
        
        return known_coords

    # Verifica se há ouro na célula especificada
    def is_gold_here(self, x: int, y: int) -> bool:
        gold_flags = self.PERCEPT["ouro"] | self.PERCEPT["anel"] | self.PERCEPT["moeda"]
        return bool(self.map[x][y][self.IDX_PERCEPT] & gold_flags)
    
    # Verifica se há uma poção na célula especificada
    def is_potion_here(self, x: int, y: int) -> bool:
        return bool(self.map[x][y][self.IDX_PERCEPT] & self.PERCEPT["poçao"])
    
    
    # Registra que um item foi pego na coordenada especificada, iniciando o timer de respawn de 300 ticks
    def register_item_picked(self, x: int, y: int) -> None:
        self.item_respawn_timers[(x, y)] = 300
    
    # Atualiza os timers de respawn (deve ser chamado a cada tick)
    def update_respawn_timers(self) -> None:
        # Itera de trás para frente para poder remover items com segurança
        expired_positions = []
        for position, ticks_remaining in self.item_respawn_timers.items():
            new_ticks = ticks_remaining - 1
            if new_ticks <= 0:
                expired_positions.append(position)
            else:
                self.item_respawn_timers[position] = new_ticks
        
        # Remove posições que expiraram
        for position in expired_positions:
            del self.item_respawn_timers[position]
    
    # Verifica se um item pode ser pego na coordenada especificada
    def can_pick_item(self, x: int, y: int) -> bool:
        return (x, y) not in self.item_respawn_timers
    
    # Retorna informações sobre items em cooldown (para debug)
    def get_respawn_info(self) -> Dict[Tuple[int, int], int]:
        return self.item_respawn_timers.copy()
    
    # Verifica se a coordenada é segura e andável
    def is_free(self, x: int, y: int) -> bool:
        if not self._inside(x, y):
            return False
        cell = self.map[x][y]
        return cell[self.IDX_SAFE] == 1 and cell[self.IDX_WALK] == 1
    
    # ------------------------------ [MÉTODOS AUXILIARES EXTERNOS] ------------------------------
    #           ------------------------------ [FIM] ------------------------------
    # ------------------------------ [MÉTODOS AUXILIARES EXTERNOS] ------------------------------



    # ------------------------------ [DEBUG] ------------------------------
    #  ----------------------------- [INÍCIO] -----------------------------
    # ------------------------------ [DEBUG] ------------------------------

    # Ativa ou desativa o print automático do mapa
    def set_auto_print(self, enabled: bool) -> None:
        self.auto_print = enabled

    # Verifica se deve fazer print automático e executa
    def _check_auto_print(self, x: int, y: int, direction: str, observations: List[str]) -> None:
        if not self.auto_print:
            return
            
        # Verifica se houve mudança significativa
        position_changed = (self.last_x != x or self.last_y != y)
        direction_changed = (self.last_direction != direction)
        observations_changed = (self.last_observations != observations)
        
        # Ignora mudanças para observações vazias ou "nenhum" se não houve mudança de posição/direção
        trivial_observations = observations == ['nenhum'] or observations == []
        
        should_print = (position_changed or direction_changed or 
                       (observations_changed and not trivial_observations))
        
        if should_print and self.last_x is not None:  
            print("\n# =============================================== MAPA DO CONHECIMENTO ================================================")
            self.print_map(x, y, direction)
            print("# =====================================================================================================================\n")

    def print_map(self, player_x: int = None, player_y: int = None, player_direction: str = None) -> None:
        # limpa a tela e move o cursor 5 linhas pra baixo
        print("\033[2J"   # limpa tudo
          "\033[5B", # move cursor 5 linhas pra baixo
          end="")
        
        colors = {
            'yellow':  '\033[33m',
            'blue':    '\033[34m',
            'red':     '\033[31m',
            'cyan':    '\033[36m',
            'gray':    '\033[90m',
            'purple':  '\033[35m',
            'magenta': '\033[95m',
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
            f"{colors['purple']}X{colors['reset']}=Poço[ctz] "
            f"{colors['cyan']}/{colors['reset']}=Telep. "
            f"{colors['cyan']}X{colors['reset']}=Telep.[ctz] "
            f"{colors['magenta']}Ø{colors['reset']}=Poço+Telep "
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
                    # Se também for poço, cor roxa (poço confirmado)
                    if perc & self.PERCEPT["poço"]:
                        ch, color = "X ", 'purple'
                    # Se também for teleporter, cor ciano (teleporter confirmado)
                    elif perc & self.PERCEPT["teleporter"]:
                        ch, color = "X ", 'cyan'
                    else:
                        ch, color = "X ", 'red'
                # 2) combinação poço+teleporter (checa antes dos individuais)
                elif perc & (self.PERCEPT["poço"] | self.PERCEPT["teleporter"]) == \
                     (self.PERCEPT["poço"] | self.PERCEPT["teleporter"]):
                    ch, color = "Ø ", 'magenta'
                # 3) poço
                elif perc & self.PERCEPT["poço"]:
                    ch, color = "° ", 'purple'  
                # 4) teleporter
                elif perc & self.PERCEPT["teleporter"]:
                    ch, color = "/ ", 'cyan'  
                # 5) anel
                elif perc & self.PERCEPT["anel"]:
                    ch, color = "A ", 'yellow'
                # 6) moeda
                elif perc & self.PERCEPT["moeda"]:
                    ch, color = "M ", 'yellow'
                # 7) ouro
                elif perc & self.PERCEPT["ouro"]:
                    ch, color = "O ", 'yellow'
                # 8) poção
                elif perc & self.PERCEPT["poçao"]:
                    ch, color = "P ", 'blue'
                # 9) visitado sem percepção
                elif visits > 0:
                    ch, color = "* ", 'white'
                # 10) não visitado
                else:
                    ch, color = "? ", 'black'

                line += colors[color] + ch + colors['reset']
            print(line)


    # ------------------------------ [DEBUG] ------------------------------
    # ------------------------------- [FIM] -----------------------------
    # ------------------------------ [DEBUG] ------------------------------