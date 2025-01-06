import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock, mainthread

import google.generativeai as genai
import time
import threading

# Importações para voz e reconhecimento de fala
import pyttsx3
import speech_recognition as sr

kivy.require('2.0.0')

class ChatInterface(BoxLayout):
    chat_history = StringProperty("")
    input_text = StringProperty("")
    assistente_falante = BooleanProperty(True)
    ligar_microfone = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(ChatInterface, self).__init__(**kwargs)
        self.orientation = 'vertical'

        # Inicialização das funcionalidades
        self.init_genai()
        self.init_voice()
        self.init_microphone()

        # Construção da interface
        self.build_ui()

    def init_genai(self):
        # Configuração da chave de API do Gemini AI
        genai.configure(api_key="AIzaSyClsshQqCZyq4nk7qv-G-zLQ4L8o8Mxyvk")

        # Inicializa o modelo 'gemini-pro' para o chat
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])

    def init_voice(self):
        if self.assistente_falante:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('rate', 160)  # Velocidade ajustada
            self.engine.setProperty('voice', voices[0].id)  # Escolha da voz
        else:
            self.engine = None

    def init_microphone(self):
        if self.ligar_microfone:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

    def build_ui(self):
        # Área de histórico de chat
        self.history_label = Label(text=self.chat_history, size_hint_y=0.8, valign='top', halign='left', markup=True)
        self.history_label.bind(size=self.history_label.setter('text_size'))
        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(self.history_label)
        self.add_widget(scroll)

        # Campo de entrada e botões
        input_layout = BoxLayout(size_hint_y=0.1)

        self.input = TextInput(text='', multiline=False, hint_text='Digite sua mensagem aqui...')
        self.input.bind(text=self.on_text)
        input_layout.add_widget(self.input)

        send_button = Button(text='Enviar', size_hint_x=0.2)
        send_button.bind(on_press=self.send_message)
        input_layout.add_widget(send_button)

        self.add_widget(input_layout)

        # Botões de controle
        control_layout = BoxLayout(size_hint_y=0.1)

        mic_button = Button(text='Usar Microfone')
        mic_button.bind(on_press=self.listen_microphone)
        control_layout.add_widget(mic_button)

        self.voice_toggle = Button(text='Desativar Voz' if self.assistente_falante else 'Ativar Voz')
        self.voice_toggle.bind(on_press=self.toggle_voice)
        control_layout.add_widget(self.voice_toggle)

        exit_button = Button(text='Sair')
        exit_button.bind(on_press=self.stop_app)
        control_layout.add_widget(exit_button)

        self.add_widget(control_layout)

        # Mensagem de boas-vindas
        bem_vindo = "# Bem-vindo ao seu Assistente de Suporte Emocional #\n### Digite 'desligar' para encerrar a sessão ###\n"
        self.update_history(bem_vindo)

    def on_text(self, instance, value):
        self.input_text = value

    def send_message(self, instance):
        texto = self.input.text.strip()
        if texto:
            self.update_history(f"[color=0000ff]Você:[/color] {texto}")
            self.input.text = ""
            threading.Thread(target=self.process_response, args=(texto,)).start()

    def listen_microphone(self, instance):
        threading.Thread(target=self.process_microphone).start()

    def toggle_voice(self, instance):
        self.assistente_falante = not self.assistente_falante
        if self.assistente_falante:
            self.voice_toggle.text = 'Desativar Voz'
            if not hasattr(self, 'engine') or self.engine is None:
                self.init_voice()
        else:
            self.voice_toggle.text = 'Ativar Voz'
            if hasattr(self, 'engine'):
                self.engine.stop()
                self.engine = None

    def stop_app(self, instance):
        App.get_running_app().stop()

    def process_response(self, texto):
        if texto.lower() == "desligar":
            self.update_history("Sessão encerrada pelo usuário.")
            self.stop_app(None)
            return

        try:
            response = self.chat.send_message(texto)
            resposta_terapeutica = response.text.strip().replace("*", "")
            self.update_history(f"[color=ff0000]Gemini:[/color] {resposta_terapeutica}")
            if self.assistente_falante and self.engine:
                self.engine.say(resposta_terapeutica)
                self.engine.runAndWait()
        except Exception as e:
            self.update_history(f"Erro ao obter resposta: {e}")

    def process_microphone(self):
        if not self.ligar_microfone:
            return

        with self.microphone as fonte:
            self.recognizer.adjust_for_ambient_noise(fonte)
            self.update_history("Estou ouvindo...")
            try:
                audio = self.recognizer.listen(fonte, timeout=5)
                self.update_history("Reconhecendo fala...")
                texto = self.recognizer.recognize_google(audio, language="pt-BR")
                self.update_history(f"[color=0000ff]Você (via microfone):[/color] {texto}")
                self.process_response(texto)
            except sr.WaitTimeoutError:
                self.update_history("Tempo esgotado para escuta.")
            except sr.UnknownValueError:
                self.update_history("Não consegui entender o que você disse. Pode repetir?")
            except sr.RequestError as e:
                self.update_history(f"Erro no serviço de reconhecimento de fala: {e}")

    @mainthread
    def update_history(self, message):
        self.chat_history += message + "\n"
        self.history_label.text = self.chat_history

class ChatApp(App):
    def build(self):
        return ChatInterface()

if __name__ == '__main__':
    ChatApp().run()
