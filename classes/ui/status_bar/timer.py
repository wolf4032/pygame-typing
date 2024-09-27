from __future__ import annotations

import pygame

from classes.ui.status_bar.children_group import ChildrenGroup
from classes.ui.bar import BarChildrenArgs
from constants import GRAY, BLACK


class TimerGroup(ChildrenGroup):
    """
    タイマーグループ
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

        Timer(self, args)

    @property
    def sprite(self) -> Timer:
        """
        スプライト

        Returns
        -------
        Timer
            唯一のスプライト
        """
        return super().sprite


class Timer(pygame.sprite.DirtySprite):
    """
    タイマースプライト

    Attributes
    ----------
    _h : int
        高さ
    _mid_h : int
        中心の配置高さ
    _w_margin : int
        余白幅比率
    image : Surface
        イメージ
    rect : Rect
        レクト
    _full_w : int
        戦闘開始時のスプライト幅
    _topleft : Tuple[int, int]
        配置サーフェスに対する左上のxy座標
    _elapsed_w : int
        時間経過により消された幅
    dirty : int
        ダーティーフラグ
    """
    
    def __init__(
            self,
            group: TimerGroup,
            args: BarChildrenArgs
    ):
        """
        コンストラクタ

        Parameters
        ----------
        group : TimerGroup
            所属グループ
        args : BarChildrenArgs
            専用引数
        """
        super().__init__(group)

        self._h = args.h
        self._mid_h = args.mid_h
        self._w_margin = args.w_margin

    def reset(self, status_bar_w: int, healths_right: int) -> None:
        """
        リセット

        Parameters
        ----------
        status_bar_w : int
            ステータスバーの幅
        healths_right : int
            残基の右端のx座標
        """
        self._setup_image(status_bar_w, healths_right)
        self._setup_rect(healths_right)

        self._full_w = self.rect.w
        self._topleft = self.rect.topleft
        self._elapsed_w = 0

        self.dirty = 1

    def _setup_image(self, status_bar_w: int, healths_right: int) -> None:
        """
        イメージの初期化

        Parameters
        ----------
        status_bar_w : int
            ステータスバーの幅
        healths_right : int
            残基の右端のx座標
        """
        w = status_bar_w - healths_right - self._w_margin * 2

        self.image = pygame.Surface((w, self._h))

        self.image.fill(GRAY)

    def _setup_rect(self, healths_right: int) -> None:
        """
        レクトの初期化

        Parameters
        ----------
        healths_right : int
            残基の右端のx座標
        """
        self.rect = self.image.get_rect()

        midleft_x = healths_right + self._w_margin

        self.rect.midleft = (midleft_x, self._mid_h)

    def update(self, frames: int, end_frames: int) -> None:
        """
        更新

        Parameters
        ----------
        frames : int
            経過フレーム数
        end_frames : int
            終了フレーム数
        """
        elapsed_rate = frames / end_frames
        elapsed_w = int(self._full_w * elapsed_rate)

        if elapsed_w > self._elapsed_w:
            size = (elapsed_w - self._elapsed_w, self.rect.h)

            if self.rect.size != size:
                self.image = pygame.Surface(size)
                self.image.fill(BLACK)
                self.rect = self.image.get_rect()

            self.rect.topleft = self._topleft
            self.rect.x += self._elapsed_w

            self._elapsed_w = elapsed_w

            self.dirty = 1