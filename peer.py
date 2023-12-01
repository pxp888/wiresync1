import json 


class Peer(dict):
    def json(self):
        return json.dumps(self)


    def froms(self, s):
        n = json.loads(s)
        for i in n:
            self[i] = n[i]

    
