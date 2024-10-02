import pygame
from pygame import Rect
from pygame.event import Event

from classes.ui.result.table.table import Table
from constants import WHITE
from classes.ui.result.info import Info


class Result(pygame.sprite.Sprite):
    """
    結果スプライト

    Attributes
    ----------
    _size_ratio : float
        サイズ比率
    _frame_w_ratio : float
        フレーム幅比率

    _base_image : Surface
        基本イメージ
        結果テーブルがなく、枠と情報スプライトだけが配置されている
    rect : Rect
        レクト
    _result_table : ResultTable
        結果テーブルスプライト
    image : Surface
        イメージ
    """
    
    _size_ratio: float = 0.8
    _frame_w_ratio: float = 0.025

    def __init__(self, screen_rect: Rect):
        """
        コンストラクタ

        Parameters
        ----------
        screen_rect : Rect
            画面レクト
        """
        self._build_base_image(screen_rect)
        self.rect = self._base_image.get_rect()
        self._draw_frame()
        self.rect.center = screen_rect.center
        self._draw_info()

        self._result_table = Table(self.rect)

    def _build_base_image(self, screen_rect: Rect) -> None:
        """
        空のイメージの初期化

        Parameters
        ----------
        screen_rect : Rect
            画面レクト
        """
        w = int(screen_rect.w * self._size_ratio)
        h = int(screen_rect.h * self._size_ratio)
        self._base_image = pygame.Surface((w, h))

    def _draw_frame(self) -> None:
        """
        枠の反映
        """
        frame_w = int(self.rect.h * self._frame_w_ratio)
        pygame.draw.rect(self._base_image, WHITE, self.rect, frame_w)

    def _draw_info(self) -> None:
        """
        情報スプライトの配置
        """
        info = Info(self.rect)

        self._base_image.blit(info.image, info.rect)
    
    @staticmethod
    def accept_input(events: list[Event]) -> bool:
        """
        入力受付

        Parameters
        ----------
        events : list[Event]
            イベントリスト

        Returns
        -------
        bool
            [R]を入力されると、再戦闘のためのTrueを返し、入力がなければFalseを返す
        """
        restart = False

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart = True

                    break

        return restart
                    
    def apply_difficulty_settings(self) -> None:
        """
        難易度に応じた設定

        現状は難易度変更機能がないため、直接各種ボーナス倍率を指定している
        """
        raw_score_ratio = 1
        accuracy_ratio = 100
        residues_ratio = 100

        self._result_table.setup_bonus_ratios(
            raw_score_ratio, accuracy_ratio, residues_ratio
        )
                    
    def build(
            self,
            score: int,
            accuracy: float,
            residues: int
    ) -> int:
        """
        結果の作成

        Parameters
        ----------
        score : int
            戦闘終了時のスコア
        accuracy : float
            正確性
        residues : int
            残基

        Returns
        -------
        int
            最終スコア
        """
        total_score = self._result_table.reset(score, accuracy, residues)

        self.image = self._base_image.copy()
        self.image.blit(self._result_table.image, self._result_table.rect)

        return total_score