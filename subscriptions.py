# -*- coding: utf-8 -*-

class Subscriptions:
    def __init__(self):
        # List for storing subscriptions to SSE
        self.subscriptions = []
        return None

    def get_subscriptions(self):
        return self.subscriptions

    def add_subscription(self, sub):
        self.subscriptions.append(sub)

    def remove_subscription(self, sub):
        self.subscriptions.remove(sub)

    def num_subscription(self):
        return len(self.subscriptions)
