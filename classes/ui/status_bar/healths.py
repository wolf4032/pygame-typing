import pygame
from pygame.sprite import LayeredDirty
from pygame import Rect, Surface

from classes.ui.bar import BarChildrenArgs
from constants import BLUE


class HealthsGroup(LayeredDirty):
    """
    残基グループ

    Attributes
    ----------
    _sprites_w_margin_ratio : float
        子要素間の余白比率

    _health_maker : HealthMaker
        残基スプライト製作機
    _sprites_w_margin : int
        子要素間の余白
    _left : int
        左端のx座標
    """

    _sprites_w_margin_ratio: float = 0.1

    def __init__(self, args: BarChildrenArgs, score_right: int):
        """
        コンストラクタ

        Parameters
        ----------
        args : BarChildrenArgs
            専用引数
        score_right : int
            スコアの右端のx座標
        """
        super().__init__()

        self._health_maker = HealthMaker(args.h, args.mid_h)
        self._sprites_w_margin = int(args.h * self._sprites_w_margin_ratio)
        self._left = score_right + args.w_margin

    @property
    def right(self) -> int:
        """
        右端のx座標

        Returns
        -------
        int
            右端のx座標
        """
        sprites_num = len(self.sprites())
        margin_sum = self._sprites_w_margin * (sprites_num - 1)

        w = self._health_maker.rect.w * sprites_num + margin_sum

        right = self._left + w

        return right
    
    def reset(self, health: int) -> None:
        """
        リセット

        Parameters
        ----------
        health : int
            残基（最大残基）
        """
        self.empty()

        self._max_health = health
        self._health = health

        left = self._left
        
        for i in range(self._health, 0, -1):
            self._health_maker.make(self, i, left)

            left += self._health_maker.rect.w + self._sprites_w_margin

    def update(self, damage: int) -> None:
        """
        更新

        Parameters
        ----------
        damage : int
            ダメージ（隕石衝突数）
        """
        self._health -= damage

        super().update(self._health)


class HealthMaker:
    """
    残基スプライト製作機

    Attributes
    ----------
    rect : Rect
        レクト
    _filled_image : Surface
        被ダメージ前イメージ
    _empty_image : Surface
        被ダメージ後イメージ
    """

    def __init__(self, h: int, mid_h: int):
        """
        コンストラクタ

        Parameters
        ----------
        h : int
            残基の高さ
        mid_h : int
            残基の中心の配置高さ
        """
        self.rect = Rect(0, 0, h, h)
        base_image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        radius = h // 2

        self._setup_filled_image(base_image, radius)
        self._setup_empty_image(base_image, radius)

        self.rect.centery = mid_h

    def _setup_filled_image(self, base_image: Surface, radius: int) -> None:
        """
        被ダメージ前イメージ初期化

        Parameters
        ----------
        base_image : Surface
            基となるイメージ
        radius : int
            半径
        """
        self._filled_image = base_image.copy()

        pygame.draw.circle(self._filled_image, BLUE, self.rect.center, radius)

    def _setup_empty_image(self, base_image: Surface, radius: int) -> None:
        """
        被ダメージ後イメージ初期化

        Parameters
        ----------
        base_image : Surface
            基となるイメージ
        radius : int
            半径
        """
        self._empty_image = base_image.copy()

        w = int(radius * 0.1)

        pygame.draw.circle(
            self._empty_image, BLUE, self.rect.center, radius, w
        )

    def make(self, group: HealthsGroup, health: int, left: int) -> None:
        """
        残基スプライトの作成

        Parameters
        ----------
        group : HealthsGroup
            残基スプライトの所属グループ
        health : int
            担当残基
        left : int
            左端のx座標
        """
        health = Health(
            group,
            health,
            self._filled_image,
            self._empty_image,
            self.rect,
            left
        )


class Health(pygame.sprite.DirtySprite):
    """
    残基スプライト

    Attributes
    ----------
    _health : int
        残基
    image : Surface
        イメージ
    _empty_image : Surface
        被ダメージ後イメージ
    rect : Rect
        レクト
    """
    
    def __init__(
            self,
            group: HealthsGroup,
            health: int,
            filled_image: Surface,
            empty_image: Surface,
            rect: Rect,
            left: int
    ):
        """
        コンストラクタ

        Parameters
        ----------
        group : HealthsGroup
            所属グループ
        health : int
            担当残基
        filled_image : Surface
            被ダメージ前イメージ
        empty_image : Surface
            被ダメージ後イメージ
        rect : Rect
            レクト
        left : int
            左端のx座標
        """
        super().__init__(group)
        self._health = health

        self.image = filled_image
        self._empty_image = empty_image
        self.rect = rect.copy()
        self.rect.left = left

    def update(self, health: int) -> None:
        """
        更新

        Parameters
        ----------
        health : int
            残基

        Returns
        -------
        None
            既に被ダメージ後の処理が行われていた場合、
            return Noneでメソッドを終了する
        """
        if self.image == self._empty_image:
            return None
        
        if self._health > health:
            self.image = self._empty_image
            self.dirty = 1