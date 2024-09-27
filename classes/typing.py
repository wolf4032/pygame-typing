import pygame

from utils.utils import Game, Utils
from constants import BLACK
from classes.screens.start import Start
from classes.screens.battle import Battle

class Typing(Game):
    """
    ゲームコントローラー

    Attributes
    ----------
    _caption : str
        タイトル
    _bg_color : tuple[int, int, int]
        背景色
    _status_bar_h_ratio : float
        ステータスバーの高さ比率
    _info_bar_h_ratio : float
        情報バーの高さ比率

    _start : Start
        スタートコントローラー
    _battle : Battle
        戦闘コントローラー
    """
    
    _caption: str = 'typing game'
    _bg_color: tuple[int, int, int] = BLACK
    _status_bar_h_ratio: float = 0.1
    _info_bar_h_ratio: float = 0.05

    def __init__(self):
        """
        コンストラクタ
        """
        super().__init__()

        pygame.mouse.set_visible(False)
        screen_size = Utils.build_screen_size()
        screen = pygame.display.set_mode(screen_size)

        self._start = Start(screen)
        self._battle = Battle(screen, screen_size)

    def run(self) -> None:
        """
        実行
        """
        self._start.run()

        while True:
            self._battle.run()