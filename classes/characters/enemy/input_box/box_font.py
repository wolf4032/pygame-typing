from abc import ABC

import pygame
from pygame import Surface, Rect
from pygame.font import Font

from utils.utils import ArgsProvider
from constants import FONT_PATH


class BoxFont(pygame.sprite.Sprite, ABC):
    """
    ボックス内文字列スプライト

    Attributes
    ----------
    _pos_h_ratio : float
        配置高さ比率

    image : Surface
        イメージ
    rect : Rect
        レクト
    """

    _pos_h_ratio: float = None

    def __init__(self):
        """
        コンストラクタ
        """
        self._check_pos_height_ratio()

        self.image: Surface = None
        self.rect: Rect = None

    @classmethod
    def _check_pos_height_ratio(cls) -> None:
        """
        配置高さ比率の確認

        Raises
        ------
        TypeError
            floatでなかった場合
        """
        if not isinstance(cls._pos_h_ratio, float):
            raise TypeError(
                f'{cls.__name__}._pos_h_ratioをfloatで再定義してください'
            )

    def update_rect_center(self, box_rect: Rect) -> None:
        """
        レクトの中心の更新

        Parameters
        ----------
        box_rect : Rect
            ボックスのレクト
        """
        x = box_rect.w // 2
        y = box_rect.h * self._pos_h_ratio

        self.rect.center = (x, y)


class FontArgsProvider(ArgsProvider, ABC):
    """
    文字列スプライト専用引数提供機

    Attributes
    ----------
    _size_ratio : float
        サイズ比率

    _initial_font : Font
        初期フォント
    _font : Font
        入力中フォント
    """
    
    _size_ratio: float = None

    def __init__(
            self,
            screen_h: int,
            magnification_power: float | int
    ):
        """
        コンストラクタ

        Parameters
        ----------
        screen_h : int
            画面高さ
        magnification_power : float | int
            拡大率
        """
        self._check_size_ratio()
        basic_font_size = int(screen_h * self._size_ratio)

        self._initial_font = Font(FONT_PATH, basic_font_size)
        self._font = FontArgsProvider._build_font(
            basic_font_size, magnification_power
        )

    @classmethod
    def _check_size_ratio(cls) -> None:
        """
        サイズ比率の確認

        Raises
        ------
        TypeError
            floatでなかった場合
        """
        if not isinstance(cls._size_ratio, float):
            raise TypeError(
                f'{cls.__name__}._size_ratioをfloatで再定義してください'
            )

    @staticmethod
    def _build_font(
        basic_font_size: int, magnification_power: float | int
    ) -> Font:
        """
        フォントの作成

        Parameters
        ----------
        basic_font_size : int
            基準フォントサイズ
        magnification_power : float | int
            拡大率

        Returns
        -------
        Font
            入力中フォント
        """
        font_size = int(basic_font_size * magnification_power)

        font = Font(FONT_PATH, font_size)

        return font