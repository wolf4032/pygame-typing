import pygame
from pygame import Surface, Rect

from utils.utils import Utils
from classes.characters.enemy.enemies import Enemies
from classes.characters.earth import EarthGroup
from classes.ui.status_bar.status_bar import StatusBar
from classes.ui.info_bar import InfoBar
from constants import FPS, BLACK
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
    _info_bar : InfoBar
        情報バースプライト
    _end_frames : int
        戦闘終了フレーム
    _result : Result
        戦闘結果スプライト
    """
    
    _battle_seconds: int = 120
    _status_bar_h_ratio: float = 0.1
    _info_bar_h_ratio: float = 0.05

    def __init__(self, screen: Surface, screen_size: tuple[int, int]):
        """
        コンストラクタ

        Parameters
        ----------
        screen : Surface
            画面サーフェス
        screen_size : tuple[int, int]
            画面サイズ
        """
        self._screen = screen
        self._setup_background(screen_size)
        self._clock = pygame.time.Clock()

        screen_rect = self._screen.get_rect()
        battle_area_rect = self._build_battle_area_rect(screen_rect)

        self._enemies = Enemies(battle_area_rect)
        self._earth = EarthGroup(battle_area_rect)
        self._status_bar = StatusBar(
            self._screen,
            screen_rect,
            self._status_bar_h_ratio
        )
        self._info_bar = InfoBar(screen_rect, self._info_bar_h_ratio)

        self._end_frames = FPS * self._battle_seconds

        self._result = Result(screen_rect)

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

    @classmethod
    def _build_battle_area_rect(cls, screen_rect: Rect) -> Rect:
        """
        戦闘領域レクトの作成

        Parameters
        ----------
        screen_rect : Rect
            画面レクト

        Returns
        -------
        Rect
            戦闘領域レクト
        """
        left = 0
        top = int(screen_rect.h * cls._status_bar_h_ratio)

        h_ratio = 1 - (cls._status_bar_h_ratio + cls._info_bar_h_ratio)
        h = int(screen_rect.h * h_ratio)

        rect = Rect(left, top, screen_rect.w, h)

        return rect

    def run(self) -> None:
        self._result.apply_difficulty_settings()

        while True:
            self._battle()

    def _battle(self) -> None:
        """
        戦闘

        Returns
        -------
        None
            戦闘終了時に、return Noneでメソッドを終了する
        """
        self._setup()

        while True:
            self._frames += 1

            if self._frames > self._end_frames:
                self._finish()

                return None
            
            self._enemies.add(self._frames, self._earth.pos)
            dirty_rects = self._draw()
            pygame.display.update(dirty_rects)

            if self._earth.health <= 0:
                self._finish()

                return None

            key = Battle._accept_input()
            self._update(key)
            self._clear()

            self._clock.tick(FPS)

    def _setup(self) -> None:
        """
        初期化
        """
        self._screen.blit(self._background, (0, 0))
        self._frames = 0

        self._enemies.reset()
        self._earth.reset(self._screen)
        self._status_bar.reset(self._screen, self._earth.health)
        self._info_bar.setup(self._screen)

        pygame.display.update()

    def _finish(self) -> None:
        """
        終了処理

        ゲームの終了処理と、結果の表示
        """
        self._update()

        self._enemies.finish()
        self._clear()

        self._build_result()

        dirty_rects = self._finish_draw()

        pygame.display.update(dirty_rects)

        self._result.accept_input()
                    
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
    def _accept_input() -> str | None:
        """
        入力受付

        Returns
        -------
        str | None
            [Esc]以外は、入力があれば、その文字列を返す
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Utils.game_quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Utils.game_quit()

                else:
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