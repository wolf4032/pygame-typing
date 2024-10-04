import networkx as nx

from pygame import Vector2, Rect
from pygame.mixer import Sound

from classes.characters.enemy.meteor import MeteorArgs, Meteor
from classes.characters.enemy.input_box.input_box import InputBoxArgs, InputBox

StartEndNode = tuple[str, int]
NodeRomajis = tuple[str, ...]
RomajiNode = tuple[NodeRomajis, int]
Nodes = list[StartEndNode | RomajiNode]


class Enemy:
    """
    敵

    Attributes
    ----------
    _first_hira : str
        頭文字のひらがな
    _key_processor : KeyProcessor
        入力処理機
    _meteor : Meteor
        隕石
    _input_box : InputBox
        入力ボックス
    """

    def __init__(
            self,
            first_hira: str,
            graph: nx.DiGraph,
            correct_key_sound: Sound,
            wrong_key_sound: Sound,
            fps: int,
            meteor_args: MeteorArgs,
            input_box_args: InputBoxArgs,
            earth_center: Vector2,
            meteor_pop_left_right_idx: tuple[int, int]
    ):
        """
        コンストラクタ

        Parameters
        ----------
        first_hira : str
            単語の先頭のひらがな１文字
        graph : nx.DiGraph
            単語のローマ字入力の全パターンを網羅した有向グラフ
            開始ノードと終了ノード以外は、ノードに対応したローマ字入力のタプルと、
            そのノードのひらがなの終了位置が、単語のどこであるかを示す整数を持つ
        correct_key_sound : Sound
            入力が正しかった場合の効果音
        wrong_key_sound : Sound
            入力が間違っていた場合の効果音
        fps : int
            FPS
        meteor_args : MeteorArgs
            隕石専用引数
        input_box_args : InputBoxArgs
            入力ボックス専用引数
        earth_center : Vector2
            地球の中心座標
        meteor_pop_left_right_idx : tuple[int, int]
            隕石湧き領域の左上の座標
        """
        self._first_hira = first_hira

        self._key_processor = KeyProcessor(
            graph, correct_key_sound, wrong_key_sound
        )

        self._meteor = Meteor(meteor_args, fps)
        assumed_keys = self._key_processor.assumed_keys
        self._input_box = InputBox(
            input_box_args,
            assumed_keys,
            earth_center,
            self._meteor.speed,
            self._meteor.pos,
            meteor_pop_left_right_idx
        )

    @property
    def accepting_keys(self) -> list[str]:
        """
        入力受け付け中のkey１文字のリスト

        Returns
        -------
        list[str]
            入力受付中のkey１文字のリスト
        """
        return self._key_processor.accepting_keys
    
    @property
    def meteor(self) -> Meteor:
        """
        隕石

        Returns
        -------
        Meteor
            隕石
        """
        return self._meteor
    
    @property
    def input_box(self) -> InputBox:
        """
        入力ボックス

        Returns
        -------
        InputBox
            入力ボックス
        """
        return self._input_box
    
    @property
    def first_hira(self) -> str:
        """
        頭文字のひらがな

        Returns
        -------
        str
            頭文字のひらがな
        """
        return self._first_hira
    
    def process_key(self, key: str) -> int | bool:
        """
        入力処理

        Parameters
        ----------
        key : str
            １文字の入力

        Returns
        -------
        int | bool
            正しい入力で敵を撃破したなら、敵撃破ポイント
            正しい入力だがまだ撃破していないなら、True
            入力が誤りならFalse
        """
        is_key_correct = True

        confirmed_keys, assumed_keys = self._key_processor.check_key(key)

        if assumed_keys:
            self._input_box.update_by_key(confirmed_keys, assumed_keys)
            self._meteor.update_by_key()

            return is_key_correct

        elif assumed_keys == '':
            self.kill()

            return self._meteor.point
        else:
            is_key_correct = False

            return is_key_correct

    def update(
            self,
            target_pos: Vector2,
            earth_rect: Rect
    ) -> None | bool:
        """
        更新

        Parameters
        ----------
        target_pos : Vector2
            移動先の方向にある座標
        earth_rect : Rect
            地球のレクト

        Returns
        -------
        None | bool
            地球と衝突したらTrue
        """
        collided = self._meteor.update(target_pos, earth_rect)

        if collided:
            return collided

        self._input_box.update(target_pos)

    def kill(self) -> None:
        """
        削除処理
        """
        self._meteor.kill()
        self._input_box.kill()


