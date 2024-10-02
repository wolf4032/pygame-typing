import networkx

import asyncio
import sys

import pygame

from utils.utils import Utils
from classes.typing import Typing


async def main():
    """
    実行
    """
    fps = await Utils.mesure_fps()

    typing = Typing(fps)

    while typing.running:
        dirty_rects = typing.run()

        if dirty_rects:
            pygame.display.update(dirty_rects)

        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    asyncio.run(main())