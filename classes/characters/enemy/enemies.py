import random
import pickle

import networkx as nx
import pygame
from pygame import Surface, Rect, Vector2
from pygame.mixer import Sound

from utils.group import (
    OverlappingReverse,
    KeepWithinReverse,
    OverlappingAreaRenderUpdates,
    KeepWithinRenderUpdates
)
from classes.characters.enemy.enemy import Enemy
from classes.characters.enemy.meteor import MeteorArgsProvider
from classes.characters.enemy.input_box.input_box import InputBoxArgsProvider
from assets.data.src import same_first_hira_tangos_dic, incompatible_hira_dic
from constants import DATA_PATH

class Enemies:
    """
    全ての敵

    Attributes
    ----------
    _add_seconds : int | float
        敵を追加する頻度の秒数

    _add_frames : int
        敵を追加する頻度のフレーム数
    _hira_tango_selecter : HiraTangoSelecter
        ひらがなの単語選択機
    _enemy_maker : EnemyMaker
        敵製作機
    _waiting_meteors : OverlappingReverse
        未入力隕石グループ
    _waiting_input_boxs : KeepWithinReverse
        未入力入力ボックスグループ
    _inputting_meteor : OverlappingAreaRenderUpdates
        入力中隕石グループ（単体）
    _inputting_input_box : KeepWithinRenderUpdates
        入力中入力ボックスグループ（単体）
    _enemies : list[Enemy]
        全敵のリスト
    _first_keys_dic : dict[str, Enemy]
        バリューはひらがなの単語、キーはバリューのローマ字の頭文字１文字である辞書
        頭文字の入力パターン数だけ、同一のバリューを持つペアが存在する
    _inputting_enemy : Enemy
        入力中の敵
    _correct_key_sound : Sound
        入力が正しかった場合の効果音
    _wrong_key_sound : Sound
        入力が間違っていた場合の効果音
    _correct_count : int
        正しい入力数
    _incorrect_count : int
        誤った入力数
    """

    _add_seconds: int | float = 2

    def __init__(self, battle_area_rect: Rect, fps: int):
        """
        コンストラクタ

        Parameters
        ----------
        battle_area_rect : Rect
            描画領域レクト
        fps : int
            FPS
        """
        self._add_frames = int(fps * self._add_seconds)

        self._hira_tango_selecter = HiraTangoSelecter()
        self._enemy_maker = EnemyMaker(battle_area_rect, fps)

        self._waiting_meteors = OverlappingReverse(battle_area_rect)
        self._waiting_input_boxs = KeepWithinReverse(battle_area_rect)

        self._inputting_meteor = OverlappingAreaRenderUpdates(battle_area_rect)
        self._inputting_input_box = KeepWithinRenderUpdates(battle_area_rect)

        self._enemies: list[Enemy] = []
        self._first_keys_dic: dict[str, Enemy] = {}
        self._inputting_enemy: Enemy = None

        self._correct_key_sound = pygame.mixer.Sound(
            'assets/sounds/correct_key.ogg'
        )
        self._wrong_key_sound = pygame.mixer.Sound(
            'assets/sounds/wrong_key.ogg'
        )

        self.reset()

    def add(self, frames: int, earth_pos: Vector2) -> None:
        """
        敵の追加

        Parameters
        ----------
        frames : int
            経過フレーム数
        earth_pos : Vector2
            地球の中心
        """
        if frames % self._add_frames == 0:
            hira_tango = self._hira_tango_selecter.select()
            enemy = self._enemy_maker.make(
                hira_tango,
                self._waiting_meteors,
                self._waiting_input_boxs,
                self._correct_key_sound,
                self._wrong_key_sound,
                earth_pos
            )

            self._enemies.append(enemy)

            self._extend_first_keys_dic(enemy)

    def _extend_first_keys_dic(self, enemy: Enemy) -> None:
        """
        first_keys_dicの拡張

        Parameters
        ----------
        enemy : Enemy
            first_keys_dicへの追加対象の敵
        """
        first_keys = enemy.accepting_keys

        for first_key in first_keys:
            self._first_keys_dic[first_key] = enemy

    def draw(self, screen: Surface) -> list[Rect]:
        """
        配置

        Parameters
        ----------
        screen : Surface
            配置先サーフェス

        Returns
        -------
        list[Rect]
            ダーティーレクト
        """
        should_draw_inputtings = self._should_draw_inputtings()

        meteor_dirty_rects = self._waiting_meteors.draw(screen)
        
        if should_draw_inputtings:
            inputting_dirty_rects = self._inputting_meteor.draw(screen)

            meteor_dirty_rects.extend(inputting_dirty_rects)

        input_box_dirty_rects = self._waiting_input_boxs.draw(screen)

        if should_draw_inputtings:
            inputting_dirty_rects = self._inputting_input_box.draw(screen)

            input_box_dirty_rects.extend(inputting_dirty_rects)

        dirty_rects = meteor_dirty_rects + input_box_dirty_rects

        return dirty_rects

    def _should_draw_inputtings(self) -> bool:
        """
        入力中の敵グループを描画するべきかの確認

        Returns
        -------
        bool
            描画するべきかどうか
        """
        should_draw = False

        sprites = self._inputting_meteor.sprites()
        lost_sprites = self._inputting_meteor.lostsprites

        if sprites or lost_sprites:
            should_draw = True

        return should_draw

    def update(
            self, key: str | None, earth_pos: Vector2, earth_rect: Rect
    ) -> tuple[int, int]:
        """
        更新

        Parameters
        ----------
        key : str | None
            １文字の入力
        earth_pos : Vector2
            地球の中心
        earth_rect : Rect
            地球のレクト

        Returns
        -------
        tuple[int, int]
            地球へのダメージと、敵撃破ポイント
        """
        point = 0

        if key:
            point = self._process_key(key)

        earth_damage = 0

        for enemy in self._enemies:
            collided = enemy.update(earth_pos, earth_rect)

            if collided:
                self._kill_enemy(enemy)

                earth_damage += 1

        return earth_damage, point
    
    def _process_key(self, key: str) -> int | None:
        """
        入力処理

        Parameters
        ----------
        key : str
            １文字の入力

        Returns
        -------
        int | None
            敵撃破ポイント
        """
        if self._inputting_enemy:
            result = self._inputting_enemy.process_key(key)

            if result:
                self._correct_count += 1

                if not isinstance(result, bool):
                    self._kill_enemy(self._inputting_enemy)

                    return result

            else:
                self._incorrect_count += 1

        elif key in self._first_keys_dic:
            self._inputting_enemy = self._first_keys_dic[key]

            self._process_for_new_inputting_enemy()

            self._inputting_enemy.process_key(key)

            self._correct_count += 1

        else:
            self._incorrect_count += 1

            self._wrong_key_sound.play()

    def _kill_enemy(self, enemy: Enemy) -> None:
        """
        敵の削除

        Parameters
        ----------
        enemy : Enemy
            削除対象の敵
        """
        if enemy == self._inputting_enemy:
            self._inputting_enemy = None

        else:
            self._contract_first_keys_dic(enemy.accepting_keys)
            self._hira_tango_selecter.deregulate(enemy.first_hira)

        self._enemies.remove(enemy)
        enemy.kill()

    def _contract_first_keys_dic(self, remove_keys: list[str]) -> None:
        """
        first_keys_dicの縮小

        Parameters
        ----------
        remove_keys : list[str]
            削除するキーのリスト
        """
        for key in remove_keys:
            del self._first_keys_dic[key]

    def _process_for_new_inputting_enemy(self) -> None:
        """
        新規入力対象への対応

        未入力グループからの削除
        first_keys_dicの縮小
        ひらがなの単語選択機の制限緩和
        入力中グループへの追加
        """
        self._inputting_enemy.kill()

        self._contract_first_keys_dic(self._inputting_enemy.accepting_keys)
        self._hira_tango_selecter.deregulate(self._inputting_enemy.first_hira)

        self._inputting_meteor.add(self._inputting_enemy.meteor)
        self._inputting_input_box.add(self._inputting_enemy.input_box)

    def clear(self, screen: Surface, bgd: Surface):
        """
        背景での上書き

        Parameters
        ----------
        screen : Surface
            配置先サーフェス
        bgd : Surface
            背景
        """
        self._waiting_meteors.clear(screen, bgd)
        self._inputting_meteor.clear(screen, bgd)
        self._waiting_input_boxs.clear(screen, bgd)
        self._inputting_input_box.clear(screen, bgd)

    def calc_accuracy(self) -> float:
        """
        正確性の算出

        Returns
        -------
        float
            正確性
        """
        inputs_num = self._correct_count + self._incorrect_count

        if inputs_num == 0:
            accuracy = 0
        else:
            accuracy = self._correct_count / inputs_num * 100
            accuracy = round(accuracy, 2)

        return accuracy
    
    def finish(self) -> None:
        """
        終了処理
        """
        for enemy in self._enemies.copy():
            self._kill_enemy(enemy)
    
    def reset(self) -> None:
        """
        リセット処理
        """
        self._correct_count = 0
        self._incorrect_count = 0


