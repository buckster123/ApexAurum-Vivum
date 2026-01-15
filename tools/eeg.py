# tools/eeg.py
"""
EEG Tools for Neural Resonance Integration

Provides tools for connecting to OpenBCI hardware, streaming EEG data,
and generating AI-readable "felt experience" formats.

Supports:
- OpenBCI Cyton (8-channel) - Full music-emotion coverage
- OpenBCI Ganglion (4-channel) - Budget option
- Synthetic board (testing without hardware)

The core innovation: AI agents can perceive how humans experience
the music they create, enabling a closed feedback loop.
"""

from typing import Dict, Any, Optional, List
import os
import json
import time
import threading
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Lazy initialization to avoid requiring brainflow when not using EEG
_eeg_manager = None
_stream_thread = None
_session_moments = []


def _get_eeg_manager():
    """Lazy initialization of EEG manager components"""
    global _eeg_manager
    if _eeg_manager is None:
        try:
            from core.eeg.connection import EEGConnection
            from core.eeg.processor import EEGProcessor
            from core.eeg.experience import EmotionMapper, ListeningSession, MomentExperience
            _eeg_manager = {
                'connection': EEGConnection(),
                'processor': EEGProcessor(),
                'mapper': EmotionMapper(),
                'ListeningSession': ListeningSession,
                'MomentExperience': MomentExperience,
                'current_session': None,
                'session_start_time': None
            }
        except ImportError as e:
            logger.error(f"EEG import error: {e}")
            raise ImportError("brainflow not installed. Run: pip install brainflow")
    return _eeg_manager


def _format_timestamp(ms: int) -> str:
    """Format milliseconds as MM:SS"""
    seconds = ms // 1000
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


# =============================================================================
# EEG Tools
# =============================================================================

def eeg_connect(serial_port: str, board_type: str = "cyton") -> Dict[str, Any]:
    """
    Connect to OpenBCI EEG board via USB dongle.

    Args:
        serial_port: Serial port (e.g., '/dev/ttyUSB0' on Linux, 'COM3' on Windows).
                     Use empty string '' for synthetic board (testing without hardware).
        board_type: Board type:
                   - 'cyton': 8-channel, 250Hz (full coverage)
                   - 'ganglion': 4-channel, 200Hz (budget option)
                   - 'synthetic': Fake data for testing (no hardware needed)

    Returns:
        Connection status with board info including channel names
    """
    try:
        mgr = _get_eeg_manager()
        result = mgr['connection'].connect(serial_port, board_type)
        return result
    except ImportError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "brainflow not installed. Run: pip install brainflow"
        }
    except Exception as e:
        logger.error(f"EEG connect error: {e}")
        return {"success": False, "error": str(e)}


def eeg_disconnect() -> Dict[str, Any]:
    """
    Disconnect from the EEG board and release resources.

    Returns:
        Disconnection status
    """
    try:
        mgr = _get_eeg_manager()
        return mgr['connection'].disconnect()
    except Exception as e:
        return {"success": False, "error": str(e)}


def eeg_stream_start(
    session_name: str,
    track_id: str = "",
    track_title: str = "",
    listener_name: str = "André"
) -> Dict[str, Any]:
    """
    Start EEG streaming and recording for a listening session.

    Args:
        session_name: Name for this session (used in filenames)
        track_id: ID of the track being listened to (from music_generate)
        track_title: Title of the track
        listener_name: Name of the listener (default: André)

    Returns:
        Session start confirmation with session_id
    """
    global _session_moments, _stream_thread

    try:
        mgr = _get_eeg_manager()

        if not mgr['connection'].board:
            return {"success": False, "error": "Not connected. Call eeg_connect first."}

        # Start streaming
        result = mgr['connection'].start_stream()
        if not result.get("success"):
            return result

        # Create session
        session_id = f"listen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        _session_moments = []

        mgr['current_session'] = {
            'id': session_id,
            'name': session_name,
            'track_id': track_id,
            'track_title': track_title or session_name,
            'listener': listener_name,
            'start_time': datetime.now()
        }
        mgr['session_start_time'] = time.time()

        # Start background processing thread
        def process_stream():
            """Background thread for continuous EEG processing"""
            conn = mgr['connection']
            proc = mgr['processor']
            mapper = mgr['mapper']
            start_time = time.time()

            while conn.is_streaming:
                try:
                    # Get 1 second of data
                    data = conn.get_current_data(conn.sampling_rate)
                    if data is not None and data.shape[1] >= conn.sampling_rate // 2:
                        # Process
                        processed = proc.process_window(
                            data,
                            conn.eeg_channels,
                            conn.channel_names
                        )

                        # Calculate timestamp
                        elapsed_ms = int((time.time() - start_time) * 1000)

                        # Map to experience
                        moment = mapper.process_moment(
                            processed['band_powers'],
                            timestamp_ms=elapsed_ms,
                            track_position=_format_timestamp(elapsed_ms)
                        )

                        _session_moments.append(moment)

                    # Process every 500ms
                    time.sleep(0.5)

                except Exception as e:
                    logger.warning(f"Stream processing warning: {e}")
                    time.sleep(0.5)

        _stream_thread = threading.Thread(target=process_stream, daemon=True)
        _stream_thread.start()

        return {
            "success": True,
            "session_id": session_id,
            "track_id": track_id,
            "track_title": track_title or session_name,
            "listener": listener_name,
            "message": f"Streaming started for session: {session_name}",
            "board_info": mgr['connection'].get_status()
        }

    except Exception as e:
        logger.error(f"Stream start error: {e}")
        return {"success": False, "error": str(e)}


