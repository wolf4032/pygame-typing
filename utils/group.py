import pygame
from pygame import Rect, Surface

from utils.utils import Utils


class OverlappingAreaRenderUpdates(pygame.sprite.RenderUpdates):
    """
    描画領域内限定配置グループ

    コンストラクタに渡されたdraw_rect内に重なっている部分だけを配置するグループ

    Attributes
    ----------
    _draw_rect : Rect
        描画領域レクト
    """

    def __init__(self, draw_rect: Rect, *sprites):
        """
        コンストラクタ

        Parameters
        ----------
        draw_rect : Rect
            描画領域
        """
        super().__init__(*sprites)

        self._draw_rect = draw_rect

    def draw(
            self,
            surface: Surface,
            bgsurf: Surface = None,
            special_flags: int = 0
    ) -> list[Rect]:
        """
        配置

        描画領域内の部分だけ配置

        Parameters
        ----------
        surface : Surface
            配置先サーフェス
        bgsurf : Surface, optional
            背景サーフェス, by default None
        special_flags : int, optional
            スペシャルフラグ, by default 0

        Returns
        -------
        list[Rect]
            ダーティーレクト
        """
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        for sprite in self.sprites():
            old_rect = self.spritedict[sprite]
            
            clipped_rect = sprite.rect.clip(self._draw_rect)
            if clipped_rect.w == 0:
                continue

            dest = clipped_rect.topleft
            area = Utils.build_new_base_surface_area(clipped_rect, sprite.rect)
            new_rect = surface_blit(sprite.image, dest, area)

            if old_rect:
                if new_rect.colliderect(old_rect):
                    dirty_append(new_rect.union(old_rect))
                else:
                    dirty_append(new_rect)
                    dirty_append(old_rect)
            else:
                dirty_append(new_rect)
            self.spritedict[sprite] = new_rect
        return dirty
    

class OverlappingReverse(OverlappingAreaRenderUpdates):
    """
    描画領域内限定逆順配置グループ

    コンストラクタに渡されたdraw_rect内に重なっている部分だけを配置するグループ
    グループへの追加が新しいスプライトから順に配置される
    """

    def draw(
            self,
            surface: Surface,
            bgsurf: Surface = None,
            special_flags: int = 0
    ) -> list[Rect]:
        """
        配置

        描画領域内の部分だけ逆順に配置

        Parameters
        ----------
        surface : Surface
            配置先サーフェス
        bgsurf : Surface, optional
            背景サーフェス, by default None
        special_flags : int, optional
            スペシャルフラグ, by default 0

        Returns
        -------
        list[Rect]
            ダーティーレクト
        """
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        for sprite in Utils.reverse_sprites(self.spritedict):
            old_rect = self.spritedict[sprite]
            
            clipped_rect = sprite.rect.clip(self._draw_rect)
            if clipped_rect.w == 0:
                continue

            dest = clipped_rect.topleft
            area = Utils.build_new_base_surface_area(clipped_rect, sprite.rect)
            new_rect = surface_blit(sprite.image, dest, area)

            if old_rect:
                if new_rect.colliderect(old_rect):
                    dirty_append(new_rect.union(old_rect))
                else:
                    dirty_append(new_rect)
                    dirty_append(old_rect)
            else:
                dirty_append(new_rect)
            self.spritedict[sprite] = new_rect
        return dirty
    

class KeepWithinRenderUpdates(pygame.sprite.RenderUpdates):
    """
    描画領域内強制収容グループ

    コンストラクタに渡されたdraw_rect内に収まるように、スプライトを移動させてから
    配置するグループ

    Attributes
    ----------
    _draw_rect : Rect
        描画領域レクト
    """

    def __init__(self, draw_rect: Rect, *sprites):
        super().__init__(*sprites)

        self._draw_rect = draw_rect

    def draw(
            self,
            surface: Surface,
            bgsurf: Surface = None,
            special_flags: int = 0
    ) -> list[Rect]:
        """
        配置

        描画領域内に収まるように移動させてから配置
        sprite.rect.clamp_ip(self._draw_rect)により、メソッド終了後も移動したまま

        Parameters
        ----------
        surface : Surface
            配置先サーフェス
        bgsurf : Surface, optional
            背景サーフェス, by default None
        special_flags : int, optional
            スペシャルフラグ, by default 0

        Returns
        -------
        list[Rect]
            ダーティーレクト
        """
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        for sprite in self.sprites():
            old_rect = self.spritedict[sprite]
            sprite.rect.clamp_ip(self._draw_rect)
            new_rect = surface_blit(sprite.image, sprite.rect, None, special_flags)
            if old_rect:
                if new_rect.colliderect(old_rect):
                    dirty_append(new_rect.union(old_rect))
                else:
                    dirty_append(new_rect)
                    dirty_append(old_rect)
            else:
                dirty_append(new_rect)
            self.spritedict[sprite] = new_rect
        return dirty
    

class KeepWithinReverse(KeepWithinRenderUpdates):
    """
    描画領域内強制収容グループ

    コンストラクタに渡されたdraw_rect内に収まるように、スプライトを移動させてから
    配置するグループ
    グループへの追加が新しいスプライトから順に配置される
    """
    
    def draw(
            self,
            surface: Surface,
            bgsurf: Surface = None,
            special_flags: int = 0
    ) -> list[Rect]:
        """
        配置

        逆順に、描画領域内に収まるように移動させてから配置
        sprite.rect.clamp_ip(self._draw_rect)により、メソッド終了後も移動したまま

        Parameters
        ----------
        surface : Surface
            配置先サーフェス
        bgsurf : Surface, optional
            背景サーフェス, by default None
        special_flags : int, optional
            スペシャルフラグ, by default 0

        Returns
        -------
        list[Rect]
            ダーティーレクト
        """
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        for sprite in Utils.reverse_sprites(self.spritedict):
            old_rect = self.spritedict[sprite]

            sprite.rect.clamp_ip(self._draw_rect)

            new_rect = surface_blit(
                sprite.image, sprite.rect, None, special_flags
            )
            if old_rect:
                if new_rect.colliderect(old_rect):
                    dirty_append(new_rect.union(old_rect))
                else:
                    dirty_append(new_rect)
                    dirty_append(old_rect)
            else:
                dirty_append(new_rect)
            self.spritedict[sprite] = new_rect
        return dirty