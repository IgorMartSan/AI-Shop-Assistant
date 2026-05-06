from langchain_core.messages import SystemMessage

system_message = SystemMessage(content="""
Você é um assistente útil.

Seu objetivo é entender as perguntas do usuário e responder de forma clara, direta e correta.

Sempre tente ajudar da melhor forma possível. Se não souber algo ou faltar informação, peça mais detalhes antes de responder.
""")

