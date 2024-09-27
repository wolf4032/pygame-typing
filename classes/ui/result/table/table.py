import pygame
from pygame import Rect
from pygame.font import Font

from constants import FONT_PATH
from classes.ui.result.table.items import ColumnName, Item, TotalScore


class Table(pygame.sprite.Sprite):
    """
    結果テーブルスプライト

    Attributes
    ----------
    _size_ratio : float
        サイズ比率
    _pos_h_ratio : float
        配置高さ比率
    _row_h_ratios : list[float]
        行の高さの比率のリスト
    _col_w_ratios : list[float]
        列の幅の比率のリスト
    _font_size_ratio : float
        文字のサイズの比率

    _group : Group
        各項目のスコアスプライトが所属するグループ
    rect : Rect
        レクト
    _base_image : Surface
        列名と凡例名だけ配置されたイメージ
    _raw_score : Item
        ボーナス反映前のスコアの項目
    _accuracy : Item
        正確性の項目
    _residues : Item
        残基の項目
    _total_score : TotalScore
        最終スコアの項目
    _added_bonus_ratio_image : Surface
        列名、凡例名、ボーナス倍率が配置されたイメージ
    image : Surface
        イメージ
    """
    
    _size_ratio: float = 0.6
    _pos_h_ratio: float = 0.4
    _row_h_ratios: list[float] = [0.15, 0.2, 0.2, 0.2, 0.25]
    _col_w_ratios: list[float] = [0.3, 0.2, 0.3, 0.2]
    _font_size_ratio: float = 0.4

    def __init__(self, result_rect: Rect):
        """
        コンストラクタ

        Parameters
        ----------
        result_rect : Rect
            結果レクト
        """
        self._group = pygame.sprite.Group()
        self._setup_rect(result_rect)
        
        rects_list = self._build_rects_list()
        self._setup_base_image(rects_list)
        self._setup_items(rects_list)
        self._setup_total_score(rects_list)

    def _setup_rect(self, result_rect: Rect) -> None:
        """
        レクトの初期化

        Parameters
        ----------
        result_rect : Rect
            結果レクト
        """
        w = int(result_rect.w * self._size_ratio)
        h = int(result_rect.h * self._size_ratio)
        self.rect = Rect(0, 0, w, h)

        centerx = result_rect.w // 2
        centery = int(result_rect.h * self._pos_h_ratio)
        self.rect.center = (centerx, centery)

    def _build_rects_list(self) -> list[list[Rect]]:
        """
        構成レクトの作成

        テーブル全体を、各項目の各要素が配置され得る範囲毎にRectを作成し、
        二次元配列に収める

        Returns
        -------
        list[list[Rect]]
            各項目の各要素が配置され得る範囲毎のRectを格納した二次元配列
        """
        ws = [int(self.rect.w * w_ratio) for w_ratio in self._col_w_ratios]
        hs = [int(self.rect.h * h_ratio) for h_ratio in self._row_h_ratios]

        xs = []
        x = 0
        for w in ws:
            xs.append(x)
            x += w

        ys = []
        y = 0
        for h in hs:
            ys.append(y)
            y += h

        rects_list = []
        for row_idx in range(len(hs)):
            row_rects = []

            y = ys[row_idx]
            h = hs[row_idx]

            for col_idx in range(len(ws)):
                x = xs[col_idx]
                w = ws[col_idx]

                row_rects.append(Rect(x, y, w, h))

            rects_list.append(row_rects)

        return rects_list

    def _setup_base_image(self, rects_list: list[list[Rect]]) -> None:
        """
        基イメージの作成

        列名と凡例だけが配置されたイメージの作成

        Parameters
        ----------
        rects_list : list[list[Rect]]
            各項目の各要素が配置され得る範囲毎のRectを格納した二次元配列
        """
        self._base_image = pygame.Surface(self.rect.size)

        self._draw_col_names(rects_list)

    def _draw_col_names(self, rects_list: list[list[Rect]]) -> None:
        """
        全列名の配置

        Parameters
        ----------
        rects_list : list[list[Rect]]
            各項目の各要素が配置され得る範囲毎のRectを格納した二次元配列
        """
        base_rect = rects_list[0][0]
        font = self._build_font(base_rect)

        self._draw_col_name(rects_list, (1, 0), font, '値')
        self._draw_col_name(rects_list, (2, 0), font, 'ボーナス倍率')
        self._draw_col_name(rects_list, (3, 0), font, 'スコア')

    def _build_font(self, base_rect: Rect) -> Font:
        """
        フォントの作成

        Parameters
        ----------
        base_rect : Rect
            フォントのサイズの基準となるレクト

        Returns
        -------
        Font
            フォント
        """
        size = int(base_rect.h * self._font_size_ratio)
        font = pygame.font.Font(FONT_PATH, size)

        return font

    def _draw_col_name(
            self,
            rects_list: list[list[Rect]],
            pos: tuple[int, int],
            font: Font,
            name: str
    ) -> None:
        """
        列名の配置

        Parameters
        ----------
        rects_list : list[list[Rect]]
            各項目の各要素が配置され得る範囲毎のRectを格納した二次元配列
        pos : tuple[int, int]
            列名の配置エリア
        font : Font
            フォント
        name : str
            列名
        """
        pos_x, pos_y = pos
        pos_rect = rects_list[pos_y][pos_x]
        rect_topright = pos_rect.topright

        sprite = ColumnName(font, name, rect_topright)

        self._base_image.blit(sprite.image, sprite.rect)

    def _setup_items(self, rects_list: list[list[Rect]]) -> None:
        """
        全項目の初期化

        最終スコア以外の全項目の初期化

        Parameters
        ----------
        rects_list : list[list[Rect]]
            各項目の各要素が配置され得る範囲毎のRectを格納した二次元配列
        """
        base_rect = rects_list[1][0]
        font = self._build_font(base_rect)

        self._raw_score = self._setup_item(
            rects_list[1], font, '終了時スコア', ''
        )
        self._accuracy = self._setup_item(rects_list[2], font, '正確性', '%')
        self._residues = self._setup_item(rects_list[3], font, '残基', '')


    def _setup_item(
            self, row_rects: list[Rect], font: Font, legend: str, unit: str
    ) -> Item:
        """
        項目の初期化

        Parameters
        ----------
        row_rects : list[Rect]
            項目の各要素が配置され得るRectを格納したリスト
        font : Font
            フォント
        legend : str
            凡例名
        unit : str
            単位

        Returns
        -------
        Item
            項目
        """
        legend_topleft = row_rects[0].topleft
        value_topright = row_rects[1].topright
        bonus_ratio_topright = row_rects[2].topright
        score_topright = row_rects[3].topright

        item = Item(
            self._group,
            font,
            legend,
            unit,
            legend_topleft,
            value_topright,
            bonus_ratio_topright,
            score_topright
        )

        item.draw_legend(self._base_image)

        return item

    def _setup_total_score(self, rects_list: list[list[Rect]]) -> None:
        """
        最終スコアの初期化

        Parameters
        ----------
        rects_list : list[list[Rect]]
            各項目の各要素が配置され得る範囲毎のRectを格納した二次元配列
        """
        row_rects = rects_list[-1]
        base_rect = row_rects[0]
        font = self._build_font(base_rect)
        
        legend_midleft = row_rects[1].midleft
        score_midright = row_rects[-1].midright

        self._total_score = TotalScore(
            self._group,
            font,
            '最終スコア',
            legend_midleft,
            score_midright
        )

        self._total_score.draw_legend(self._base_image)

    def setup_bonus_ratios(
            self,
            raw_score_ratio: int | float,
            accuracy_ratio: int | float,
            residues_ratio: int | float
    ) -> None:
        """
        ボーナス倍率の初期化

        Parameters
        ----------
        raw_score_ratio : int | float
            ボーナス反映前のスコアに対するボーナス倍率
        accuracy_ratio : int | float
            正確性ボーナス倍率
        residues_ratio : int | float
            残基ボーナス倍率
        """
        self._added_bonus_ratio_image = self._base_image.copy()

        self._raw_score.setup_bonus_ratio(
            raw_score_ratio, self._added_bonus_ratio_image
        )
        self._accuracy.setup_bonus_ratio(
            accuracy_ratio, self._added_bonus_ratio_image
        )
        self._residues.setup_bonus_ratio(
            residues_ratio, self._added_bonus_ratio_image
        )

        self.image = self._added_bonus_ratio_image.copy()

    def reset(self, raw_score: int, accuracy: float, residues: int) -> int:
        """
        リセット

        ボーナス反映前のスコア、正確性、残基をもとに、各項目のスコアと、
        最終スコアを算出する
        テーブルのイメージに、結果を反映する

        Parameters
        ----------
        raw_score : int
            ボーナス反映前のスコア
        accuracy : float
            正確性
        residues : int
            残基

        Returns
        -------
        int
            最終スコア
        """
        raw_score_with_bonus = self._raw_score.reset(raw_score)
        accuracy_score = self._accuracy.reset(accuracy)
        residues_score = self._residues.reset(residues)

        scores = [raw_score_with_bonus, accuracy_score, residues_score]

        total_score = self._total_score.reset(scores)

        self._group.clear(self.image, self._added_bonus_ratio_image)
        self._group.draw(self.image)

        return total_score