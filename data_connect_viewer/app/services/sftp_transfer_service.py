import asyncio
import logging

from app.core.database import session_scope
from app.core.config import settings
from app.repositories.record_repository import list_records_for_export
from app.services.app_setting_service import get_sftp_settings
from app.services.export_service import render_json

logger = logging.getLogger(__name__)


def transfer_export_json() -> None:
    import paramiko

    with session_scope() as session:
        sftp_settings = get_sftp_settings(session)
        if not sftp_settings.enabled:
            return

        records = list(
            list_records_for_export(
                session,
                filters={},
                limit=settings.export_max_rows,
            )
        )
        content = render_json(records)

    transport = paramiko.Transport((sftp_settings.sftp_host, 22))
    try:
        transport.connect(username=sftp_settings.sftp_username, password=sftp_settings.sftp_password)
        with paramiko.SFTPClient.from_transport(transport) as client:
            with client.file(sftp_settings.sftp_remote_path, "w") as remote_file:
                remote_file.write(content)
    finally:
        transport.close()


async def sftp_transfer_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        wait_seconds = 60
        try:
            with session_scope() as session:
                sftp_settings = get_sftp_settings(session)
            wait_seconds = max(60, sftp_settings.sftp_frequency_minutes * 60)
            if sftp_settings.enabled:
                await asyncio.to_thread(transfer_export_json)
        except Exception as exc:
            logger.exception("SFTP transfer failed: %s", exc)

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=wait_seconds)
        except asyncio.TimeoutError:
            continue
