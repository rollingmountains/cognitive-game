from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.storage.jsonstore import JsonStore
import random
import requests

# Only set window size on desktop
import kivy
if kivy.platform == 'win' or kivy.platform == 'linux' or kivy.platform == 'macosx':
    from kivy.core.window import Window
    Window.size = (360, 640)


class QuoteApp(App):
    QUOTES_URL = "https://raw.githubusercontent.com/rollingmountains/cognitive-game/refs/heads/main/quotes.json"

    def build(self):
        self.store = JsonStore('quoteapp_data.json')
        self.quotes = []
        self.seen_ids = set()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        self.status_label = Label(
            text='Loading quotes...',
            font_size='14sp',
            size_hint=(1, None),
            height=30,
            color=(0.7, 0.7, 0.7, 1)
        )
        self.quote_label = Label(
            text='',
            font_size='18sp',
            size_hint=(1, None),
            height=0,
            # desktop default, Android will resize automatically
            text_size=(360 - 40, None),
            halign='center',
            valign='top'
        )
        self.next_button = Button(
            text='Next Quote',
            size_hint=(None, None),
            size=(200, 60),
            pos_hint={'center_x': 0.5},
            font_size='18sp',
            disabled=True
        )
        self.next_button.bind(on_press=self.show_quote)

        layout.add_widget(self.status_label)
        layout.add_widget(Label(size_hint=(1, 1)))  # top spacer
        layout.add_widget(self.quote_label)
        layout.add_widget(self.next_button)
        layout.add_widget(Label(size_hint=(1, 1)))  # bottom spacer

        self.load_quotes()
        return layout

    def load_quotes(self):
        try:
            response = requests.get(self.QUOTES_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.quotes = data.get('quotes', [])
            self.store.put('cached_quotes', quotes=self.quotes)
            self.seen_ids = set(self.store.get('seen_ids')[
                                'ids']) if self.store.exists('seen_ids') else set()
            self.status_label.text = f'{len(self.quotes)} quotes loaded'
            self.next_button.disabled = False
        except Exception:
            if self.store.exists('cached_quotes'):
                self.quotes = self.store.get('cached_quotes')['quotes']
                self.seen_ids = set(self.store.get('seen_ids')[
                                    'ids']) if self.store.exists('seen_ids') else set()
                self.status_label.text = f'Offline mode: {len(self.quotes)} cached quotes'
                self.next_button.disabled = False
            else:
                self.status_label.text = 'Failed to load quotes. Check internet connection.'
                self.next_button.disabled = True

    def get_available_quotes(self):
        all_ids = {q['id'] for q in self.quotes}
        if self.seen_ids >= all_ids:
            self.seen_ids = set()
            self.store.put('seen_ids', ids=list(self.seen_ids))
        return [q for q in self.quotes if q['id'] not in self.seen_ids]

    def show_quote(self, instance):
        available = self.get_available_quotes()
        if not available:
            self.quote_label.text = 'No quotes available'
            return
        quote = random.choice(available)
        self.seen_ids.add(quote['id'])
        self.store.put('seen_ids', ids=list(self.seen_ids))
        self.quote_label.text = f'"{quote["text"]}"'
        self.quote_label.texture_update()
        self.quote_label.height = self.quote_label.texture_size[1] + 20
        remaining = len(available) - 1
        self.status_label.text = 'Round complete! Starting fresh...' if remaining == 0 else f'{remaining} quotes remaining this round'


if __name__ == '__main__':
    QuoteApp().run()
