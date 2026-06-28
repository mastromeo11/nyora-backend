import os
import json
import threading
from typing import Dict, Any, List

ADAPTIVE_UI_FILE_PATH = os.path.abspath("storage/adaptive_ui_memory.json")
_lock = threading.Lock()

def _load_ui_store() -> Dict[str, Any]:
    os.makedirs(os.path.dirname(ADAPTIVE_UI_FILE_PATH), exist_ok=True)
    if os.path.exists(ADAPTIVE_UI_FILE_PATH):
        try:
            with open(ADAPTIVE_UI_FILE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"interactions": {}, "profile": {}}

def _save_ui_store(data: Dict[str, Any]):
    try:
        temp_path = ADAPTIVE_UI_FILE_PATH + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=4)
        os.replace(temp_path, ADAPTIVE_UI_FILE_PATH)
    except Exception as e:
        print(f"[ADAPTIVE UI STORE] Error saving store: {e}")

def record_ui_interaction(
    user_id: str,
    tab: str,
    layout: str,
    theme: str,
    screen_size: str
):
    """
    Saves a record of UI interaction settings and tab clicks for habit learning.
    """
    with _lock:
        data = _load_ui_store()
        
        # Log tab clicks count
        user_ints = data["interactions"].setdefault(user_id, {})
        tab_clicks = user_ints.setdefault("tab_clicks", {})
        tab_clicks[tab] = tab_clicks.get(tab, 0) + 1
        
        # Log layout choices
        layouts = user_ints.setdefault("layouts", {})
        layouts[layout] = layouts.get(layout, 0) + 1

        # Log theme choices
        themes = user_ints.setdefault("themes", {})
        themes[theme] = themes.get(theme, 0) + 1

        # Record screen size
        user_ints["last_screen_size"] = screen_size

        # Compile UI profiles dynamically based on habits
        most_clicked_tabs = sorted(tab_clicks.items(), key=lambda x: x[1], reverse=True)
        preferred_tabs = [item[0] for item in most_clicked_tabs]
        
        preferred_layout = max(layouts.items(), key=lambda x: x[1])[0] if layouts else "split_view"
        preferred_theme = max(themes.items(), key=lambda x: x[1])[0] if themes else "dark_cyber"

        data["profile"][user_id] = {
            "preferred_tabs_order": preferred_tabs,
            "preferred_layout": preferred_layout,
            "preferred_theme": preferred_theme,
            "last_screen_size": screen_size
        }
        
        _save_ui_store(data)

def get_adaptive_ui_profile(user_id: str) -> Dict[str, Any]:
    """
    Returns the UI customization parameters for the user's habits.
    """
    with _lock:
        data = _load_ui_store()
        return data["profile"].get(user_id, {
            "preferred_tabs_order": ["chat", "dashboard", "graphs", "simulations"],
            "preferred_layout": "split_view",
            "preferred_theme": "dark_cyber",
            "last_screen_size": "desktop"
        })
