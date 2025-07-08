import random

# Máquina de estados do bot (1 = mais alta prioridade → 7 = mais baixa)
# 1) Evade         – se levar um tiro
# 2) FindPotion    – energia < 30 e conhece poção
# 3) FindGold      – ouro vai spawnar
# 4) FindPotion    – energia < 50 e poção até 16 de Manhattan
# 5) FindPotion    – energia < 100 e poção “monopólio” próxima
# 6) FindGold      – ≥750 turns sem pegar ouro ou ouro possível em memória
# 7) Exploration   – estado base/fallback

# Estado base (prioridade 7)
def Exploration(): 
    # Explora aleatoriamente conforme percentuais:
    # 2%  → bloco conhecido aleatório
    # 3%  → bloco livre aleatório
    # 5%  → bloco conhecido com ≤10 de distância
    # 10% → bloco livre entre 5–15 de distância
    # 15% → bloco livre até 5 de distância
    # resto→ bloco livre mais próximo
    pass

# Gatilho: viu inimigo em Exploration ou LookForOponent
# Estado de combate (faz A* de tiro/avanço/recua conforme distância)
def Attack(): 
    # 1) Mede dist = manhattan(player, inimigo)
    # 2) Escolhe ação:
    #    • 10–8: 1 tiro (–10 energia) + move forward (–1)
    #    •  8–6: 2 tiros + move forward
    #    •  6–3: 3 tiros, mantém posição
    #    •  3–1: 4 tiros + move backward
    # 3) Se inimigo some (fora de visão/alcance) → retorna a Exploration()
    pass

# Gatilho: ouviu “steps” (sons de passos) no Exploration
# Procura inimigo girando até 3 vezes, cooldown de 5s
def LookForOponent():     
    # 1) Ao ouvir “steps”, entra aqui e define t_start
    # 2) Gira para até 3 direções faltantes, buscando inimigo
    # 3) Se vê inimigo → chama Attack()
    # 4) Se steps cessam ou completa 3 giros → retorna a Exploration()
    # 5) Não repete por 5 segundos (cooldown interno)
    pass

# Prioridades 2, 4 e 5: energia baixa e poções em diferentes raios
def FindPotion():
    # PRIORIDADES 2, 4 e 5
    # Gatilhos:
    #  - energia < 30  → qualquer poção conhecida
    #  - energia < 50  → poção ≤16 de Manhattan
    #  - energia < 100 → “poção-base” próxima (monopólio)
    #
    # Fluxo:
    # 1) Seleciona poção válida na memória
    # 2) Rota A* até lá
    # 3) Se chega antes do spawn → espera parado
    # 4) Se levar hit enquanto espera:
    #      a) tenta outra poção plausível
    #      b) se não houver → Evade()
    pass

# Prioridades 3 e 6: oportunidade de ouro (spawn iminente ou memória longa)
def FindGold():
    # PRIORIDADES 3 e 6
    # Gatilhos:
    #  - ouro vai spawnar em breve (calcula cooldown + distância)
    #  - passou muito tempo sem ouro (≥750 turns) ou memória de ouro
    #
    # Fluxo:
    # 1) Escolhe o “melhor” alvo de ouro
    # 2) Executa A* até lá, monopolizando spawn
    pass

# Prioridade 1: levou um hit
def Evade():
    # 1) Ao receber hit, armazena t_hit e limpa memória de evade
    # 2) Tenta mover 1 bloco:
    #    a) primeiro no eixo preferido, só pra frente em relaçao a pos atual (ex.: horizontal)
    #       – se célula livre, move e retorna
    #    b) senão, tenta no outro eixo (vertical)
    # 3) Se levar novo hit em ≤2 s:
    #    – inverte ordem de eixos (tenta vertical antes de horizontal)
    # 4) Se as duas tentativas não resolverem, tenta dar um go to para algum lugar com ao menos 3 de distancia manhattam:
    #    – calcula A* até a célula 
    #    – reseta lógica de memória de evade
    pass

# APENAS PARA CONSULTA (não faz parte da versão final)
def Random(): 
    n = random.randint(0,7)
    if   n == 0: decision = "virar_direita"
    elif n == 1: decision = "virar_esquerda"
    elif n == 2: decision = "andar"
    elif n == 3: decision = "atacar"
    elif n == 4: decision = "pegar_ouro"
    elif n == 5: decision = "pegar_anel"
    elif n == 6: decision = "pegar_powerup"
    elif n == 7: decision = "andar_re"
    else:        decision = ""
    print(decision)
    return decision
