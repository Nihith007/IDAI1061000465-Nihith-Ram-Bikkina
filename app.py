"""
Mindful Work — Smart Stress Relief Pod Companion App
=====================================================
FutureForward Wellness | Design Thinking for Innovation — Year 1 Summative

Single-file version: all models, controllers, and views in one file.
Run with:
    pip install customtkinter matplotlib
    python mindful_work_app.py
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

import json
import os
import platform
import random
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
from tkinter import messagebox
from typing import Callable, Optional

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

ctk.set_default_color_theme("blue")

# ─────────────────────────────────────────────────────────────────────────────
# DATA — CONSTANTS & PRESETS
# ─────────────────────────────────────────────────────────────────────────────

DATA_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

PRESETS = {
    "warm_lofi_lavender": {
        "name": "Sunset Calm",
        "lighting": "warm",
        "music": "lo-fi",
        "aroma": "lavender",
        "description": "Warm amber lighting with lo-fi beats and calming lavender",
    },
    "cool_nature_eucalyptus": {
        "name": "Forest Refresh",
        "lighting": "cool",
        "music": "nature",
        "aroma": "eucalyptus",
        "description": "Cool blue-white light with forest sounds and refreshing eucalyptus",
    },
    "color_binaural_citrus": {
        "name": "Focus Flow",
        "lighting": "color_therapy",
        "music": "binaural",
        "aroma": "citrus",
        "description": "Color-cycling therapy lights with binaural beats and energizing citrus",
    },
    "warm_classical_sandalwood": {
        "name": "Deep Unwind",
        "lighting": "warm",
        "music": "classical",
        "aroma": "sandalwood",
        "description": "Soft warm glow with classical piano and grounding sandalwood",
    },
}

LIGHTING_OPTIONS  = ["warm", "cool", "color_therapy"]
MUSIC_OPTIONS     = ["lo-fi", "nature", "binaural", "classical"]
AROMA_OPTIONS     = ["lavender", "eucalyptus", "citrus", "sandalwood"]
DURATION_OPTIONS  = [5, 10, 15, 20]
ROLES             = ["Software Engineer", "Project Manager", "Designer",
                     "Data Analyst", "HR Manager", "Marketing Lead", "Employee"]

BREATHING_PATTERNS = {
    "box_breathing": {
        "name": "Box Breathing",
        "phases": [("Breathe In", 4), ("Hold", 4), ("Breathe Out", 4), ("Hold", 4)],
    },
    "4_7_8_breathing": {
        "name": "4-7-8 Breathing",
        "phases": [("Breathe In", 4), ("Hold", 7), ("Breathe Out", 8)],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# MODEL — USER
# ─────────────────────────────────────────────────────────────────────────────

class User:
    """Represents an employee user of the Mindful Work pod system."""

    def __init__(self, user_id, name, role="Employee", avatar_emoji="🧑",
                 preferences=None, history=None, streak=0,
                 total_sessions=0, total_minutes=0,
                 created_at=None, last_login=None):
        self.user_id        = user_id
        self.name           = name
        self.role           = role
        self.avatar_emoji   = avatar_emoji
        self.preferences    = preferences or self._default_preferences()
        self.history        = history or []
        self.streak         = streak
        self.total_sessions = total_sessions
        self.total_minutes  = total_minutes
        self.created_at     = created_at or datetime.now().isoformat()
        self.last_login     = last_login or datetime.now().isoformat()

    @staticmethod
    def _default_preferences():
        return {
            "lighting": "warm", "music": "lo-fi", "aroma": "lavender",
            "aroma_intensity": 5, "meditation": "box_breathing",
            "session_duration": 10, "dark_mode": False,
            "preset_weights": {
                "warm_lofi_lavender": 1.0, "cool_nature_eucalyptus": 1.0,
                "color_binaural_citrus": 1.0, "warm_classical_sandalwood": 1.0,
            },
        }

    def to_dict(self):
        return {
            "user_id": self.user_id, "name": self.name, "role": self.role,
            "avatar_emoji": self.avatar_emoji, "preferences": self.preferences,
            "history": self.history, "streak": self.streak,
            "total_sessions": self.total_sessions, "total_minutes": self.total_minutes,
            "created_at": self.created_at, "last_login": self.last_login,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def update_streak(self):
        if self.last_login:
            try:
                last  = datetime.fromisoformat(self.last_login).date()
                today = datetime.now().date()
                diff  = (today - last).days
                if diff == 1:   self.streak += 1
                elif diff > 1:  self.streak = 1
            except (ValueError, TypeError):
                self.streak = 1
        self.last_login = datetime.now().isoformat()

    def add_session_to_history(self, session_data):
        self.history.append(session_data)
        self.total_sessions += 1
        self.total_minutes  += session_data.get("duration_minutes", 0)

    def get_recent_stress_scores(self, n=7):
        return [s.get("stress_score", 5.0) for s in self.history if "stress_score" in s][-n:]

    def get_feedback_deltas(self):
        return [s.get("stress_score", 5) - s.get("post_score", 5) for s in self.history]


# ─────────────────────────────────────────────────────────────────────────────
# MODEL — USER MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class UserManager:
    """Manages user persistence to local JSON file."""

    def __init__(self, filepath=USERS_FILE):
        self.filepath = filepath
        self._ensure_data_file()

    def _ensure_data_file(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            self._write_demo_data(); return
        try:
            with open(self.filepath) as f:
                data = json.load(f)
            if not isinstance(data, dict) or "users" not in data:
                self._write_demo_data()
        except (json.JSONDecodeError, IOError):
            self._write_demo_data()

    def _write_demo_data(self):
        demo = {"users": {
            "priya": User(
                user_id="priya", name="Priya Sharma", role="Software Engineer",
                avatar_emoji="👩‍💻",
                history=[
                    {"date": "2026-04-14", "stress_score": 7.5, "post_score": 4.0,
                     "preset": "warm_lofi_lavender", "duration_minutes": 10,
                     "heart_rate": 88, "hrv": 35},
                    {"date": "2026-04-15", "stress_score": 6.0, "post_score": 3.5,
                     "preset": "cool_nature_eucalyptus", "duration_minutes": 15,
                     "heart_rate": 82, "hrv": 42},
                    {"date": "2026-04-16", "stress_score": 8.0, "post_score": 4.5,
                     "preset": "warm_lofi_lavender", "duration_minutes": 10,
                     "heart_rate": 92, "hrv": 30},
                ],
                streak=3, total_sessions=3, total_minutes=35,
            ).to_dict(),
            "rahul": User(
                user_id="rahul", name="Rahul Mehta", role="Project Manager",
                avatar_emoji="👨‍💼",
                history=[
                    {"date": "2026-04-15", "stress_score": 6.5, "post_score": 3.0,
                     "preset": "warm_classical_sandalwood", "duration_minutes": 20,
                     "heart_rate": 78, "hrv": 45},
                    {"date": "2026-04-16", "stress_score": 7.0, "post_score": 3.5,
                     "preset": "warm_classical_sandalwood", "duration_minutes": 15,
                     "heart_rate": 80, "hrv": 40},
                ],
                streak=2, total_sessions=2, total_minutes=35,
            ).to_dict(),
        }}
        with open(self.filepath, "w") as f:
            json.dump(demo, f, indent=2)

    def _load_all(self):
        try:
            with open(self.filepath) as f:
                data = json.load(f)
            if not isinstance(data, dict) or "users" not in data:
                self._write_demo_data()
                with open(self.filepath) as f: data = json.load(f)
            return data
        except (json.JSONDecodeError, IOError):
            self._write_demo_data()
            with open(self.filepath) as f: return json.load(f)

    def _save_all(self, data):
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def get_user(self, user_id) -> Optional[User]:
        d = self._load_all()["users"].get(user_id)
        return User.from_dict(d) if d else None

    def save_user(self, user: User):
        data = self._load_all()
        data["users"][user.user_id] = user.to_dict()
        self._save_all(data)

    def list_users(self):
        return list(self._load_all()["users"].keys())

    def create_user(self, user_id, name, role="Employee"):
        user = User(user_id=user_id, name=name, role=role)
        self.save_user(user); return user

    def delete_all_history(self, user_id):
        user = self.get_user(user_id)
        if user:
            user.history = []; user.total_sessions = 0
            user.total_minutes = 0; user.streak = 0
            self.save_user(user)


# ─────────────────────────────────────────────────────────────────────────────
# MODEL — SESSION & STRESS ANALYZER
# ─────────────────────────────────────────────────────────────────────────────

class StressAnalyzer:
    WEIGHT_SURVEY     = 0.30
    WEIGHT_HEART_RATE = 0.35
    WEIGHT_VOICE      = 0.35

    @staticmethod
    def normalize_heart_rate(hr):
        return ((max(55.0, min(120.0, hr)) - 55.0) / 65.0) * 10.0

    @staticmethod
    def normalize_hrv(hrv):
        return ((80.0 - max(15.0, min(80.0, hrv))) / 65.0) * 10.0

    @classmethod
    def compute_stress_score(cls, survey_score, heart_rate=None, hrv=None, voice_score=None):
        components, weights, explanations = [], [], []
        components.append(survey_score); weights.append(cls.WEIGHT_SURVEY)
        explanations.append(f"Self-report: {survey_score:.1f}/10")

        if heart_rate is not None and hrv is not None:
            physio = (cls.normalize_heart_rate(heart_rate) + cls.normalize_hrv(hrv)) / 2.0
            components.append(physio); weights.append(cls.WEIGHT_HEART_RATE)
            explanations.append(f"Wearable: HR={heart_rate:.0f}bpm, HRV={hrv:.0f}ms (stress={physio:.1f}/10)")
        elif heart_rate is not None:
            components.append(cls.normalize_heart_rate(heart_rate)); weights.append(cls.WEIGHT_HEART_RATE)
            explanations.append(f"Wearable: HR={heart_rate:.0f}bpm")

        if voice_score is not None:
            components.append(voice_score); weights.append(cls.WEIGHT_VOICE)
            explanations.append(f"Voice analysis: stress={voice_score:.1f}/10")

        total_w = sum(weights)
        score   = max(1.0, min(10.0, sum(c * (w / total_w) for c, w in zip(components, weights))))
        conflict_note = ""
        if heart_rate is not None and abs(survey_score - score) > 2.5 and score > survey_score:
            conflict_note = (" Note: physiological indicators suggest higher stress than self-assessment.")
        level = "Low" if score <= 3.5 else ("Medium" if score <= 6.5 else "High")
        return round(score, 1), level, " | ".join(explanations) + conflict_note


class MockWearable:
    def __init__(self):
        self.connected  = False
        self.heart_rate = 72.0
        self.hrv        = 50.0
        self._running   = False
        self._thread    = None

    def connect(self):
        self.connected  = True
        self.heart_rate = random.uniform(68, 95)
        self.hrv        = random.uniform(25, 60)
        return True

    def disconnect(self):
        self._running = False; self.connected = False

    def start_streaming(self, callback=None):
        if not self.connected: return
        self._running = True
        def _stream():
            while self._running and self.connected:
                self.heart_rate = max(55, min(120, self.heart_rate + random.uniform(-2.0, 2.0)))
                self.hrv        = max(15, min(80,  self.hrv        + random.uniform(-3.0, 3.0)))
                if callback: callback(self.heart_rate, self.hrv)
                time.sleep(1.5)
        self._thread = threading.Thread(target=_stream, daemon=True)
        self._thread.start()

    def stop_streaming(self):
        self._running = False


class MockVoiceAnalyzer:
    def __init__(self):
        self.analyzing = False
        self.result    = None

    def analyze(self, duration=3.0, callback=None):
        self.analyzing = True; self.result = None
        def _analyze():
            time.sleep(duration)
            self.result = round(random.uniform(3.0, 8.5), 1)
            self.analyzing = False
            if callback: callback(self.result)
        threading.Thread(target=_analyze, daemon=True).start()


class Session:
    def __init__(self, user_id, stress_score, stress_level, preset_key,
                 lighting, music, aroma, aroma_intensity, meditation,
                 duration_minutes, heart_rate=None, hrv=None, voice_score=None):
        self.user_id         = user_id
        self.stress_score    = stress_score
        self.stress_level    = stress_level
        self.preset_key      = preset_key
        self.lighting        = lighting
        self.music           = music
        self.aroma           = aroma
        self.aroma_intensity = aroma_intensity
        self.meditation      = meditation
        self.duration_minutes= duration_minutes
        self.heart_rate      = heart_rate
        self.hrv             = hrv
        self.voice_score     = voice_score
        self.started_at      = None
        self.ended_at        = None
        self.post_score      = None
        self.completed       = False
        self.elapsed_seconds = 0

    def start(self): self.started_at = datetime.now().isoformat()
    def end(self, early=False):
        self.ended_at = datetime.now().isoformat(); self.completed = not early

    def to_history_dict(self):
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "stress_score": self.stress_score, "post_score": self.post_score or self.stress_score,
            "preset": self.preset_key, "lighting": self.lighting, "music": self.music,
            "aroma": self.aroma, "meditation": self.meditation,
            "duration_minutes": self.duration_minutes, "elapsed_seconds": self.elapsed_seconds,
            "heart_rate": self.heart_rate, "hrv": self.hrv,
            "voice_score": self.voice_score, "completed": self.completed,
        }


# ─────────────────────────────────────────────────────────────────────────────
# MODEL — AI RECOMMENDATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

EMA_ALPHA = 0.3
COLD_START_RULES = {"Low": "cool_nature_eucalyptus", "Medium": "warm_lofi_lavender", "High": "warm_classical_sandalwood"}
STRESS_AFFINITY  = {
    "Low":    {"warm_lofi_lavender": 0.8, "cool_nature_eucalyptus": 1.2, "color_binaural_citrus": 1.1, "warm_classical_sandalwood": 0.7},
    "Medium": {"warm_lofi_lavender": 1.2, "cool_nature_eucalyptus": 1.0, "color_binaural_citrus": 0.9, "warm_classical_sandalwood": 1.0},
    "High":   {"warm_lofi_lavender": 1.0, "cool_nature_eucalyptus": 0.8, "color_binaural_citrus": 0.7, "warm_classical_sandalwood": 1.3},
}


class AIRecommendationEngine:
    def recommend(self, stress_level, stress_score, preset_weights, history=None):
        if not history:
            key  = COLD_START_RULES.get(stress_level, "warm_lofi_lavender")
            info = PRESETS[key].copy()
            return key, info, (f"First-time recommendation: '{info['name']}' based on {stress_level.lower()} stress. "
                               "AI will personalise over time.")

        affinity = STRESS_AFFINITY.get(stress_level, STRESS_AFFINITY["Medium"])
        scores   = {k: preset_weights.get(k, 1.0) * affinity.get(k, 1.0) for k in PRESETS}
        best_key = max(scores, key=scores.get)
        info     = PRESETS[best_key].copy()

        success = sum(1 for s in history if s.get("preset") == best_key and s.get("stress_score", 5) - s.get("post_score", 5) > 0)
        total   = sum(1 for s in history if s.get("preset") == best_key)
        if total:
            reasoning = (f"'{info['name']}' worked {success}/{total} times. Optimal for your {stress_level.lower()} stress (score: {stress_score}).")
        else:
            reasoning = (f"AI recommends '{info['name']}' for {stress_level.lower()} stress (score: {stress_score}).")
        return best_key, info, reasoning

    def recommend_duration(self, score):
        if score <= 3.5: return 5
        elif score <= 6.0: return 10
        elif score <= 8.0: return 15
        else: return 20

    def recommend_aroma_intensity(self, score):
        return min(10, max(1, int(score)))

    @staticmethod
    def update_weights(preset_weights, preset_key, stress_score, post_score):
        delta        = stress_score - post_score
        success_rate = max(0.0, min(1.0, delta / stress_score)) if stress_score > 0 else 0.5
        old_w        = preset_weights.get(preset_key, 1.0)
        new_w        = max(0.3, min(3.0, EMA_ALPHA * (1.0 + success_rate) + (1.0 - EMA_ALPHA) * old_w))
        updated      = preset_weights.copy()
        updated[preset_key] = round(new_w, 3)
        return updated

    @staticmethod
    def generate_insight(history):
        if not history: return "Complete your first session to receive personalised insights!"
        if len(history) < 2: return "A few more sessions and the AI will identify your optimal patterns."
        pd = {}
        for s in history:
            k     = s.get("preset", "unknown")
            delta = s.get("stress_score", 5) - s.get("post_score", 5)
            pd.setdefault(k, []).append(delta)
        best = max(pd, key=lambda k: sum(pd[k]) / len(pd[k]))
        avg  = sum(pd[best]) / len(pd[best])
        name  = PRESETS.get(best, {}).get("name", best)
        aroma = PRESETS.get(best, {}).get("aroma", "")
        music = PRESETS.get(best, {}).get("music", "")
        return (f"You respond best to {aroma.title()} + {music.title()} ('{name}'). "
                f"Average stress reduction: {avg:.1f} pts per session.")

    @staticmethod
    def should_suggest_counselor(history):
        if len(history) < 3: return False
        return all(s.get("stress_score", 0) >= 8.0 for s in history[-3:])


# ─────────────────────────────────────────────────────────────────────────────
# CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────

class AppController:
    def __init__(self):
        self.user_manager   = UserManager()
        self.ai_engine      = AIRecommendationEngine()
        self.stress_analyzer= StressAnalyzer()
        self.wearable       = MockWearable()
        self.voice_analyzer = MockVoiceAnalyzer()

        self.current_user         = None
        self.current_session      = None
        self.current_stress_score = 5.0
        self.current_stress_level = "Medium"
        self.current_stress_explanation = ""

        self.survey_score = 5.0
        self.heart_rate   = None
        self.hrv          = None
        self.voice_score  = None

        self._session_running   = False
        self._session_thread    = None
        self._timer_callback    = None
        self._session_end_callback = None
        self._action_in_progress = False

    # Auth
    def login(self, user_id):
        user = self.user_manager.get_user(user_id)
        if user:
            user.update_streak(); self.user_manager.save_user(user)
            self.current_user = user
        return user

    def get_available_users(self): return self.user_manager.list_users()

    def register_user(self, name, role="Employee"):
        name = name.strip()
        if not name: return None
        user_id = name.lower().replace(" ", "_")
        if self.user_manager.get_user(user_id): return None
        user = self.user_manager.create_user(user_id, name, role)
        self.current_user = user; return user

    def delete_user(self, user_id):
        data = self.user_manager._load_all()
        if user_id in data["users"]:
            del data["users"][user_id]; self.user_manager._save_all(data)
            if self.current_user and self.current_user.user_id == user_id:
                self.current_user = None
            return True
        return False

    def get_user_display_info(self, user_id):
        user = self.user_manager.get_user(user_id)
        if user:
            return {"name": user.name, "role": user.role, "emoji": user.avatar_emoji,
                    "sessions": user.total_sessions, "streak": user.streak}
        return None

    # Stress check
    def set_survey_score(self, score): self.survey_score = max(1.0, min(10.0, score))

    def connect_wearable(self):
        ok = self.wearable.connect()
        if ok: self.heart_rate = self.wearable.heart_rate; self.hrv = self.wearable.hrv
        return ok

    def disconnect_wearable(self): self.wearable.disconnect(); self.wearable.stop_streaming()

    def start_wearable_stream(self, callback=None):
        def _on(hr, hrv):
            self.heart_rate = hr; self.hrv = hrv
            if callback: callback(hr, hrv)
        self.wearable.start_streaming(_on)

    def start_voice_analysis(self, callback=None):
        def _on(score):
            self.voice_score = score
            if callback: callback(score)
        self.voice_analyzer.analyze(duration=3.0, callback=_on)

    def compute_stress(self):
        score, level, exp = self.stress_analyzer.compute_stress_score(
            self.survey_score, self.heart_rate, self.hrv, self.voice_score)
        self.current_stress_score = score
        self.current_stress_level = level
        self.current_stress_explanation = exp
        return score, level, exp

    def reset_stress_inputs(self):
        self.survey_score = 5.0; self.heart_rate = None
        self.hrv = None; self.voice_score = None
        self.wearable.disconnect(); self.wearable.stop_streaming()

    # AI
    def get_recommendation(self):
        if not self.current_user:
            key = "warm_lofi_lavender"; return key, PRESETS[key], "Please log in first."
        return self.ai_engine.recommend(
            self.current_stress_level, self.current_stress_score,
            self.current_user.preferences.get("preset_weights", {}),
            self.current_user.history)

    def get_recommended_duration(self): return self.ai_engine.recommend_duration(self.current_stress_score)
    def get_recommended_aroma_intensity(self): return self.ai_engine.recommend_aroma_intensity(self.current_stress_score)

    # Session
    def create_session(self, preset_key, lighting, music, aroma,
                       aroma_intensity, meditation, duration_minutes):
        self.current_session = Session(
            user_id=self.current_user.user_id if self.current_user else "guest",
            stress_score=self.current_stress_score, stress_level=self.current_stress_level,
            preset_key=preset_key, lighting=lighting, music=music, aroma=aroma,
            aroma_intensity=aroma_intensity, meditation=meditation,
            duration_minutes=duration_minutes,
            heart_rate=self.heart_rate, hrv=self.hrv, voice_score=self.voice_score)
        return self.current_session

    def start_session(self, timer_callback=None, end_callback=None):
        if not self.current_session or self._session_running: return
        self.current_session.start()
        self._session_running = True
        self._timer_callback = timer_callback
        self._session_end_callback = end_callback
        total = self.current_session.duration_minutes * 60

        def _run():
            elapsed = 0
            while self._session_running and elapsed < total:
                time.sleep(1)
                if not self._session_running: break
                elapsed += 1; self.current_session.elapsed_seconds = elapsed
                try:
                    if self._timer_callback: self._timer_callback(elapsed, total)
                except Exception: pass
            if self._session_running:
                self._session_running = False
                try:
                    if self._session_end_callback: self._session_end_callback()
                except Exception: pass

        self._session_thread = threading.Thread(target=_run, daemon=True)
        self._session_thread.start()

    def pause_session(self): self._session_running = False

    def resume_session(self, timer_callback=None, end_callback=None):
        if not self.current_session: return
        self._session_running = True
        self._timer_callback       = timer_callback or self._timer_callback
        self._session_end_callback = end_callback or self._session_end_callback
        total         = self.current_session.duration_minutes * 60
        start_elapsed = self.current_session.elapsed_seconds

        def _run():
            elapsed = start_elapsed
            while self._session_running and elapsed < total:
                time.sleep(1)
                if not self._session_running: break
                elapsed += 1; self.current_session.elapsed_seconds = elapsed
                try:
                    if self._timer_callback: self._timer_callback(elapsed, total)
                except Exception: pass
            if self._session_running:
                self._session_running = False
                try:
                    if self._session_end_callback: self._session_end_callback()
                except Exception: pass

        self._session_thread = threading.Thread(target=_run, daemon=True)
        self._session_thread.start()

    def end_session_early(self):
        self._session_running = False
        if self.current_session: self.current_session.end(early=True)

    def complete_session(self, post_score):
        if not self.current_session or not self.current_user: return
        self.current_session.post_score = post_score
        self.current_session.end(early=False)
        rec = self.current_session.to_history_dict()
        self.current_user.add_session_to_history(rec)
        updated = self.ai_engine.update_weights(
            self.current_user.preferences.get("preset_weights", {}),
            self.current_session.preset_key,
            self.current_session.stress_score, post_score)
        self.current_user.preferences["preset_weights"] = updated
        self.user_manager.save_user(self.current_user)

    @property
    def is_session_running(self): return self._session_running

    # Progress
    def get_weekly_stress_data(self):
        return self.current_user.get_recent_stress_scores(7) if self.current_user else []

    def get_ai_insight(self):
        if not self.current_user: return "Log in to see personalised insights."
        return self.ai_engine.generate_insight(self.current_user.history)

    def should_show_counselor_card(self):
        return self.ai_engine.should_suggest_counselor(self.current_user.history) if self.current_user else False

    def get_user_stats(self):
        if not self.current_user:
            return {"total_sessions": 0, "total_minutes": 0, "streak": 0, "avg_improvement": 0.0}
        deltas = self.current_user.get_feedback_deltas()
        return {
            "total_sessions": self.current_user.total_sessions,
            "total_minutes":  self.current_user.total_minutes,
            "streak":         self.current_user.streak,
            "avg_improvement": round(sum(deltas) / len(deltas), 1) if deltas else 0.0,
        }

    def clear_user_history(self):
        if self.current_user:
            self.user_manager.delete_all_history(self.current_user.user_id)
            self.current_user.history = []; self.current_user.total_sessions = 0
            self.current_user.total_minutes = 0; self.current_user.streak = 0

    def debounce_action(self):
        if self._action_in_progress: return False
        self._action_in_progress = True
        def _release(): time.sleep(0.5); self._action_in_progress.__class__  # noqa
        threading.Thread(target=lambda: (time.sleep(0.5), setattr(self, '_action_in_progress', False)), daemon=True).start()
        return True

    def cleanup(self):
        self._session_running = False
        self.wearable.stop_streaming(); self.wearable.disconnect()
        if self.current_session and not self.current_session.ended_at:
            self.current_session.end(early=True)
            if self.current_user:
                self.current_user.add_session_to_history(self.current_session.to_history_dict())
                self.user_manager.save_user(self.current_user)


# ─────────────────────────────────────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────────────────────────────────────

def _pick_font(candidates, fallback="Helvetica"):
    try:
        root = tk._default_root
        if root is None: return fallback
        available = set(tkfont.families(root))
        for name in candidates:
            if name in available: return name
    except Exception: pass
    return fallback


class Theme:
    PRIMARY          = ("#6C9BCF", "#7AAED4")
    SECONDARY        = ("#A6D1E6", "#4A8BAF")
    ACCENT_BLUSH     = ("#FFE2E2", "#4A3035")
    ACCENT_SAGE      = ("#B8E0D2", "#2D4A40")
    BACKGROUND       = ("#F8F9FD", "#1A1D23")
    TEXT             = ("#2C3E50", "#ECF0F1")
    TEXT_SECONDARY   = ("#7F8C8D", "#95A5A6")
    CARD_BG          = ("#FFFFFF", "#252830")
    SUCCESS          = ("#27AE60", "#2ECC71")
    WARNING          = ("#F39C12", "#F1C40F")
    DANGER           = ("#E74C3C", "#E74C3C")
    BORDER           = ("#E8EDF2", "#353840")
    DARK_PRIMARY     = ("#5B8DB8", "#5B8DB8")
    STRESS_LOW       = ("#27AE60", "#2ECC71")
    STRESS_MEDIUM    = ("#F39C12", "#F1C40F")
    STRESS_HIGH      = ("#E74C3C", "#E74C3C")
    LIGHTING_COLORS  = {"warm": ("#FFB347","#CC8A30"), "cool": ("#87CEEB","#5A9AB5"), "color_therapy": ("#DDA0DD","#9B6E9B")}
    SESSION_BG       = {"warm": ("#f5576c","#c44455"), "cool": ("#4facfe","#3A8AD0"), "color_therapy": ("#764ba2","#5C3980"), "default": ("#667eea","#5065C0")}
    SESSION_OVERLAY  = ("#8BADD4", "#6B8DAA")
    SESSION_TEXT     = ("#FFFFFF", "#FFFFFF")
    SESSION_TEXT_DIM = ("#E8E8E8", "#CCCCCC")
    HEADING_SIZE     = 24; SUBHEADING_SIZE = 18; BODY_SIZE = 14; SMALL_SIZE = 12; CAPTION_SIZE = 11
    CORNER_RADIUS    = 16; PADDING = 20; CARD_PADDING = 16; SPACING = 12
    MOOD_EMOJIS      = ["😌","🙂","😐","😕","😟","😣","😫","😰","😵","🤯"]
    _heading_font    = ""; _body_font = ""

    @staticmethod
    def hex(c): return c[0] if isinstance(c, (tuple, list)) else c

    @staticmethod
    def hex_dark(c): return (c[1] if len(c) > 1 else c[0]) if isinstance(c, (tuple, list)) else c

    @classmethod
    def _resolve_fonts(cls):
        if not cls._heading_font:
            cls._heading_font = _pick_font(("Poppins","Inter","SF Pro Display","Helvetica Neue","Segoe UI","Helvetica"))
        if not cls._body_font:
            cls._body_font = _pick_font(("Nunito","Inter","SF Pro Text","Helvetica Neue","Segoe UI","Helvetica"))

    @classmethod
    def get_font(cls, style="body", size=0):
        cls._resolve_fonts()
        if style == "heading":    return (cls._heading_font, size or cls.HEADING_SIZE, "bold")
        if style == "subheading": return (cls._heading_font, size or cls.SUBHEADING_SIZE, "bold")
        if style == "small":      return (cls._body_font, size or cls.SMALL_SIZE)
        if style == "caption":    return (cls._body_font, size or cls.CAPTION_SIZE)
        return (cls._body_font, size or cls.BODY_SIZE)

    @classmethod
    def get_emoji_font(cls, size=48):
        sys_name = platform.system()
        if sys_name == "Darwin":  return ("Apple Color Emoji", size)
        if sys_name == "Windows": return ("Segoe UI Emoji", size)
        return ("Noto Color Emoji", size)

    @classmethod
    def stress_color(cls, level):
        return {"Low": cls.STRESS_LOW, "Medium": cls.STRESS_MEDIUM, "High": cls.STRESS_HIGH}.get(level, cls.TEXT_SECONDARY)

    @classmethod
    def mood_emoji(cls, score):
        return cls.MOOD_EMOJIS[max(0, min(9, int(score) - 1))]


# ─────────────────────────────────────────────────────────────────────────────
# VIEW — LOGIN SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.controller = controller; self.parent_app = parent
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=Theme.BACKGROUND)
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

    def on_show(self):
        for w in self.scroll.winfo_children(): w.destroy()
        c = self.scroll

        logo = ctk.CTkFrame(c, fg_color=Theme.BACKGROUND); logo.pack(pady=(30,10))
        ctk.CTkLabel(logo, text="🧘", font=Theme.get_emoji_font(56)).pack()
        ctk.CTkLabel(logo, text="Mindful Work", font=Theme.get_font("heading",30), text_color=Theme.PRIMARY).pack(pady=(5,0))
        ctk.CTkLabel(logo, text="Smart Stress Relief Pod", font=Theme.get_font("body",13), text_color=Theme.TEXT_SECONDARY).pack()
        ctk.CTkLabel(logo, text="by FutureForward Wellness", font=Theme.get_font("caption"), text_color=Theme.TEXT_SECONDARY).pack(pady=(2,0))

        user_ids = self.controller.get_available_users()
        if user_ids:
            card = ctk.CTkFrame(c, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.CARD_BG, border_width=1, border_color=Theme.BORDER)
            card.pack(fill="x", padx=40, pady=(15,10))
            ctk.CTkLabel(card, text="Welcome back! Select your profile:", font=Theme.get_font("subheading",15), text_color=Theme.TEXT).pack(padx=Theme.CARD_PADDING, pady=(Theme.CARD_PADDING,8))
            uf = ctk.CTkFrame(card, fg_color=Theme.CARD_BG); uf.pack(padx=Theme.CARD_PADDING, pady=(0,Theme.CARD_PADDING))
            colors = [Theme.ACCENT_BLUSH, Theme.ACCENT_SAGE]
            cols = min(len(user_ids), 2); uf.grid_columnconfigure(list(range(cols)), weight=1)
            for i, uid in enumerate(user_ids):
                info = self.controller.get_user_display_info(uid)
                if not info: continue
                bf = ctk.CTkFrame(uf, corner_radius=12, fg_color=colors[i%2], border_width=1, border_color=Theme.BORDER)
                bf.grid(row=i//2, column=i%2, padx=6, pady=5, sticky="ew")
                tr = ctk.CTkFrame(bf, fg_color=colors[i%2]); tr.pack(fill="x", padx=6, pady=(6,0))
                ctk.CTkButton(tr, text="✕", width=26, height=26, font=Theme.get_font("body",13),
                              fg_color=Theme.DANGER, hover_color=("#C0392B","#C0392B"),
                              text_color=("#FFFFFF","#FFFFFF"), corner_radius=13,
                              command=lambda u=uid: self._delete(u)).pack(side="right")
                ctk.CTkLabel(bf, text=info["emoji"], font=Theme.get_emoji_font(32)).pack(pady=(4,2))
                ctk.CTkLabel(bf, text=info["name"], font=Theme.get_font("body",14), text_color=Theme.TEXT).pack()
                ctk.CTkLabel(bf, text=info["role"], font=Theme.get_font("caption"), text_color=Theme.TEXT_SECONDARY).pack()
                ctk.CTkLabel(bf, text=f"🔥 {info.get('streak',0)} day streak · {info.get('sessions',0)} sessions",
                             font=Theme.get_font("caption"), text_color=Theme.TEXT_SECONDARY).pack(pady=(2,4))
                ctk.CTkButton(bf, text=f"Login as {info['name'].split()[0]}", font=Theme.get_font("body",12),
                              fg_color=Theme.PRIMARY, hover_color=Theme.DARK_PRIMARY,
                              corner_radius=10, height=34,
                              command=lambda u=uid: self._login(u)).pack(padx=14, pady=(2,12))

        rc = ctk.CTkFrame(c, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.CARD_BG, border_width=1, border_color=Theme.PRIMARY)
        rc.pack(fill="x", padx=40, pady=(10,10))
        ctk.CTkLabel(rc, text="➕  New here? Create your profile", font=Theme.get_font("subheading",15), text_color=Theme.PRIMARY).pack(padx=Theme.CARD_PADDING, pady=(Theme.CARD_PADDING,8))
        form = ctk.CTkFrame(rc, fg_color=Theme.CARD_BG); form.pack(fill="x", padx=Theme.CARD_PADDING, pady=(0,Theme.CARD_PADDING))
        ctk.CTkLabel(form, text="Full Name", font=Theme.get_font("body",13), text_color=Theme.TEXT).pack(anchor="w")
        self.name_entry = ctk.CTkEntry(form, placeholder_text="e.g. Priya Sharma", font=Theme.get_font("body",13),
                                       fg_color=Theme.BACKGROUND, border_color=Theme.BORDER,
                                       text_color=Theme.TEXT, corner_radius=10, height=38)
        self.name_entry.pack(fill="x", pady=(4,10))
        ctk.CTkLabel(form, text="Role", font=Theme.get_font("body",13), text_color=Theme.TEXT).pack(anchor="w")
        self.role_var = ctk.StringVar(value="Employee")
        ctk.CTkOptionMenu(form, values=ROLES, variable=self.role_var, font=Theme.get_font("body",13),
                          fg_color=Theme.BACKGROUND, button_color=Theme.PRIMARY,
                          button_hover_color=Theme.DARK_PRIMARY, dropdown_fg_color=Theme.CARD_BG,
                          text_color=Theme.TEXT, corner_radius=10, height=38).pack(fill="x", pady=(4,12))
        self.error_lbl = ctk.CTkLabel(form, text="", font=Theme.get_font("small"), text_color=Theme.DANGER)
        self.error_lbl.pack()
        ctk.CTkButton(form, text="🚀  Register & Start", font=Theme.get_font("body",15),
                      fg_color=Theme.SUCCESS, hover_color=("#219A52","#219A52"),
                      corner_radius=12, height=44, command=self._register).pack(fill="x", pady=(4,0))

        ctk.CTkLabel(c, text="Transform workplace stress into focus, calmness, and productivity",
                     font=Theme.get_font("caption"), text_color=Theme.TEXT_SECONDARY).pack(pady=(10,20))

    def _delete(self, uid):
        if not self.controller.debounce_action(): return
        info = self.controller.get_user_display_info(uid)
        name = info["name"] if info else uid
        if messagebox.askyesno("Delete Profile", f"Delete {name}'s profile?\n\nAll history will be removed.", icon="warning"):
            self.controller.delete_user(uid); self.on_show()

    def _login(self, uid):
        if not self.controller.debounce_action(): return
        user = self.controller.login(uid)
        if user: self.parent_app.show_screen("home")

    def _register(self):
        if not self.controller.debounce_action(): return
        name = self.name_entry.get().strip()
        if not name: self.error_lbl.configure(text="⚠️ Please enter your name."); return
        if len(name) < 2: self.error_lbl.configure(text="⚠️ Name must be at least 2 characters."); return
        user = self.controller.register_user(name, self.role_var.get())
        if user is None: self.error_lbl.configure(text="⚠️ A user with this name already exists."); return
        self.error_lbl.configure(text=""); self.controller.login(user.user_id)
        self.parent_app.show_screen("home")


# ─────────────────────────────────────────────────────────────────────────────
# VIEW — HOME SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class HomeScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.controller = controller; self.parent_app = parent
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)
        hdr = ctk.CTkFrame(self, fg_color=Theme.BACKGROUND)
        hdr.grid(row=0, column=0, sticky="ew", padx=15, pady=(15,0))
        ctk.CTkLabel(hdr, text="🏠  Home", font=Theme.get_font("heading",20), text_color=Theme.TEXT).pack(side="left")
        ctk.CTkButton(hdr, text="← Logout", font=Theme.get_font("body",13),
                      fg_color=Theme.CARD_BG, text_color=Theme.DANGER, hover_color=Theme.ACCENT_BLUSH,
                      width=80, height=32, corner_radius=8, command=self._logout).pack(side="right")
        self.content = ctk.CTkScrollableFrame(self, fg_color=Theme.BACKGROUND)
        self.content.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.content.grid_columnconfigure(0, weight=1)

    def on_show(self):
        for w in self.content.winfo_children(): w.destroy()
        user = self.controller.current_user
        if not user: return
        first = user.name.split()[0]

        g = ctk.CTkFrame(self.content, fg_color=Theme.BACKGROUND); g.pack(fill="x", pady=(10,5))
        ctk.CTkLabel(g, text=f"{user.avatar_emoji}  Hi {first}, how are you feeling?",
                     font=Theme.get_font("heading",22), text_color=Theme.PRIMARY, anchor="w").pack(fill="x")
        ctk.CTkLabel(g, text=f"{user.role} · 🔥 {user.streak} day streak",
                     font=Theme.get_font("body"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x", pady=(2,0))

        cta = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.PRIMARY); cta.pack(fill="x", pady=15)
        inn = ctk.CTkFrame(cta, fg_color=Theme.PRIMARY); inn.pack(fill="x", padx=Theme.CARD_PADDING, pady=Theme.CARD_PADDING)
        ctk.CTkLabel(inn, text="Ready for a wellness break?", font=Theme.get_font("subheading",18),
                     text_color=("#FFFFFF","#FFFFFF"), anchor="w").pack(fill="x")
        ctk.CTkLabel(inn, text="Take 60 seconds to check your stress level and get a personalised pod session.",
                     font=Theme.get_font("body",13), text_color=("#E8E8E8","#CCCCCC"),
                     anchor="w", wraplength=400).pack(fill="x", pady=(4,12))
        ctk.CTkButton(inn, text="🧠  Begin Stress Check", font=Theme.get_font("body",15),
                      fg_color=("#FFFFFF","#FFFFFF"), text_color=Theme.PRIMARY, hover_color=Theme.ACCENT_BLUSH,
                      corner_radius=12, height=44, command=self._start_check).pack(fill="x")

        ctk.CTkLabel(self.content, text="Today's Wellness Summary", font=Theme.get_font("subheading",16),
                     text_color=Theme.TEXT, anchor="w").pack(fill="x", pady=(10,8))
        stats = self.controller.get_user_stats()
        sg = ctk.CTkFrame(self.content, fg_color=Theme.BACKGROUND); sg.pack(fill="x")
        sg.grid_columnconfigure((0,1), weight=1)
        for i, (e, lbl, val) in enumerate([("🧘","Sessions",str(stats["total_sessions"])),
                                            ("⏱️","Minutes",str(stats["total_minutes"])),
                                            ("🔥","Streak",f"{stats['streak']} days"),
                                            ("📈","Avg Relief",f"{stats['avg_improvement']:+.1f} pts")]):
            card = ctk.CTkFrame(sg, corner_radius=12, fg_color=Theme.CARD_BG, border_width=1, border_color=Theme.BORDER)
            card.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            ci = ctk.CTkFrame(card, fg_color=Theme.CARD_BG); ci.pack(padx=12, pady=10)
            ctk.CTkLabel(ci, text=f"{e} {lbl}", font=Theme.get_font("caption"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
            ctk.CTkLabel(ci, text=val, font=Theme.get_font("subheading",20), text_color=Theme.TEXT).pack(anchor="w")

        ic = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.ACCENT_SAGE, border_width=1, border_color=Theme.BORDER)
        ic.pack(fill="x", pady=(15,5))
        ii = ctk.CTkFrame(ic, fg_color=Theme.ACCENT_SAGE); ii.pack(fill="x", padx=Theme.CARD_PADDING, pady=Theme.CARD_PADDING)
        ctk.CTkLabel(ii, text="💡 AI Insight", font=Theme.get_font("body",14), text_color=Theme.TEXT, anchor="w").pack(fill="x")
        ctk.CTkLabel(ii, text=self.controller.get_ai_insight(), font=Theme.get_font("body",13),
                     text_color=Theme.TEXT, anchor="w", wraplength=380, justify="left").pack(fill="x", pady=(4,0))

        if self.controller.should_show_counselor_card():
            cc = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.ACCENT_BLUSH, border_width=1, border_color=Theme.DANGER)
            cc.pack(fill="x", pady=(10,5))
            ctk.CTkLabel(cc, text="🤝  We've noticed consistently high stress levels.\nConsider reaching out to your HR team or a wellness counselor.",
                         font=Theme.get_font("body",13), text_color=Theme.TEXT, wraplength=380, justify="left").pack(padx=Theme.CARD_PADDING, pady=Theme.CARD_PADDING)

        ctk.CTkButton(self.content, text="📊  View Progress & History", font=Theme.get_font("body",13),
                      fg_color=Theme.SECONDARY, text_color=Theme.TEXT, hover_color=Theme.ACCENT_SAGE,
                      corner_radius=10, height=40, command=self._view_progress).pack(fill="x", pady=(15,10))

    def _start_check(self):
        if not self.controller.debounce_action(): return
        self.controller.reset_stress_inputs(); self.parent_app.show_screen("stress_check")

    def _view_progress(self):
        if not self.controller.debounce_action(): return
        self.parent_app.show_screen("feedback")

    def _logout(self):
        if not self.controller.debounce_action(): return
        self.controller.current_user = None; self.parent_app.show_screen("login")


# ─────────────────────────────────────────────────────────────────────────────
# VIEW — STRESS CHECK SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class StressCheckScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.controller = controller; self.parent_app = parent
        self._wearable_connected = False; self._voice_done = False
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)
        hdr = ctk.CTkFrame(self, fg_color=Theme.BACKGROUND)
        hdr.grid(row=0, column=0, sticky="ew", padx=15, pady=(15,5))
        ctk.CTkButton(hdr, text="← Back", font=Theme.get_font("body",13),
                      fg_color=Theme.CARD_BG, text_color=Theme.PRIMARY, hover_color=Theme.BORDER,
                      width=70, height=32, corner_radius=8,
                      command=lambda: self.parent_app.show_screen("home")).pack(side="left")
        ctk.CTkLabel(hdr, text="Stress Check", font=Theme.get_font("heading",20), text_color=Theme.TEXT).pack(side="left", padx=15)
        self.content = ctk.CTkScrollableFrame(self, fg_color=Theme.BACKGROUND)
        self.content.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.content.grid_columnconfigure(0, weight=1)

    def on_show(self):
        for w in self.content.winfo_children(): w.destroy()
        self._wearable_connected = False; self._voice_done = False
        self.controller.reset_stress_inputs()

        # Survey
        sc = self._card("😌 How are you feeling right now?"); sc.pack(fill="x", pady=8)
        self.emoji_lbl = ctk.CTkLabel(sc, text=Theme.mood_emoji(5), font=Theme.get_emoji_font(48)); self.emoji_lbl.pack(pady=(5,0))
        self.survey_slider = ctk.CTkSlider(sc, from_=1, to=10, number_of_steps=9, width=300, height=20,
                                           fg_color=Theme.BORDER, progress_color=Theme.PRIMARY,
                                           button_color=Theme.PRIMARY, button_hover_color=Theme.DARK_PRIMARY,
                                           command=self._on_survey)
        self.survey_slider.set(5); self.survey_slider.pack(pady=8)
        sf = ctk.CTkFrame(sc, fg_color=Theme.CARD_BG); sf.pack(fill="x", padx=30)
        ctk.CTkLabel(sf, text="Calm", font=Theme.get_font("caption"), text_color=Theme.STRESS_LOW).pack(side="left")
        self.score_lbl = ctk.CTkLabel(sf, text="5 / 10", font=Theme.get_font("body"), text_color=Theme.TEXT)
        self.score_lbl.pack(side="left", expand=True)
        ctk.CTkLabel(sf, text="Stressed", font=Theme.get_font("caption"), text_color=Theme.STRESS_HIGH).pack(side="right")

        # Wearable
        wc = self._card("⌚ Wearable Data (Optional)"); wc.pack(fill="x", pady=8)
        ctk.CTkLabel(wc, text="Connect your smartwatch for physiological stress indicators.",
                     font=Theme.get_font("small"), text_color=Theme.TEXT_SECONDARY, wraplength=350).pack()
        self.wear_btn = ctk.CTkButton(wc, text="🔗  Connect Wearable", font=Theme.get_font("body",13),
                                      fg_color=Theme.SECONDARY, text_color=Theme.TEXT, hover_color=Theme.ACCENT_SAGE,
                                      corner_radius=10, height=38, command=self._connect_wearable)
        self.wear_btn.pack(pady=8)
        self.hr_lbl  = ctk.CTkLabel(wc, text="", font=Theme.get_font("body"), text_color=Theme.TEXT); self.hr_lbl.pack()
        self.hrv_lbl = ctk.CTkLabel(wc, text="", font=Theme.get_font("body"), text_color=Theme.TEXT); self.hrv_lbl.pack()
        self.wear_status = ctk.CTkLabel(wc, text="", font=Theme.get_font("caption"), text_color=Theme.TEXT_SECONDARY); self.wear_status.pack(pady=(0,5))

        # Voice
        vc = self._card("🎙️ Voice Tone Analysis (Optional)"); vc.pack(fill="x", pady=8)
        ctk.CTkLabel(vc, text="Speak naturally for a few seconds to analyse stress in your voice.",
                     font=Theme.get_font("small"), text_color=Theme.TEXT_SECONDARY, wraplength=350).pack()
        self.voice_btn = ctk.CTkButton(vc, text="🎤  Analyse Voice", font=Theme.get_font("body",13),
                                       fg_color=Theme.SECONDARY, text_color=Theme.TEXT, hover_color=Theme.ACCENT_SAGE,
                                       corner_radius=10, height=38, command=self._start_voice)
        self.voice_btn.pack(pady=8)
        self.voice_status = ctk.CTkLabel(vc, text="", font=Theme.get_font("body"), text_color=Theme.TEXT); self.voice_status.pack(pady=(0,5))

        ctk.CTkButton(self.content, text="🧠  Compute Stress Score", font=Theme.get_font("body",15),
                      fg_color=Theme.PRIMARY, hover_color=Theme.DARK_PRIMARY, corner_radius=12,
                      height=46, command=self._compute).pack(fill="x", pady=(15,5))
        self.result_frame = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.BACKGROUND)
        self.result_frame.pack(fill="x", pady=(5,15))

    def _card(self, title):
        c = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.CARD_BG, border_width=1, border_color=Theme.BORDER)
        ctk.CTkLabel(c, text=title, font=Theme.get_font("body",15), text_color=Theme.TEXT).pack(anchor="w", padx=Theme.CARD_PADDING, pady=(Theme.CARD_PADDING,5))
        return c

    def _on_survey(self, val):
        s = round(val); self.emoji_lbl.configure(text=Theme.mood_emoji(s))
        self.score_lbl.configure(text=f"{s} / 10"); self.controller.set_survey_score(float(s))

    def _connect_wearable(self):
        if self._wearable_connected:
            self.controller.disconnect_wearable(); self._wearable_connected = False
            self.wear_btn.configure(text="🔗  Connect Wearable")
            self.hr_lbl.configure(text=""); self.hrv_lbl.configure(text="")
            self.wear_status.configure(text="Disconnected"); return
        if self.controller.connect_wearable():
            self._wearable_connected = True; self.wear_btn.configure(text="⏏️  Disconnect")
            self.wear_status.configure(text="✅ Connected — streaming live data", text_color=Theme.SUCCESS)
            def _upd(hr, hrv):
                try:
                    self.hr_lbl.configure(text=f"❤️ Heart Rate: {hr:.0f} bpm")
                    self.hrv_lbl.configure(text=f"📊 HRV: {hrv:.0f} ms")
                except Exception: pass
            self.controller.start_wearable_stream(callback=_upd)
            _upd(self.controller.heart_rate or 72, self.controller.hrv or 50)
        else:
            self.wear_status.configure(text="⚠️ Could not connect.", text_color=Theme.WARNING)

    def _start_voice(self):
        if self._voice_done: return
        self.voice_btn.configure(state="disabled", text="🎤  Analysing...")
        self.voice_status.configure(text="🔴 Recording...", text_color=Theme.DANGER)
        def _done(score):
            try:
                self._voice_done = True
                self.voice_btn.configure(state="normal", text="✅  Analysis Complete")
                self.voice_status.configure(text=f"Voice stress score: {score:.1f} / 10", text_color=Theme.TEXT)
            except Exception: pass
        self.controller.start_voice_analysis(callback=_done)

    def _compute(self):
        if not self.controller.debounce_action(): return
        score, level, exp = self.controller.compute_stress()
        for w in self.result_frame.winfo_children(): w.destroy()
        self.result_frame.configure(fg_color=Theme.CARD_BG, border_width=1, border_color=Theme.stress_color(level))
        ctk.CTkLabel(self.result_frame, text=f"Stress Level: {level}", font=Theme.get_font("subheading",18),
                     text_color=Theme.stress_color(level)).pack(padx=Theme.CARD_PADDING, pady=(Theme.CARD_PADDING,4))
        ctk.CTkLabel(self.result_frame, text=f"Score: {score} / 10", font=Theme.get_font("heading",28), text_color=Theme.TEXT).pack()
        ctk.CTkLabel(self.result_frame, text=exp, font=Theme.get_font("small"), text_color=Theme.TEXT_SECONDARY,
                     wraplength=360, justify="left").pack(padx=Theme.CARD_PADDING, pady=(8,4))
        ctk.CTkButton(self.result_frame, text="🎯  Get Pod Recommendation →", font=Theme.get_font("body",15),
                      fg_color=Theme.PRIMARY, hover_color=Theme.DARK_PRIMARY, corner_radius=12, height=44,
                      command=self._go_pod).pack(fill="x", padx=Theme.CARD_PADDING, pady=(10,Theme.CARD_PADDING))
        self.controller.wearable.stop_streaming()

    def _go_pod(self):
        if not self.controller.debounce_action(): return
        self.parent_app.show_screen("pod_customization")


# ─────────────────────────────────────────────────────────────────────────────
# VIEW — POD CUSTOMIZATION SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class PodCustomizationScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.controller = controller; self.parent_app = parent
        self._recommended_key = ""; self._selected_preset = ""
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)
        hdr = ctk.CTkFrame(self, fg_color=Theme.BACKGROUND)
        hdr.grid(row=0, column=0, sticky="ew", padx=15, pady=(15,5))
        ctk.CTkButton(hdr, text="← Back", font=Theme.get_font("body",13),
                      fg_color=Theme.CARD_BG, text_color=Theme.PRIMARY, hover_color=Theme.BORDER,
                      width=70, height=32, corner_radius=8,
                      command=lambda: self.parent_app.show_screen("stress_check")).pack(side="left")
        ctk.CTkLabel(hdr, text="Pod Setup", font=Theme.get_font("heading",20), text_color=Theme.TEXT).pack(side="left", padx=15)
        self.content = ctk.CTkScrollableFrame(self, fg_color=Theme.BACKGROUND)
        self.content.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.content.grid_columnconfigure(0, weight=1)

    def on_show(self):
        for w in self.content.winfo_children(): w.destroy()
        rec_key, rec_info, reasoning = self.controller.get_recommendation()
        self._recommended_key = rec_key; self._selected_preset = rec_key

        rc = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.ACCENT_SAGE, border_width=2, border_color=Theme.SUCCESS)
        rc.pack(fill="x", pady=(5,10))
        ri = ctk.CTkFrame(rc, fg_color=Theme.ACCENT_SAGE); ri.pack(fill="x", padx=Theme.CARD_PADDING, pady=Theme.CARD_PADDING)
        ctk.CTkLabel(ri, text="⭐ Recommended for you", font=Theme.get_font("body",13), text_color=Theme.SUCCESS,
                     fg_color=Theme.CARD_BG, corner_radius=8).pack(anchor="w")
        ctk.CTkLabel(ri, text=rec_info["name"], font=Theme.get_font("subheading",18), text_color=Theme.TEXT, anchor="w").pack(fill="x", pady=(8,2))
        ctk.CTkLabel(ri, text=rec_info["description"], font=Theme.get_font("body",13), text_color=Theme.TEXT_SECONDARY, anchor="w", wraplength=380).pack(fill="x")
        ctk.CTkLabel(ri, text=f"💡 {reasoning}", font=Theme.get_font("small"), text_color=Theme.TEXT_SECONDARY,
                     anchor="w", wraplength=380, justify="left").pack(fill="x", pady=(6,0))

        ctk.CTkLabel(self.content, text="Choose a Preset", font=Theme.get_font("subheading",16), text_color=Theme.TEXT, anchor="w").pack(fill="x", pady=(10,5))
        self.preset_btns = {}
        pf = ctk.CTkFrame(self.content, fg_color=Theme.BACKGROUND); pf.pack(fill="x")
        pf.grid_columnconfigure((0,1), weight=1)
        for i, (key, preset) in enumerate(PRESETS.items()):
            is_rec = key == rec_key
            btn = ctk.CTkButton(pf,
                text=f"{'⭐ ' if is_rec else ''}{preset['name']}\n{preset['lighting'].title()} · {preset['music'].title()} · {preset['aroma'].title()}",
                font=Theme.get_font("small"),
                fg_color=Theme.PRIMARY if is_rec else Theme.CARD_BG,
                text_color=("#FFFFFF","#FFFFFF") if is_rec else Theme.TEXT,
                hover_color=Theme.DARK_PRIMARY if is_rec else Theme.BORDER,
                border_width=1, border_color=Theme.PRIMARY if is_rec else Theme.BORDER,
                corner_radius=12, height=60, command=lambda k=key: self._select_preset(k))
            btn.grid(row=i//2, column=i%2, padx=4, pady=4, sticky="ew")
            self.preset_btns[key] = btn

        ctk.CTkLabel(self.content, text="Fine-Tune Settings", font=Theme.get_font("subheading",16), text_color=Theme.TEXT, anchor="w").pack(fill="x", pady=(15,5))
        cc = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.CARD_BG, border_width=1, border_color=Theme.BORDER); cc.pack(fill="x", pady=5)
        ci = ctk.CTkFrame(cc, fg_color=Theme.CARD_BG); ci.pack(fill="x", padx=Theme.CARD_PADDING, pady=Theme.CARD_PADDING)

        ctk.CTkLabel(ci, text="💡 Lighting", font=Theme.get_font("body",13), text_color=Theme.TEXT).pack(anchor="w", pady=(0,4))
        self.lighting_var = ctk.StringVar(value=rec_info.get("lighting","warm"))
        ctk.CTkSegmentedButton(ci, values=LIGHTING_OPTIONS, variable=self.lighting_var,
                               font=Theme.get_font("small"), fg_color=Theme.BORDER,
                               selected_color=Theme.PRIMARY, selected_hover_color=Theme.DARK_PRIMARY,
                               corner_radius=10).pack(fill="x", pady=(0,10))

        ctk.CTkLabel(ci, text="🎵 Music", font=Theme.get_font("body",13), text_color=Theme.TEXT).pack(anchor="w", pady=(0,4))
        self.music_var = ctk.StringVar(value=rec_info.get("music","lo-fi"))
        ctk.CTkOptionMenu(ci, values=MUSIC_OPTIONS, variable=self.music_var, font=Theme.get_font("body",13),
                          fg_color=Theme.SECONDARY, button_color=Theme.PRIMARY, button_hover_color=Theme.DARK_PRIMARY,
                          dropdown_fg_color=Theme.CARD_BG, corner_radius=10, height=36).pack(fill="x", pady=(0,10))

        ctk.CTkLabel(ci, text="🌸 Aroma", font=Theme.get_font("body",13), text_color=Theme.TEXT).pack(anchor="w", pady=(0,4))
        self.aroma_var = ctk.StringVar(value=rec_info.get("aroma","lavender"))
        ctk.CTkSegmentedButton(ci, values=AROMA_OPTIONS, variable=self.aroma_var,
                               font=Theme.get_font("small"), fg_color=Theme.BORDER,
                               selected_color=Theme.PRIMARY, selected_hover_color=Theme.DARK_PRIMARY,
                               corner_radius=10).pack(fill="x", pady=(0,8))
        ctk.CTkLabel(ci, text="Aroma Intensity", font=Theme.get_font("caption"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        self.aroma_slider = ctk.CTkSlider(ci, from_=1, to=10, number_of_steps=9, height=16,
                                          fg_color=Theme.BORDER, progress_color=Theme.ACCENT_SAGE, button_color=Theme.PRIMARY)
        self.aroma_slider.set(self.controller.get_recommended_aroma_intensity()); self.aroma_slider.pack(fill="x", pady=(2,10))

        ctk.CTkLabel(ci, text="🧘 Breathing Exercise", font=Theme.get_font("body",13), text_color=Theme.TEXT).pack(anchor="w", pady=(0,4))
        self.med_var = ctk.StringVar(value="box_breathing")
        ctk.CTkSegmentedButton(ci, values=["box_breathing","4_7_8_breathing"], variable=self.med_var,
                               font=Theme.get_font("small"), fg_color=Theme.BORDER,
                               selected_color=Theme.PRIMARY, selected_hover_color=Theme.DARK_PRIMARY,
                               corner_radius=10).pack(fill="x", pady=(0,10))

        ctk.CTkLabel(ci, text="⏱️ Session Duration", font=Theme.get_font("body",13), text_color=Theme.TEXT).pack(anchor="w", pady=(0,4))
        dur_strs = [f"{d} min" for d in DURATION_OPTIONS]
        self.dur_var = ctk.StringVar(value=f"{self.controller.get_recommended_duration()} min")
        ctk.CTkSegmentedButton(ci, values=dur_strs, variable=self.dur_var,
                               font=Theme.get_font("small"), fg_color=Theme.BORDER,
                               selected_color=Theme.PRIMARY, selected_hover_color=Theme.DARK_PRIMARY,
                               corner_radius=10).pack(fill="x", pady=(0,5))

        ctk.CTkLabel(self.content, text="Preview", font=Theme.get_font("subheading",16), text_color=Theme.TEXT, anchor="w").pack(fill="x", pady=(15,5))
        self.preview_card = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS,
                                         fg_color=Theme.LIGHTING_COLORS.get(rec_info.get("lighting","warm"), Theme.CARD_BG), height=80)
        self.preview_card.pack(fill="x", pady=5)
        self.preview_text = ctk.CTkLabel(self.preview_card, text=self._pstr(rec_info), font=Theme.get_font("body",13),
                                          text_color=Theme.TEXT, wraplength=380)
        self.preview_text.pack(padx=Theme.CARD_PADDING, pady=Theme.CARD_PADDING)
        self.lighting_var.trace_add("write", lambda *_: self._upd_preview())
        self.music_var.trace_add("write",   lambda *_: self._upd_preview())
        self.aroma_var.trace_add("write",   lambda *_: self._upd_preview())

        ctk.CTkButton(self.content, text="▶️  Start Session", font=Theme.get_font("body",16),
                      fg_color=Theme.SUCCESS, hover_color=("#219A52","#219A52"),
                      corner_radius=14, height=50, command=self._start).pack(fill="x", pady=(15,20))

    def _pstr(self, info):
        return (f"💡 {info.get('lighting','warm').replace('_',' ').title()}  ·  "
                f"🎵 {info.get('music','lo-fi').title()}  ·  🌸 {info.get('aroma','lavender').title()}")

    def _upd_preview(self):
        l = self.lighting_var.get(); m = self.music_var.get(); a = self.aroma_var.get()
        self.preview_card.configure(fg_color=Theme.LIGHTING_COLORS.get(l, Theme.CARD_BG))
        self.preview_text.configure(text=f"💡 {l.replace('_',' ').title()}  ·  🎵 {m.title()}  ·  🌸 {a.title()}")

    def _select_preset(self, key):
        self._selected_preset = key; p = PRESETS[key]
        for k, btn in self.preset_btns.items():
            if k == key:
                btn.configure(fg_color=Theme.PRIMARY, text_color=("#FFFFFF","#FFFFFF"), border_color=Theme.PRIMARY)
            else:
                btn.configure(fg_color=Theme.CARD_BG, text_color=Theme.TEXT,
                              border_color=Theme.PRIMARY if k == self._recommended_key else Theme.BORDER)
        self.lighting_var.set(p["lighting"]); self.music_var.set(p["music"]); self.aroma_var.set(p["aroma"])

    def _start(self):
        if not self.controller.debounce_action(): return
        try: dur = int(self.dur_var.get().replace(" min",""))
        except (ValueError, AttributeError): dur = 10
        self.controller.create_session(
            preset_key=self._selected_preset, lighting=self.lighting_var.get(),
            music=self.music_var.get(), aroma=self.aroma_var.get(),
            aroma_intensity=int(self.aroma_slider.get()),
            meditation=self.med_var.get(), duration_minutes=dur)
        self.parent_app.show_screen("active_session")


# ─────────────────────────────────────────────────────────────────────────────
# VIEW — ACTIVE SESSION SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class ActiveSessionScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Theme.SESSION_BG["default"])
        self.controller = controller; self.parent_app = parent
        self._animation_running = False; self._paused = False
        self._breathing_phase_idx = 0; self._breathing_tick = 0
        self._pattern = BREATHING_PATTERNS["box_breathing"]; self._bg_hex = "#667eea"
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(2, weight=1)

        self.top_bar = ctk.CTkFrame(self, fg_color=Theme.SESSION_BG["default"])
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(15,0))
        self.session_lbl = ctk.CTkLabel(self.top_bar, text="Session Active", font=Theme.get_font("body",14), text_color=Theme.SESSION_TEXT)
        self.session_lbl.pack(side="left")
        self.end_btn = ctk.CTkButton(self.top_bar, text="End Early", font=Theme.get_font("small"),
                                     fg_color=Theme.SESSION_OVERLAY, text_color=Theme.SESSION_TEXT,
                                     corner_radius=8, width=80, height=30, command=self._end_early)
        self.end_btn.pack(side="right")
        self.pause_btn = ctk.CTkButton(self.top_bar, text="⏸ Pause", font=Theme.get_font("small"),
                                       fg_color=Theme.SESSION_OVERLAY, text_color=Theme.SESSION_TEXT,
                                       corner_radius=8, width=80, height=30, command=self._toggle_pause)
        self.pause_btn.pack(side="right", padx=(0,8))

        self.info_frame = ctk.CTkFrame(self, fg_color=Theme.SESSION_BG["default"])
        self.info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10,0))
        self.music_lbl = ctk.CTkLabel(self.info_frame, text="🎵 Lo-fi", font=Theme.get_font("body",13), text_color=Theme.SESSION_TEXT_DIM)
        self.music_lbl.pack(side="left")
        self.aroma_lbl = ctk.CTkLabel(self.info_frame, text="🌸 Lavender", font=Theme.get_font("body",13), text_color=Theme.SESSION_TEXT_DIM)
        self.aroma_lbl.pack(side="right")

        self.canvas_frame = ctk.CTkFrame(self, fg_color=Theme.SESSION_BG["default"])
        self.canvas_frame.grid(row=2, column=0, sticky="nsew")
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="#667eea", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.timer_lbl = ctk.CTkLabel(self, text="00:00", font=Theme.get_font("heading",36), text_color=Theme.SESSION_TEXT)
        self.timer_lbl.grid(row=3, column=0, pady=(5,5))
        self.progress_bar = ctk.CTkProgressBar(self, width=300, height=6,
                                               fg_color=Theme.SESSION_OVERLAY,
                                               progress_color=("#FFFFFF","#FFFFFF"), corner_radius=3)
        self.progress_bar.set(0); self.progress_bar.grid(row=4, column=0, pady=(0,20))

    def on_show(self):
        s = self.controller.current_session
        if not s: return
        bg = Theme.SESSION_BG.get(s.lighting, Theme.SESSION_BG["default"])
        self._bg_hex = Theme.hex_dark(bg)
        self.configure(fg_color=bg); self.top_bar.configure(fg_color=bg)
        self.info_frame.configure(fg_color=bg); self.canvas_frame.configure(fg_color=bg)
        self.canvas.configure(bg=self._bg_hex)
        self.music_lbl.configure(text=f"🎵 {s.music.title()}")
        self.aroma_lbl.configure(text=f"🌸 {s.aroma.title()} ({s.aroma_intensity})")
        self.session_lbl.configure(text=f"🧘 {PRESETS.get(s.preset_key,{}).get('name','Custom')}")
        self._paused = False; self.pause_btn.configure(text="⏸ Pause")
        self._animation_running = True
        self._pattern = BREATHING_PATTERNS.get(s.meditation, BREATHING_PATTERNS["box_breathing"])
        self._breathing_phase_idx = 0; self._breathing_tick = 0
        self.controller.start_session(timer_callback=self._on_tick, end_callback=self._on_complete)
        self._animate()

    def _on_canvas_resize(self, event): self.canvas.delete("all"); self._draw_circle(0.5)

    def _draw_circle(self, scale):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 10 or h < 10: return
        cx, cy = w / 2, h / 2; maxr = min(w, h) * 0.30; minr = maxr * 0.35
        r = minr + (maxr - minr) * scale
        self.canvas.delete("circle","phase_text")
        self.canvas.create_oval(cx-r-10,cy-r-10,cx+r+10,cy+r+10, fill="", outline="#9BAFC8", width=15, tags="circle")
        self.canvas.create_oval(cx-r,cy-r,cx+r,cy+r, fill="#8BADD4", outline="#C8D8E8", width=3, tags="circle")
        phases = self._pattern["phases"]; phase_name = phases[self._breathing_phase_idx % len(phases)][0]
        self.canvas.create_text(cx, cy-10, text=phase_name, fill="#FFFFFF", font=Theme.get_font("subheading",20), tags="phase_text")
        self.canvas.create_text(cx, cy+20, text=self._pattern["name"], fill="#D8E4F0", font=Theme.get_font("small"), tags="phase_text")

    def _animate(self):
        if not self._animation_running or self._paused: return
        phases = self._pattern["phases"]; idx = self._breathing_phase_idx % len(phases)
        name, dur = phases[idx]; prog = self._breathing_tick / (dur * 10)
        scale = prog if "In" in name else (1.0 - prog if "Out" in name else (1.0 if idx > 0 and "In" in phases[idx-1][0] else 0.2))
        self._draw_circle(max(0.15, min(1.0, scale)))
        self._breathing_tick += 1
        if self._breathing_tick >= dur * 10: self._breathing_tick = 0; self._breathing_phase_idx += 1
        if self._animation_running: self.after(100, self._animate)

    def _on_tick(self, elapsed, total):
        rem = max(0, total - elapsed)
        try:
            self.timer_lbl.configure(text=f"{rem//60:02d}:{rem%60:02d}")
            self.progress_bar.set(elapsed / total if total else 0)
        except Exception: pass

    def _on_complete(self):
        self._animation_running = False
        try: self.parent_app.show_screen("feedback")
        except Exception: pass

    def _toggle_pause(self):
        if self._paused:
            self._paused = False; self.pause_btn.configure(text="⏸ Pause")
            self.controller.resume_session(timer_callback=self._on_tick, end_callback=self._on_complete)
            self._animation_running = True; self._animate()
        else:
            self._paused = True; self.pause_btn.configure(text="▶ Resume")
            self.controller.pause_session(); self._animation_running = False

    def _end_early(self):
        if not self.controller.debounce_action(): return
        self._animation_running = False; self.controller.end_session_early()
        self.parent_app.show_screen("feedback")

    def on_hide(self): self._animation_running = False


# ─────────────────────────────────────────────────────────────────────────────
# VIEW — FEEDBACK / PROGRESS SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class FeedbackScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.controller = controller; self.parent_app = parent; self._chart_canvas = None
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)
        hdr = ctk.CTkFrame(self, fg_color=Theme.BACKGROUND)
        hdr.grid(row=0, column=0, sticky="ew", padx=15, pady=(15,5))
        ctk.CTkButton(hdr, text="← Home", font=Theme.get_font("body",13),
                      fg_color=Theme.CARD_BG, text_color=Theme.PRIMARY, hover_color=Theme.BORDER,
                      width=70, height=32, corner_radius=8, command=self._go_home).pack(side="left")
        ctk.CTkLabel(hdr, text="Progress", font=Theme.get_font("heading",20), text_color=Theme.TEXT).pack(side="left", padx=15)
        self.content = ctk.CTkScrollableFrame(self, fg_color=Theme.BACKGROUND)
        self.content.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.content.grid_columnconfigure(0, weight=1)

    def on_show(self):
        for w in self.content.winfo_children(): w.destroy()
        self._chart_canvas = None
        session = self.controller.current_session
        if session and session.started_at: self._build_feedback()
        self._build_stats(); self._build_chart(); self._build_insight()
        af = ctk.CTkFrame(self.content, fg_color=Theme.BACKGROUND); af.pack(fill="x", pady=(15,5))
        ctk.CTkButton(af, text="🧠  New Stress Check", font=Theme.get_font("body",14),
                      fg_color=Theme.PRIMARY, hover_color=Theme.DARK_PRIMARY, corner_radius=12,
                      height=42, command=self._new_check).pack(fill="x", pady=4)
        ctk.CTkButton(af, text="🗑️  Clear History", font=Theme.get_font("body",13),
                      fg_color=Theme.CARD_BG, text_color=Theme.DANGER, hover_color=Theme.ACCENT_BLUSH,
                      border_width=1, border_color=Theme.DANGER, corner_radius=10,
                      height=36, command=self._clear).pack(fill="x", pady=4)

    def _build_feedback(self):
        card = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.ACCENT_BLUSH, border_width=1, border_color=Theme.BORDER)
        card.pack(fill="x", pady=(5,10))
        inner = ctk.CTkFrame(card, fg_color=Theme.ACCENT_BLUSH); inner.pack(fill="x", padx=Theme.CARD_PADDING, pady=Theme.CARD_PADDING)
        ctk.CTkLabel(inner, text="How do you feel now?", font=Theme.get_font("subheading",16), text_color=Theme.TEXT).pack()
        self.post_emoji = ctk.CTkLabel(inner, text="😌", font=Theme.get_emoji_font(40)); self.post_emoji.pack(pady=(5,0))
        self.post_slider = ctk.CTkSlider(inner, from_=1, to=10, number_of_steps=9, width=280, height=18,
                                         fg_color=Theme.BORDER, progress_color=Theme.SUCCESS,
                                         button_color=Theme.SUCCESS, command=self._on_post_slide)
        self.post_slider.set(3); self.post_slider.pack(pady=8)
        sf = ctk.CTkFrame(inner, fg_color=Theme.ACCENT_BLUSH); sf.pack(fill="x", padx=20)
        ctk.CTkLabel(sf, text="Much Better", font=Theme.get_font("caption"), text_color=Theme.SUCCESS).pack(side="left")
        self.post_score_lbl = ctk.CTkLabel(sf, text="3 / 10", font=Theme.get_font("body"), text_color=Theme.TEXT)
        self.post_score_lbl.pack(side="left", expand=True)
        ctk.CTkLabel(sf, text="Same/Worse", font=Theme.get_font("caption"), text_color=Theme.DANGER).pack(side="right")
        ctk.CTkButton(inner, text="✅  Submit Feedback", font=Theme.get_font("body",14),
                      fg_color=Theme.SUCCESS, hover_color=("#219A52","#219A52"),
                      corner_radius=10, height=40, command=self._submit).pack(fill="x", pady=(10,0))

    def _on_post_slide(self, val):
        s = round(val); self.post_emoji.configure(text=Theme.mood_emoji(s)); self.post_score_lbl.configure(text=f"{s} / 10")

    def _submit(self):
        if not self.controller.debounce_action(): return
        self.controller.complete_session(float(round(self.post_slider.get()))); self.on_show()

    def _build_stats(self):
        stats = self.controller.get_user_stats()
        if stats["total_sessions"] == 0:
            ec = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.CARD_BG, border_width=1, border_color=Theme.BORDER); ec.pack(fill="x", pady=10)
            ctk.CTkLabel(ec, text="🌱 No sessions yet!\n\nStart your first stress check to begin\ntracking your wellness journey.",
                         font=Theme.get_font("body",14), text_color=Theme.TEXT_SECONDARY, justify="center").pack(padx=Theme.CARD_PADDING, pady=30)
            return
        sg = ctk.CTkFrame(self.content, fg_color=Theme.BACKGROUND); sg.pack(fill="x", pady=5)
        sg.grid_columnconfigure((0,1), weight=1)
        for i, (e, lbl, val, col) in enumerate([("🧘","Total Sessions",str(stats["total_sessions"]),Theme.PRIMARY),
                                                 ("⏱️","Minutes Meditated",str(stats["total_minutes"]),Theme.SECONDARY),
                                                 ("🔥","Day Streak",str(stats["streak"]),Theme.WARNING),
                                                 ("📈","Avg Stress Relief",f"{stats['avg_improvement']:+.1f}",Theme.SUCCESS)]):
            c = ctk.CTkFrame(sg, corner_radius=12, fg_color=Theme.CARD_BG, border_width=1, border_color=Theme.BORDER)
            c.grid(row=i//2, column=i%2, padx=4, pady=4, sticky="ew")
            ctk.CTkLabel(c, text=f"{e} {lbl}", font=Theme.get_font("caption"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(10,2))
            ctk.CTkLabel(c, text=val, font=Theme.get_font("heading",22), text_color=col).pack(anchor="w", padx=10, pady=(0,10))

    def _build_chart(self):
        data = self.controller.get_weekly_stress_data()
        if not data: return
        ctk.CTkLabel(self.content, text="📊 Stress Trend (Recent Sessions)", font=Theme.get_font("subheading",16),
                     text_color=Theme.TEXT, anchor="w").pack(fill="x", pady=(15,5))
        cc = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.CARD_BG, border_width=1, border_color=Theme.BORDER); cc.pack(fill="x", pady=5)
        hd = Theme.hex_dark; chart_bg = hd(Theme.CARD_BG)
        fig = Figure(figsize=(4.5, 2.5), dpi=100, facecolor=chart_bg)
        ax  = fig.add_subplot(111)
        x   = list(range(1, len(data)+1))
        ax.plot(x, data, color=hd(Theme.PRIMARY), linewidth=2.5, marker="o", markersize=7,
                markerfacecolor=hd(Theme.ACCENT_BLUSH), markeredgecolor=hd(Theme.PRIMARY), markeredgewidth=2)
        ax.fill_between(x, data, alpha=0.15, color=hd(Theme.PRIMARY))
        ax.set_xlim(0.5, len(data)+0.5); ax.set_ylim(0, 10.5)
        ax.set_xlabel("Session", fontsize=10, color=hd(Theme.TEXT_SECONDARY))
        ax.set_ylabel("Stress Score", fontsize=10, color=hd(Theme.TEXT_SECONDARY))
        ax.set_facecolor(chart_bg); ax.tick_params(colors=hd(Theme.TEXT_SECONDARY), labelsize=9)
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(hd(Theme.BORDER)); ax.spines["bottom"].set_color(hd(Theme.BORDER))
        ax.grid(axis="y", alpha=0.3, color=hd(Theme.BORDER)); fig.tight_layout(pad=1.5)
        canvas = FigureCanvasTkAgg(fig, master=cc); canvas.draw(); canvas.get_tk_widget().pack(padx=8, pady=8)
        self._chart_canvas = canvas

    def _build_insight(self):
        ic = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.ACCENT_SAGE, border_width=1, border_color=Theme.BORDER); ic.pack(fill="x", pady=(10,5))
        ctk.CTkLabel(ic, text="💡 AI Insight", font=Theme.get_font("body",14), text_color=Theme.TEXT).pack(anchor="w", padx=Theme.CARD_PADDING, pady=(Theme.CARD_PADDING,4))
        ctk.CTkLabel(ic, text=self.controller.get_ai_insight(), font=Theme.get_font("body",13),
                     text_color=Theme.TEXT, wraplength=380, justify="left").pack(anchor="w", padx=Theme.CARD_PADDING, pady=(0,Theme.CARD_PADDING))
        if self.controller.should_show_counselor_card():
            cc = ctk.CTkFrame(self.content, corner_radius=Theme.CORNER_RADIUS, fg_color=Theme.ACCENT_BLUSH, border_width=1, border_color=Theme.DANGER); cc.pack(fill="x", pady=5)
            ctk.CTkLabel(cc, text="🤝  We've noticed consistently high stress.\nPlease consider speaking with your HR team\nor a wellness counselor.",
                         font=Theme.get_font("body",13), text_color=Theme.TEXT, justify="left", wraplength=380).pack(padx=Theme.CARD_PADDING, pady=Theme.CARD_PADDING)

    def _go_home(self): self.parent_app.show_screen("home")

    def _new_check(self):
        if not self.controller.debounce_action(): return
        self.controller.reset_stress_inputs(); self.controller.current_session = None
        self.parent_app.show_screen("stress_check")

    def _clear(self):
        if not self.controller.debounce_action(): return
        self.controller.clear_user_history(); self.on_show()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP WINDOW
# ─────────────────────────────────────────────────────────────────────────────

class MindfulWorkApp(ctk.CTk):
    APP_TITLE  = "Mindful Work — Smart Stress Relief Pod"
    MIN_WIDTH  = 480
    MIN_HEIGHT = 720

    def __init__(self):
        super().__init__()
        self.title(self.APP_TITLE)
        self.geometry(f"{self.MIN_WIDTH}x{self.MIN_HEIGHT}")
        self.minsize(self.MIN_WIDTH, 600)
        self.configure(fg_color=Theme.BACKGROUND)

        self.update_idletasks()
        x = (self.winfo_screenwidth()  - self.MIN_WIDTH)  // 2
        y = (self.winfo_screenheight() - self.MIN_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        self.controller = AppController()
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)
        self.screens = {}; self._current_screen = ""

        for name, Cls in [("login",          LoginScreen),
                          ("home",           HomeScreen),
                          ("stress_check",   StressCheckScreen),
                          ("pod_customization", PodCustomizationScreen),
                          ("active_session", ActiveSessionScreen),
                          ("feedback",       FeedbackScreen)]:
            s = Cls(self, self.controller)
            s.parent_app = self; self.screens[name] = s

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.show_screen("login")

    def show_screen(self, name):
        if name not in self.screens: return
        if self._current_screen and self._current_screen in self.screens:
            cur = self.screens[self._current_screen]
            if hasattr(cur, "on_hide"): cur.on_hide()
            cur.grid_forget()
        tgt = self.screens[name]
        tgt.grid(row=0, column=0, sticky="nsew")
        if hasattr(tgt, "on_show"): tgt.on_show()
        self._current_screen = name

    def _on_close(self):
        if self.controller.is_session_running:
            if not messagebox.askyesno("Session Active",
                                       "A session is still running. Exit anyway?", icon="warning"):
                return
        self.controller.cleanup(); self.destroy()


def main():
    app = MindfulWorkApp()
    app.mainloop()


if __name__ == "__main__":
    main()
