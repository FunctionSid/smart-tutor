"""Chat channels module with plugin architecture."""

from smarttutor.partners.channels.base import BaseChannel
from smarttutor.partners.channels.manager import ChannelManager

__all__ = ["BaseChannel", "ChannelManager"]
