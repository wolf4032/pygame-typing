from typing import Any
from abc import ABC, abstractmethod
import sys
import asyncio

import pygame
from pygame import Rect
from pygame.sprite import Sprite, DirtySprite, AbstractGroup


class Game(ABC):
    """
    ゲームコントローラー基底抽象クラス

    Attributes
    ----------
    _caption : str
        タイトル
    """

    _caption: str = None

    def __init__(self, *args: Any):
        """
        コンストラクタ
        """
        self._check_caption()
        Game.initialize(self._caption)

    @classmethod
    def _check_caption(cls) -> None:
        """
        タイトルの確認

        Raises
        ------
        TypeError
            タイトルがstrではない場合
        """
        if not isinstance(cls._caption, str):
            raise TypeError(
                f'{cls.__name__}._captionをstrで再定義してください'
            )

    @staticmethod
    def initialize(caption : str) -> None:
        """
        初期化

        Parameters
        ----------
        caption : str
            タイトル
        """
        pygame.init()
        pygame.display.set_caption(caption)

    @abstractmethod
    def run(self) -> None:
        """
        初期化
        """
        pass


class Utils:
    """
    ユーティリティクラス
    """

    @staticmethod
    def game_quit() -> None:
        """
        ゲームの終了
        """
        pygame.quit()
        sys.exit()

    @staticmethod
    def build_screen_size() -> tuple[int, int]:
        """
        スクリーンサイズの作成

        Returns
        -------
        tuple[int, int]
            スクリーンの幅と高さ
        """
        info = pygame.display.Info()
        width = info.current_w
        height = info.current_h

        size = (width, height)

        return size
    
    @staticmethod
    async def mesure_fps() -> int:
        """
        FPSの計測

        clock.get_fps()の結果が０の場合は、実行環境がデスクトップであると仮定し、
        60FPSになるようにする

        Returns
        -------
        int
            FPSの計測結果
        """
        clock = pygame.time.Clock()

        for _ in range(11):
            clock.tick()

            await asyncio.sleep(0)

        fps = clock.get_fps()

        if fps == 0:
            fps = 60
        
        else:
            fps = round(fps / 10) * 10

        return fps
    
    @staticmethod
    def build_new_base_surface_area(
        rect: Rect, new_base_rect: Rect
    ) -> tuple[int, int, int, int]:
        """
        新しい配置先サーフェスに対するエリアの取得

        元々のrectの配置先サーフェスAから、配置先を、
        配置先サーフェスAに直接配置されているサーフェスBに変更した場合の、
        rectのエリアを作成する

        元のrectの原点をサーフェスAの左上とすると、
        原点がサーフェスBの左上になるように、rectを平行移動させている

        Parameters
        ----------
        rect : Rect
            レクト
        new_base_rect : Rect
            新しい配置先サーフェス

        Returns
        -------
        tuple[int, int, int, int]
            新しい配置先サーフェスに対するエリア
        """
        x = rect.x - new_base_rect.x
        y = rect.y - new_base_rect.y

        area = (x, y, rect.w, rect.h)

        return area
    
    @staticmethod
    def reverse_sprites(spritedict: dict[Any, Rect | None]) -> list[Sprite]:
        """
        逆順にspriteの取得

        draw()のself.sprites()をself.reverse_sprites()にすることで、
        groupへの追加が新しいspriteから順にblitされるようにできる

        Parameters
        ----------
        spritedict : dict[Any, Rect  |  None]
            スプライトの辞書

        Returns
        -------
        list[Sprite]
            グループへの追加が新しい順のスプライトのリスト
        """
        sprites = list(spritedict)
        sprites.reverse()
        return sprites


class ArgsProvider(ABC):
    """
    専用引数提供機
    """

    @abstractmethod
    def provide(self, *args) -> Any:
        """
        専用引数の提供

        Returns
        -------
        Any
            専用引数
        """
        pass

    
class DamagedSprite(pygame.sprite.DirtySprite):
    """
    ダメージを受けるスプライト

    Attributes
    ----------
    _damage_expression_seconds : int | float
        ダメージ描写継続秒数

    _damaged_count : int
        ダメージ描写経過フレーム数
    image : Surface
        イメージ
    _normal_image : Surface
        通常時イメージ
    _damaged_image : Surface
        被ダメージ時イメージ
    dirty : int
        ダーティーフラグ
    """

    _damage_expression_seconds: int | float = 0.1

    def __init__(self, group: AbstractGroup, fps: int):
        """
        コンストラクタ

        Parameters
        ----------
        group : AbstractGroup
            所属グループ
        fps : int
            FPS
        """
        super().__init__(group)

        self._damage_expression_frames = int(
            fps * self._damage_expression_seconds
        )

        self._damaged_count: int = None
        self.image: pygame.Surface = None
        self._normal_image: pygame.Surface = None
        self._damaged_image: pygame.Surface = None
        self.dirty = 1

    def _damaged(self) -> None:
        """
        被ダメージ処理
        """
        self.image = self._damaged_image
        self._damaged_count = 0
        self.dirty = 1
    
    def _update_damage_situation(self) -> None:
        """
        ダメージ状況の更新
        """
        if isinstance(self._damaged_count, int):
            self._damaged_count += 1
            
        if self._damaged_count == self._damage_expression_frames:
            self.image = self._normal_image

            self._damaged_count = None

            self.dirty = 1


class SpriteAccessibleLayerdDirty(pygame.sprite.LayeredDirty, ABC):
    """
    所属スプライトアクセス可能グループ

    唯一の所属スプライトにアクセスするゲッターを持ったグループ
    """
    
    def _lookup_sprite(self) -> DirtySprite:
        """
        スプライトの取得

        唯一のスプライトの取得

        Returns
        -------
        DirtySprite
            スプライト
        """
        return self.sprites()[0]
    
    @property
    @abstractmethod
    def sprite(self) -> DirtySprite:
        """
        スプライト

        Returns
        -------
        DirtySprite
            唯一のスプライト
        """
        return self._lookup_sprite()