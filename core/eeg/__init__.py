# core/eeg/__init__.py
"""
Neural Resonance EEG Integration Module

Provides EEG acquisition, processing, and emotion mapping
for the ApexAurum music-emotion feedback loop.

Supports:
- OpenBCI Cyton (8-channel)
- OpenBCI Ganglion (4-channel)
- Synthetic board (testing without hardware)
"""

from .connection import EEGConnection
from .processor import EEGProcessor, BandPower
from .experience import EmotionMapper, MomentExperience, ListeningSession

__all__ = [
    'EEGConnection',
    'EEGProcessor',
    'BandPower',
    'EmotionMapper',
    'MomentExperience',
    'ListeningSession'
]
