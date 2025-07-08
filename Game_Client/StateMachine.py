from typing import Callable, Dict, Any, Optional, Tuple, List
import random
from PathFinder import PathFinder

class GameStateMachine:
    """Três estados funcionais: Exploration ⇄ LookForOponent ⇄ Attack."""
    def __init__(self):
        self.state = "Exploration"
        self._look_cooldown_until = 0  # Para controle de cooldown de 5s
        self.handlers: Dict[str, Callable[[Any], str]] = {
            "Exploration":      self._exploration,
            "LookForOponent":   self._look_for_oponent,
            "Attack":           self._attack,
        }
        
        # Sistema de navegação
        self._current_path: List[str] = []  # Caminho atual sendo seguido
        self._current_target: Optional[Tuple[int, int]] = None  # Destino atual
        self._path_finder: Optional[PathFinder] = None

    # ---------- API pública ----------
    def next_action(self, ctx) -> str:
        # Inicializa PathFinder se necessário
        if self._path_finder is None:
            self._path_finder = PathFinder(ctx.map_knowledge)
        else:
            # Atualiza a referência do MapKnowledge no PathFinder
            self._path_finder.map_knowledge = ctx.map_knowledge
            
        previous_state = self.state
        self._pick_state(ctx)
        
        # Se mudou de estado, limpa navegação atual
        if previous_state != self.state:
            self._clear_navigation()
            
        return self.handlers[self.state](ctx) or ""

    # ---------- Transições ----------
    def _pick_state(self, a):
        if a.see_enemy():                                # viu inimigo → Attack
            self.state = "Attack"
            return
        if a.look_mode_active():                         # ainda procurando
            self.state = "LookForOponent"
            return
        if a.hear_steps() and a.game_time_ticks >= self._look_cooldown_until:  # ouviu steps e não está em cooldown
            a.start_look_mode()
            self.state = "LookForOponent"
            return
        self.state = "Exploration"                       # fallback

    # ---------- Handlers ----------
    def _attack(self, a):
        if not a.see_enemy():                            # perdeu alvo
            return ""                                    # volta p/ Exploration
        
        dist = a.enemy_dist()
        
        # Implementa as regras de combate baseadas na distância Manhattan
        if 10 >= dist >= 8:                              # 10-8: 1 tiro + move forward
            if a.energy >= 10:  # Verifica se tem energia para atirar
                return "atacar"
            else:
                return "andar"
        elif 8 > dist >= 6:                              # 8-6: 2 tiros + move forward  
            if a.energy >= 20:  # Precisa de energia para 2 tiros
                return "atacar"  # Por simplicidade, fazemos 1 tiro por vez
            else:
                return "andar"
        elif 6 > dist >= 3:                              # 6-3: 3 tiros, mantém posição
            if a.energy >= 10:
                return "atacar"
            else:
                return ""  # Mantém posição sem energia
        elif 3 > dist >= 1:                              # 3-1: 4 tiros + move backward
            if a.energy >= 10:
                return "atacar"
            else:
                return "andar_re"
        else:
            return "andar"  # Fallback - se aproxima

    def _look_for_oponent(self, a):
        if a.see_enemy():                                # achou → Attack
            self.state = "Attack"
            return ""
        if a.look_step_done():                           # completou 3 giros/timeout
            self._look_cooldown_until = a.game_time_ticks + 50  # Cooldown de 5 segundos (50 ticks)
            return ""                                    # cai p/ Exploration
        return "virar_direita"                           # gira procurando

    def _exploration(self, a):
        # Se já tem um caminho em andamento, continua seguindo
        if self._current_path:
            return self._follow_current_path()
        
        # Se chegou ao destino atual, limpa navegação
        if (self._current_target and 
            a.player.x == self._current_target[0] and 
            a.player.y == self._current_target[1]):
            self._clear_navigation()
        
        # Escolhe novo destino aleatoriamente conforme percentuais especificados
        rand = random.randint(1, 100)
        tgt = None
        
        if rand <= 2:  # 2% → bloco conhecido aleatório
            known_coords = a.map_knowledge.get_known_coordinates(a.player.x, a.player.y, 0)
            tgt = random.choice(known_coords) if known_coords else None
        elif rand <= 5:  # 3% → bloco livre aleatório  
            free_coords = a.map_knowledge.get_free_coordinates(a.player.x, a.player.y, 0)
            tgt = random.choice(free_coords) if free_coords else None
        elif rand <= 10:  # 5% → bloco conhecido com ≤10 de distância
            known_coords = a.map_knowledge.get_known_coordinates(a.player.x, a.player.y, 10)
            tgt = random.choice(known_coords) if known_coords else None
        elif rand <= 20:  # 10% → bloco livre entre 5–15 de distância
            free_coords = a.map_knowledge.get_free_coordinates(a.player.x, a.player.y, random.randint(5, 15))
            tgt = random.choice(free_coords) if free_coords else None
        elif rand <= 35:  # 15% → bloco livre até 5 de distância
            free_coords = a.map_knowledge.get_free_coordinates(a.player.x, a.player.y, 5)
            tgt = random.choice(free_coords) if free_coords else None
        else:  # resto → bloco livre mais próximo
            tgt = a.map_knowledge.get_free_coordinate_nearest(a.player.x, a.player.y)
        
        # Se encontrou um alvo, calcula caminho e inicia navegação
        if tgt:
            return self._navigate_to_target(a, tgt)
        else:
            # Se não há alvo, gira para explorar
            return "virar_esquerda"
    
    # ---------- Sistema de Navegação ----------

    # Limpa o caminho e destino atuais.
    def _clear_navigation(self):
        self._current_path = []
        self._current_target = None
    
    # Inicia a navegação para um novo destino.
    def _navigate_to_target(self, a, target: Tuple[int, int]) -> str:
        self._current_target = target
        
        # Calcula caminho usando PathFinder
        path = self._path_finder.go_to(
            a.player.x, a.player.y, a.dir, 
            target[0], target[1]
        )
        
        # Se não conseguiu encontrar caminho, limpa navegação e gira
        if not path:
            self._clear_navigation()
            return "virar_esquerda"
        
        self._current_path = path
        return self._follow_current_path()
    
    # Segue o próximo passo do caminho atual.
    def _follow_current_path(self) -> str:
        if not self._current_path:
            return ""
        
        # Pega próxima ação e remove da lista
        next_action = self._current_path.pop(0)
        return next_action

