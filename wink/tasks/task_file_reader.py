import logging
from typing import Optional
from rest_framework.request import Request
from logs import configure_logging
from wink.interfaces import FileUpload
from wink.models_wink.files import FilesModel


log = logging.getLogger(__name__)
configure_logging(logging.INFO)
def task_process_file_upload(file_id: int, request: Request) -> bool:
    """
    We can have a very big size of file.
    This is TASK helping us upload a file and don't stop the workflow user's stream
    :param file_id:
    :param request:
    :return:
    """
    file = request.FILES['file']
    if not file:
        log.error("[%s]: Request-File was not found .", __name__)
        return False

    try:
        global file_path
        file_path: Optional[FilesModel] = FilesModel.objects.filter(id=file_id).first()
        if not file_path:
            log.error("[%s]: File was not found in db", __name__)
            return False
    except Exception as error:
        log.error("[%s]: Error of Db connection => %s ",( __name__, error.args[0]))
        return False

    try:
        read_bool = True
        # CREATE THE BASIS FILE
        with open(file, "rb") as source:
            with open(f"{file_path.upload}/{file_path.name}", 'wb') as destination:
                while read_bool:
                    chunk = source.read(10 * 1024 *1024)
                    if chunk:
                        destination.write(chunk)
                    else:
                        read_bool = False
    except Exception as e:
        log.error("[%s]: Error of Db connection => %s ",( __name__, e.args[0]))
        return False
    log.info("[%s]: Uploaded %s bytes", __name__, len(source.read()))
    return True
