import pygame
from pygame import Surface, Rect
from pygame.event import Event

from classes.characters.enemy.enemies import Enemies
from classes.characters.earth import EarthGroup
from classes.ui.status_bar.status_bar import StatusBar
from constants import BLACK
from classes.ui.result.result import Result


class Battle:
    """
    戦闘コントローラー

    Attributes
    ----------
    _battle_seconds : int
        戦闘秒数
    _status_bar_h_ratio : float
        ステータスバーの高さ比率
    _info_bar_h_ratio : float
        情報バーの高さ比率

    _screen : Surface
        画面サーフェス
    _background : Surface
        背景サーフェス
    _clock : Clock
        クロック、毎フレームの更新に必要
    _enemies : Enemies
        全敵
    _earth : EarthGroup
        地球のグループ
    _status_bar : StatusBar
        ステータスバースプライト
    _end_frames : int
        戦闘終了フレーム
    _result : Result
        戦闘結果スプライト
    """
    
    _battle_seconds: int = 120
    _status_bar_h_ratio: float = 0.1
    _info_bar_h_ratio: float = 0

    def __init__(
            self, screen: Surface, screen_size: tuple[int, int], fps: int
    ):
        """
        コンストラクタ

        Parameters
        ----------
        screen : Surface
            画面サーフェス
        screen_size : tuple[int, int]
            画面サイズ
        fps : int
            FPS
        """
        self._screen = screen
        self._fps = fps
        self._setup_background(screen_size)
        self._clock = pygame.time.Clock()

        self._screen_rect = self._screen.get_rect()
        battle_area_rect = self._build_battle_area_rect()

        self._enemies = Enemies(battle_area_rect, fps)
        self._earth = EarthGroup(battle_area_rect, fps)
        self._status_bar = StatusBar(
            self._screen,
            self._screen_rect,
            self._status_bar_h_ratio
        )

        self._end_frames = self._fps * self._battle_seconds

        self._result = Result(self._screen_rect)

        self._is_finish = False

    def _setup_background(self, size: tuple[int, int]) -> None:
        """
        背景サーフェスの初期化

        Parameters
        ----------
        size : tuple[int, int]
            画面サイズ
        """
        self._background = pygame.Surface(size)
        self._background.fill(BLACK)

    def _build_battle_area_rect(self) -> Rect:
        """
        戦闘領域レクトの作成

        Returns
        -------
        Rect
            戦闘領域レクト
        """
        left = 0
        top = int(self._screen_rect.h * self._status_bar_h_ratio)

        h_ratio = 1 - (self._status_bar_h_ratio + self._info_bar_h_ratio)
        h = int(self._screen_rect.h * h_ratio)

        rect = Rect(left, top, self._screen_rect.w, h)

        return rect
    
    def setup(self) -> list[Rect]:
        """
        初期化

        Returns
        -------
        list[Rect]
            ダーティーレクト
        """
        self._result.apply_difficulty_settings()

        self._setup()

    # def run(self) -> None:
    #     """
    #     実行
    #     """
    #     self._result.apply_difficulty_settings()

    #     while True:
    #         self._battle()

    # def _battle(self) -> None:
    #     """
    #     戦闘

    #     Returns
    #     -------
    #     None
    #         戦闘終了時に、return Noneでメソッドを終了する
    #     """
    #     self._setup()

    #     while True:
    #         self._frames += 1

    #         if self._frames > self._end_frames:
    #             self._finish()

    #             return None
            
    #         self._enemies.add(self._frames, self._earth.pos)
    #         dirty_rects = self._draw()
    #         pygame.display.update(dirty_rects)

    #         if self._earth.health <= 0:
    #             self._finish()

    #             return None

    #         key = Battle._accept_input()
    #         self._update(key)
    #         self._clear()

    #         self._clock.tick(FPS)

    def run(self, events: list[Event]) -> tuple[list[Rect] | None, bool]:
        """
        実行

        Parameters
        ----------
        events : list[Event]
            イベントリスト

        Returns
        -------
        tuple[list[Rect] | None, bool]
            ダーティーレクトと、ビュー変更するかどうかのbool
            画面の更新が不要の場合は、ダーティーレクトがNoneとして返される
        """
        dirty_rects = None
        should_change_view = False

        if self._is_finish:
            restart = self._result.accept_input(events)

            if restart:
                self._setup()

                return [self._screen_rect], should_change_view

            return dirty_rects, should_change_view

        dirty_rects = self._battle(events)

        return dirty_rects, should_change_view

    def _battle(self, events: list[Event]) -> list[Rect]:
        """
        戦闘

        Parameters
        ----------
        events : list[Event]
            イベントリスト

        Returns
        -------
        list[Rect]
            ダーティーレクト
        """
        self._frames += 1
        self._clear()

        if self._check_finish():
            dirty_rects = self._finish()

            return dirty_rects
        
        self._enemies.add(self._frames, self._earth.pos)
        dirty_rects = self._draw()

        key = Battle._accept_input(events)
        self._update(key)

        self._clock.tick(self._fps)

        return dirty_rects
    
    def _check_finish(self) -> bool:
        """
        戦闘終了かどうかの確認

        Returns
        -------
        bool
            戦闘終了ならTrue、戦闘継続ならFalse
        """
        is_time_over = self._frames > self._end_frames
        is_earth_dead = self._earth.health <= 0
        condition = is_time_over | is_earth_dead

        if condition:
            self._is_finish = True
        
        return condition
    
    def _setup(self) -> None:
        """
        初期化
        """
        self._screen.blit(self._background, (0, 0))
        self._frames = 0

        self._enemies.reset()
        self._earth.reset(self._screen)
        self._status_bar.reset(self._screen, self._earth.health)

        self._is_finish = False

    def _finish(self) -> list[Rect]:
        """
        終了処理

        ゲームの終了処理と、結果の表示

        Returns
        -------
        list[Rect]
            ダーティーレクト
        """
        self._update()

        self._enemies.finish()
        self._clear()

        self._build_result()

        dirty_rects = self._finish_draw()

        return dirty_rects
                    
    def _finish_draw(self) -> list[Rect]:
        """
        終了処理での配置

        Returns
        -------
        list[Rect]
            ダーティーレクト
        """
        dirty_rects = self._draw()

        self._screen.blit(self._result.image, self._result.rect)

        dirty_rects.append(self._result.rect)

        return dirty_rects

    def _draw(self) -> list[Rect]:
        """
        配置

        Returns
        -------
        list[Rect]
            ダーティーレクト
        """
        enemies_dirty_rects = self._enemies.draw(self._screen)

        earths_dirty_rects = self._earth.draw(self._screen)

        status_bar_dirty_rects = self._status_bar.draw_children(self._screen)

        dirty_rects = (
            enemies_dirty_rects + earths_dirty_rects + status_bar_dirty_rects
        )

        return dirty_rects

    @staticmethod
    def _accept_input(events: list[Event]) -> str | None:
        """
        入力受付

        Parameters
        ----------
        events : list[Event]
            イベントリスト

        Returns
        -------
        str | None
            入力があれば、その１文字を返す
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                key: str = event.unicode

                return key
                
    def _update(self, key: str | None = None) -> None:
        """
        更新

        Parameters
        ----------
        key : str | None, optional
            入力があれば、その文字列
            なければ、デフォルト値のNone
        """
        damage, point = self._enemies.update(
            key, self._earth.pos, self._earth.rect
        )

        self._earth.update(damage)

        self._status_bar.update(self._frames, self._end_frames, point, damage)

    def _clear(self) -> None:
        """
        背景の上書き

        次のフレームに向けて画面上から消すべきスプライトがある位置に、
        背景を上書きすることで、スプライトを消す
        """
        self._enemies.clear(self._screen, self._background)

    def _build_result(self) -> int:
        """
        結果の作成

        Returns
        -------
        int
            最終スコア
        """
        score = self._status_bar.score
        accuracy = self._enemies.calc_accuracy()
        residues = self._earth.health

        result = self._result.build(score, accuracy, residues)

        return result