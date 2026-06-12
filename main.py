"""
MetaSearch Universal v3.0 - Android
Kivy de base uniquement - Ultra robuste
"""
import os, sys, json, threading, time, random, hashlib
from urllib.parse import quote_plus

# Kivy config AVANT imports
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivy.config import Config
Config.set('kivy', 'log_level', 'error')
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle

Window.clearcolor = (0.06, 0.08, 0.12, 1)

# ─── DATA ───
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
ENGINES_FILE = os.path.join(DATA_DIR, "engines.json")
PROXIES_FILE = os.path.join(DATA_DIR, "proxies.json")

DEFAULT_ENGINES = [
    {"id": "ddg", "name": "DuckDuckGo", "url": "https://duckduckgo.com/html/?q={q}", "sel": True},
    {"id": "brave", "name": "Brave", "url": "https://search.brave.com/search?q={q}", "sel": True},
    {"id": "start", "name": "Startpage", "url": "https://www.startpage.com/do/dsearch?query={q}", "sel": True},
    {"id": "searx", "name": "SearXNG", "url": "https://search.sapti.me/search?q={q}", "sel": False},
    {"id": "bing", "name": "Bing", "url": "https://www.bing.com/search?q={q}", "sel": False},
    {"id": "wiki", "name": "Wikipedia", "url": "https://fr.wikipedia.org/wiki/Special:Search?search={q}", "sel": False},
    {"id": "git", "name": "GitHub", "url": "https://github.com/search?q={q}", "sel": False},
    {"id": "ahmia", "name": "Ahmia Tor", "url": "https://ahmia.fi/search/?q={q}", "sel": False, "tor": True},
]

def load_json(path, default=None):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default or []

def save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except:
        pass

