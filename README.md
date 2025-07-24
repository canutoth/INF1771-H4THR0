# INF1771 – Trabalho 4: Desafio Final IA - BATALHA DE BOTS

## Enunciado
O objetivo deste desafio é programar a inteligência artificial que controlará um drone num labirinto de dimensões 59 × 34, coletando o máximo de tesouros possível e enfrentando drones adversários, com energia inicial de 100 pontos, munição ilimitada (10 de dano por tiro) e sensores de brisa, flash, redLight, blueLight, greenLight, weakLight, passos e mira .

O labirinto deve ser representado por uma matriz 59 × 34, o agente inicia em posição aleatória, e cada ação (mover para frente/trás, virar à esquerda/direita, pegar objeto, atirar, observar) custa –1 ponto .

Os sensores percebem:  
- **Brisa** em células adjacentes a poços;  
- **Flash** adjacente a teletransportadores;  
- **RedLight/BlueLight/GreenLight/WeakLight** para itens na posição atual;  
- **Passos** de inimigos adjacentes;  
- **Enemy** em linha de visão até 10 células;  
- **Impacto** ao colidir com parede .

A comunicação com o servidor de treino é por Socket TCP/IP (porta 8888) usando protocolo texto (“;” como separador); o servidor alterna entre os estados **Ready** (30 s para preparação), **Game** (jogo) e **Gameover** (30s para resultados).

Os comandos disponíveis no DevKit são:  
- `sendForward()` / `w` – andar para frente  
- `sendBackward()` / `s` – andar de ré  
- `sendTurnLeft()` / `a` – virar à esquerda  
- `sendTurnRight()` / `d` – virar à direita  
- `sendGetItem()` / `t` – pegar item  
- `sendShoot()` / `e` – atirar  
- métodos para observações, status do jogo, posição e scoreboard .

---

## Execução do Projeto
- Escolhemos fazer com máquina de estados

Grupo
- Theo Canuto
- Hanna Epelboim
- Robbie Carvalho

## Requisitos

- Windows
- Python 3.11
- Pygame

## Instalação do Python 3.11

Abra o terminal (PowerShell) e execute:

```powershell
winget search Python.Python
winget install Python.Python.3.11
py -3.11 --version
```

## Instalação das dependências

Instale dependências na versão correta do Python:

```powershell
py -3.11 -m pip install pygame
py -3.11 -m pip install keyboard
```

## Como rodar o servidor (visualizador)

No terminal, execute:

```powershell
cd Server_Vizualizer
py -3.11 main.pyc
```

## Como rodar o bot

Abra outro terminal e execute:

```powershell
cd .\Game_Client
py -3.11 Program.py
```

---

Se tiver dúvidas ou problemas, abra uma issue ou entre em contato com o responsável pelo projeto.
