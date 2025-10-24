# ----------------------------Observer--------------------------------
class EmailObserver:
    def update(self, message):
        print(f"Sending email: {message}")


class SMSObserver:
    def update(self, message):
        print(f"Sending SMS: {message}")


class PushObserver:
    def update(self, message):
        print(f"Sending push notification: {message}")


# ----------------------------Subject--------------------------------


class NotificationService:
    def __init__(self):
        self._observers = set()  # - observers: List[Observer]

    def attach(self, observer):  # + attach(o)
        self._observers.add(observer)

    def detach(self, observer):  # + detach(o)
        self._observers.discard(observer)

    def set_state(self, message):  # + set_state(x)
        # state change logic would go here
        self._notify(message)  # calls notify() internally

    def _notify(self, message):  # - notify(): for o in obs: o.update(state)
        for observer in self._observers:
            observer.update(message)


# ----------------------------Client--------------------------------


class Currency:
    def __init__(self, name, price, subject):
        self.name = name
        self.price = price
        self.subject = subject  # uses shared NotificationService

    def change_price(self, new_price):
        self.price = new_price
        self.subject.set_state(f"{self.name} price changed to {self.price}")


if __name__ == "__main__":
    notification_service = NotificationService()

    # Observers
    email = EmailObserver()
    sms = SMSObserver()
    push = PushObserver()

    # Attach observers to the subject
    notification_service.attach(email)
    notification_service.attach(sms)
    notification_service.attach(push)

    # Clients (Currencies)
    usd = Currency("USD", 20, notification_service)
    eur = Currency("EUR", 30, notification_service)

    usd.change_price(50)
    eur.change_price(10)