class KeyProcessor:
    """
    入力処理機

    Attributes
    ----------
    _start_node : tuple[str, int]
        開始ノード
    _end_node : tuple[str, int]
        終了ノード

    _graph : nx.DiGraph
        単語のローマ字入力の全パターンを網羅した有向グラフ
        開始ノードと終了ノード以外は、ノードに対応したローマ字入力のタプルと、
        そのノードのひらがなの終了位置が、単語のどこであるかを示す整数を持つ

        各ノードは一塊のローマ字入力を担当し、例えば、'っしょ'という日本語に対して、
        'っ'、'っし'、'っしょ'のいずれの入力を実行しても誤りではなく、
        このグラフは取り得る全ての入力パターンの分岐を網羅している
    _keys_for_now_node : str
        入力途中のノードの入力済み文字列
    _confirmed_nodes_keys : str
        入力済みの全ノードに入力された文字列
    _now_nodes : list[StartEndNode | RomajiNode]
        入力中のノードのリスト

        'っしょ'に対する'っ'、'っし'、'っしょ'のように、プレイヤーの入力に対して、
        現状入力対象になり得る全ノードを内包している
    _assumed_keys : str
        入力済みの文字列に続くであろう文字列
    _allow_n : bool
        'n'が入力された場合、次の入力として、'n'を正解とするかどうかのフラグ
    _accepting_keys : list[str]
        正解である１文字の入力のリスト
    _correct_key_sound : Sound
        入力が正しかった場合の効果音
    _wrong_key_sound : Sound
        入力が間違っていた場合の効果音
    """
    
    _start_node = ('start', 0)
    _end_node = ('end', -1)

    def __init__(
            self,
            graph: nx.DiGraph,
            correct_key_sound: Sound,
            wrong_key_sound: Sound
    ):
        """
        コンストラクタ

        Parameters
        ----------
        graph : nx.DiGraph
            単語のローマ字入力の全パターンを網羅した有向グラフ
            開始ノードと終了ノード以外は、ノードに対応したローマ字入力のタプルと、
            そのノードのひらがなの終了位置が、単語のどこであるかを示す整数を持つ
        correct_key_sound : Sound
            入力が正しかった場合の効果音
        wrong_key_sound : Sound
            入力が間違っていた場合の効果音
        """
        self._graph = graph
        self._keys_for_now_node = ''
        self._confirmed_nodes_keys = ''

        self._update_now_nodes(self._start_node)
        self._update_assumed_keys()

        self._allow_n = False
        self._update_accepting_keys()

        self._correct_key_sound = correct_key_sound
        self._wrong_key_sound = wrong_key_sound

    @property
    def accepting_keys(self) -> list[str]:
        """
        正解である１文字の入力のリスト

        Returns
        -------
        list[str]
            正解である１文字の入力のリスト
        """
        return self._accepting_keys
    
    @property
    def assumed_keys(self) -> str:
        """
        入力済みの文字列に続くであろう文字列

        入力が開始されるまでは、最短の入力パターン

        Returns
        -------
        str
            入力済みの文字列に続くであろう文字列
        """
        return self._assumed_keys
    
    def _update_now_nodes(
            self, pre_node: RomajiNode | StartEndNode
    ) -> None:
        """
        入力中のノードのリストの更新

        Parameters
        ----------
        pre_node : RomajiNode | StartEndNode
            入力が完了したノード
        """
        self._now_nodes: Nodes = list(self._graph.successors(pre_node))

        if self._now_nodes == [self._end_node]:
            self._assumed_keys = ''

    def _update_assumed_keys(self) -> None:
        """
        入力予測文字列の更新
        """
        shortest_path = self._find_shortest_path()

        if self._keys_for_now_node:
            now_node_romajis: NodeRomajis = shortest_path[0][0]

            for romaji in now_node_romajis:
                if romaji.startswith(self._keys_for_now_node):
                    self._build_assumed_keys(shortest_path, romaji)

                    break

        else:
            self._build_assumed_keys(shortest_path)

    def _update_accepting_keys(self) -> None:
        """
        正解入力リストの更新

        list(accepting_keys)としているのは、_allow_n = Trueになった場合の、
        .append('n')を可能とするため
        """
        accepting_idx = len(self._keys_for_now_node)
        accepting_keys = {
            romaji[accepting_idx] for node in self._now_nodes
            for romaji in node[0]
            if romaji.startswith(self._keys_for_now_node)
        }

        self._accepting_keys = list(accepting_keys)

        if self._allow_n:
            self._accepting_keys.append('n')

    def _find_shortest_path(self) -> Nodes:
        """
        最短入力経路の探索

        Returns
        -------
        Nodes
            最短入力経路のノードのリスト
        """
        shortest_path_len = float('inf')

        for node in self._now_nodes:
            path = nx.shortest_path(self._graph, node, self._end_node)
            path_len = len(path)

            if path_len < shortest_path_len:
                shortest_path = path
                shortest_path_len = path_len

        return shortest_path
    
    def _build_assumed_keys(self, path: Nodes, romaji: str = None) -> None:
        """
        入力予測文字列の作成

        現在入力中のノードの全ローマ字入力パターンの中で、
        入力済みの文字列と同じ始まり方のローマ字が渡される
        渡されたローマ字のうち、未入力の部分から入力予測文字列が始まるようにする

        ローマ字が渡されなかった場合、現在のノードは入力済みとみなし、
        入力予測文字列を以降の経路のノードをもとに、最短の文字列で作成する

        Parameters
        ----------
        path : Nodes
            ある入力パターンのノードのリスト
        romaji : str, optional
            ある一塊のローマ字、デフォルト値はNone
        """
        if romaji:
            now_node_keys = romaji.replace(self._keys_for_now_node, '', 1)

            next_nodes_key_lst = [node[0][0] for node in path[1:-1]]
            next_nodes_keys = ''.join(next_nodes_key_lst)

            self._assumed_keys = now_node_keys + next_nodes_keys

        else:
            next_nodes_key_lst = [node[0][0] for node in path[:-1]]

            self._assumed_keys = ''.join(next_nodes_key_lst)

    def check_key(self, key: str) -> tuple[str | None, str | None]:
        """
        入力の確認

        返り値のassumed_keys
            ただの文字列　→　入力成功且つ、継続
            空文字　→　入力成功且つ、終了
            None　→　誤った入力

        Returns
        -------
        tuple[str | None, str | None]
            入力が正しければ、入力済み文字列と、入力予測文字列を返す
            入力が誤りであれば、Noneが二つのタプルを返す
        """
        if key in self._accepting_keys:
            dummy_keys = self._keys_for_now_node + key

            if self._allow_n:
                self._allow_n = False
                self._accepting_keys.pop()

                if dummy_keys == 'n':
                    self._confirmed_nodes_keys += dummy_keys
                    
                    return self._confirmed_nodes_keys, self._assumed_keys

            self._process_dummy_keys(dummy_keys)

            confirmed_keys = (
                self._confirmed_nodes_keys + self._keys_for_now_node
            )
            assumed_keys = self._assumed_keys

            self._correct_key_sound.play()

        else:
            confirmed_keys = None
            assumed_keys = None

            self._wrong_key_sound.play()

        return confirmed_keys, assumed_keys
        
    def _process_dummy_keys(self, dummy_keys: str) -> None:
        """
        仮入力の処理

        以降の入力に備える

        Parameters
        ----------
        dummy_keys : str
            仮入力

            現在入力中のノードに対して入力済みの文字列に、
            新たに入力した１文字を付け足したもの
        """
        now_nodes = []

        for now_node in self._now_nodes:
            romajis: NodeRomajis = now_node[0]

            if any(romaji == dummy_keys for romaji in romajis):
                if 'nn' in romajis:
                    self._allow_n = True

                self._prepare_for_next_nodes(dummy_keys, now_node)

                now_nodes.clear()

                break

            elif any(romaji.startswith(dummy_keys) for romaji in romajis):
                now_nodes.append(now_node)

        if now_nodes:
            self._process_for_now_nodes(dummy_keys, now_nodes)

        self._update_accepting_keys()
        self._update_assumed_keys()

    def _prepare_for_next_nodes(
            self, dummy_keys: str, pre_node: RomajiNode
    ) -> None:
        """
        次のノードの準備

        Parameters
        ----------
        dummy_keys : str
            仮入力
        pre_node : RomajiNode
            入力が完了したノード
        """
        self._confirmed_nodes_keys += dummy_keys
        self._update_now_nodes(pre_node)
        self._keys_for_now_node = ''

    def _process_for_now_nodes(
            self, dummy_keys: str, now_nodes: list[RomajiNode]
    ) -> None:
        """
        入力中ノード継続処理

        Parameters
        ----------
        dummy_keys : str
            仮入力
        now_nodes : list[RomajiNode]
            入力中のノードのリスト
        """
        self._keys_for_now_node = dummy_keys
        self._now_nodes = now_nodes