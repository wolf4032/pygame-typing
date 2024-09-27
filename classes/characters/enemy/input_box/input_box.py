from __future__ import annotations
from dataclasses import dataclass

import pygame
from pygame import Vector2

from constants import WHITE, ORANGE
from classes.characters.enemy.input_box.tango import (
    Tango, TangoArgsProvider, TangoArgs
)
from classes.characters.enemy.input_box.word.word import (
    Word, WordArgsProvider, WordArgs
)
from classes.characters.enemy.input_box.box_font import BoxFont
from utils.utils import ArgsProvider
from utils.group import KeepWithinReverse


class InputBox(pygame.sprite.Sprite):
    """
    入力ボックススプライト

    Attributes
    ----------
    _frame_w_ratio : float
        枠比率

    _speed : int | float
        移動速度
    _is_waiting : Literal[True]
        入力待機中フラグ
    _should_check_tango_w : Literal[True]
        日本語表記の長さを調べるべきかどうかのフラグ
    _tango : Tango
        日本語表記のスプライト
    _word : Word
        ローマ字のスプライト
    _size : list[int]
        イメージのサイズ
    _pos : Vector2
        中心位置
    _h : int
        入力中高さ
    _w_margin : int
        幅の余白
    _frame_w : int
        枠幅
    image : Surface
        イメージ
    rect : Rect
        レクト
    """

    _frame_w_ratio = 0.05

    def __init__(
            self,
            args: InputBoxArgs,
            assumed_keys: str,
            earth_center: Vector2,
            meteor_speed: int | float,
            meteor_center: Vector2,
            meteor_pop_left_right_idx: tuple[int, int]
    ):
        """
        コンストラクタ

        Parameters
        ----------
        args : InputBoxArgs
            専用引数
        assumed_keys : str
            入力予測文字列
        earth_center : Vector2
            地球の中心
        meteor_speed : int | float
            隕石の移動速度
        meteor_center : Vector2
            隕石の中心
        meteor_pop_left_right_idx : tuple[int, int]
            隕石湧き領域の左上の座標
        """
        super().__init__(args.group)

        self._speed = meteor_speed
        self._is_waiting = True
        self._should_check_tango_w = True

        self._tango = Tango(args.tango_args)
        self._word = Word(args.word_args, assumed_keys)

        self._setup_size(args.initial_h, args.initial_w_margin)
        self._setup_pos(
            earth_center,
            meteor_center,
            args.meteor_radius,
            meteor_pop_left_right_idx
        )
        
        self._h = args.h
        self._w_margin = args.w_margin
        initial_frame_w = int(args.initial_h * self._frame_w_ratio)
        self._frame_w = int(self._h * self._frame_w_ratio)

        self.image = pygame.Surface(self._size)
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, WHITE, self.rect, initial_frame_w)
        self.rect.center = self._pos
        self._blit_font(self._tango)
        self._blit_font(self._word)

    def _setup_size(self, initial_h: int, initial_w_margin: int) -> None:
        """
        サイズの初期化

        Parameters
        ----------
        initial_h : int
            初期高さ
        initial_w_margin : int
            初期の幅の余白
        """
        self._size = [0, initial_h]
        self._update_width(initial_w_margin)

    def _setup_pos(
            self,
            earth_center: Vector2,
            meteor_center: Vector2,
            meteor_radius: int,
            meteor_pop_left_right_idx: tuple[int, int]
    ) -> None:
        """
        位置の初期化

        Parameters
        ----------
        earth_center : Vector2
            地球の中心
        meteor_center : Vector2
            隕石の中心
        meteor_radius : int
            隕石の半径
        meteor_pop_left_right_idx : tuple[int, int]
            隕石湧き領域の左上の座標
        """
        meteor_x = meteor_center.x
        box_w, box_h = self._size

        if meteor_x in meteor_pop_left_right_idx:
            meteor_to_box_distance = meteor_radius + box_w // 2

        else:
            meteor_to_box_distance = meteor_radius + box_h // 2

        direction = (meteor_center - earth_center).normalize()

        self._pos = meteor_center + direction * meteor_to_box_distance

    def _blit_font(self, font: BoxFont) -> None:
        """
        文字列スプライトの配置

        Parameters
        ----------
        font : BoxFont
            文字列スプライト
        """
        font.update_rect_center(self.rect)
        self.image.blit(font.image, font.rect)

    def update(self, target_pos: Vector2) -> None:
        """
        更新

        Parameters
        ----------
        target_pos : Vector2
            移動先の方向にある座標
        """
        self._move(target_pos)

    def _move(self, target_pos: Vector2) -> None:
        """
        移動

        Parameters
        ----------
        target_pos : Vector2
            移動先座標
        """
        self._pos = self._pos.move_towards(target_pos, self._speed)
        
        self.rect.center = self._pos

    def update_by_key(self, confirmed_keys: str, assumed_keys: str) -> None:
        """
        入力による更新

        Parameters
        ----------
        confirmed_keys : str
            入力済み文字列
        assumed_keys : str
            入力予測文字列
        """
        if self._is_waiting:
            self._tango.update_by_key()
            self._size[1] = self._h

        self._word.update_by_key(confirmed_keys, assumed_keys)

        self._update_image()

        if self._is_waiting:
            self._is_waiting = False

    def _update_image(self) -> None:
        """
        イメージの更新
        """
        is_w_updated = self._update_width(self._w_margin)

        if is_w_updated:
            self.image = pygame.Surface(self._size)

            self.rect = self.image.get_rect()
            pygame.draw.rect(self.image, ORANGE, self.rect, self._frame_w)

            self._blit_font(self._tango)

        self._blit_font(self._word)

    def _update_width(self, w_margin: int) -> bool:
        """
        幅の更新

        Parameters
        ----------
        w_margin : int
            幅の余白

        Returns
        -------
        bool
            更新されたかどうか
        """
        updated = False

        base_w = self._word.rect.w

        if self._should_check_tango_w:
            tango_w = self._tango.rect.w

            if tango_w > base_w:
                if self._is_waiting:
                    base_w = tango_w

                else:
                    return updated
                
            else:
                self._should_check_tango_w = False

        w = base_w + w_margin

        if w != self._size[0]:
            self._size[0] = w
            
            updated = True

        return updated
    

