from __future__ import annotations

import pygame

from classes.ui.bar import BarChildrenArgs
from classes.ui.status_bar.children_group import ChildrenGroup
from constants import WHITE, FONT_PATH


class ScoreGroup(ChildrenGroup):
    """
    スコアグループ
    """

    def __init__(self, args: BarChildrenArgs):
        """
        コンストラクタ

        Parameters
        ----------
        args : BarChildrenArgs
            専用引数
        """
        super().__init__()

        Score(self, args)

    @property
    def sprite(self) -> Score:
        """
        スプライト

        Returns
        -------
        Score
            唯一の所属スプライト
        """
        return super().sprite
    
    @property
    def right(self) -> int:
        """
        スプライトの右端のx座標

        Returns
        -------
        int
            スプライトの右端のx座標
        """
        return self.sprite.rect.right
    
    @property
    def score(self) -> int:
        """
        スコア

        Returns
        -------
        int
            スコア
        """
        return self.sprite.score


class Score(pygame.sprite.DirtySprite):
    """
    スコアスプライト

    Attributes
    ----------
    _num_of_digits : int
        表示桁数

    _font : Font
        フォント
    _score : int
        スコア
    image : Surface
        イメージ
    rect : Rect
        レクト
    """
    
    _num_of_digits: int = 6

    def __init__(
            self,
            group: ScoreGroup,
            args: BarChildrenArgs
    ):
        """
        コンストラクタ

        Parameters
        ----------
        group : ScoreGroup
            所属グループ
        args : BarChildrenArgs
            専用引数
        """
        super().__init__(group)

        self._font = pygame.font.Font(FONT_PATH, args.h)
        self.reset()
        self._setup_rect(args.w_margin, args.mid_h)

    @property
    def score(self) -> int:
        """
        スコア

        Returns
        -------
        int
            スコア
        """
        return self._score
    
    def reset(self) -> None:
        """
        リセット
        """
        self._score = 0
        self._update_image()

        self.dirty = 1

    def _update_image(self) -> None:
        """
        イメージの更新
        """
        text = str(self._score)

        text_len = len(text)

        if text_len < self._num_of_digits:
            zero_nums = self._num_of_digits - text_len
            zero_texts = '0' * zero_nums

            text = zero_texts + text

        self.image = self._font.render(text, True, WHITE)

    def _setup_rect(self, w_margin: int, mid_h: int) -> None:
        """
        レクトの初期化

        Parameters
        ----------
        w_margin : int
            画面左端から、スプライトの左端までの余白
        mid_h : int
            中心の配置高さ
        """
        self.rect = self.image.get_rect()

        self.rect.midleft = (w_margin, mid_h)

    def update(self, point: int) -> None:
        """
        更新

        Parameters
        ----------
        point : int
            獲得ポイント
        """
        self._score += point

        self._update_image()

        self.dirty = 1