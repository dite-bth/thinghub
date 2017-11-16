# -*- coding: utf-8 -*-

from sets import Set

class Subscriptions:
    def __init__(self):
        # List for storing subscriptions to SSE
        self.subscriptions = Set([])
        return None

    def get_subscriptions(self):
        return self.subscriptions

    def add_subscription(self, sub):
        self.subscriptions.add(sub)

    def remove_subscription(self, sub):
        self.subscriptions.remove(sub)

    def num_subscriptions(self):
        return len(self.subscriptions)