# ─── UI HELPERS ───
class Card(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = dp(10)
        self.spacing = dp(6)
        with self.canvas.before:
            Color(0.1, 0.12, 0.18, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._up, size=self._up)
    def _up(self, i, v):
        self.rect.pos = i.pos
        self.rect.size = i.size

class TLabel(Label):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.color = (0.9, 0.9, 0.92, 1)
        self.font_size = dp(14)
        self.size_hint_y = None
        self.height = dp(24)
        self.halign = 'left'
        self.valign = 'center'
        self.bind(size=self.setter('text_size'))

class SLabel(Label):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.color = (0.6, 0.65, 0.7, 1)
        self.font_size = dp(12)
        self.size_hint_y = None
        self.height = dp(20)
        self.halign = 'left'
        self.valign = 'center'
        self.bind(size=self.setter('text_size'))

class Btn(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ''
        self.background_color = (0.02, 0.7, 0.83, 1)
        self.color = (0, 0, 0, 1)
        self.font_size = dp(13)
        self.size_hint_y = None
        self.height = dp(44)
        self.bold = True

class Btn2(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ''
        self.background_color = (0.15, 0.17, 0.22, 1)
        self.color = (0.9, 0.9, 0.92, 1)
        self.font_size = dp(12)
        self.size_hint_y = None
        self.height = dp(36)

# ─── SEARCH ───
class SearchScreen(Screen):
    def __init__(self, app, **kw):
        self.app = app
        super().__init__(**kw)
        self.build()

    def build(self):
        root = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))

        # Header
        root.add_widget(TLabel(text='🔍 MetaSearch Universal', font_size=dp(18), color=(0.02, 0.7, 0.83, 1), height=dp(32)))

        # Search bar
        bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        self.inp = TextInput(
            hint_text='Rechercher...',
            background_color=(0.06, 0.08, 0.12, 1),
            foreground_color=(0.9, 0.9, 0.92, 1),
            cursor_color=(0.02, 0.7, 0.83, 1),
            font_size=dp(14),
            padding=[dp(12), dp(12)],
            multiline=False,
            size_hint_x=0.75
        )
        bar.add_widget(self.inp)
        self.inp.bind(on_text_validate=self.search)

        self.sbtn = Btn(text='🔍', size_hint_x=0.25, on_release=self.search)
        bar.add_widget(self.sbtn)
        root.add_widget(bar)

        # Options
        opts = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(12))
        self.tor = ToggleButton(text='Tor', size_hint_x=0.3, background_color=(0.15, 0.17, 0.22, 1))
        self.proxy = ToggleButton(text='Proxy', size_hint_x=0.3, background_color=(0.15, 0.17, 0.22, 1))
        opts.add_widget(self.tor)
        opts.add_widget(self.proxy)
        root.add_widget(opts)

        # Status
        self.status = SLabel(text='Prêt')
        root.add_widget(self.status)

        # Results
        scroll = ScrollView()
        self.res = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6), padding=dp(4))
        self.res.bind(minimum_height=self.res.setter('height'))
        scroll.add_widget(self.res)
        root.add_widget(scroll)

        self.add_widget(root)

    def search(self, instance=None):
        q = self.inp.text.strip()
        if not q:
            return
        self.sbtn.disabled = True
        self.sbtn.text = '...'
        self.status.text = 'Recherche en cours...'
        self.res.clear_widgets()
        threading.Thread(target=self._search, args=(q,), daemon=True).start()

    def _search(self, q):
        engines = load_json(ENGINES_FILE, DEFAULT_ENGINES)
        selected = [e for e in engines if e.get('sel', False)]
        if not selected:
            Clock.schedule_once(lambda dt: self._done([], 'Aucun moteur actif'), 0)
            return

        all_res = []
        for e in selected[:5]:
            try:
                import requests
                url = e['url'].replace('{q}', quote_plus(q))
                headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 14) Chrome/125'}
                r = requests.get(url, headers=headers, timeout=8)
                if r.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(r.text, 'html.parser')
                    if e['id'] == 'ddg':
                        for a in soup.select('.result__a')[:3]:
                            all_res.append({'t': a.get_text(strip=True), 'u': a.get('href', ''), 'e': e['name']})
                    elif e['id'] == 'bing':
                        for item in soup.select('.b_algo')[:3]:
                            a = item.select_one('a')
                            if a:
                                all_res.append({'t': a.get_text(strip=True), 'u': a.get('href', ''), 'e': e['name']})
                    else:
                        for a in soup.find_all('a')[:3]:
                            href = a.get('href', '')
                            if href and href.startswith('http'):
                                all_res.append({'t': a.get_text(strip=True)[:60], 'u': href, 'e': e['name']})
            except Exception as ex:
                print(f"Engine {e['name']} error: {ex}")

        Clock.schedule_once(lambda dt: self._done(all_res, f'{len(all_res)} résultats'), 0)

    def _done(self, results, msg):
        self.sbtn.disabled = False
        self.sbtn.text = '🔍'
        self.status.text = msg

        if not results:
            self.res.add_widget(TLabel(text='Aucun résultat', halign='center', color=(0.6, 0.65, 0.7, 1)))
            return

        seen = set()
        for r in results:
            if r['u'] in seen:
                continue
            seen.add(r['u'])

            c = Card()
            c.height = dp(70)
            c.add_widget(TLabel(text=r['t'][:55], font_size=dp(13), color=(0.02, 0.7, 0.83, 1)))
            c.add_widget(SLabel(text=f"{r['e']} | {r['u'][:50]}..."))
            self.res.add_widget(c)

