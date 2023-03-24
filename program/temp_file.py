
class Decoder():

    # /指令 -param -
    def process(self, exp: str):
        exp = exp.strip("#")
        params = exp.split(" ")
        return params
