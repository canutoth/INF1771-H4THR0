# INTERFACE DE DEBUG - Sistema de visualização e controle para depuração

import pygame, threading
from textwrap import wrap
from Debug.debug_bot  import BotDebugManager
from Debug.debug_game_ai import GameAIDebugManager


class DebugInterface:
    
    def __init__(self):
        pygame.init()
        self.w, self.h = 400, 560
        self.screen = None
        
        # Paleta de cores padronizada
        self.col = {
            "bg": (30, 30, 30),      # Fundo principal
            "on": (0, 150, 0),       # Botão ativo
            "off": (150, 0, 0),      # Botão inativo
            "txt": (255, 255, 255),  # Texto
            "panel": (50, 50, 50),   # Painel de fundo
        }
        
        # Fontes padronizadas para toda a interface
        self.font_medium = pygame.font.Font(None, 21) 

        # Gerenciadores de debug (definidos externamente)
        self.bot: BotDebugManager | None = None
        self.ai:  GameAIDebugManager | None = None

        # Estado atual do jogo (atualizado pela IA)
        self.last_status: tuple | None = None   # (x, y, direção, estado, pontos, energia)
        self.last_obs:    str = ""              # Observações da IA

        # Configuração dos botões principais (x, y, largura, altura, texto, ação)
        self.btns = [
            (50,  50, 300, 40, "Debug Bot",        "bot_dbg"),
            (50, 100, 300, 40, "Filtro Repetições","bot_filter"),
            (50, 150, 300, 40, "Debug IA",         "ai_dbg"),
            (50, 200, 300, 40, "Controle Manual",  "ai_manual"),
            (50, 250, 300, 40, "Raw Mode",         "bot_raw"),    
        ]
        
        # Configuração dos botões de controle manual
        self.mbtns = [
            (170,340,60,28,"FRENTE","up"), (110,371,60,28,"V_ESQ","left"),
            (230,371,60,28,"V_DIR","right"), (170,402,60,28,"TRÁS","down"),
            (320,340,60,28,"ATK","attack"), (320,371,60,28,"OURO","gold"),
            (320,402,60,28,"ANEL","ring"),  (320,433,60,28,"PWR","powerup"),
        ]
        self.running = True

    # =========================================================================
    # MÉTODOS DE CONFIGURAÇÃO E VINCULAÇÃO EXTERNA
    # =========================================================================
    
    def set_debug_managers(self, bot_dbg, ai_dbg):
        self.bot, self.ai = bot_dbg, ai_dbg
        if ai_dbg:
            ai_dbg.bind_ui(self)

    # =========================================================================
    # MÉTODOS DE ATUALIZAÇÃO DE DADOS (CHAMADOS PELA IA)
    # =========================================================================
    
    def update_status(self, x, y, direction, state, score, energy):
        self.last_status = (x, y, direction, state, score, energy)

    def update_observation(self, obs_list):
        self.last_obs = ', '.join(obs_list)

    # =========================================================================
    # MÉTODOS AUXILIARES DE RENDERIZAÇÃO
    # =========================================================================
    def _text(self, txt):
        font = self.font_medium
        return font.render(txt, True, self.col["txt"])

    def _draw_btn(self, x, y, w, h, label, active):
        pygame.draw.rect(self.screen, self.col["on" if active else "off"], (x, y, w, h))
        pygame.draw.rect(self.screen, self.col["txt"], (x, y, w, h), 2)
        text_surf = self._text(label)
        text_x = x + w//2 - text_surf.get_width()//2
        text_y = y + h//2 - text_surf.get_height()//2
        self.screen.blit(text_surf, (text_x, text_y))

    def _draw_mbtn(self, x, y, w, h, label):
        pygame.draw.rect(self.screen, self.col["panel"], (x, y, w, h))
        pygame.draw.rect(self.screen, self.col["txt"], (x, y, w, h), 1)
        text_surf = self._text(label)
        text_x = x + w//2 - text_surf.get_width()//2
        text_y = y + h//2 - text_surf.get_height()//2
        self.screen.blit(text_surf, (text_x, text_y))

    # =========================================================================
    # GERENCIAMENTO DE ESTADOS DOS BOTÕES
    # =========================================================================
    
    def _states(self):
        if not self.bot or not self.ai:
            return [False] * 4
        return [
            self.bot.debug_enabled,
            self.bot.filter_enabled,
            self.ai.debug_enabled,
            self.ai.manual_mode,
            self.bot.raw_enabled, 
        ]

    # =========================================================================
    # PAINEL DE STATUS E OBSERVAÇÕES (RODAPÉ)
    # =========================================================================
    def _draw_footer(self):
        footer_y = 470
        pygame.draw.rect(self.screen, self.col["panel"],
                         (0, footer_y, self.w, self.h - footer_y))

        # =====================================================================
        # SEÇÃO DE STATUS DO JOGADOR
        # =====================================================================
        if self.last_status:
            x, y, d, st, scr, en = self.last_status
            status_lines = [
                f"POSIÇÃO: ({x},{y})   DIREÇÃO: {d}",
                f"ESTADO: {st}   PONTOS: {scr}   ENERGIA: {en}",
            ]
            for i, line in enumerate(status_lines):
                surf = self.font_medium.render(line, True, self.col["txt"])
                self.screen.blit(surf,
                    (self.w // 2 - surf.get_width() // 2,
                     footer_y + 8 + i * 24))

        # =====================================================================
        # SEÇÃO DE OBSERVAÇÕES DA IA
        # =====================================================================
        # Centraliza o bloco "OBS:" + texto das observações
        obs_text = self.last_obs or "nenhum"
        obs_lines = wrap(obs_text, 48)[:3]  # Máximo 3 linhas

        # Renderiza título e linhas para calcular largura total
        title_surf = self.font_medium.render("OBS:", True, self.col["txt"])
        text_surfs = [self.font_medium.render(line, True, self.col["txt"]) for line in obs_lines]
        max_text_width = max([surf.get_width() for surf in text_surfs] + [0])
        total_width = title_surf.get_width() + 12 + max_text_width  # 12px de espaçamento

        # Calcula posicionamento centralizado
        center_x = self.w // 2
        title_y = footer_y + 60
        
        obs_x = center_x - total_width // 2
        text_x = obs_x + title_surf.get_width() + 12

        # Desenha título "OBS:" e texto das observações
        self.screen.blit(title_surf, (obs_x, title_y))
        for i, surf in enumerate(text_surfs):
            self.screen.blit(surf, (text_x, title_y + i * 18))

    # =========================================================================
    # LÓGICA DE INTERAÇÃO E CONTROLE
    # =========================================================================
    
    def _toggle(self, act):
        if not self.bot or not self.ai:
            return
        if   act == "bot_dbg":    self.bot.toggle_debug()
        elif act == "bot_filter": self.bot.toggle_filter()
        elif act == "ai_dbg":     self.ai.toggle_debug()
        elif act == "ai_manual":  self.ai.toggle_manual()
        elif act == "bot_raw":    self.bot.toggle_raw()

    def _click(self, pos):
        x, y = pos
        # Verifica clique nos botões principais
        for bx, by, bw, bh, _, act in self.btns:
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self._toggle(act)
                return
        # Verifica clique nos botões de controle manual (se ativo)
        if self.ai and self.ai.manual_mode:
            for bx, by, bw, bh, _, cmd in self.mbtns:
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.ai.add_manual_command(cmd)
                    return

    # =========================================================================
    # RENDERIZAÇÃO PRINCIPAL DA INTERFACE
    # =========================================================================
    
    def _draw(self):
        self.screen.fill(self.col["bg"])
        
        # Título principal da interface
        title_surf = self._text("Sistema de Debug")
        title_x = self.w//2 - title_surf.get_width()//2
        self.screen.blit(title_surf, (title_x, 15))

        # Desenha botões principais com seus estados
        for i, (x, y, w, h, lbl, _) in enumerate(self.btns):
            self._draw_btn(x, y, w, h, lbl, self._states()[i])

        # Desenha controles manuais se estiverem ativos
        if self.ai and self.ai.manual_mode:
            control_surf = self._text("Interface - Controle")
            control_x = self.w//2 - control_surf.get_width()//2
            self.screen.blit(control_surf, (control_x, 310))
            for x, y, w, h, lbl, _ in self.mbtns:
                self._draw_mbtn(x, y, w, h, lbl)

        # Desenha painel de status e observações
        self._draw_footer()
        pygame.display.flip()

    # =========================================================================
    # LOOP PRINCIPAL DA THREAD DE INTERFACE
    # =========================================================================
    def _loop(self):
        if self.screen is None:
            self.screen = pygame.display.set_mode((self.w, self.h))
            pygame.display.set_caption("Debug Control")

        clk = pygame.time.Clock()
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self._click(e.pos)
            self._draw()
            clk.tick(60)
        pygame.quit()

    # =========================================================================
    # INTERFACE PÚBLICA
    # =========================================================================
    
    def start(self):
        threading.Thread(target=self._loop, daemon=True).start()


# =============================================================================
# FUNÇÕES GLOBAIS DE CONVENIÊNCIA
# =============================================================================
# Implementação singleton para acesso global à interface de debug

_dbg_ui = None

def get_debug_interface():
    global _dbg_ui
    if _dbg_ui is None:
        _dbg_ui = DebugInterface()
    return _dbg_ui

def start_debug_interface(bot_dbg, ai_dbg):
    ui = get_debug_interface()
    ui.set_debug_managers(bot_dbg, ai_dbg)
    ui.start()
