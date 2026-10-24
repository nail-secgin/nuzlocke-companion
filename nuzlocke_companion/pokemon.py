class Pokemon():
    def __init__(self, name, nickname, route, state, dex_id, level=1, location=1, id = None, nuzlocke_id = None):
        self.name = name
        self.nickname = nickname
        self.level = level
        self.route = route
        self.state = state
        self.location = location
        self.dex_id = dex_id
        self.id = id
        self.nuzlocke_id = nuzlocke_id

