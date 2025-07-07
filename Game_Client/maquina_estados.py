import random
def SurvivalDecision(): #pouca energia
    pass

def ExplorationDecision(): #normal
    pass

def AttackDecision(): #soh qnd tiverem mais 2 outros bots
    pass

def CollectDecision(): #a* p voltar p ouro mais prox ou coleta mais vantajosa
    pass

def RunawayDecision(): #atiraram em mim
    pass

def ItsAboutTimeDecision(): #ultimos X seg... sipa ficar parado seja bom
    pass

def aleatorio():
    n = random.randint(0,7)
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
    print(decision)
    return decision