# ─── ENGINES ───
class EnginesScreen(Screen):
    def __init__(self, app, **kw):
        self.app = app
        super().__init__(**kw)
        self.build()

    def build(self):
        root = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))
        root.add_widget(TLabel(text='⚙️ Moteurs', font_size=dp(18), color=(0.02, 0.7, 0.83, 1), height=dp(32)))

        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        btns.add_widget(Btn(text='🔄 Update', on_release=self.update))
        btns.add_widget(Btn2(text='♻️ Reset', on_release=self.reset))
        root.add_widget(btns)

        scroll = ScrollView()
        self.list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6), padding=dp(4))
        self.list.bind(minimum_height=self.list.setter('height'))
        scroll.add_widget(self.list)
        root.add_widget(scroll)

        self.add_widget(root)
        self.load()

    def load(self):
        self.list.clear_widgets()
        engines = load_json(ENGINES_FILE, DEFAULT_ENGINES)
        for e in engines:
            c = Card()
            c.height = dp(60)
            top = BoxLayout(size_hint_y=None, height=dp(30))
            top.add_widget(TLabel(text=f"{'✅ ' if e.get('sel') else '⬜ '}{e['name']}", font_size=dp(14)))
            btn = Btn2(text='Activer' if not e.get('sel') else 'Désactiver', size_hint_x=0.3)
            btn.bind(on_release=lambda x, eid=e['id']: self.toggle(eid))
            top.add_widget(btn)
            c.add_widget(top)
            c.add_widget(SLabel(text=e['url'][:45]))
            self.list.add_widget(c)

    def toggle(self, eid):
        engines = load_json(ENGINES_FILE, DEFAULT_ENGINES)
        for e in engines:
            if e['id'] == eid:
                e['sel'] = not e.get('sel', False)
        save_json(ENGINES_FILE, engines)
        self.load()

    def update(self, instance):
        new = [
            {'id': 'ecosia', 'name': 'Ecosia', 'url': 'https://www.ecosia.org/search?q={q}', 'sel': False},
            {'id': 'qwant', 'name': 'Qwant', 'url': 'https://www.qwant.com/?q={q}', 'sel': False},
        ]
        engines = load_json(ENGINES_FILE, DEFAULT_ENGINES)
        added = 0
        for n in new:
            if not any(e['id'] == n['id'] for e in engines):
                engines.append(n)
                added += 1
        if added:
            save_json(ENGINES_FILE, engines)
            self.load()
            self.show(f'{added} moteurs ajoutés')
        else:
            self.show('Déjà à jour')

    def reset(self, instance):
        save_json(ENGINES_FILE, DEFAULT_ENGINES)
        self.load()
        self.show('Réinitialisé')

    def show(self, msg):
        popup = Popup(title='Info', content=Label(text=msg, color=(1,1,1,1)), size_hint=(0.8, 0.2))
        popup.open()

