import pygame
from pygame.font import Font

from constants import WHITE


class Assumed(pygame.sprite.Sprite):
    """
    入力予測文字列スプライト

    Attributes
    ----------
    _font : Font
        フォント
    image : Surface
        イメージ
    rect : Rect
        レクト
    """
    
    def __init__(self, initial_font: Font, font: Font, keys: str):
        """
        コンストラクタ

        Parameters
        ----------
        initial_font : Font
            初期フォント
        font : Font
            入力中のフォント
        keys : str
            初期入力予測文字列
        """
        self._font = font
        self.image = initial_font.render(keys, True, WHITE)
        self.rect = self.image.get_rect()

    def update_by_key(self, keys: str, confirmed_rect_w: int) -> None:
        """
        入力による更新

        Parameters
        ----------
        keys : str
            新しい入力予測文字列
        confirmed_rect_w : int
            入力済み文字列のレクトの幅
        """
        self.image = self._font.render(keys, True, WHITE)
        self.rect = self.image.get_rect(topleft=(confirmed_rect_w, 0))