class HiraTangoSelecter:
    """
    ひらがなの単語選択機

    Attributes
    ----------
    _same_first_hira_tangos_dic : dict[str, tuple[str, ...]]
        キーはひらがな１文字、バリューはキーを頭文字に持つ
        全てのひらがなの単語である辞書

    _incompatible_hira_dic : dict[str, tuple[str, ...]]
        キーはひらがな１文字、バリューはキーのローマ字の頭文字が
        重複するひらがな１文字のタプルである辞書
    _selectable_first_hiras : list[str]
        選択可能なひらがな１文字のリスト
    _unselectable_first_hiras_dic : dict[str, int]
        キーは選択不可のひらがな１文字、バリューはキーの制限の強さを示す数である辞書
    """

    _same_first_hira_tangos_dic = same_first_hira_tangos_dic

    def __init__(self):
        """
        コンストラクタ
        """
        self._setup_incompatible_hira_dic(incompatible_hira_dic)

        self._selectable_first_hiras = list(
            self._same_first_hira_tangos_dic.keys()
        )
        self._unselectable_first_hiras_dic: dict[str, int] = {}

    def _setup_incompatible_hira_dic(
            self, incompatible_hira_dic: dict[str, tuple[str, ...]]
    ) -> None:
        """
        共存不可のひらがなの辞書の初期化

        Parameters
        ----------
        incompatible_hira_dic : dict[str, tuple[str, ...]]
            キーはひらがな１文字、バリューはキーのローマ字の頭文字が
            重複するひらがな１文字のタプルである辞書
        """
        self._incompatible_hira_dic: dict[str, tuple[str, ...]] = {}

        for hira, compatitors in incompatible_hira_dic.items():
            if hira in self._same_first_hira_tangos_dic:
                compatitors = (
                    compatitor
                    for compatitor in compatitors
                    if compatitor in self._same_first_hira_tangos_dic
                )

                self._incompatible_hira_dic[hira] = compatitors

    def select(self) -> str:
        """
        ひらがなの単語の選択

        Returns
        -------
        str
            ひらがなの単語
        """
        first_hira = random.choice(self._selectable_first_hiras)

        self._regulate_selection_targets(first_hira)

        if first_hira in self._incompatible_hira_dic:
            incompatible_hiras = self._incompatible_hira_dic[first_hira]
            for hira in incompatible_hiras:
                self._regulate_selection_targets(hira)

        selectable_tangos = self._same_first_hira_tangos_dic[first_hira]
        hira_tango = random.choice(selectable_tangos)

        return hira_tango

    def _regulate_selection_targets(self, hira: str) -> None:
        """
        選択対象の制限

        Parameters
        ----------
        hira : str
            制限対象のひらがな１文字
        """
        if hira not in self._unselectable_first_hiras_dic:
            self._unselectable_first_hiras_dic[hira] = 1

            self._selectable_first_hiras.remove(hira)

        else:
            self._unselectable_first_hiras_dic[hira] += 1

    def deregulate(self, first_hira: str) -> None:
        """
        選択対象の制限緩和

        Parameters
        ----------
        first_hira : str
            制限緩和対象のひらがな１文字
        """
        self._add_hira_to_selectable_first_hiras(first_hira)

        if first_hira in self._incompatible_hira_dic:
            incompatible_hiras = self._incompatible_hira_dic[first_hira]
            for hira in incompatible_hiras:
                self._add_hira_to_selectable_first_hiras(hira)

    def _add_hira_to_selectable_first_hiras(self, hira: str) -> None:
        """
        選択可能リストへの追加

        制限の状態次第では追加が持ち越される

        Parameters
        ----------
        hira : str
            追加対象のひらがな１文字
        """
        hira_num = self._unselectable_first_hiras_dic[hira]

        if hira_num == 1:
            self._selectable_first_hiras.append(hira)

            self._unselectable_first_hiras_dic.pop(hira)

        else:
            self._unselectable_first_hiras_dic[hira] -= 1