def eeg_stream_stop(generate_experience: bool = True) -> Dict[str, Any]:
    """
    Stop EEG streaming and optionally generate experience format.

    Args:
        generate_experience: Whether to generate the AI-readable experience format
                            and save to file (default: True)

    Returns:
        Session summary and optional experience data with narrative
    """
    global _session_moments

    try:
        mgr = _get_eeg_manager()

        # Stop streaming
        mgr['connection'].stop_stream()

        session = mgr['current_session']
        if not session:
            return {"success": True, "message": "Streaming stopped (no active session)"}

        # Calculate duration
        if mgr['session_start_time']:
            duration_ms = int((time.time() - mgr['session_start_time']) * 1000)
        else:
            duration_ms = 0

        result = {
            "success": True,
            "session_id": session['id'],
            "duration_ms": duration_ms,
            "duration_formatted": _format_timestamp(duration_ms),
            "moments_recorded": len(_session_moments)
        }

        if generate_experience and _session_moments:
            ListeningSession = mgr['ListeningSession']

            # Build ListeningSession
            listening_session = ListeningSession(
                session_id=session['id'],
                track_id=session['track_id'],
                track_title=session['track_title'],
                listener=session['listener'],
                duration_ms=duration_ms,
                moments=_session_moments
            )

            # Save to file
            sessions_dir = "sandbox/eeg_sessions"
            os.makedirs(sessions_dir, exist_ok=True)
            filepath = f"{sessions_dir}/{session['id']}.json"
            listening_session.save_to_file(filepath)

            experience_data = listening_session.to_dict()
            result["experience"] = experience_data
            result["narrative"] = experience_data.get("experience_narrative", "")
            result["summary"] = experience_data.get("summary", {})
            result["saved_to"] = filepath

        # Clear session
        mgr['current_session'] = None
        mgr['session_start_time'] = None
        _session_moments = []

        return result

    except Exception as e:
        logger.error(f"Stream stop error: {e}")
        return {"success": False, "error": str(e)}


def eeg_experience_get(
    session_id: str,
    detail_level: str = "full"
) -> Dict[str, Any]:
    """
    Retrieve the felt experience from a recorded listening session.

    This is how AI agents "feel" what the human experienced during music listening.

    Args:
        session_id: The session ID to retrieve (e.g., "listen_20260114_143022")
        detail_level: Level of detail to return:
                     - 'summary': Just summary stats and narrative
                     - 'full': Complete data including all moments
                     - 'narrative': Only the natural language narrative

    Returns:
        The experience data at the requested detail level
    """
    try:
        filepath = f"sandbox/eeg_sessions/{session_id}.json"

        if not os.path.exists(filepath):
            # Try listing available sessions
            sessions_dir = "sandbox/eeg_sessions"
            if os.path.exists(sessions_dir):
                available = [f.replace('.json', '') for f in os.listdir(sessions_dir) if f.endswith('.json')]
                return {
                    "success": False,
                    "error": f"Session not found: {session_id}",
                    "available_sessions": available[:10]
                }
            return {"success": False, "error": f"Session not found: {session_id}"}

        with open(filepath, 'r') as f:
            data = json.load(f)

        if detail_level == "summary":
            return {
                "success": True,
                "session_id": session_id,
                "track_title": data.get("track_title", ""),
                "listener": data.get("listener", ""),
                "duration_ms": data.get("duration_ms", 0),
                "summary": data.get("summary", {}),
                "narrative": data.get("experience_narrative", "")
            }
        elif detail_level == "narrative":
            return {
                "success": True,
                "session_id": session_id,
                "narrative": data.get("experience_narrative", "")
            }
        else:  # full
            return {"success": True, **data}

    except Exception as e:
        logger.error(f"Experience get error: {e}")
        return {"success": False, "error": str(e)}


