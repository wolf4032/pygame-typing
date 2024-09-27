from abc import ABC
from typing import Any

from utils.utils import SpriteAccessibleLayerdDirty


class ChildrenGroup(SpriteAccessibleLayerdDirty, ABC):
    """
    子要素のグループ
    """
    
    def reset(self, *args: Any) -> None:
        """
        リセット

        唯一の所属スプライトのreset()を実行する
        """
        self.sprite.reset(*args)