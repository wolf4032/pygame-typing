import pygame
from pygame.event import Event
from pygame import Rect

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

    def __init__(self, fps: int):
        """
        コンストラクタ

        Parameters
        ----------
        fps : int
            FPS
        """
        super().__init__()

        pygame.mouse.set_visible(False)

        screen_size = Utils.build_screen_size()
        screen = pygame.display.set_mode(screen_size)
        self._screen_rect = screen.get_rect()

        self._start = Start(screen)
        self._battle = Battle(screen, screen_size, fps)

        self._running = True
        self._view = self._start

    @property
    def running(self) -> bool:
        return self._running

    def run(self) -> list[Rect] | None:
        """
        実行

        Returns
        -------
        list[Rect] | None
            画面の更新が必要な場合はダーティーレクト
            画面の更新が必要ない場合はNone
        """
        events = pygame.event.get()

        self._check_termination_request(events)

        if not self._running:
            return None

        dirty_rects, should_change_view = self._view.run(events)

        if should_change_view:
            self._change_view()

            dirty_rects = [self._screen_rect]

        return dirty_rects

    def _check_termination_request(self, events: list[Event]) -> None:
        """
        終了要請の確認

        Parameters
        ----------
        events : list[Event]
            イベントリスト
        """
        for event in events:
            if event.type == pygame.QUIT:
                self._running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._running = False

    def _change_view(self) -> None:
        """
        ビューの変更
        """
        if self._view == self._start:
            self._view = self._battle

        self._view.setup()