class Debugger():
    def __init__(self):
        self.gs=[
                '__builtins__',
                '__doc__',
                '__loader__',
                'Debugger',
                '__file__',
                '__name__',
                '__cached__',
                '__spec__',
                '__package__',
                ]
        self.ls=[
                ]

    def output():
        pass
    def showvars(self):
        print('Globals:')
        for g in globals().items():
            if g[0] not in self.gs:
                try:
                    print(g[0]+':'+g[1])
                except:
                    print(g[0]+':____')
        print('Locals:')
        for l in locals().items():
            if l[0] not in self.ls:
                try:
                    print(l[0]+':'+l[1])
                except:
                    print(l[0]+'____')
        
