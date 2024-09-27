from __future__ import annotations
from dataclasses import dataclass

from pygame import Surface

from classes.characters.enemy.input_box.box_font import (
    BoxFont, FontArgsProvider
)
from constants import WHITE


class Tango(BoxFont):
    """
    日本語表記スプライト

    Attributes
    ----------
    _pos_h_ratio : float
        配置高さ比率

    image : Surface
        イメージ
    rect : Rect
        レクト
    _updated_image : Surface
        更新後イメージ
    """

    _pos_h_ratio = 0.35

    def __init__(self, args: TangoArgs):
        """
        コンストラクタ

        Parameters
        ----------
        args : TangoArgs
            専用引数
        """
        self.image = args.initial_image
        self.rect = self.image.get_rect()
        
        self._updated_image = args.image

    def update_by_key(self) -> None:
        """
        入力による更新
        """
        self.image = self._updated_image
        self.rect = self.image.get_rect()


class TangoArgsProvider(FontArgsProvider):
    """
    日本語表記スプライト専用引数提供機

    Attributes
    ----------
    _size_ratio : float
        サイズ比率

    _initial_font : Font
        初期フォント
    _font : Font
        入力中フォント
    _hira_tango_tango_dic : dict[str, str]
        キーがひらがな、バリューが漢字やカタカナなどの日本語表記である辞書
    """

    _size_ratio = 0.025

    def __init__(
            self,
            exist_rect_h: int,
            magnification_power: float | int,
            hira_tango_tango_dic: dict[str, str]
    ):
        """
        コンストラクタ

        Parameters
        ----------
        exist_rect_h : int
            描画領域レクトの高さ
        magnification_power : float | int
            拡大率
        hira_tango_tango_dic : dict[str, str]
            キーがひらがな、バリューが漢字やカタカナなどの日本語表記である辞書
        """
        super().__init__(exist_rect_h, magnification_power)

        self._hira_tango_tango_dic = hira_tango_tango_dic

    def provide(self, hira_tango: str) -> TangoArgs:
        """
        専用引数の提供

        Parameters
        ----------
        hira_tango : str
            ひらがなの単語

        Returns
        -------
        TangoArgs
            日本語表記スプライト専用引数
        """
        tango = self._hira_tango_tango_dic[hira_tango]

        initial_image = self._initial_font.render(tango, True, WHITE)
        image = self._font.render(tango, True, WHITE)

        args = TangoArgs(initial_image, image)

        return args


@dataclass(frozen=True)
class TangoArgs:
    """
    日本語表記スプライト専用引数

    initial_image : Surface
        初期イメージ
    image : Surface
        入力中イメージ
    """
    
    initial_image: Surface
    image: Surface