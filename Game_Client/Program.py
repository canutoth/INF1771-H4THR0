# INICIAR PROGRAMA
from Bot import Bot
from Debug.debug_interface import start_debug_interface

if __name__ == "__main__":
    # Criar instância do bot
    bot = Bot()
    
    # Iniciar interface de debug em thread separada
    debug_thread = start_debug_interface(bot.debug_manager, bot.gameAi.debug_manager)
    
    print("# Sistema de debug iniciado - Interface gráfica disponível")
    print("# Bot executando...")

