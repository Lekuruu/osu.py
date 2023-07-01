from typing import List, Optional
from dateutil.tz import tzlocal
from datetime import datetime

import platform
import hashlib
import psutil


class ClientHash:

    """The client hash is used to identify a device on the server side."""

    def __init__(self, executable_hash: str) -> None:
        """
        Args:
            `executable_hash`: str
                The hash of your `osu!.exe`.
                Can also be retrieved from `/web/check-updates.php`

                Warning: Bancho will refuse the connection, if your version is too old!
        """

        self.executable_hash = executable_hash

    def __repr__(self) -> str:
        return f"{self.executable_hash}:{self.adapter_string}:{self.adapter_hash}:{self.uninstall_id}:{self.disk_signature}:"

    @property
    def adapters(self) -> List[str]:
        return [
            psutil.net_if_addrs()[adapter][0].address
            for adapter in psutil.net_if_addrs()
        ]

    @property
    def adapter_string(self) -> str:
        if platform.system() in ["Linux", "Darwin"]:
            return "runningunderwine"

        adapters = [
            adapter.replace("-", "")
            for adapter in self.adapters
            if adapter.count("-") == 5
        ]
        adapters.insert(3, "")
        return ".".join(adapters)

    @property
    def adapter_hash(self) -> str:
        return hashlib.md5(self.adapter_string.encode()).hexdigest()

    @property
    def uninstall_id(self) -> str:
        return hashlib.md5(b"unknown").hexdigest()  # TODO

    @property
    def disk_signature(self) -> str:
        return hashlib.md5(b"unknown").hexdigest()  # TODO


class ClientInfo:

    """Sent when logging in to bancho.

    Parameters:
        `version`: str
            Client version (e.g. b20220829)

        `utc_offset`: int
            UTC offset for this device

        `display_city`: bool
            Probably has something to do with the world map inside osu!

        `hash`: osu.objects.client.ClientHash
            See above

        `friendonly_dms`: bool
            aka. "Block non-friend dms"
    """

    def __init__(self, version: str, updates: dict) -> None:
        """
        Args:
            `version`: str
                Client version (e.g. b20220829)

            `updates`: dict
                Update response from `/web/check-updates.php`
        """

        self.hash = ClientHash(self.get_file_hash(updates))
        self.version = version

        self.friendonly_dms = False
        self.display_city = False

        self.utc_offset = round(
            datetime.now(tzlocal()).utcoffset().total_seconds() / 3600
        )

    def __repr__(self) -> str:
        return f"{self.version}|{self.utc_offset}|{int(self.display_city)}|{self.hash}|{int(self.friendonly_dms)}"

    @classmethod
    def get_file_hash(cls, updates: dict) -> Optional[str]:
        for file in updates:
            if file["filename"] == "osu!.exe":
                return file["file_hash"]
        return None
