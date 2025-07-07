import random
def SurvivalDecision(): #pouca energia
    #se jah achei uma pocao 
        #a* para pocao
        #fico parado esperando ela respawnar
        #se fui atingido enquanto espero
            #se tiver outra pocao e pocao num range plausivel
                #a* para outra pocao
            #dou uma voltinha rs
    #se nao volto para exploration mode neh, fazer oq
    pass

def ExplorationDecision(): #normal
    #perg do tempo de respawn
    pass

def AttackDecision(): #soh qnd tiverem mais 2 outros bots
    #se tiver na minha frente (linha reta)
        #atiro 
        #se oponente se afastar
            #ando frente
    #se tiver a um de manhattan
        #chuto uma direcao (safe) para ir e tento me alinhar com ele
    pass

def CollectDecision(): #a* p voltar p ouro mais prox ou coleta mais vantajosa
    #rodo a* para o ouro que der mais recompensa
    pass

def RunawayDecision(): #atiraram em mim
    #se nao tiver ninguem na frente
        #ando frente
    #se tiver alguem na frente
        #ando ré
    pass

def ItsAboutTimeDecision(): #ultimos X seg... sipa ficar parado seja bom
    #rodo a* para ouro mais proximo
    #se distancia razoavel
        #vou ate ouro mais proximo
    #fico parado para nao gastar energia
    decision = "virar_direita" #placeholder
    print(decision)
    return decision

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
