import pygame
from pygame.font import Font
from pygame import Surface
from pygame.sprite import Group

from constants import WHITE
from classes.ui.result.table.item_infos import Legend, Value, BonusRatio, Score


class ColumnName(pygame.sprite.Sprite):
    """
    列名スプライト

    Attributes
    ----------
    image : Surface
        イメージ
    rect : Rect
        レクト
    """

    def __init__(self, font: Font, name: str, topright: tuple[int, int]):
        """
        コンストラクタ

        Parameters
        ----------
        font : Font
            フォント
        name : str
            列名
        topright : tuple[int, int]
            右上の配置基準位置
        """
        self.image = font.render(name, True, WHITE)
        self.rect = self.image.get_rect(topright=topright)


class ItemHelper:
    """
    項目のヘルパークラス

    Attributes
    ----------
    _legend : Legend
        凡例スプライト
    """

    def __init__(self):
        """
        コンストラクタ
        """
        self._legend: Legend = None

    def draw_legend(self, result_table: Surface) -> None:
        """
        凡例の配置

        Parameters
        ----------
        result_table : Surface
            配置先テーブル
        """
        result_table.blit(self._legend.image, self._legend.rect)


class Item(ItemHelper):
    """
    項目

    結果の項目

    Attributes
    ----------
    _legend : Legend
        凡例スプライト
    _value : Value
        値スプライト
    _bonus_ratio : BonusRatio
        ボーナス倍率のスプライト
    _score : Score
        スコアスプライト
    """

    def __init__(
            self,
            group: Group,
            font: Font,
            legend: str,
            unit: str,
            legend_topleft: tuple[int, int],
            value_topright: tuple[int, int],
            bonus_ratio_topright: tuple[int, int],
            score_topright: tuple[int, int]
    ):
        """
        コンストラクタ

        Parameters
        ----------
        group : Group
            所属グループ
        font : Font
            フォント
        legend : str
            凡例名
        unit : str
            単位
        legend_topleft : tuple[int, int]
            凡例の、左上の配置基準位置
        value_topright : tuple[int, int]
            値の、右上の配置基準位置
        bonus_ratio_topright : tuple[int, int]
            ボーナス倍率の、右上の配置基準位置
        score_topright : tuple[int, int]
            スコアの、右上の配置基準位置
        """
        self._legend = Legend(font, legend, topleft=legend_topleft)
        self._value = Value(group, font, value_topright, unit)
        self._bonus_ratio = BonusRatio(font, bonus_ratio_topright)
        self._score = Score(group, font, topright=score_topright)

    def setup_bonus_ratio(
            self, bonus_ratio: int | float, result_table: Surface
    ) -> None:
        """
        ボーナス倍率の初期化

        Parameters
        ----------
        bonus_ratio : int | float
            ボーナス倍率
        result_table : Surface
            配置先テーブル
        """
        self._bonus_ratio.reset(bonus_ratio)
        
        result_table.blit(self._bonus_ratio.image, self._bonus_ratio.rect)

    def reset(self, value_num: int | float) -> int:
        """
        リセット

        今回の戦闘の結果をもとに該当スコアを計算し、該当する値のスプライトと、
        スコアのスプライトを更新する

        Parameters
        ----------
        value_num : int | float
            スコア算出に用いる値

        Returns
        -------
        int
            該当スコア
        """
        self._value.reset(value_num)

        score = self._bonus_ratio.calc_score(value_num)

        self._score.reset(score)

        return score


class TotalScore(ItemHelper):
    """
    最終スコア

    最終スコアの項目

    Attributes
    ----------
    _legend : Legend
        凡例スプライト
    _score : Score
        スコアスプライト
    """
    
    def __init__(
            self,
            group: Group,
            font: Font,
            legend: str,
            legend_midleft: tuple[int, int],
            score_midright: tuple[int, int]
    ):
        """
        コンストラクタ

        Parameters
        ----------
        group : Group
            所属グループ
        font : Font
            フォント
        legend : str
            凡例名
        legend_midleft : tuple[int, int]
            凡例の、真ん中左の配置基準位置
        score_midright : tuple[int, int]
            スコアの、真ん中右の配置基準位置
        """
        self._legend = Legend(font, legend, midleft=legend_midleft)
        self._score = Score(group, font, midright=score_midright)

    def reset(self, scores: list[int]) -> int:
        """
        リセット

        最終スコアの算出と、スコアスプライトの更新

        Parameters
        ----------
        scores : list[int]
            最終スコア算出に必要な各種スコア

        Returns
        -------
        int
            最終スコア
        """
        total_score = sum(scores)

        self._score.reset(total_score)

        return total_score
   