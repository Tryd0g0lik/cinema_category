from django.dispatch import Signal
from django.core.signals import request_finished

# from wink.tasks.task_file_reader import handle_file_upload_signal

# from wink.tasks.task_file_reader import task_process_file_upload

parser_signal = Signal()
# parser_signal.connect(handle_file_upload_signal)
