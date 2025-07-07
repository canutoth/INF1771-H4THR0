from typing import Dict, List, Optional
from dto.ScoreBoard import ScoreBoard

# CLASSE DO SCOREBOARD KNOWLEDGE
# RESPONSÁVEL POR GERENCIAR O CONHECIMENTO DOS SCOREBOARDS DOS JOGADORES
class ScoreboardKnowledge:
    
    def __init__(self):  
        self.players: Dict[int, ScoreBoard] = {}  # Dicionário id -> ScoreBoard
        self.vida_inicial = 100  # Vida inicial de cada jogador
        self.vida_critica = 20   # Threshold para considerar vida crítica

    def update_scoreboard(self, scoreboard_list: List[ScoreBoard]):
        self.players.clear()  # limpa para reescrever

        for sb in scoreboard_list:
            player_id = getattr(sb, "id", None)
            if player_id is not None:
                self.players[player_id] = sb
            else:
                # fallback: usa hash do nome+score para evitar colisão direta
                self.players[hash(sb.name + str(sb.score))] = sb

    # Retorna o número total de jogadores conhecidos.
    def get_total_players(self) -> int:
        return len(self.players)
    
    # Retorna o número de jogadores vivos (energia > 0).
    def get_alive_players(self) -> int:
        return sum(1 for player in self.players.values() if player.energy > 0)
    
    # Retorna o número de jogadores mortos (energia <= 0).
    def get_dead_players(self) -> int:
        return sum(1 for player in self.players.values() if player.energy <= 0)
    
    # Calcula a porcentagem de vida total restante. 
    def get_total_health_percentage(self, include_dead: bool = False) -> float:
        if include_dead:
            players_to_consider = list(self.players.values())
        else:
            players_to_consider = [p for p in self.players.values() if p.connected]
        
        if not players_to_consider:
            return 0.0
        
        total_possible_health = len(players_to_consider) * self.vida_inicial

        current_total_health = sum(player.energy for player in players_to_consider)
        
        return current_total_health / total_possible_health if total_possible_health > 0 else 0.0
    
    # Retorna o número de jogadores em estado crítico (vida <= 20).
    def get_critical_health_players(self) -> int:
        return sum(1 for player in self.players.values() 
                  if player.connected and player.energy <= self.vida_critica)
    
    # Retorna jogadores categorizados por status de vida.
    def get_players_by_health_status(self) -> Dict[str, List[str]]:
        result = {
            'healthy': [],
            'critical': [],
            'dead': []
        }
        for player in self.players.values():
            if player.energy <= 0:
                result['dead'].append(player.name)
            elif player.energy <= self.vida_critica:
                result['critical'].append(player.name)
            else:
                result['healthy'].append(player.name)
        return result
    
    # Retorna informações de um jogador específico pelo id.
    def get_player_info(self, player_id: int) -> Optional[ScoreBoard]:
        return self.players.get(player_id)
    
    

    
