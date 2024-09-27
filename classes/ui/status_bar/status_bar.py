import pygame
from pygame import Rect, Surface

from constants import B_BLACK
from classes.ui.bar import BarChildrenArgs
from classes.ui.status_bar.score import ScoreGroup
from classes.ui.status_bar.healths import HealthsGroup
from classes.ui.status_bar.timer import TimerGroup


class StatusBar(pygame.sprite.Sprite):
    """
    ステータスバースプライト

    Attributes
    ----------
    _children_margin_ratio : float
        子要素間の余白幅比率
    _children_h_ratio : float
        子要素の高さ比率

    _bgd : Surface
        背景サーフェス
    rect : Rect
        レクト
    _score : ScoreGroup
        スコアグループ
     _healths : HealthsGroup
        残基グループ
     _timer : TimerGroup
        タイマーグループ
    """
    
    _children_margin_ratio: float = 0.025
    _children_h_ratio: float = 0.8

    def __init__(
            self,
            screen: Surface,
            screen_rect: Rect,
            h_ratio: int
    ):
        """
        コンストラクタ

        Parameters
        ----------
        screen : Surface
            画面サーフェス
        screen_rect : Rect
            画面レクト
        h_ratio : int
            高さ比率
        """
        self._setup_bgd(screen_rect, h_ratio)
        self.rect = self._bgd.get_rect(topleft=screen_rect.topleft)

        children_args = BarChildrenArgs(
            self.rect, self._children_margin_ratio, self._children_h_ratio
        )

        score_right = self._setup_score(screen, children_args)
        self._setup_healths(screen, score_right, children_args)
        self._timer = TimerGroup(children_args)

    @property
    def score(self) -> int:
        """
        スコア

        Returns
        -------
        int
            スコア
        """
        return self._score.score
    
    def _setup_bgd(self, screen_rect: Rect, h_ratio: int) -> None:
        """
        背景の初期化

        Parameters
        ----------
        screen_rect : Rect
            画面レクト
        h_ratio : int
            高さ比率
        """
        size = (screen_rect.w, int(screen_rect.h * h_ratio))
        self._bgd = pygame.Surface(size)
        self._bgd.fill(B_BLACK)
    
    def _setup_score(self, screen: Surface, args: BarChildrenArgs) -> int:
        """
        スコアグループの初期化

        Parameters
        ----------
        screen : Surface
            画面サーフェス
        args : BarChildrenArgs
            専用引数

        Returns
        -------
        int
            スコアスプライトの右端のx座標
        """
        self._score = ScoreGroup(args)
        self._score.clear(screen, self._bgd)

        return self._score.right

    def _setup_healths(
            self, screen: Surface, score_right: int, args: BarChildrenArgs
    ) ->None:
        """
        残基グループの初期化

        Parameters
        ----------
        screen : Surface
            画面サーフェス
        score_right : int
            スコアスプライトの右端のx座標
        args : BarChildrenArgs
            専用引数
        """
        self._healths = HealthsGroup(args, score_right)
        self._healths.clear(screen, self._bgd)

    def reset(self, screen: Surface, health: int) -> None:
        """
        リセット

        Parameters
        ----------
        screen : Surface
            画面サーフェス
        health : int
            残基（最大残基）
        """
        self.image = self._bgd.copy()

        self._score.reset()
        self._healths.reset(health)
        self._timer.reset(self.rect.w, self._healths.right)

        screen.blit(self.image, self.rect)
        self.draw_children(screen)

    def draw_children(self, screen: Surface) -> list[Rect]:
        """
        子要素の配置

        Parameters
        ----------
        screen : Surface
            画面サーフェス

        Returns
        -------
        list[Rect]
            ダーティーレクト
        """
        timer_dirty_rects = self._timer.draw(screen)
        score_dirty_rects = self._score.draw(screen)
        healths_dirty_rects = self._healths.draw(screen)

        dirty_rects = (
            timer_dirty_rects + score_dirty_rects + healths_dirty_rects
        )

        return dirty_rects

    def update(
            self, frames: int, end_frames: int, point: int, damage: int
    ) -> None:
        """
        更新

        Parameters
        ----------
        frames : int
            経過フレーム数
        end_frames : int
            終了フレーム数
        point : int
            獲得ポイント
        damage : int
            隕石衝突数
        """
        self._timer.update(frames, end_frames)

        if point:
            self._score.update(point)

        if damage:
            self._healths.update(damage)