class EnemyMaker:
    """
    敵製作機

    Attributes
    ----------
    _fps : int
        FPS
    _hira_tango_graph_dic : dict[str, DiGraph]
        キーがひらがなの単語、バリューがキーのローマ字入力パターンのグラフである辞書
    _meteor_args_provider : MeteorArgsProvider
        隕石専用引数提供機
    _input_box_args_provider : InputBoxArgsProvider
        入力ボックス専用引数提供機
    """
    
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
        self._fps = fps

        tango_dic, graph_dic = EnemyMaker._build_hira_tango_dics()

        self._hira_tango_graph_dic = graph_dic

        self._meteor_args_provider = MeteorArgsProvider(exist_rect, fps)
        self._input_box_args_provider = InputBoxArgsProvider(
            exist_rect.h, tango_dic
        )
    
    @staticmethod
    def _build_hira_tango_dics() -> tuple[dict[str, str], dict[str, nx.DiGraph]]:
        """
        ひらがなの単語の辞書達の製作

        Returns
        -------
        tuple[dict[str, str], dict[str, nx.DiGraph]]
            両者の辞書のキーはひらがなの単語で共通
            前者のバリューは、キーの日本語表記
            後者のバリューは、キーのローマ字入力パターンのグラフ
        """
        word_data = EnemyMaker._read_word_data(DATA_PATH)

        hira_tango_tango_dic: dict[str, str] = {
            hira_tango: data['表記'] for hira_tango, data in word_data.items()
        }
        hira_tango_graph_dic: dict[str, nx.DiGraph] = {
            hira_tango: data['グラフ']
            for hira_tango, data in word_data.items()
        }

        return hira_tango_tango_dic, hira_tango_graph_dic

    @staticmethod
    def _read_word_data(
        word_data_path: str
    ) -> dict[str, dict[str, str | nx.DiGraph]]:
        """
        単語データの読み込み

        Parameters
        ----------
        word_data_path : str
            単語データが保存されているパス

        Returns
        -------
        dict[str, dict[str, str | nx.DiGraph]]
            キーはひらがなの単語、バリューはキーの情報の辞書である辞書
            情報の辞書はひらがなの単語の'表記'と'グラフ'を持つ
        """
        with open(word_data_path, 'rb') as f:
            word_data = pickle.load(f)

        return word_data
        
    def make(
            self,
            hira_tango: str,
            meteors: OverlappingReverse,
            input_boxs: KeepWithinReverse,
            correct_key_sound: Sound,
            wrong_key_sound: Sound,
            earth_center: Vector2
    ) -> Enemy:
        """
        敵の製作

        Parameters
        ----------
        hira_tango : str
            ひらがなの単語
        meteors : OverlappingReverse
            隕石のグループ
        input_boxs : KeepWithinReverse
            入力ボックスのグループ
        correct_key_sound : Sound
            入力が正しかった場合の効果音
        wrong_key_sound : Sound
            入力が間違っていた場合の効果音
        earth_center : Vector2
            地球の中心

        Returns
        -------
        Enemy
            敵
        """
        first_hira = hira_tango[0]
        graph = self._hira_tango_graph_dic[hira_tango]

        meteor_args = self._meteor_args_provider.provide(meteors)
        input_box_args = self._input_box_args_provider.provide(
            hira_tango, input_boxs, self._meteor_args_provider.radius
        )

        enemy = Enemy(
            first_hira,
            graph,
            correct_key_sound,
            wrong_key_sound,
            self._fps,
            meteor_args,
            input_box_args,
            earth_center,
            self._meteor_args_provider.pop_left_right_idx
        )

        return enemy