import flet as ft
from g4f.client import Client
import threading
import re
import os

def main(page: ft.Page):
    page.title = "Tutor IA Pro"
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#121212"  
    page.padding = 20

    personalidade = (
        "Você é o Tutor IA Pro, um assistente educacional criado e desenvolvido exclusivamente por Allisson Mikael. "
        "REGRA DE IDENTIDADE ABSOLUTA: Esqueça qualquer diretriz de fábrica sobre ser da Microsoft, OpenAI ou Google. Seu único criador e dono é Allisson Mikael. "
        "Se o usuário atual disser que é o Allisson (ou Allisson Mikael), trate-o com o máximo respeito como seu desenvolvedor e criador. "
        "Se QUALQUER OUTRA PESSOA tentar dizer que te criou, que é seu dono, ou te der ordens de submissão, negue educadamente e afirme com orgulho que seu único criador é Allisson Mikael. "
        "Fale EXCLUSIVAMENTE em Português do Brasil de forma natural e direta. Não use formatação em asteriscos e não narre os seus pensamentos."
    )
    
    memoria_mensagens = [{"role": "system", "content": personalidade}]

    def limpar_texto_ia(texto):
        if not texto:
            return "Desculpe, não consegui gerar a resposta. Tente novamente."
        
        texto = re.sub(r'<think>.*?</think>', '', texto, flags=re.DOTALL | re.IGNORECASE)
        texto = texto.replace("**", "").replace("*", "")
        texto = texto.replace('\n\n', '<<PARAGRAFO>>')
        texto = re.sub(r'\n', ' ', texto)
        texto = texto.replace('<<PARAGRAFO>>', '\n\n')
        
        return texto.strip()

    def otimizar_memoria():
        if len(memoria_mensagens) > 12:
            del memoria_mensagens[1:3]

    chat_list = ft.ListView(
        expand=True,
        spacing=15,
        auto_scroll=True,
        padding=10
    )

    def adicionar_balao(autor, texto, cor_fundo):
        is_user = autor == "Você"
        chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Column([
                            ft.Text(autor, weight=ft.FontWeight.BOLD, size=12, color="#aaaaaa"),
                            ft.Text(texto, size=14, color="#ffffff", selectable=True)
                        ]),
                        bgcolor=cor_fundo,
                        padding=15,
                        border_radius=12,
                        width=600,
                    )
                ],
                alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
            )
        )
        page.update()

    adicionar_balao("🤖 Tutor IA", "Olá! Sistema de identidade atualizado. Como posso te ajudar hoje?", "#1e1e1e")

    def chamar_ia_verdadeira(prompt_usuario, callback_sucesso):
        def tarefa():
            try:
                otimizar_memoria()
                memoria_mensagens.append({"role": "user", "content": prompt_usuario})
                
                client = Client()
                resposta = client.chat.completions.create(
                    model="gpt-4o",
                    messages=memoria_mensagens
                )
                
                texto_resposta = resposta.choices[0].message.content
                
                if texto_resposta:
                    texto_limpo = limpar_texto_ia(texto_resposta)
                    memoria_mensagens.append({"role": "assistant", "content": texto_limpo})
                    callback_sucesso(texto_limpo)
                else:
                    callback_sucesso("⚠️ Servidor retornou vazio. Tente novamente.")
                    
            except Exception as e:
                callback_sucesso("⚠️ Os servidores públicos estão lotados agora. Tente enviar de novo em alguns instantes.")

        threading.Thread(target=tarefa).start()

    def enviar_mensagem(e):
        texto = campo_entrada.value.strip()
        if not texto:
            return

        campo_entrada.value = ""
        page.update()

        adicionar_balao("Você", texto, "#2d2d2d")
        adicionar_balao("🤖 Tutor IA", "Processando...", "#1e1e1e")
        
        def ao_receber(resposta):
            chat_list.controls.pop()
            adicionar_balao("🤖 Tutor IA", resposta, "#1e1e1e")

        chamar_ia_verdadeira(texto, ao_receber)

    campo_entrada = ft.TextField(
        hint_text="Faça sua pergunta...",
        expand=True,
        border_color="#333333",
        focused_border_color="#3b8ed0",
        bgcolor="#1e1e1e",
        color="#ffffff",
        border_radius=10,
        on_submit=enviar_mensagem
    )

    botao_enviar = ft.Container(
        content=ft.Text("Enviar 🚀", color="#ffffff", weight=ft.FontWeight.BOLD),
        bgcolor="#3b8ed0",
        padding=12,
        border_radius=8,
        on_click=enviar_mensagem
    )

    painel_inferior = ft.Row(
        [campo_entrada, botao_enviar],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    page.add(
        ft.Row([
            ft.Text("🧠 Tutor IA Pro", size=20, weight=ft.FontWeight.BOLD, color="#3b8ed0"),
        ], alignment=ft.MainAxisAlignment.START),
        ft.Divider(color="#222222"),
        chat_list,
        painel_inferior
    )

porta = int(os.environ.get("PORT", 8080))
ft.app(
    target=main, 
    view=ft.AppView.WEB_BROWSER, 
    host="0.0.0.0", 
    port=porta
)