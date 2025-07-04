# t4-desafio-final-h4thr0-bot

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
