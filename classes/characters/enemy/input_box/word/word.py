from __future__ import annotations
from dataclasses import dataclass

import pygame
from pygame.font import Font

from classes.characters.enemy.input_box.box_font import (
    BoxFont, FontArgsProvider
)
from classes.characters.enemy.input_box.word.confirmed import Confirmed
from classes.characters.enemy.input_box.word.assumed import Assumed
from constants import WHITE


class Word(BoxFont):
    """
    ローマ字スプライト

    Attributes
    ----------
    _pos_h_ratio : float
        配置高さ比率

    _confirmed : Confirmed
        入力済み文字列スプライト
    _assumed : Assumed
        入力予測文字列スプライト
    image : Surface
        イメージ
    rect : Rect
        レクト
    _h : int
        入力中のイメージの高さ
    """

    _pos_h_ratio = 0.7

    def __init__(self, args: WordArgs, assumed_keys: str):
        """
        コンストラクタ

        Parameters
        ----------
        args : WordArgs
            専用引数
        assumed_keys : str
            入力予測文字列
        """
        self._confirmed = Confirmed(args.font)
        self._assumed = Assumed(args.initial_font, args.font, assumed_keys)

        self._setup_image(args.initial_h)
        self.rect = self.image.get_rect()

        self._h = args.h

    def _setup_image(self, initial_h: int) -> None:
        """
        イメージの初期化

        Parameters
        ----------
        initial_h : int
            初期のイメージの高さ
        """
        w = self._assumed.rect.w
        self.image = pygame.Surface((w, initial_h))

        self.image.blit(self._assumed.image, self._assumed.rect)

    def update_by_key(self, confirmed_keys: str, assumed_keys: str) -> None:
        """
        入力による更新

        Parameters
        ----------
        confirmed_keys : str
            入力済み文字列
        assumed_keys : str
            入力予測文字列
        """
        self._confirmed.update_by_key(confirmed_keys)
        self._assumed.update_by_key(assumed_keys, self._confirmed.rect.w)

        self._update_image()
        self.rect = self.image.get_rect()

    def _update_image(self) -> None:
        """
        イメージの更新
        """
        confirmed_w = self._confirmed.rect.w
        assumed_w = self._assumed.rect.w
        w = confirmed_w + assumed_w

        self.image = pygame.Surface((w, self._h))
        
        self.image.blit(self._confirmed.image, self._confirmed.rect)
        self.image.blit(self._assumed.image, self._assumed.rect)


class WordArgsProvider(FontArgsProvider):
    """
    Word専用引数提供機

    Attributes
    ----------
    _size_ratio : float
        サイズ比率
    _highest_key: str
        最も高い文字列
        これの高さがイメージの高さになる

    _initial_font : Font
        初期フォント
    _font : Font
        入力中フォント
    _initial_h : int
        初期高さ
    _h : int
        入力中高さ
    """

    _size_ratio = 0.02
    _highest_key = 'j'

    def __init__(
            self,
            exist_rect_h: int,
            magnification_power: float | int
    ):
        """
        コンストラクタ

        Parameters
        ----------
        exist_rect_h : int
            描画領域の高さ
        magnification_power : float | int
            拡大率
        """
        super().__init__(exist_rect_h, magnification_power)

        self._setup_heights()

    def _setup_heights(self) -> None:
        """
        高さの初期化
        """
        highest_initial_image = self._initial_font.render(
            self._highest_key, True, WHITE
        )
        highest_image = self._font.render(self._highest_key, True, WHITE)

        self._initial_h = highest_initial_image.get_height()
        self._h = highest_image.get_height()

    def provide(self) -> WordArgs:
        """
        専用引数の提供

        Returns
        -------
        WordArgs
            専用引数
        """
        args = WordArgs(
            self._initial_font, self._font, self._initial_h, self._h
        )

        return args
    

@dataclass(frozen=True)
class WordArgs:
    """
    Word専用引数

    Attributes
    ----------
    initial_font : Font
        初期フォント
    font : Font
        入力中フォント
    initial_h : int
        初期高さ
    h : int
        入力中高さ
    """
    
    initial_font: Font
    font: Font
    initial_h: int
    h: int