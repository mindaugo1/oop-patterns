class EmailObserver:
    def execute(self, message):
        print(f"Sending email: {message}")


class SMSObserver:
    def execute(self, message):
        print(f"Sending SMS: {message}")


class PushNotificationObserver:
    def execute(self, message):
        print(f"Sending push notification: {message}")


class NotificationService:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify(self, message):
        for observer in self.observers:
            observer.execute(message)


class Currency:
    def __init__(self, price):
        self.price = price
        self.notification_center = NotificationService()

    def change_price(self, price):
        self.price = price
        notification_service.notify(f"price changed to {self.price}")


if __name__ == "__main__":
    notification_service = NotificationService()

    email = EmailObserver()
    sms = SMSObserver()
    push_notification = PushNotificationObserver()

    notification_service.add_observer(email)
    notification_service.add_observer(sms)
    notification_service.add_observer(push_notification)

    usd = Currency(price=20)
    eur = Currency(price=30)

    usd.change_price(price=50)
    eur.change_price(price=10)