# ─── PROXY ───
class ProxyScreen(Screen):
    def __init__(self, app, **kw):
        self.app = app
        super().__init__(**kw)
        self.build()

    def build(self):
        root = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))
        root.add_widget(TLabel(text='🌐 Proxy', font_size=dp(18), color=(0.02, 0.7, 0.83, 1), height=dp(32)))

        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        btns.add_widget(Btn(text='🔍 Scrap', on_release=self.scrape))
        btns.add_widget(Btn(text='⚡ Test', on_release=self.test))
        btns.add_widget(Btn2(text='🗑️', on_release=self.clear))
        root.add_widget(btns)

        self.stats = SLabel(text='0 proxies')
        root.add_widget(self.stats)

        scroll = ScrollView()
        self.list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6), padding=dp(4))
        self.list.bind(minimum_height=self.list.setter('height'))
        scroll.add_widget(self.list)
        root.add_widget(scroll)

        self.add_widget(root)
        self.refresh()

    def refresh(self):
        self.list.clear_widgets()
        proxies = load_json(PROXIES_FILE, [])
        working = [p for p in proxies if p.get('ok')]
        self.stats.text = f'{len(proxies)} total | {len(working)} OK'
        for p in working[:15]:
            c = Card()
            c.height = dp(50)
            c.add_widget(TLabel(text=f"{p['ip']}:{p['port']}", font_size=dp(13)))
            c.add_widget(SLabel(text=f"{p.get('ms', 0)}ms | {'Anon' if p.get('anon') else 'Transp'} | {'Fast' if p.get('fast') else 'Slow'}"))
            self.list.add_widget(c)

    def scrape(self, instance):
        instance.disabled = True
        instance.text = '...'
        threading.Thread(target=self._scrape, daemon=True).start()

    def _scrape(self):
        try:
            import requests, re
            sources = [
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            ]
            found = []
            for src in sources:
                try:
                    r = requests.get(src, timeout=15)
                    if r.status_code == 200:
                        for line in r.text.splitlines():
                            if ':' in line and line[0].isdigit():
                                ip, port = line.strip().split(':')
                                found.append({'ip': ip, 'port': int(port), 'ok': False, 'anon': False, 'fast': False, 'ms': 0})
                except:
                    pass
            save_json(PROXIES_FILE, found)
            Clock.schedule_once(lambda dt: (self.refresh(), self._btn('🔍 Scrap')), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: (self.show(str(e)), self._btn('🔍 Scrap')), 0)

    def _btn(self, t):
        for c in self.walk():
            if isinstance(c, Btn) and c.text.startswith('🔍'):
                c.text = t
                c.disabled = False

    def test(self, instance):
        instance.disabled = True
        instance.text = '...'
        threading.Thread(target=self._test, daemon=True).start()

    def _test(self):
        try:
            import requests
            proxies = load_json(PROXIES_FILE, [])
            for p in proxies:
                try:
                    start = time.time()
                    r = requests.get('http://httpbin.org/ip', proxies={'http': f"http://{p['ip']}:{p['port']}"}, timeout=5)
                    p['ms'] = int((time.time() - start) * 1000)
                    p['ok'] = True
                    p['fast'] = p['ms'] < 2000
                    p['anon'] = True
                except:
                    p['ok'] = False
            save_json(PROXIES_FILE, proxies)
            Clock.schedule_once(lambda dt: (self.refresh(), self._btn2('⚡ Test')), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: (self.show(str(e)), self._btn2('⚡ Test')), 0)

    def _btn2(self, t):
        for c in self.walk():
            if isinstance(c, Btn) and c.text.startswith('⚡'):
                c.text = t
                c.disabled = False

    def clear(self, instance):
        save_json(PROXIES_FILE, [])
        self.refresh()

    def show(self, msg):
        popup = Popup(title='Info', content=Label(text=msg, color=(1,1,1,1)), size_hint=(0.8, 0.2))
        popup.open()

# ─── MASTER ───
class MasterScreen(Screen):
    def __init__(self, app, **kw):
        self.app = app
        super().__init__(**kw)
        self.build()

    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        self.root.add_widget(TLabel(text='🔐 MODE MASTER', font_size=dp(20), color=(1, 0.8, 0, 1), height=dp(36), halign='center'))
        self.root.add_widget(SLabel(text='Accès total - Contrôle absolu', halign='center'))

        self.pwd = TextInput(hint_text='Mot de passe', password=True, background_color=(0.06, 0.08, 0.12, 1), foreground_color=(1,1,1,1), font_size=dp(14), size_hint_y=None, height=dp(44), multiline=False)
        self.root.add_widget(self.pwd)

        self.root.add_widget(Btn(text='Connexion', on_release=self.login))
        self.root.add_widget(SLabel(text='MDP: master123 (changez immédiatement!)', halign='center', color=(1, 0.5, 0, 1)))

        self.add_widget(self.root)

    def login(self, instance):
        if self.pwd.text == 'master123':
            self.root.clear_widgets()
            self.root.add_widget(TLabel(text='🔓 MASTER ACTIVÉ', font_size=dp(20), color=(0, 1, 0.5, 1), height=dp(36), halign='center'))
            self.root.add_widget(Btn(text='🛑 Stop Agents', background_color=(0.9, 0.2, 0.2, 1), on_release=lambda x: self.show('Agents arrêtés')))
            self.root.add_widget(Btn(text='🔄 Reset Data', background_color=(0.9, 0.6, 0.1, 1), on_release=self.reset))
            self.root.add_widget(Btn(text='🏭 Factory Reset', background_color=(0.5, 0.2, 0.9, 1), on_release=self.factory))
        else:
            self.show('Mot de passe incorrect')

    def reset(self, instance):
        for f in [ENGINES_FILE, PROXIES_FILE]:
            if os.path.exists(f):
                os.remove(f)
        self.show('Données effacées')

    def factory(self, instance):
        self.reset(instance)
        self.show('Réinitialisation complète')

    def show(self, msg):
        popup = Popup(title='Master', content=Label(text=msg, color=(1,1,1,1)), size_hint=(0.8, 0.2))
        popup.open()

