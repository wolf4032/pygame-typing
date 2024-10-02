from __future__ import annotations
import random
from dataclasses import dataclass

import pygame
from pygame import Vector2, Rect, Surface

from utils.utils import DamagedSprite, ArgsProvider
from utils.group import OverlappingReverse
from constants import GREEN, D_GREEN


class Meteor(DamagedSprite):
    """
    隕石スプライト

    Attributes
    ----------
    _point : int
        撃破ポイント

    _speed : int | float
        移動速度
    _pos : Vector2
        中心座標
    _normal_image : Surface
        通常時イメージ
    _damaged_image : Surface
        被ダメージ時イメージ
    image : Surface
        イメージ
    rect : Rect
        レクト
    """

    _point: int = 100

    def __init__(self, args: MeteorArgs, fps: int):
        """
        コンストラクタ

        Parameters
        ----------
        args : MeteorArgs
            専用引数
        fps: int
            FPS
        """
        super().__init__(args.group, fps)

        self._speed = args.speed
        self._pos = args.pop_pos
        self._normal_image = args.normal_image
        self._damaged_image = args.damaged_image

        self.image = self._normal_image
        self.rect = self.image.get_rect(center=self._pos)
    
    @property
    def pos(self) -> Vector2:
        """
        中心座標

        Returns
        -------
        Vector2
            中心座標
        """
        return self._pos
    
    @property
    def speed(self) -> int | float:
        """
        移動速度

        Returns
        -------
        int | float
            移動速度
        """
        return self._speed
    
    @property
    def point(self) -> int:
        """
        撃破ポイント

        Returns
        -------
        int
            撃破ポイント
        """
        return self._point

    def update(self, target_pos: Vector2, earth_rect: Rect) -> None | bool:
        """
        更新

        self._update_damage_situation()や、self._damaged()によって
        dirtyフラグが更新されるが、隕石スプライトはLayeredDirty所属ではないため、
        dirtyフラグに関わらず、常に描画が更新される

        Parameters
        ----------
        target_pos : Vector2
            移動先の方向にある座標
        earth_rect : Rect
            地球のレクト

        Returns
        -------
        None | bool
            _description_
        """
        self._update_damage_situation()

        self._move(target_pos)

        collided = self.rect.colliderect(earth_rect)

        if collided:
            return collided

    def update_by_key(self) -> None:
        """
        入力による更新
        """
        self._damaged()

    def _move(self, target_pos: Vector2) -> None:
        """
        移動

        Parameters
        ----------
        target_pos : Vector2
            移動先の方向にある座標
        """
        self._pos = self._pos.move_towards(target_pos, self._speed)

        self.rect.center = self._pos


class MeteorArgsProvider(ArgsProvider):
    """
    隕石専用引数提供機

    Attributes
    ----------
    _base_speed_ratio : float
        移動速度割合
    _pop_areas : tuple[str, str, str, str]
        全湧き領域のリスト
    _radius_ratio : float
        半径の比率

    _base_speed : int | float
        基礎スピード
    _radius : int
        半径
    _normal_image : Surface
        通常時イメージ
    _damaged_image : Surface
        被ダメージ時イメージ
    _left_idx : int
        左の湧き領域のx座標
    _top_idx : int
        上の湧き領域のy座標
    _right_idx : int
        右の湧き領域のx座標
    _bottom_idx : int
        下の湧き領域のy座標
    """

    _base_speed_ratio = 0.05
    _pop_areas = ('top', 'bottom', 'right', 'left')
    _radius_ratio = 0.05

    def __init__(self, exist_rect: Rect, fps: int):
        """
        コンストラクタ

        Parameters
        ----------
        exist_rect : Rect
            描画領域レクト
        fps : int
            FPS
        """
        self._base_speed = round(
            exist_rect.h * self._base_speed_ratio / fps, 2
        )
        self._radius = int(exist_rect.h * self._radius_ratio)
        self._setup_images()

        self._left_idx = exist_rect.left - self._radius
        self._top_idx = exist_rect.top - self._radius
        self._right_idx = exist_rect.right + self._radius
        self._bottom_idx = exist_rect.bottom + self._radius

    @property
    def radius(self) -> int:
        """
        半径

        Returns
        -------
        int
            半径
        """
        return self._radius
    
    @property
    def pop_left_right_idx(self) -> tuple[int, int]:
        """
        左の湧き領域のx座標と、右の湧き領域のx座標

        Returns
        -------
        tuple[int, int]
            左の湧き領域のx座標と、右の湧き領域のx座標
        """
        return self._left_idx, self._right_idx

    def _setup_images(self) -> None:
        """
        全イメージの初期化
        """
        image_size = (self._radius * 2, self._radius * 2)
        base_image = pygame.Surface(image_size, pygame.SRCALPHA)

        circle_center = (self._radius, self._radius)

        self._normal_image = base_image.copy()
        pygame.draw.circle(
            self._normal_image, GREEN, circle_center, self._radius
        )

        self._damaged_image = base_image.copy()
        pygame.draw.circle(
            self._damaged_image, D_GREEN, circle_center, self._radius
        )
    
    def provide(self, meteors: OverlappingReverse) -> MeteorArgs:
        """
        引数の提供

        Parameters
        ----------
        meteors : OverlappingReverse
            隕石グループ

        Returns
        -------
        MeteorArgs
            隕石の引数
        """
        pop_pos = self._build_pop_pos()
        speed = self._base_speed

        args = MeteorArgs(
            meteors,
            speed,
            self._normal_image,
            self._damaged_image,
            pop_pos
        )

        return args

    def _build_pop_pos(self) -> Vector2:
        """
        湧き座標の作成

        Returns
        -------
        Vector2
            湧き座標
        """
        pop_area = random.choice(self._pop_areas)

        if pop_area in ('left', 'right'):
            y = random.randint(self._top_idx, self._bottom_idx)

            if pop_area == 'left':
                x = self._left_idx

            elif pop_area == 'right':
                x = self._right_idx

        elif pop_area in ('top', 'bottom'):
            x = random.randint(self._left_idx, self._right_idx)

            if pop_area == 'top':
                y = self._top_idx

            elif pop_area == 'bottom':
                y = self._bottom_idx

        pop_pos = pygame.math.Vector2(x, y)

        return pop_pos
    

@dataclass(frozen=True)
class MeteorArgs:
    """
    隕石専用引数

    Attributes
    ----------
    group : OverlappingReverse
        隕石のグループ
    speed : int | float
        移動速度
    normal_image : Surface
        通常時イメージ
    damaged_image : Surface
        被ダメージ時イメージ
    pop_pos : Vector2
        湧き座標
    """
    
    group: OverlappingReverse
    speed: int | float
    normal_image: Surface
    damaged_image: Surface
    pop_pos: Vector2