class InputBoxArgsProvider(ArgsProvider):
    """
    入力ボックス専用引数提供機

    Attributes
    ----------
    _magnification_power : float
        拡大率
    _h_ratio : float
        高さ比率
    _margin_ratio : float
        余白比率

    _initial_h : int
        初期高さ
    _h : int
        入力中高さ
    _initial_w_margin : int
        初期の幅の余白
    _w_margin : int
        入力中の幅の余白
    _word_args : WordArgs
        ローマ字スプライト専用引数
    _tango_args_provider : TangoArgsProvider
        日本語表記スプライト専用引数提供機
    """

    _magnification_power = 1.3
    _h_ratio = 0.08
    _margin_ratio = 0.04

    def __init__(
            self, exist_rect_h: int, tango_dic: dict[str, str]
    ):
        """
        コンストラクタ

        Parameters
        ----------
        exist_rect_h : int
            描画領域レクトの高さ
        tango_dic : dict[str, str]
            キーがひらがな、バリューが漢字やカタカナなどの日本語表記である辞書
        """
        self._setup_args(exist_rect_h)
        self._setup_word_args(exist_rect_h)

        self._tango_args_provider = TangoArgsProvider(
            exist_rect_h, self._magnification_power, tango_dic
        )

    def _setup_args(self, exist_rect_h: int) -> None:
        """
        引数の初期化

        Parameters
        ----------
        exist_rect_h : int
            描画領域レクトの高さ
        """
        self._initial_h = int(exist_rect_h * self._h_ratio)
        self._h = int(self._initial_h * self._magnification_power)

        self._initial_w_margin = int(exist_rect_h * self._margin_ratio)
        self._w_margin = int(
            self._initial_w_margin * self._magnification_power
        )

    def _setup_word_args(self, exist_rect_h: int) -> None:
        """
        ローマ字スプライト専用引数の初期化

        Parameters
        ----------
        exist_rect_h : int
            描画領域レクトの高さ
        """
        args_provider = WordArgsProvider(
            exist_rect_h, self._magnification_power
        )
        self._word_args = args_provider.provide()
    
    def provide(
            self,
            hira_tango: str,
            input_boxs: KeepWithinReverse,
            meteor_radius: int
    ) -> InputBoxArgs:
        """
        引数の提供

        Parameters
        ----------
        hira_tango : str
            ひらがなの単語
        input_boxs : KeepWithinReverse
            入力ボックスのグループ
        meteor_radius : int
            隕石の半径

        Returns
        -------
        InputBoxArgs
            入力ボックスの引数
        """
        tango_args = self._tango_args_provider.provide(hira_tango)

        args = InputBoxArgs(
            input_boxs,
            tango_args,
            self._word_args,
            self._initial_h,
            self._h,
            self._initial_w_margin,
            self._w_margin,
            meteor_radius
        )

        return args


@dataclass(frozen=True)
class InputBoxArgs:
    """
    入力ボックス専用引数

    Attributes
    ----------
    group : KeepWithinReverse
        入力ボックスのグループ
    tango_args : TangoArgs
        日本語表記スプライト専用引数
    word_args : WordArgs
        ローマ字スプライト専用引数
    initial_h : int
        初期高さ
    h : int
        入力中高さ
    initial_w_margin : int
        初期の幅の余白
    w_margin : int
        入力中の幅の余白
    meteor_radius : int
        隕石の半径
    """
    
    group: KeepWithinReverse
    tango_args: TangoArgs
    word_args: WordArgs
    initial_h: int
    h: int
    initial_w_margin: int
    w_margin: int
    meteor_radius: int