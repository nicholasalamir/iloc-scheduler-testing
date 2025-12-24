class OP:
    def __init__(self):
        # Matches the 14 columns of the IR table in the assignment description
        # Line number, then opcode, then three consecutive entries for operands with (SR, VR, PR, and NU)
        self.data = [None] * 14
        self.prev = None
        self.next = None
    def setNext(self, next):
        self.next = next
    def getNext(self):
        return self.next
    def setPrev(self, prev):
        self.prev = prev
    def getPrev(self):
        return self.prev
    def getData(self):
        return self.data