"""
wink/tasks/task_start_rotation.py
"""

import time
import uuid
import logging
from django.apps import apps
from celery import shared_task
from logs import configure_logging
from wink.redis_utils import get_redis_client

log = logging.getLogger(__name__)
configure_logging(logging.INFO)

FilesModel = apps.get_model("wink", "FilesModel")
IntermediateFilesModel = apps.get_model("wink", "IntermediateFilesModel")

"""
'RUN_LOCK_KEY' - This is checker. It prevent the async's start for a one 'inner_pk'
 'ACTIVE_COUNT_KEY' = This is a limit for upload's session for a one file
"""
# per-rotator lock
RUN_LOCK_KEY = "rotator:run_lock:%s"
# per-rotator stop flag
STOP_FLAG_KEY = "rotator:stop_lock:%s"
# per-file active session
ACTIVE_COUNT_KEY = "rotator:active_count:%s"
# mark that session started
ROTATION_MARK_KEY = "rotator:mark_count:%s"

MAX_CONCURRENT = 10
# Lua - secret script the decrement (It will not reach a number less than zero)
DECR_SAFE_LUA = """
local k = KEYS[1]
if redis.call("exists", k) == 1 then
    local v = tonumber(redis.call("get", k)) or 0
    if v > 0 then
        return redis.call("decr", k)
    end
    return 0
end
return 0
"""


