import pygame
from pygame import Rect, Surface

from constants import B_BLACK, WHITE, FONT_PATH
from classes.ui.bar import BarChildrenArgs


class InfoBar(pygame.sprite.Sprite):
    """
    情報バースプライト

    Attributes
    ----------
    _children_w_margin_ratio: float
        子要素間の余白比率
    _children_h_ratio: float
        子要素の高さ比率

    image: Surface
        イメージ
    rect: Rect
        レクト
    _info: Info
        情報スプライト
    """

    _children_w_margin_ratio: float = 0.025
    _children_h_ratio: float = 0.8

    def __init__(self, screen_rect: Rect, h_ratio: int):
        """
        コンストラクタ

        Parameters
        ----------
        screen_rect : Rect
            画面レクト
        h_ratio : int
            高さ比率
        """
        self._setup_image(screen_rect, h_ratio)
        self.rect = self.image.get_rect(bottomleft=screen_rect.bottomleft)

        self._setup_info()
        self.image.blit(self._info.image, self._info.rect)

    def _setup_image(self, screen_rect: Rect, h_ratio: int) -> None:
        """
        イメージの初期化

        Parameters
        ----------
        screen_rect : Rect
            画面レクト
        h_ratio : int
            高さ比率
        """
        size = (screen_rect.w, int(screen_rect.h * h_ratio))
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill(B_BLACK)

    def _setup_info(self) -> None:
        """
        情報スプライトの初期化
        """
        children_args = BarChildrenArgs(
            self.rect, self._children_w_margin_ratio, self._children_h_ratio
        )
        self._info = Info(children_args)

    def setup(self, screen: Surface) -> None:
        """
        初期化

        Parameters
        ----------
        screen : Surface
            画面サーフェス
        """
        screen.blit(self.image, self.rect)


class Info(pygame.sprite.Sprite):
    """
    情報スプライト

    Attributes
    ----------
    _message : str
        情報

    image : Surface
        イメージ
    rect : Rect
        レクト
    """
    
    _message: str = '[Esc]: 終了'

    def __init__(self, args: BarChildrenArgs):
        """
        コンストラクタ

        Parameters
        ----------
        args : BarChildrenArgs
            専用引数
        """
        font = pygame.font.Font(FONT_PATH, args.h)

        self.image = font.render(self._message, True, WHITE)
        self._setup_rect(args.w_margin, args.mid_h)

    def _setup_rect(self, w_margin: int, mid_h: int) -> None:
        """
        レクトの初期化

        Parameters
        ----------
        w_margin : int
            幅方向の余白
        mid_h : int
            中心の配置高さ
        """
        self.rect = self.image.get_rect()

        self.rect.midleft = (w_margin, mid_h)