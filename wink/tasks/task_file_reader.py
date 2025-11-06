import asyncio
import logging
import os
import threading
import datetime
from typing import Optional
import io

from celery import shared_task

# from celery import shared_task
# from django.dispatch import receiver
from rest_framework.request import Request
from logs import configure_logging
from project import settings
from wink.interfaces import FileUpload
from wink.redis_utils import get_redis_client

# from wink.signals import parser_signal

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


# @shared_task(dind=False)
def task_file_reader(file_name, bytes_io):
    # FILE_LOCK_KEY = "file:{inter_pk}"
    # r = get_redis_client()
    # file_key = FILE_LOCK_KEY.format(inter_pk=file_id)
    # got = r.set(file_key, file)
    #
    # bytes_io.seek(0)
    # if not got:
    #     log.info("Rotator already running for inter_pk=%s", file_id)
    #     return False
    #     # Запускаем асинхронную функцию в event loop
    def _run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(handle_uploaded_file(file_name, bytes_io))
        except Exception as e:
            log.error(e)
            return

    thread = threading.Thread(target=_run_async)
    thread.daemon = True  # Демонизированный поток
    thread.start()


def handle_uploaded_file(path, f):
    with open(path, "wb+") as destination:
        for chunk in f.chunks(10 * 1024 * 1024):
            destination.write(chunk)


# def handle_file_upload_signal(sender, file_id: int, uploaded_file, **kwargs):
#     """
#     Celery задача получает только сериализуемые данные
#     """
#     # Запускаем асинхронную функцию в event loop
#     # loop = asyncio.get_event_loop()
#     # result = loop.run_until_complete(
#     # asyncio.run()
#     def _run_async():
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#             loop.run_until_complete(task_process_file_upload(file_id, uploaded_file))
#     thread = threading.Thread(target=_run_async)
#     thread.daemon = True  # Демонизированный поток
#     thread.start()
# )
#
# def save_file_worker(file_name, bytes_io):
#     """
#     Функция-воркер для сохранения файла в потоке
#     """
#     # from io import BytesIO
#     # bytes_io = BytesIO(bytes_io_data)
#
#     # from django.core.files.uploadedfile import UploadedFile
#      # ваши байты
#
#     date = datetime.date.today().strftime("%Y-%m-%d").split("-")
#     file_path = f"upload\\{date[0]}\\{date[1]}\\{date[2]}\\{file_name}"
#     try:
#         read_bool = True
#         import os
#         from django.conf import settings
#         upload_dir = os.path.join(settings.MEDIA_ROOT, file_path)
#         try:
#             bytes_io.seek(0)
#             os.makedirs(os.path.dirname(upload_dir), exist_ok=True)
#         except OSError:
#             pass
#         with open(upload_dir, "wb+") as destination:
#             for chunk in bytes_io.chunks():
#                 destination.write(chunk)
#         # chunk_size = 10 * 1024 * 1024
# in_memory = io.BytesIO(bytes_io, )
# in_memory.write(bytes_io)
# in_memory.seek(0)
# with open(upload_dir, 'wb') as destination:
# for i in range(0, len(in_memory), chunk_size):
# for i in in_memory.read(chunk_size):
# destination.write(chunk)
# chunk = in_memory[i:i + chunk_size]
# destination.write(in_memory.read())

# with open(upload_dir, 'wb') as destination:
#     while read_bool:
#         # for chunk in uploaded_file_io.chunks(10 * 1024 * 1024):  # 10MB chunks
#         chunk = bytes_io.read(10 * 1024 * 1024)  # 10MB chunks
#         if chunk:
#             destination.write(chunk)
#         else:
#             read_bool = False


# except Exception as e:
#     log.error("[%s]: Error of Db connection => %s ",( __name__, e.args[0]))
#     return False

#
#
# async def task_process_file_upload(file_id: int, uploaded_file) -> bool:
#     """
#     We can have a very big size of file.
#     This is TASK helping us upload a file and don't stop the workflow user's stream
#     :param int file_id:
#     :param Request request:
#     :return:
#     """
#     from wink.models_wink.files import FilesModel
#     # uploaded_file = request.FILES['upload']
#     if not uploaded_file :
#         log.error("[%s]: Request-File was not found .", __name__)
#         return False
#
#     file_obj: Optional[FilesModel] = await asyncio.to_thread(lambda : FilesModel.objects.filter(id=file_id).first())
#
#     date = datetime.date.today().strftime("%Y-%m-%d").split("-")
#     file_path = f"upload\\{date[0]}\\{date[1]}\\{date[2]}\\{file_obj.name}"
#     try:
#         read_bool = True
#         import os
#         from django.conf import settings
#         upload_dir = os.path.join(settings.MEDIA_ROOT, file_path)
#         try:
#
#             os.makedirs(os.path.dirname(upload_dir), exist_ok=True)
#         except OSError:
#             pass
#
#         with open(upload_dir, 'w+b') as destination:
#             while read_bool:
#                 for chunk in uploaded_file.chunks(10 * 1024 * 1024):  # 10MB chunks
#                     if chunk:
#                         destination.write(chunk)
#                     else:
#                         read_bool = False
#
#
#
#     except Exception as e:
#         log.error("[%s]: Error of Db connection => %s ",( __name__, e.args[0]))
#         return False
#     # log.info("[%s]: Uploaded %s bytes", __name__, len(source.read()))
#     return True