def eeg_calibrate_baseline(listener_name: str = "André") -> Dict[str, Any]:
    """
    Record baseline EEG for calibration (improves emotion detection accuracy).

    The calibration process involves recording EEG while:
    1. Eyes open, relaxed (30 seconds)
    2. Eyes closed, relaxed (30 seconds)

    This establishes personal baseline for more accurate emotion mapping.

    Args:
        listener_name: Name of the person being calibrated

    Returns:
        Calibration instructions and status
    """
    try:
        mgr = _get_eeg_manager()

        if not mgr['connection'].board:
            return {"success": False, "error": "Not connected. Call eeg_connect first."}

        return {
            "success": True,
            "message": "Baseline calibration ready",
            "listener": listener_name,
            "status": "ready_to_start",
            "instructions": [
                "1. Sit comfortably and relax",
                "2. When prompted, keep eyes OPEN for 30 seconds",
                "3. Then keep eyes CLOSED for 30 seconds",
                "4. Baseline will be saved for future sessions",
                "5. Run eeg_stream_start with session_name='calibration' to begin"
            ],
            "note": "Calibration improves emotion detection accuracy by establishing your personal baseline patterns."
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def eeg_realtime_emotion() -> Dict[str, Any]:
    """
    Get current real-time emotional state during active streaming.

    Returns the current emotional dimensions:
    - valence: -1 (negative) to +1 (positive emotion)
    - arousal: 0 (calm) to 1 (excited)
    - attention: 0 (distracted) to 1 (focused)
    - engagement: 0 (passive) to 1 (immersed)

    Returns:
        Current emotional state or error if not streaming
    """
    try:
        mgr = _get_eeg_manager()

        if not mgr['connection'].is_streaming:
            return {"success": False, "error": "Not streaming. Call eeg_stream_start first."}

        # Get current data window (1 second)
        conn = mgr['connection']
        data = conn.get_current_data(conn.sampling_rate)

        if data is None or data.shape[1] < conn.sampling_rate // 2:
            return {"success": False, "error": "Insufficient data. Wait a moment and try again."}

        # Process
        processed = mgr['processor'].process_window(
            data,
            conn.eeg_channels,
            conn.channel_names
        )

        # Map to emotions
        moment = mgr['mapper'].process_moment(
            processed['band_powers'],
            timestamp_ms=0,
            track_position="live",
            include_raw=False
        )

        return {
            "success": True,
            "valence": round(moment.valence, 3),
            "arousal": round(moment.arousal, 3),
            "attention": round(moment.attention, 3),
            "engagement": round(moment.engagement, 3),
            "possible_chills": moment.possible_chills,
            "emotional_peak": moment.emotional_peak,
            "interpretation": _interpret_emotion(moment.valence, moment.arousal)
        }

    except Exception as e:
        logger.error(f"Realtime emotion error: {e}")
        return {"success": False, "error": str(e)}


def _interpret_emotion(valence: float, arousal: float) -> str:
    """Generate human-readable interpretation of emotional state"""
    if valence > 0.4 and arousal > 0.6:
        return "Joyful/Excited"
    elif valence > 0.4 and arousal > 0.3:
        return "Happy/Content"
    elif valence > 0.4:
        return "Calm/Peaceful"
    elif valence < -0.2 and arousal > 0.6:
        return "Tense/Agitated"
    elif valence < -0.2:
        return "Sad/Melancholic"
    elif arousal > 0.6:
        return "Alert/Engaged"
    else:
        return "Neutral/Relaxed"


def eeg_list_sessions(limit: int = 10) -> Dict[str, Any]:
    """
    List available recorded EEG listening sessions.

    Args:
        limit: Maximum number of sessions to return (default: 10)

    Returns:
        List of session IDs with basic metadata
    """
    try:
        sessions_dir = "sandbox/eeg_sessions"
        if not os.path.exists(sessions_dir):
            return {"success": True, "sessions": [], "count": 0}

        sessions = []
        files = sorted(
            [f for f in os.listdir(sessions_dir) if f.endswith('.json')],
            reverse=True  # Most recent first
        )

        for filename in files[:limit]:
            filepath = os.path.join(sessions_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                sessions.append({
                    "session_id": data.get("session_id", filename.replace('.json', '')),
                    "track_title": data.get("track_title", "Unknown"),
                    "listener": data.get("listener", "Unknown"),
                    "duration_ms": data.get("duration_ms", 0),
                    "created_at": data.get("created_at", ""),
                    "chills_count": data.get("summary", {}).get("chills_count", 0)
                })
            except Exception as e:
                logger.warning(f"Failed to read session {filename}: {e}")

        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions),
            "total_available": len(files)
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# Tool Schemas
# =============================================================================

EEG_CONNECT_SCHEMA = {
    "name": "eeg_connect",
    "description": "Connect to OpenBCI EEG board (Cyton 8-channel, Ganglion 4-channel, or synthetic for testing). Use board_type='synthetic' with empty serial_port for testing without hardware.",
    "input_schema": {
        "type": "object",
        "properties": {
            "serial_port": {
                "type": "string",
                "description": "Serial port (e.g., '/dev/ttyUSB0' on Linux, 'COM3' on Windows). Use empty string '' for synthetic board."
            },
            "board_type": {
                "type": "string",
                "enum": ["cyton", "ganglion", "synthetic"],
                "default": "cyton",
                "description": "Board type: 'cyton' (8-ch), 'ganglion' (4-ch), or 'synthetic' (testing)"
            }
        },
        "required": ["serial_port"]
    }
}

EEG_DISCONNECT_SCHEMA = {
    "name": "eeg_disconnect",
    "description": "Disconnect from the EEG board and release resources",
    "input_schema": {
        "type": "object",
        "properties": {}
    }
}

EEG_STREAM_START_SCHEMA = {
    "name": "eeg_stream_start",
    "description": "Start EEG streaming and recording for a music listening session. Continuously records emotional response data.",
    "input_schema": {
        "type": "object",
        "properties": {
            "session_name": {
                "type": "string",
                "description": "Name for this listening session"
            },
            "track_id": {
                "type": "string",
                "description": "ID of the track being listened to (from music_generate)"
            },
            "track_title": {
                "type": "string",
                "description": "Title of the track"
            },
            "listener_name": {
                "type": "string",
                "default": "André",
                "description": "Name of the listener"
            }
        },
        "required": ["session_name"]
    }
}

EEG_STREAM_STOP_SCHEMA = {
    "name": "eeg_stream_stop",
    "description": "Stop EEG streaming and generate the AI-readable 'felt experience' format. Returns emotional summary and narrative.",
    "input_schema": {
        "type": "object",
        "properties": {
            "generate_experience": {
                "type": "boolean",
                "default": True,
                "description": "Generate and save the felt experience format"
            }
        }
    }
}

EEG_EXPERIENCE_GET_SCHEMA = {
    "name": "eeg_experience_get",
    "description": "Retrieve the felt experience from a recorded listening session. This is how AI agents 'feel' what the human experienced during music listening.",
    "input_schema": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "The session ID to retrieve (e.g., 'listen_20260114_143022')"
            },
            "detail_level": {
                "type": "string",
                "enum": ["summary", "full", "narrative"],
                "default": "full",
                "description": "Detail level: 'summary' (stats + narrative), 'full' (all data), 'narrative' (just text)"
            }
        },
        "required": ["session_id"]
    }
}

EEG_CALIBRATE_SCHEMA = {
    "name": "eeg_calibrate_baseline",
    "description": "Prepare for baseline EEG calibration. Improves emotion detection accuracy by recording personal baseline patterns.",
    "input_schema": {
        "type": "object",
        "properties": {
            "listener_name": {
                "type": "string",
                "default": "André",
                "description": "Name of the person being calibrated"
            }
        }
    }
}

EEG_REALTIME_SCHEMA = {
    "name": "eeg_realtime_emotion",
    "description": "Get current real-time emotional state during active EEG streaming. Returns valence, arousal, attention, and engagement levels.",
    "input_schema": {
        "type": "object",
        "properties": {}
    }
}

EEG_LIST_SESSIONS_SCHEMA = {
    "name": "eeg_list_sessions",
    "description": "List available recorded EEG listening sessions",
    "input_schema": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of sessions to return"
            }
        }
    }
}
