import uuid


class SessionManager:

    def __init__(self):
        self.sessions = {}

    def create(self, agent, config):

        session_id = str(uuid.uuid4())

        self.sessions[session_id] = {
            "agent": agent,
            "config": config,
        }

        return session_id

    def get(self, session_id):
        return self.sessions.get(session_id)

    def delete(self, session_id):

        if session_id in self.sessions:
            del self.sessions[session_id]
            return True

        return False

    def list_sessions(self):

        return list(self.sessions.keys())


session_manager = SessionManager()
