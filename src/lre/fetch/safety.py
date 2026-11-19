import ipaddress
import socket
from urllib.parse import urlsplit


def validate_url(url: str, block_private: bool = True) -> None:
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
        raise ValueError("Only public HTTP(S) URLs are allowed")
    if not block_private:
        return
    try:
        addresses = {row[4][0] for row in socket.getaddrinfo(parts.hostname, parts.port or (443 if parts.scheme == "https" else 80), type=socket.SOCK_STREAM)}
        if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
            raise ValueError("Private or non-public destination blocked")
    except socket.gaierror as exc:
        raise ValueError("Unable to resolve destination") from exc
