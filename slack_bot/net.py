"""Network helpers shared by the bot.

Some networks publish IPv6 addresses that don't connect (seen with Google APIs).
curl falls back to IPv4 at once, but Python tries every IPv6 address with a full
timeout first, so requests appear to hang. prefer_ipv4() keeps all addresses but
orders IPv4 first; it is process-wide and safe to call more than once.
"""

from __future__ import annotations

import socket

_original_getaddrinfo = socket.getaddrinfo


def _ipv4_first(*args, **kwargs):
    infos = _original_getaddrinfo(*args, **kwargs)
    return sorted(infos, key=lambda info: 0 if info[0] == socket.AF_INET else 1)


def prefer_ipv4() -> None:
    socket.getaddrinfo = _ipv4_first
