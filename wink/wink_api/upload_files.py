import asyncio
from typing import Type, Union

from wink.interfaces import A, B, C


async def handle_uploaded_file(
    path: str, f, index: int, callback: Union[Type[A] | Type[B] | Type[C]]
):
    """
    :param callback:
    :param str path:
    :param f: it from django's 'request.FILES["upload"]'
    :param int index:
    :return: void FilesModel
    """
    with open(path, "wb+") as destination:
        for chunk in f.chunks(10 * 1024 * 1024):
            destination.write(chunk)
    path = path.split("upload")[1].replace("\\", "/")
    f_oblect = await asyncio.to_thread(lambda: callback.objects.get(id=index))
    f_oblect.upload = f"upload{path}"
    await f_oblect.asave()
