"""Session notes and tags system"""
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json
from src.utils.logger import default_logger as logger


class SessionNotesManager:
    """Manages session notes and tags"""
    
    def __init__(self, notes_file: Optional[Path] = None):
        """
        Initialize session notes manager.
        
        Args:
            notes_file: File to store notes
        """
        if notes_file is None:
            notes_file = Path(__file__).parent.parent.parent / "data" / "session_notes.json"
        
        self.notes_file = Path(notes_file)
        self.notes_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.notes_data = self._load_notes()
        
        logger.info("Session notes manager initialized")
    
    def _load_notes(self) -> Dict:
        """Load notes from file"""
        if self.notes_file.exists():
            try:
                with open(self.notes_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading notes: {e}")
        
        return {'sessions': {}, 'tags': []}
    
    def _save_notes(self):
        """Save notes to file"""
        try:
            with open(self.notes_file, 'w') as f:
                json.dump(self.notes_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving notes: {e}")
    
    def add_session_note(self, session_id: str, note: str, tags: Optional[List[str]] = None):
        """
        Add a note to a session.
        
        Args:
            session_id: Session ID
            note: Note text
            tags: Optional list of tags
        """
        if session_id not in self.notes_data['sessions']:
            self.notes_data['sessions'][session_id] = {
                'notes': [],
                'tags': []
            }
        
        self.notes_data['sessions'][session_id]['notes'].append({
            'text': note,
            'timestamp': datetime.now().isoformat()
        })
        
        if tags:
            current_tags = set(self.notes_data['sessions'][session_id]['tags'])
            current_tags.update(tags)
            self.notes_data['sessions'][session_id]['tags'] = list(current_tags)
            
            # Update global tags list
            global_tags = set(self.notes_data['tags'])
            global_tags.update(tags)
            self.notes_data['tags'] = sorted(list(global_tags))
        
        self._save_notes()
        logger.info(f"Added note to session {session_id}")
    
    def get_session_notes(self, session_id: str) -> Dict:
        """Get notes for a session"""
        return self.notes_data['sessions'].get(session_id, {'notes': [], 'tags': []})
    
    def get_all_tags(self) -> List[str]:
        """Get all available tags"""
        return self.notes_data['tags']
    
    def search_by_tag(self, tag: str) -> List[str]:
        """
        Search sessions by tag.
        
        Args:
            tag: Tag to search for
        
        Returns:
            List of session IDs
        """
        matching_sessions = []
        
        for session_id, data in self.notes_data['sessions'].items():
            if tag in data['tags']:
                matching_sessions.append(session_id)
        
        return matching_sessions
    
    def delete_session_notes(self, session_id: str):
        """Delete all notes for a session"""
        if session_id in self.notes_data['sessions']:
            del self.notes_data['sessions'][session_id]
            self._save_notes()
