from dataclasses import dataclass

from Application import Application

# Will group amount of applications with same rank
@dataclass
class ApplicationGroup(Application):
    amount: int

    def __init__(self, app: Application, am: int):
        super().__init__(rank=app.rank, name=app.name, rooms=app.rooms, grossArea=app.grossArea, estPrice=app.estPrice, addr=app.addr, url=app.url)
        self.amount = am

    def __str__(self):
        return self.rank + " - " + self.name + " - " + str(self.rooms) + " værelses - " + str(self.area) + "m2 - " + str(self.estPrice) + "kr - " + self.url