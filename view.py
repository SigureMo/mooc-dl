class Interactive():
    def __init__(self, attr_name, check, config, ignore_config):
        self.attr_name = attr_name
        self.attr_default = config.get(attr_name)
        self.config = config
        self.check = check
        self.isignore = isignore(ignore_config, attr_name )

    def getvalue(self, hint):
        if self.check(self.attr_default)['result'] and self.isignore:
            attr_value = self.attr_default
        else:
            while True:
                k = input(hint)
                attr_value = self.check(k)['result']
                if attr_value:
                    break
                else:
                    print(self.check(k)['err_msg'])
        self.config.set(attr, k)
        self.config.save()
        return attr_value

    def isignore(config,attr):
        try:
            if eval(config.get(attr))==True:
                return True
            else:
                config.set(attr, 'False')
                return False
        except:
            config.set(attr, 'False')
            return False
        finally:
            config.save()

def get_tid():
    def check(k):
        if config.get(root_name) and os.path.exists(config.get(root_name)):
    my_interactive=Interactive(root_name, check, \
                               Config('data/config.txt','$'), \
                               Config('data/IgnoreOptions.txt',' is ignore? '))
    
        

    return my_interactive.getvalue(self, hint):
