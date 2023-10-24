from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel
from kivy.uix.image import AsyncImage
import openai

openai.api_key = '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'

KV = """
<MainScreen>:
    BoxLayout:
        orientation: "vertical"
        spacing: "10dp"
        padding: "10dp"

        MDTopAppBar:
            title: "Pasos para usar intelicuento:"
            md_bg_color: app.theme_cls.primary_color

        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                spacing: "10dp"  # Agregar espacio entre los elementos
                adaptive_height: True

                MDLabel:
                    text:
                        "- Piensa y escribe una historia divertida y emocionante. Incluye personajes, lugares interesantes y cosas emocionantes que pasen.[/color][/size]\\n" \
                        "\\n" \
                        "- Lee lo que escribiste y asegúrate de que se vea bien y cuente la historia como tú quieres.[/color][/size]\\n" \
                        "\\n" \
                        "- Haz clic en el botón para enviar tu historia.[/color][/size]\\n" \
                        "\\n" \
                        "- La aplicación tomará tu historia y la convertirá en un cuento usando su tecnología especial de inteligencia artificial. ¡Es como magia![/color][/size]\\n" \
                        "\\n" \
                        "- Una vez que el cuento esté listo, podrás leerlo y descubrir la historia que se creó basada en lo que escribiste.[/color][/size]"
                    markup: True
                    halign: "left"
                    font_style: "Body1"
                    size_hint_y: None
                    height: self.texture_size[1]
                
        RelativeLayout:  # Usar RelativeLayout para posicionar el cuadro de texto y el botón
            MDTextField:
                id: input_text
                hint_text: "Empieza a crear tu intelicuento"
                helper_text_mode: "on_focus"
                multiline: True
                size_hint_x: 0.8  

            MDFillRoundFlatButton:
                text: "Enviar"
                on_release: app.on_send_press(input_text.text)
                pos_hint: {"right": 1}  
                size_hint_x: 0.2  

<ResponseScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "56dp"
            padding: "10dp"
            spacing: "10dp"
            elevation: 10
            md_bg_color: app.theme_cls.primary_color

            MDIconButton:
                icon: "arrow-left"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: app.go_back_to_main_screen()

            MDLabel:
                text: "¡Aquí esta tu Intelicuento!"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1

        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                spacing: "10dp"
                padding: "10dp"
                adaptive_height: True

                MDLabel:
                    id: response_label
                    text: ""
                    font_style: "Body1"
                    theme_text_color: "Primary"
                    size_hint_y: None
                    height: self.texture_size[1]

        AsyncImage:
            id: generated_image
            size_hint_y: None
            height: "200dp"

ScreenManager:
    MainScreen:
        name: "main"
    ResponseScreen:
        name: "response"
"""


class MainScreen(Screen):
    pass


class ResponseScreen(Screen):
    pass


class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        return Builder.load_string(KV)

    def on_send_press(self, input_text):
        if input_text.strip() == "":
            print("No puedes enviar un prompt vacío.")
        else:
            response_text, image_url = self.get_dalle_response(input_text)
            print(f"Mensaje enviado: {input_text}")
            print(f"Respuesta de OpenAI: {response_text}")
            print(f"URL de la imagen generada: {image_url}")
            self.show_response_screen(response_text, image_url)

    def get_dalle_response(self, prompt):
        response_text = self.get_openai_response(prompt)
        response_image = self.generate_image_with_dalle(prompt)
        return response_text, response_image

    def get_openai_response(self, input_text):
        role = "Escritor de cuentos infantiles"
        prompt = f"{role}: {input_text}\n"  

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.8,
        )
        return response['choices'][0]['text']

    def generate_image_with_dalle(self, prompt):
        # Verificar si el indicador "dibujo infantil" está presente en el prompt
        # Si no está presente, lo agregamos al inicio del prompt
        if "dibujo infantil" not in prompt.lower():
            prompt = f"dibujo para cuento infantil: {prompt}"

        # Parámetros para la solicitud a la API de DALL-E
        params = {
            "prompt": prompt,
            "n": 1,
            "size": "512x512",
        }

        try:
            response = openai.Image.create(**params)
            if 'data' in response and len(response['data']) > 0:
                # Obtener la URL de la imagen generada
                image_data = response['data'][0]['url']
                return image_data
            else:
                print("No se recibieron datos válidos de la API de DALL-E.")
        except Exception as e:
            print(f"Error en la solicitud a la API de DALL-E: {e}")

        return None

    def show_response_screen(self, response_text, image_url):
        response_screen = self.root.get_screen("response")
        response_screen.ids.response_label.text = response_text
        response_screen.ids.generated_image.source = image_url
        self.root.current = "response"

    def go_back_to_main_screen(self):
        self.root.current = "main"


if __name__ == "__main__":
    MyApp().run()