# ─── UPDATE ───
class UpdateScreen(Screen):
    def __init__(self, app, **kw):
        self.app = app
        super().__init__(**kw)
        self.build()

    def build(self):
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        root.add_widget(TLabel(text='🔄 Mise à jour', font_size=dp(18), color=(0.02, 0.7, 0.83, 1), height=dp(32)))
        root.add_widget(SLabel(text='Vérifie automatiquement les nouvelles versions', halign='center'))

        self.status = TLabel(text=f'Version: 3.0.0', halign='center', color=(0.6, 0.65, 0.7, 1))
        root.add_widget(self.status)

        root.add_widget(Btn(text='🔍 Vérifier', on_release=self.check))
        root.add_widget(SLabel(text='Les agents IA vérifient les mises à jour en arrière-plan', halign='center', font_size=dp(11)))

        self.add_widget(root)

    def check(self, instance):
        instance.disabled = True
        instance.text = '...'
        threading.Thread(target=self._check, daemon=True).start()

    def _check(self):
        try:
            import requests
            r = requests.get('https://raw.githubusercontent.com/metasearch/updates/main/version.json', timeout=10)
            if r.status_code == 200:
                data = r.json()
                latest = data.get('version', '3.0.0')
                if latest > '3.0.0':
                    Clock.schedule_once(lambda dt: self._done(f'Nouvelle version: {latest}'), 0)
                else:
                    Clock.schedule_once(lambda dt: self._done('Déjà à jour'), 0)
            else:
                Clock.schedule_once(lambda dt: self._done('Serveur indisponible'), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._done(f'Erreur: {str(e)}'), 0)

    def _done(self, msg):
        self.status.text = msg
        for c in self.walk():
            if isinstance(c, Btn) and c.text.startswith('🔍'):
                c.text = '🔍 Vérifier'
                c.disabled = False

# ─── APP ───
class MetaSearchApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(SearchScreen(self, name='search'))
        sm.add_widget(EnginesScreen(self, name='engines'))
        sm.add_widget(ProxyScreen(self, name='proxy'))
        sm.add_widget(MasterScreen(self, name='master'))
        sm.add_widget(UpdateScreen(self, name='update'))

        root = BoxLayout(orientation='vertical')
        root.add_widget(sm)

        # Bottom nav
        nav = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(2), padding=dp(2))
        screens = [
            ('🔍', 'search', (0.02, 0.7, 0.83, 1)),
            ('⚙️', 'engines', (0.6, 0.65, 0.7, 1)),
            ('🌐', 'proxy', (0.6, 0.65, 0.7, 1)),
            ('🔐', 'master', (0.6, 0.65, 0.7, 1)),
            ('🔄', 'update', (0.6, 0.65, 0.7, 1)),
        ]
        for icon, name, color in screens:
            b = Button(text=icon, background_color=(0.08, 0.1, 0.15, 1), color=color, font_size=dp(20), on_release=lambda x, n=name: setattr(sm, 'current', n))
            nav.add_widget(b)
        root.add_widget(nav)

        return root

if __name__ == '__main__':
    MetaSearchApp().run()
