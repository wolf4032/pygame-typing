import pygame
from pygame.font import Font

from constants import GRAY


class Confirmed(pygame.sprite.Sprite):
    """
    入力済み文字列スプライト

    Attributes
    ----------
    _font : Font
        入力中フォント
    """
    
    def __init__(self, font: Font):
        """
        コンストラクタ

        Parameters
        ----------
        font : Font
            入力中フォント
        """
        self._font = font

    def update_by_key(self, keys: str) -> None:
        """
        入力による更新

        Parameters
        ----------
        keys : str
            新しい入力済み文字列
        """
        self.image = self._font.render(keys, True, GRAY)
        self.rect = self.image.get_rect()