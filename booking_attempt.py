import asyncio
from playwright.async_api import Page

class Booking:
    def __init__(self, automation_dets: dict, page: Page):
        self.details = automation_dets
        self.page = page
        self.id = automation_dets.get('id', '??')
        self.name = automation_dets.get('name', self.id)
    
    def __repr__(self):
        return f"Booking: [id={self.id}, name={self.name}]"