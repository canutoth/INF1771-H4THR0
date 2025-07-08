from typing import List, Tuple
from queue import PriorityQueue
from MapKnowledge import MapKnowledge

# CLASSE DO PATHFINDER
# RESPONSÁVEL POR CALCULAR CAMINHOS USANDO O ALGORITMO A*
class PathFinder:
    
    # Direções: North, East, South, West
    DIRECTIONS = ["north", "east", "south", "west"]
    
    # Vetores de deslocamento para cada direção
    DIRECTION_VECTORS = {
        "north": (0, -1),
        "east":  (1, 0),
        "south": (0, 1),
        "west":  (-1, 0)
    }
    
    # Mapeamento de direção para índice
    DIR_TO_INDEX = {direction: i for i, direction in enumerate(DIRECTIONS)}
    
    def __init__(self, map_knowledge: MapKnowledge):
        self.map_knowledge = map_knowledge
    
    # Calcula a quantidade mínima de passos necessários para chegar ao destino.
    def time_estimated_to_go(self, current_x: int, current_y: int, current_direction: str, 
                            target_x: int, target_y: int) -> int:
        
        # Chama o go_to para obter o caminho
        path = self.go_to(current_x, current_y, current_direction, target_x, target_y)
        
        # Retorna a quantidade de passos necessários
        return len(path)
    
    # Calcula o caminho do ponto atual até o destino usando A*.
    # Args:
        #current_x, current_y: Posição atual do agente.
        # current_direction: Direção atual do agente.
        # target_x, target_y: Posição de destino.
    # Retorno:
        #  Lista de ações ["andar", "virar_esquerda", "virar_direita"]
    def go_to(self, current_x: int, current_y: int, current_direction: str, 
              target_x: int, target_y: int) -> List[str]:

        # Se já está no destino, não precisa se mover
        if current_x == target_x and current_y == target_y:
            return []
        
        # Verifica se o destino é válido
        if not self._inside(target_x, target_y):
            return []
        
        # Obtém o mapa seguro
        safe_map = self.map_knowledge.get_safe_map()
        
        # Verifica se o destino é passável
        if safe_map[target_x][target_y] != 1:
            return []
        
        # Estado inicial: (x, y, direction_index)
        current_dir_index = self.DIR_TO_INDEX.get(current_direction.lower(), 0)
        start_state = (current_x, current_y, current_dir_index)
        goal_position = (target_x, target_y)
        
        # Executa A*
        g_scores, predecessors, actions = self._a_star(safe_map, start_state, goal_position)
        
        # Extrai o caminho
        path = self._extract_path(g_scores, predecessors, actions, goal_position)
        return path

    # Implementa o algoritmo A*.  
    # Retorno:
        # Tupla (g_scores, predecessors, actions) - sempre encontra um caminho
    def _a_star(self, safe_map: List[List[int]], start_state: Tuple[int, int, int], 
                goal_position: Tuple[int, int]) -> Tuple[dict, dict, dict]:

        priority_queue = PriorityQueue()
        g_scores = {start_state: 0}
        predecessors = {start_state: None}
        actions = {start_state: None}
        
        # Heurística inicial (distância Manhattan)
        h_initial = self._manhattan_distance(start_state[:2], goal_position)
        priority_queue.put((h_initial, start_state))
        
        while not priority_queue.empty():
            _, current_state = priority_queue.get()
            current_x, current_y, current_dir = current_state
            
            # Verifica se chegou ao destino (qualquer direção)
            if (current_x, current_y) == goal_position:
                return g_scores, predecessors, actions
            
            # Explora vizinhos
            for next_state, cost, action in self._get_neighbors(safe_map, current_x, current_y, current_dir):
                new_g_score = g_scores[current_state] + cost
                
                if new_g_score < g_scores.get(next_state, float('inf')):
                    g_scores[next_state] = new_g_score
                    predecessors[next_state] = current_state
                    actions[next_state] = action
                    
                    # Heurística (distância Manhattan)
                    h_score = self._manhattan_distance(next_state[:2], goal_position)
                    f_score = new_g_score + h_score
                    priority_queue.put((f_score, next_state))
        
        # Nunca deveria chegar aqui, pois sempre há um caminho
        return g_scores, predecessors, actions
    
    # Retorna os vizinhos possíveis de uma posição com suas ações correspondentes.
    # Retorno:
        # Lista de tuplas ((next_x, next_y, next_dir), cost, action)
    def _get_neighbors(self, safe_map: List[List[int]], x: int, y: int, 
                      direction_index: int) -> List[Tuple[Tuple[int, int, int], int, str]]:
        neighbors = []
        
        # Virar à esquerda (custo 1)
        left_dir = (direction_index - 1) % 4
        neighbors.append(((x, y, left_dir), 1, "virar_esquerda"))
        
        # Virar à direita (custo 1)
        right_dir = (direction_index + 1) % 4
        neighbors.append(((x, y, right_dir), 1, "virar_direita"))
        
        # Andar para frente (custo 1, se possível)
        dx, dy = self.DIRECTION_VECTORS[self.DIRECTIONS[direction_index]]
        next_x, next_y = x + dx, y + dy
        
        # Verifica se a próxima posição é válida e passável
        if (self._inside(next_x, next_y) and safe_map[next_x][next_y] == 1):
            neighbors.append(((next_x, next_y, direction_index), 1, "andar"))
        
        return neighbors
    
    # Extrai o caminho de ações do resultado do A*.   
    # Returns:
        # Lista de ações para chegar ao destino
    def _extract_path(self, g_scores: dict, predecessors: dict, actions: dict, 
                     goal_position: Tuple[int, int]) -> List[str]:
        
        # Encontra o estado final com menor custo (qualquer direção no destino)
        goal_states = [
            (goal_position[0], goal_position[1], d) 
            for d in range(4) 
            if (goal_position[0], goal_position[1], d) in g_scores
        ]
        
        # Se não encontrou nenhum caminho para o destino, retorna lista vazia
        if not goal_states:
            return []
        
        # Escolhe o estado com menor custo
        end_state = min(goal_states, key=lambda state: g_scores[state])
        
        # Reconstrói o caminho
        path = []
        current_state = end_state
        
        while actions[current_state] is not None:
            path.append(actions[current_state])
            current_state = predecessors[current_state]
        
        # Retorna o caminho na ordem correta
        return list(reversed(path))
    
    # Calcula a distância Manhattan entre duas posições.
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    # Verifica se as coordenadas estão dentro dos limites do mapa.
    def _inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.map_knowledge.WIDTH and 0 <= y < self.map_knowledge.HEIGHT


# Função de conveniência para linkar o PathFinder com o MapKnowledge.
def create_path_finder(map_knowledge: MapKnowledge) -> PathFinder:
    return PathFinder(map_knowledge)

