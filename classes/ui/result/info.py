import pygame
from pygame import Rect
from pygame.font import Font

from constants import WHITE, FONT_PATH

class Info(pygame.sprite.Sprite):
    """
    情報文字列スプライト

    Attributes
    ----------
    _font_size_ratio : float
        フォントサイズ比率
    _pos_h_ratio : float
        配置高さ比率

    image : Surface
        イメージ
    rect : Rect
        レクト
    """
    
    _font_size_ratio: float = 0.05
    _pos_h_ratio: float = 0.85

    def __init__(self, result_rect: Rect):
        """
        コンストラクタ

        Parameters
        ----------
        result_rect : Rect
            結果レクト
        """
        font = self._build_font(result_rect)
        self.image = font.render('[R]: 再スタート', True, WHITE)
        self._setup_rect(result_rect)

    def _build_font(self, result_rect: Rect) -> Font:
        """
        フォントの作成

        Parameters
        ----------
        result_rect : Rect
            結果レクト

        Returns
        -------
        Font
            フォント
        """
        size = int(result_rect.h * self._font_size_ratio)
        font = pygame.font.Font(FONT_PATH, size)

        return font
        
    def _setup_rect(self, result_rect: Rect) -> None:
        """
        レクトの初期化

        Parameters
        ----------
        result_rect : Rect
            結果レクト
        """
        mid_w = result_rect.w // 2
        mid_h = int(result_rect.h * self._pos_h_ratio)
        center = (mid_w, mid_h)

        self.rect = self.image.get_rect(center=center)