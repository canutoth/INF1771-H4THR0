from typing import Callable, Dict, Any, Optional, Tuple, List
import random
from PathFinder import PathFinder

# CLASSE BASE DO STATE MACHINE
# TRÊS ESTADOS FUNCIONAIS: Exploration ⇄ LookForOponent ⇄ Attack.
class GameStateMachine:
    def __init__(self):
        self.state = "Exploration"
        # Attack
        self._attack_count = 0
        self._attack_cooldown_until = 0
        self._attack_sequence: List[str] = []

        # Look-mode
        self._look_mode = False             # se está girando pra achar inimigo
        self._look_turns = 0                # quantos giros já fez
        self._look_cooldown_until = 0       # tick até poder reativar look-mode

        # Navegação
        self._current_path: List[str] = []  # Caminho atual sendo seguido
        self._current_target: Optional[Tuple[int, int]] = None  # Destino atual
        self._path_finder: Optional[PathFinder] = None

        # Evade
        self._last_hit_time = None
        self._last_evade_axis = 0   # 0 = nenhum, 1 = frente/trás ou 2 = esquerda/direita
        self._evade_sequence: List[str] = []
        self.AXIS = {
            "nenhum": 0,
            "frente/trás": 1,  
            "esquerda/direita":  2
        }

        # FindGold
        self._gold_objective_position = None 

        # FindPotion
        self._potion_objective_position = None 

        self.handlers: Dict[str, Callable[[Any], str]] = {
            "Exploration":      self._exploration,
            "LookForOponent":   self._look_for_oponent,
            "Attack":           self._attack,
            "Evade":            self._evade, 
            "FindGold":         self._find_gold,
            "FindPotion":       self._find_potion  
        }
        
    # ---------- API pública ----------
    def next_action(self, game_ai) -> str:
        if self._path_finder is None:
            self._path_finder = PathFinder(game_ai.map_knowledge)
        else:
            self._path_finder.map_knowledge = game_ai.map_knowledge
        prev = self.state
        self._pick_state(game_ai)

        if self._last_hit_time is not None and game_ai.game_time_ticks - self._last_hit_time > 5:
            self._evade_sequence.clear()
            self._last_hit_time = None # Reseta o tempo do último hit após 5 ticks (tenta ir pra frente/trás primeiro)
            self._last_evade_axis = self.AXIS["nenhum"]  # Reseta lógica de evade

        # Se mudou de estado
        if prev != self.state:
            # Se mudou de estado e estava em FindPotion, limpa navegação
            if prev == "FindPotion":
                self._clear_navigation()

            # Se mudou de estado e estava em FindGold, limpa navegação
            if prev == "FindGold":
                self._clear_navigation()

            # Se mudou de estado e estava em Attack, reseta contagem e sequência
            if prev == "Attack":
                self._attack_sequence.clear()
                self._attack_count = 0

            # Se mudou de estado e estava em Exploration, limpa navegação
            if prev == "Exploration":
                self._clear_navigation()

        return self.handlers[self.state](game_ai) or ""

    # ---------- Transições ----------
    def _pick_state(self, game_ai):

        # Se tomou dano -> Evade
        if game_ai.take_hit():
            self.state = "Evade"
            self._last_hit_time = game_ai.game_time_ticks
            return
        
        # Se poçao conhecida e energia <=30 -> FindPotion
        have_potion = game_ai.have_potion()
        if have_potion[0] and game_ai.energy_leq(30):  
            self._potion_objective_position = have_potion[1] # posição da poçao, recebe tuple[int,int]
            self.state = "FindPotion"
            return

        # Viu inimigo e não está em cooldown -> Attack
        if game_ai.see_enemy() and game_ai.game_time_ticks >= self._attack_cooldown_until:  
            self.state = "Attack"
            return
            
        # Se ouro disponível conhecido está a <2s de tempo de distância sobrando de respawn -> FindGold
        gold_spawning_soon = game_ai.gold_spawning_soon()
        if gold_spawning_soon[0]:
            self._gold_objective_position = gold_spawning_soon[1] # posição do ouro, recebe tuple[int,int]
            self.state = "FindGold"
            return
        
        # Se poçao disponível conhecida e energia <50 e alguma energia até 15 manhattan -> FindPotion
        have_potion = game_ai.have_potion()
        if have_potion[0] and game_ai.energy_leq(50):  
            self._potion_objective_position = have_potion[1] # posição da poçao, recebe tuple[int,int]
            self.state = "FindPotion"
            return

        # Se poçao disponível conhecida está a <2s de tempo de distância sobrando de respawn, energia <=90 e a distancia até 10 manhattam -> FindPotion
        potion_spawning_soon = game_ai.potion_spawning_soon()
        if potion_spawning_soon[0]:
            self._potion_objective_position = potion_spawning_soon[1] # posição da poçao, recebe tuple[int,int]
            self.state = "FindPotion"
            return
        
        # Se conhece ouro disponível e está 500+ rounds sem aumentar score -> FindGold
        if not game_ai.scored_recently(500):
            have_gold = game_ai.have_gold()
            if have_gold[0]:  
                self._gold_objective_position = have_gold[1] # posição da poçao, recebe tuple[int,int]
                self.state = "FindGold"
                return
        
        # Está no modo look -> LookForOponent
        if self._look_mode:
            self.state = "LookForOponent"
            return

        # Ouviu passos e não está em cooldown -> LookForOponent
        if game_ai.hear_steps() and game_ai.game_time_ticks >= self._look_cooldown_until:
            self._look_mode = True
            self._look_turns = 0
            self.state = "LookForOponent"
            return
        
        # Se não está em nenhum outro estado -> Exploration
        self.state = "Exploration"                      

    # ---------- Handlers ----------
    def _attack(self, game_ai):
        if game_ai.game_time_ticks < self._attack_cooldown_until:
            return ""
        if not game_ai.see_enemy():                            # perdeu alvo
            return ""                                    # volta p/ Exploration
        dist = game_ai.enemy_dist()
        
         # se sequência vazia, construí-la de acordo com a distância
        if not self._attack_sequence:
            dist = game_ai.enemy_dist()
            if 10 >= dist >= 8:
                # 1 tiro + move forward
                nx, ny = game_ai.NextPositionRelative(1, "frente")
                if game_ai.map_knowledge.is_free(nx, ny):
                  self._attack_sequence = ["atacar", "andar"]
                else:
                  self._attack_sequence = ["atacar"]
            elif 8 > dist >= 6:
                # 2 tiros + move forward
                nx, ny = game_ai.NextPositionRelative(1, "frente")
                if game_ai.map_knowledge.is_free(nx, ny):
                  self._attack_sequence = ["atacar", "atacar", "andar"]
                else:
                  self._attack_sequence = ["atacar"]
            elif 6 > dist >= 3:
                # 3 tiros, mantém posição
                self._attack_sequence = ["atacar"] * 3
            elif 3 > dist >= 1:
                # 4 tiros + move backward
                nx, ny = game_ai.NextPositionRelative(1, "atras")
                if game_ai.map_knowledge.is_free(nx, ny):
                    self._attack_sequence = ["atacar"] * 4 + ["andar_re"]
                else:
                    self._attack_sequence = ["atacar"]
        # pega próxima ação
        action = self._attack_sequence.pop(0)
        # contador e cooldown após 10 tiros consecutivos
        if action == "atacar":
            self._attack_count += 1
            if self._attack_count > 10:
                self._attack_cooldown_until = game_ai.game_time_ticks + 10
                return ""
        return action


    def _look_for_oponent(self, game_ai):
        # se avistar inimigo durante o look, interrompe e parte pra Attack
        if game_ai.see_enemy():
            self._look_mode = False      # desativa look-mode
            self.state = "Attack"        # muda pra estado de ataque
            return ""
        
        # contabiliza mais um giro procurando oponente
        self._look_turns += 1
        
        # se já girou 3 vezes ou não ouve mais passos, encerra o look-mode
        if self._look_turns >= 3 or not game_ai.hear_steps():
            self._look_mode = False                                     # reset do look-mode
            self._look_cooldown_until = game_ai.game_time_ticks + 50    # aplica cooldown de 5s
            self.state = "Exploration"                                  # volta ao modo de exploração
            return ""
        
        return "virar_direita"  # gira mais uma vez para a direita


    def _exploration(self, game_ai):
        # Se já tem um caminho em andamento, continua seguindo
        if self._current_path:
            if self._current_path[0] == "andar": 
                nx, ny = game_ai.NextPositionRelative(1, "frente")
                if not game_ai.map_knowledge.is_free(nx, ny): # Não é seguro andar p frente
                    self._clear_navigation() # Limpa navegação se não for seguro andar p frente (Andar em linha reta ruim)
                    return "virar_esquerda" if random.random() < 0.5 else "virar_direita" # Gira
            return self._follow_current_path()
        
        # Escolhe novo destino aleatoriamente conforme percentuais especificados
        rand = random.randint(1, 100)
        tgt = None
        
        # Ir para blocos seguros completamente aleatórios (2%)
        if rand <= 1:  # 1% → bloco conhecido aleatório
            known_coords = game_ai.map_knowledge.get_known_coordinates(game_ai.player.x, game_ai.player.y, 0)
            tgt = random.choice(known_coords) if known_coords else None
        elif rand <= 2:  # 1% → bloco livre aleatório  
            free_coords = game_ai.map_knowledge.get_free_coordinates(game_ai.player.x, game_ai.player.y, 0)
            tgt = random.choice(free_coords) if free_coords else None


        # Ir para blocos seguros aleatórios porém perto (8%)
        elif rand <= 4:  # 2% → bloco conhecido com ≤10 de distância
            known_coords = game_ai.map_knowledge.get_known_coordinates(game_ai.player.x, game_ai.player.y, 10)
            tgt = random.choice(known_coords) if known_coords else None
        elif rand <= 10:  # 6% → bloco livre entre ≤10 de distância
            free_coords = game_ai.map_knowledge.get_free_coordinates(game_ai.player.x, game_ai.player.y, 10)
            tgt = random.choice(free_coords) if free_coords else None

        # Ir para bloco livre mais próximo (20%)
        elif rand <= 30:  # 20% → bloco livre mais próximo
            tgt = game_ai.map_knowledge.get_free_coordinate_nearest(game_ai.player.x, game_ai.player.y)
        
        # Follow straight line for 3-15 blocks (random) or until blocked (front block not safe), then turn (50/50 right or left) (70%)
        else:
            nx, ny = game_ai.NextPositionRelative(1, "frente")
            if game_ai.map_knowledge.is_free(nx, ny):
                num_steps = random.randint(3, 15)
                # enfileira N vezes "andar"
                self._current_path = ["andar"] * num_steps
            # após avançar, vira à esquerda ou direita
                if random.random() < 0.5:
                    self._current_path.append("virar_esquerda")
                else:
                    self._current_path.append("virar_direita")
                return self._follow_current_path()
            else:
                # Se o bloco à frente não é seguro, gira para explorar
                return "virar_esquerda" if random.random() < 0.5 else "virar_direita"
            
        # Se encontrou um alvo, calcula caminho e inicia navegação
        if tgt:
            return self._navigate_to_target(game_ai, tgt)
        else:
            # Se não há alvo, gira para explorar
            return "virar_esquerda"
    
    def _evade(self, game_ai):
        # Se não tomou dano no ultimo tick, sai desse modo
        if not game_ai.take_hit():
            return ""

        if not self._evade_sequence:
            # Ir para frente/tras
            if self._last_evade_axis == self.AXIS["nenhum"] or self._last_evade_axis == self.AXIS["esquerda/direita"]: 
                self._last_evade_axis = self.AXIS["frente/trás"]

                #Verifica se é possivel ir pra frente/trás
                #Se sim, vai pra frente/trás

                # Pode ir pra frente?
                nx, ny = game_ai.NextPositionRelative(1, "frente")
                if game_ai.map_knowledge.is_free(nx, ny):
                    self._evade_sequence = ["andar"]
                
                # Pode ir pra trás?
                nx, ny = game_ai.NextPositionRelative(1, "atras")
                if game_ai.map_knowledge.is_free(nx, ny):
                    self._evade_sequence = ["andar_re"]
            
            # Ir para esquerda/direita
            if self._last_evade_axis == self.AXIS["frente/trás"]: 
                self._last_evade_axis = self.AXIS["esquerda/direita"]

                #Verifica se é possivel ir pra esquerda/direita
                #Se sim, vai pra esquerda/direita

                # Pode ir pra esquerda?
                nx, ny = game_ai.NextPositionRelative(1, "esquerda")
                if game_ai.map_knowledge.is_free(nx, ny):
                    self._evade_sequence = ["virar_esquerda", "andar"]
                # Pode ir pra direita?
                nx, ny = game_ai.NextPositionRelative(1, "direita")
                if game_ai.map_knowledge.is_free(nx, ny):
                    self._evade_sequence = ["virar_direita", "andar"]  

        # pega próxima ação
        action = self._evade_sequence.pop(0)
        return action  

    def _find_gold(self, game_ai): 

        # Se já tem um caminho em andamento, continua seguindo
        if self._current_path:
            return self._follow_current_path()
        
        # Se há um alvo atual, ele é o target de navegação
        tgt = self._gold_objective_position
        
        # Faz a navegação para o alvo
        return self._navigate_to_target(game_ai, tgt)

    def _find_potion(self, game_ai):
        # Se já tem um caminho em andamento, continua seguindo
        if self._current_path:
            return self._follow_current_path()
        
        # Se há um alvo atual, ele é o target de navegação
        tgt = self._potion_objective_position
        
        # Faz a navegação para o alvo
        return self._navigate_to_target(game_ai, tgt)
    
    # ---------- Sistema de Navegação ----------

    # Limpa o caminho e destino atuais.
    def _clear_navigation(self):
        self._current_path = []
        self._current_target = None
    
    # Inicia a navegação para um novo destino.
    def _navigate_to_target(self, game_ai, target: Tuple[int, int]) -> str:
        self._current_target = target
        
        # Calcula caminho usando PathFinder
        path = self._path_finder.go_to(
            game_ai.player.x, game_ai.player.y, game_ai.dir, 
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