@shared_task(
    name="start_rotation",
    bind=False,
    authretry_for=(TimeoutError,),
)
def start_rotation(inter_pk: int, interval: int = 90, duration: int = 600) -> bool:
    """
    Description: Start rotating 'refer' for 'IntermediateFileModel' with 'pk=inner_pk',
    - 'MAX_CONCURRENT' session per 'FilersModel.upload'.
    - uses CAS upload to change refer safely
    - 'refer' This is a special key of security for file working.
    :param int inter_pk: uses Redis lock to prevent double start for same.
    :param int interval: This is a tine/seconds after which the 'refer' is updating.
    :param int duration:  This is a max quantity of seconds for rotating the 'refer'.
    :return:
    """
    log.info("[%s]Starting rotator for inter_pk=%s", __name__, str(inter_pk))
    if inter_pk is None:
        log.info("start_rotation called with inter_pk=None")
        return False
    print("HALLO WORD!!")
    r = get_redis_client()
    lock_key = RUN_LOCK_KEY % str(inter_pk)
    stop_key = STOP_FLAG_KEY % str(inter_pk)
    rotator_mark = ROTATION_MARK_KEY % str(inter_pk)

    """
    There we got sure  what we making an one request to processing the file
    "1" - it's symply a flag for mark the session
    """
    lock_ttl = int(duration + 30)
    got = r.set(lock_key, "1", nx=True, ex=lock_ttl)
    if not got:
        log.info("Rotator already running for inter_pk=%s", str(inter_pk))
        return False
    log.info(
        "Rotator for inter_pk=%s",
        str(inter_pk),
    )
    try:
        try:
            # load file
            inst = IntermediateFilesModel.objects.select_related("upload").get(
                pk=inter_pk
            )
        except Exception:
            log.error(
                "IntermediateFilesModel pk=%s not foud",
                str(inter_pk),
            )
            r.delete(lock_key)
            return False
        """
        This is a special key - It's current quantity  sessions on 'FilersModel.upload' for one file.
        """
        file_pk = inst.upload
        count_key = ACTIVE_COUNT_KEY % str(file_pk)
        try:
            global count
            # --------- REDIS incr ---------
            # https://redis-docs.ru/commands/incr/
            # Increments the number stored at key by one. If the key does not exist, it is set to 0 before performing the operation
            count = r.incr(count_key)
            # ------------------------------
            if count == 1:
                # --------- REDIS expire -------
                # https://redis-docs.ru/commands/expire/
                # This setting  TTL to duration + some buffer so stale counters axpire
                r.expire(count_key, duration + 60)
                # ------------------------------
        except Exception:
            log.exception("Redis incr failed for file_pk=%s", str(file_pk))
            r.delete(lock_key)

        # If more than the quantity MAX_CONCURRENT -> It's max number users for a one file.
        if count > MAX_CONCURRENT:
            try:
                r.eval(DECR_SAFE_LUA, 1, count_key)
            except Exception:
                log.exception("Failed safe-decr for file_pk=%s", str(file_pk))
            r.delete(lock_key)
            log.info(
                "Active session limit reached for file_pk=%s (max=%s). Aborting start.",
                str(file_pk),
                str(MAX_CONCURRENT),
            )
            return False
        # MArk that rotator started & used for external awareness
        r.set(rotator_mark, "1", ex=duration + 30)
        log.info(
            "Rotator started for inter_pk=%s (file_pk=%s). active_count=%s",
            str(inter_pk),
            str(file_pk),
            str(count),
        )
        end_time = time.time() + duration
        while time.time() < end_time:
            # Check STOP flag
            if r.get(stop_key):
                log.info(
                    "Stop flag observed for inter_pk=%s, exiting rotator loop",
                    str(inter_pk),
                )
                break
            # REFRESH instance to get current refer
            try:
                inst = IntermediateFilesModel.objects.get(pk=file_pk)
            except Exception:
                log.info(
                    "IntermediateModel gone for inter_pk=%s, exiting", str(inter_pk)
                )
                break
            # CURRENT REFER
            current_refer = inst.refer
            new_uuid = uuid.uuid4()
            try:
                # CAS UPDATE
                updated = IntermediateFilesModel.objects.filter(
                    pk=inter_pk, refer=current_refer
                ).update(refer=new_uuid)
                if updated == 0:
                    log.error(
                        "inter_pk=%s refer updated -> %s", str(inter_pk), new_uuid
                    )
                else:
                    log.info(
                        "inter_pk=%s CAS update returned 0 (someone else updated).",
                        str(inter_pk),
                    )
            except Exception:
                log.error(
                    "inter_pk=%s CAS update returned 0 (someone else updated).",
                    str(inter_pk),
                )
            # SLEPT INTERVAL
            slept = 0
            step = 1
            while slept < interval:
                if r.get(stop_key):
                    break
                time.sleep(step)
                slept += step
            if r.get(stop_key):
                break

        log.info("Rotator finished for inter_pk=%s", str(inter_pk))
    finally:
        # CLEANUP - REMOVE LOCK & ROTATOR_MARK & DELETE STOP FLAG & DECREMENT active count
        try:
            r.delete(lock_key)
            r.delete(rotator_mark)
            r.delete(stop_key)
        except Exception:
            log.exception("Redis cleanup failed keys for inter_pk=%s", str(inter_pk))
        # SAFE DECREMENT ACTIVE COUNT
        try:
            if "count_key" in locals():
                r.eval(DECR_SAFE_LUA, 1, count_key)
        except Exception:
            log.exception(
                "Safe decrement failed for inter_pk=%s (file_pk=%s)",
                str(inter_pk),
                locals().get("file_pk"),
            )
    return True


@shared_task(
    name=__name__,
    bind=False,
    authretry_for=(TimeoutError,),
)
def stop_rotation(inter_pk: int, enough: int = 300) -> bool:
    """
    Description: Set stop-flag for a ratator.
    The runing start start_rotator wil observe this flag and stop/
    :param int inter_pk: uses Redis lock to prevent double start for same.
    :return: bool
    """
    if inter_pk is None:
        log.info("stop_rotation called with inter_pk=None")
        return False
    r = get_redis_client()
    stop_key = STOP_FLAG_KEY % str(inter_pk)
    try:
        # Time -  minutes is enough
        r.set(stop_key, "1", nx=True, ex=enough)
        log.info("Stop flag set for inter_pk=%s", str(inter_pk))
    except Exception:
        log.exception("Failed to set stop flag for inter_pk=%s", str(inter_pk))
        return False
    return True
