from __future__ import annotations

import pygame
from pygame import Rect, Vector2, Surface

from utils.utils import DamagedSprite, SpriteAccessibleLayerdDirty
from constants import BLUE, D_BLUE


class EarthGroup(SpriteAccessibleLayerdDirty):
    """
    地球グループ
    """

    def __init__(self, battle_area_rect: Rect, fps: int):
        """
        コンストラクタ

        Parameters
        ----------
        battle_area_rect : Rect
            戦闘領域レクト

        fps: int
            FPS
        """
        super().__init__()

        Earth(self, battle_area_rect, fps)

    @property
    def sprite(self) -> Earth:
        """
        １つのスプライト

        Returns
        -------
        Earth
            地球スプライト
        """
        return super().sprite
    
    @property
    def health(self) -> int:
        """
        地球の残基

        Returns
        -------
        int
            地球の残基
        """
        return self.sprite.health
    
    @property
    def pos(self) -> Vector2:
        """
        地球の中心

        Returns
        -------
        Vector2
            地球の中心
        """
        return self.sprite.pos
    
    @property
    def rect(self) -> Rect:
        """
        レクト

        Returns
        -------
        Rect
            地球のレクト
        """
        return self.sprite.rect
    
    def reset(self, screen: Surface) -> None:
        """
        リセット

        次戦に向けた地球のリセット

        Parameters
        ----------
        screen : Surface
            配置先サーフェス
        """
        self.sprite.reset()

        self.draw(screen)


class Earth(DamagedSprite):
    """
    地球スプライト

    Attributes
    ----------
    _max_health : int
        最大残基
    _radius_ratio : float
        半径比率

    _health : int
        残基
    rect : Rect
        レクト
    _normal_image : Surface
        通常時イメージ
    _damaged_image : Surface
        被ダメージ時イメージ
    image : Surface
        イメージ
    _pos : Vector2
        中心座標
    _damage_sound : Sound
        ダメージを受けたときの効果音
    """
    
    _max_health: int = 5
    _radius_ratio: float = 0.05

    def __init__(self, group: EarthGroup, battle_area_rect: Rect, fps: int):
        """
        コンストラクタ

        Parameters
        ----------
        group : EarthGroup
            地球グループ
        battle_area_rect : Rect
            戦闘領域レクト
        fps: int
            FPS
        """
        super().__init__(group, fps)

        self.reset()

        radius = int(battle_area_rect.h * self._radius_ratio)
        diameter = radius * 2

        basic_image = pygame.Surface((diameter, diameter))
        self.rect = basic_image.get_rect()

        self._setup_normal_image(basic_image, radius)
        self._setup_damaged_image(basic_image, radius)

        self.image = self._normal_image

        self.rect.center = battle_area_rect.center

        self._pos = Vector2(self.rect.centerx, self.rect.centery)

        self._damage_sound = pygame.mixer.Sound(
            'assets/sounds/earth_damage.ogg'
        )

    @property
    def pos(self) -> Vector2:
        """
        中心座標の取得

        Vector2のメソッドが座標の更新に便利
        self.rect.centerは、tuple[int, int]

        Returns
        -------
        Vector2
            中心座標
        """
        return self._pos
    
    @property
    def health(self) -> int:
        """
        残基

        Returns
        -------
        int
            残基
        """
        return self._health

    def _setup_normal_image(self, basic_image: Surface, radius: int) -> None:
        """
        通常時イメージの初期化

        Parameters
        ----------
        basic_image : Surface
            基となるイメージ
        radius : int
            地球の半径
        """
        self._normal_image = basic_image.copy()
        pygame.draw.circle(self._normal_image, BLUE, self.rect.center, radius)

    def _setup_damaged_image(self, basic_image: Surface, radius: int) -> None:
        """
        被ダメージ時イメージの初期化

        Parameters
        ----------
        basic_image : Surface
            基となるイメージ
        radius : int
            地球の半径
        """
        self._damaged_image = basic_image.copy()
        pygame.draw.circle(
            self._damaged_image, D_BLUE, self.rect.center, radius
        )

    def update(self, damage: int = None) -> None:
        """
        更新

        Parameters
        ----------
        damage : int, optional
            被ダメージ
            ダメージを受けていなければ、デフォルト値のNone
        """
        if damage:
            self._health -= damage

            self._damage_sound.play()

            if self._health <= 0:
                pass

            else:
                self._damaged()
        
        else:
            self._update_damage_situation()

    def reset(self) -> None:
        """
        リセット
        """
        self._health = self._max_health

        self.dirty = 1