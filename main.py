from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
import random
import requests
import json
import os

# Set window size for testing on desktop
Window.size = (360, 640)


class QuoteApp(App):
    def build(self):
        # URL to your quotes JSON file (replace with your actual URL)
        self.quotes_url = "https://github.com/rollingmountains/cognitive-game/blob/main/quotes.json"

        # Local storage for caching quotes and tracking seen quotes
        self.store = JsonStore('quoteapp_data.json')

        # Initialize quotes list and seen tracking
        self.quotes = []
        self.seen_ids = set()

        # Main layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Status label for loading/error messages
        self.status_label = Label(
            text='Loading quotes...',
            font_size='14sp',
            size_hint=(1, None),
            height=30,
            color=(0.7, 0.7, 0.7, 1)
        )

        # Quote label (starts empty)
        self.quote_label = Label(
            text='',
            font_size='18sp',
            size_hint=(1, None),
            height=0,
            text_size=(Window.width - 40, None),
            halign='center',
            valign='top'
        )

        # Spacer to push button toward middle
        self.top_spacer = BoxLayout(size_hint=(1, 1))

        # Next button
        self.next_button = Button(
            text='Next Quote',
            size_hint=(None, None),
            size=(200, 60),
            pos_hint={'center_x': 0.5},
            font_size='18sp',
            disabled=True
        )
        self.next_button.bind(on_press=self.show_quote)

        # Bottom spacer
        self.bottom_spacer = BoxLayout(size_hint=(1, 1))

        # Add widgets to layout
        layout.add_widget(self.status_label)
        layout.add_widget(self.top_spacer)
        layout.add_widget(self.quote_label)
        layout.add_widget(self.next_button)
        layout.add_widget(self.bottom_spacer)

        # Load quotes
        self.load_quotes()

        return layout

    def load_quotes(self):
        """Fetch quotes from URL, with fallback to cached version"""
        try:
            # Try to fetch from URL
            response = requests.get(self.quotes_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            self.quotes = data.get('quotes', [])

            # Cache the quotes locally
            self.store.put('cached_quotes', quotes=self.quotes)

            # Load seen IDs from storage
            if self.store.exists('seen_ids'):
                self.seen_ids = set(self.store.get('seen_ids')['ids'])
            else:
                self.seen_ids = set()

            self.status_label.text = f'{len(self.quotes)} quotes loaded'
            self.next_button.disabled = False

        except Exception as e:
            # If fetch fails, try to load from cache
            if self.store.exists('cached_quotes'):
                self.quotes = self.store.get('cached_quotes')['quotes']

                if self.store.exists('seen_ids'):
                    self.seen_ids = set(self.store.get('seen_ids')['ids'])
                else:
                    self.seen_ids = set()

                self.status_label.text = f'Offline mode: {len(self.quotes)} cached quotes'
                self.next_button.disabled = False
            else:
                self.status_label.text = 'Failed to load quotes. Check internet connection.'
                self.next_button.disabled = True

    def get_available_quotes(self):
        """Get quotes that haven't been seen in current round"""
        all_ids = {q['id'] for q in self.quotes}

        # If all quotes have been seen, reset the round
        if self.seen_ids >= all_ids:
            self.seen_ids = set()
            self.store.put('seen_ids', ids=list(self.seen_ids))

        # Return quotes not yet seen
        available = [q for q in self.quotes if q['id'] not in self.seen_ids]
        return available

    def show_quote(self, instance):
        """Show a random quote from available pool"""
        available_quotes = self.get_available_quotes()

        if not available_quotes:
            self.quote_label.text = 'No quotes available'
            return

        # Pick a random quote from available ones
        quote_obj = random.choice(available_quotes)

        # Mark as seen
        self.seen_ids.add(quote_obj['id'])
        self.store.put('seen_ids', ids=list(self.seen_ids))

        # Format and display quote
        quote_text = f'"{quote_obj["text"]}'
        self.quote_label.text = quote_text

        # Adjust label height based on text
        self.quote_label.texture_update()
        self.quote_label.height = self.quote_label.texture_size[1] + 20

        # Update status
        remaining = len(available_quotes) - 1
        if remaining == 0:
            self.status_label.text = 'Round complete! Starting fresh...'
        else:
            self.status_label.text = f'{remaining} quotes remaining this round'


if __name__ == '__main__':
    QuoteApp().run()
