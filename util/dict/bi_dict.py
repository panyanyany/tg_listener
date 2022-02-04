class BiDict(dict):
    a = dict()
    b = dict()

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            self.a[k] = v
            self.b[v] = k

    def __getitem__(self, item):
        if item in self.a:
            return self.a[item]
        return self.b[item]
