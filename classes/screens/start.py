import pygame
from pygame import Surface, Rect
from pygame.event import Event

from constants import FONT_PATH, WHITE


class Start:
    """
    スタートコントローラー
    """

    def __init__(self, screen: Surface):
        """
        コンストラクタ

        Parameters
        ----------
        screen : Surface
            画面サーフェス
        """
        Start._setup(screen)
        self.rect = screen.get_rect()

    @staticmethod
    def _setup(screen: Surface) -> None:
        """
        初期化

        Parameters
        ----------
        screen : Surface
            画面サーフェス
        """
        font_sticker = FontSticker(screen)

        title = 'タイピングゲーム'
        font_sticker.stick(title, 0.1, 0.4, screen)

        info = '[Space]: 開始'
        font_sticker.stick(info, 0.04, 0.8, screen)

    def run(self, events: list[Event]) -> tuple[list[Rect] | None, bool]:
        """
        実行

        Parameters
        ----------
        events : list[Event]
            イベントリスト

        Returns
        -------
        tuple[list[Rect] | None, bool]
            ダーティーレクトと、ビュー変更するかどうかのbool
            画面の更新が不要の場合は、ダーティーレクトがNoneとして返される
        """
        dirty_rects = None
        should_change_view = self._check_events(events)

        if self.rect:
            dirty_rects = [self.rect]
            self.rect = None

        return dirty_rects, should_change_view
        
    def _check_events(self, events: list[Event]) -> bool:
        """
        イベントリストの確認
        
        ビューの変更が必要かどうかをboolで返すだけ

        Parameters
        ----------
        events : list[Event]
            イベントリスト

        Returns
        -------
        bool
            ビューを変更するかどうかのbool
        """
        should_change_view = False
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    should_change_view = True

                    return should_change_view
                    

class FontSticker:
    """
    文字列配置機

    Attributes
    ----------
    _screen_h : int
        画面高さ
    _mid_w : int
        画面の幅の中心
    """
    
    def __init__(self, screen: Surface):
        """
        コンストラクタ

        Parameters
        ----------
        screen : Surface
            画面サーフェス
        """
        screen_rect = screen.get_rect()

        self._screen_h = screen_rect.h
        self._mid_w = screen_rect.w // 2

    def stick(
            self, text: str, size_ratio: float, h_ratio: float, screen: Surface
    ) -> None:
        """
        文字列の配置

        Parameters
        ----------
        text : str
            文字列
        size_ratio : float
            サイズ比率
        h_ratio : float
            配置高さ比率
        screen : Surface
            配置先サーフェス
        """
        image = self._setup_image(text, size_ratio)
        rect = self._setup_rect(image, h_ratio)

        screen.blit(image, rect)

    def _setup_image(self, text: str, size_ratio: float) -> Surface:
        """
        イメージの初期化

        Parameters
        ----------
        text : str
            配置文字列
        size_ratio : float
            サイズ比率

        Returns
        -------
        Surface
            文字列イメージ
        """
        size = int(self._screen_h * size_ratio)
        font = pygame.font.Font(FONT_PATH, size)
        image = font.render(text, True, WHITE)

        return image

    def _setup_rect(self, image: Surface, h_ratio: float) -> Rect:
        """
        レクトの初期化

        Parameters
        ----------
        image : Surface
            文字列イメージ
        h_ratio : float
            配置高さ比率

        Returns
        -------
        Rect
            文字列レクト
        """
        rect = image.get_rect()
        rect.centerx = self._mid_w
        rect.centery = int(self._screen_h * h_ratio)

        return rect