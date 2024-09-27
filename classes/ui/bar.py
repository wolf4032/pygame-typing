from pygame import Rect

class BarChildrenArgs:
    """
    バーの子要素専用引数

    Attributes
    ----------
    _w_margin : int
        余白幅
    _h : int
        高さ
    _mid_h : int
        中心の配置高さ
    """
    
    def __init__(self, bar_rect: Rect, w_margin_ratio: float, h_ratio: float):
        """
        コンストラクタ

        Parameters
        ----------
        bar_rect : Rect
            バーのレクト
        w_margin_ratio : float
            余白の幅の比率
        h_ratio : float
            高さ比率
        """
        self._w_margin = int(bar_rect.w * w_margin_ratio)
        self._h = int(bar_rect.h * h_ratio)
        self._mid_h = bar_rect.h // 2

    @property
    def h(self) -> int:
        """
        高さ

        Returns
        -------
        int
            高さ
        """
        return self._h
    
    @property
    def mid_h(self) -> int:
        """
        中心の配置高さ

        Returns
        -------
        int
            中心の配置高さ
        """
        return self._mid_h
    
    @property
    def w_margin(self) -> int:
        """
        余白の幅

        Returns
        -------
        int
            余白の幅
        """
        return self._w_margin