class Sharpness:
    "Object used to encapsulate sharpness data"
    def __init__(self, red=0, orange=0, yellow=0, green=0, blue=0, white=0, purple=0):
        self.values = [
            max(red, 0),
            max(orange, 0), 
            max(yellow, 0),
            max(green, 0),
            max(blue, 0),
            max(white, 0),
            max(purple, 0)
        ]

        # cap to 400
        total = sum(self.values)
        if total > 400:
            self.subtract(total - 400)
    
    def subtract(self, amount: int):
        if amount < 0:
            raise Exception("Amount to subtract must be positive")

        remaining = amount
        for idx, value in reversed(list(enumerate(self.values))):
            to_remove = min(remaining, value)
            self.values[idx] = value - to_remove
            remaining -= to_remove
            
            if remaining <= 0:
                break

    def to_object(self):
        return {
            'red': self.values[0],
            'orange': self.values[1],
            'yellow': self.values[2],
            'green': self.values[3],
            'blue': self.values[4],
            'white': self.values[5],
            'purple': self.values[6]
        }