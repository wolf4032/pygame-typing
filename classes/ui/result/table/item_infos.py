from abc import ABC, abstractmethod
from typing import Any

import pygame
from pygame.font import Font
from pygame.sprite import Group

from constants import WHITE


class Legend(pygame.sprite.Sprite):
    """
    凡例スプライト

    Attributes
    ----------
    image : Surface
        イメージ
    rect : Rect
        レクト
    """

    def __init__(
            self,
            font: Font,
            legend: str,
            *,
            topleft: tuple[int, int] = None,
            midleft: tuple[int, int] = None
    ):
        """
        コンストラクタ

        Parameters
        ----------
        font : Font
            フォント
        legend : str
            凡例
        topleft : tuple[int, int], optional
            左上の配置基準位置, by default None
        midleft : tuple[int, int], optional
            真ん中左の配置基準位置, by default None
        """
        self.image = font.render(legend, True, WHITE)
        self._setup_rect(topleft, midleft)

    def _setup_rect(
            self,
            topleft: tuple[int, int] | None,
            midleft: tuple[int, int] | None
    ) -> None:
        """
        レクトの初期化

        Parameters
        ----------
        topleft : tuple[int, int] | None
            左上の配置基準位置
        midleft : tuple[int, int] | None
            真ん中左の配置基準位置

        Raises
        ------
        ValueError
            topleftとmidleftのどちらかだけ渡した場合以外
        """
        if topleft and (not midleft):
            self.rect = self.image.get_rect(topleft=topleft)

        elif midleft and (not topleft):
            self.rect = self.image.get_rect(midleft=midleft)

        else:
            raise ValueError('topleftとmidleftは、どちらかだけ渡してください')


class TableNum(pygame.sprite.Sprite, ABC):
    """
    テーブル上の数値スプライトの基底抽象クラス

    Attributes
    ----------
    _font : Font
        フォント
    """

    def __init__(self, group: Group, font: Font):
        """
        コンストラクタ

        Parameters
        ----------
        group : Group
            所属グループ
        font : Font
            フォント
        """
        super().__init__(group)

        self._font = font

    @abstractmethod
    def reset(self, *args: Any) -> Any:
        """
        リセット

        Returns
        -------
        Any
            ボーナス反映後のスコアなど
        """
        pass


class Value(TableNum):
    """
    値スプライト

    最終スコア以外の各項目の元の値

    Attributes
    ----------
    _topright : tuple[int, int]
        右上の配置基準位置
    _unit : str
        単位
    """

    def __init__(
            self,
            group: Group,
            font: Font,
            topright: tuple[int, int],
            unit: str
    ):
        """
        コンストラクタ

        Parameters
        ----------
        group : Group
            所属グループ
        font : Font
            フォント
        topright : tuple[int, int]
            右上の配置基準位置
        unit : str
            単位
        """
        super().__init__(group, font)

        self._topright = topright
        self._unit = unit

    def reset(self, value_num: int | float) -> None:
        """
        リセット

        Parameters
        ----------
        value_num : int | float
            項目の元の値
        """
        text = f'{value_num}{self._unit}'

        self.image = self._font.render(text, True, WHITE)
        self.rect = self.image.get_rect(topright=self._topright)


class BonusRatio(TableNum):
    """
    ボーナス倍率のスプライト

    Attributes
    ----------
    _font : Font
        フォント
    _topright : tuple[int, int]
        右上の配置基準位置
    """

    def __init__(self, font: Font, topright: tuple[int, int]):
        """
        コンストラクタ

        Parameters
        ----------
        font : Font
            フォント
        topright : tuple[int, int]
            右上の配置基準位置
        """
        self._font = font
        self._topright = topright

    def reset(self, bonus_ratio_num: int | float) -> None:
        """
        リセット

        Parameters
        ----------
        bonus_ratio_num : int | float
            ボーナス倍率
        """
        if bonus_ratio_num == 1:
            self._ratio = 1
            text = 'ー'

        else:
            text = f'× {bonus_ratio_num}'
            self._ratio = bonus_ratio_num

        self.image = self._font.render(text, True, WHITE)
        self.rect = self.image.get_rect(topright=self._topright)

    def calc_score(self, value: int | float) -> int:
        """
        スコアの計算

        ボーナスが反映されたスコアを返す

        Parameters
        ----------
        value : int | float
            ボーナス算出対象の数値

        Returns
        -------
        int
            ボーナスが反映されたスコア
        """
        score = int(value * self._ratio)

        return score


class Score(TableNum):
    """
    スコアスプライト

    Attributes
    ----------
    _topright : tuple[int, int] | None
        右上の配置基準位置
    _midright : tuple[int, int] | None
        真ん中右の配置基準位置
    """
    
    def __init__(
            self,
            group: Group,
            font: Font,
            *,
            topright: tuple[int, int] = None,
            midright: tuple[int, int] = None
    ):
        """
        コンストラクタ

        Parameters
        ----------
        group : Group
            所属グループ
        font : Font
            フォント
        topright : tuple[int, int], optional
            右上の配置基準位置, by default None
        midright : tuple[int, int], optional
            真ん中右の配置基準に位置, by default None
        """
        super().__init__(group, font)

        self._setup_pos(topright, midright)

    def _setup_pos(
            self,
            topright: tuple[int, int] | None,
            midright: tuple[int, int] | None
    ) -> None:
        """
        配置基準位置の初期化

        Parameters
        ----------
        topright : tuple[int, int] | None
            右上の配置基準位置
        midright : tuple[int, int] | None
            真ん中右の配置基準

        Raises
        ------
        ValueError
            toprightとmidrightのどちらかだけ渡した場合以外
        """
        if topright and (not midright):
            self._topright = topright
            self._midright = None

        elif midright and (not topright):
            self._midright = midright
            self._topright = None

        else:
            raise ValueError(
                'toprightとmidrightは、どちらかだけ渡してください'
            )
        
    def reset(self, score: int) -> None:
        """
        リセット

        Parameters
        ----------
        score : int
            スコア
        """
        score = str(score)

        self.image = self._font.render(score, True, WHITE)
        
        if self._topright:
            self.rect = self.image.get_rect(topright=self._topright)

        elif self._midright:
            self.rect = self.image.get_rect(midright=self._midright)