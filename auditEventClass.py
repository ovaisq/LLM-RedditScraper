class AuditEvent:
    def __init__(self, timestamp, source, reference_id, action):
        self.timestamp = timestamp
        self.source = source
        self.reference_id = reference_id
        self.action = action