class uclass0(object):
    def __init__(self,
                 _cuid = [-1],
                 **kwargs):
        self.cuid = _cuid
        self.cuid.append(_cuid[-1] + 1)
        self.cuid.pop(0)

class uclass1(object):
    cuid = -1
    def __init__(self, **kwargs):
        self.cuid = self.cuid + 1

class uclass2(object):
    cuid = [-1]
    def __init__(self, **kwargs):
        self.cuid.append(self.cuid[-1] + 1)
        self.cuid.pop(0)

class uclass3(object):
    cuid = -1
    def __init__(self, **kwargs):
        uclass3.cuid = uclass3.cuid + 1

class uclass4(uclass3):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class uclass5(uclass4):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

for i in range(0,10):
    j = uclass0(), uclass1(), uclass2(), uclass3(), uclass4(), uclass5()
    print([k.cuid for k in j])
