import feedparser
from bs4 import BeautifulSoup
from atproto import Client

# Configurações
RSS_FEEDS = [
    "https://www.vaticannews.va/pt.rss.xml",  # Feed do Vatican News PT
    # "https://siteficticio.xml",  # Feed fictício (descomente para adicionar)
]
BLUESKY_USERNAME = "seu_usuario_bluesky"
BLUESKY_PASSWORD = "sua_senha_bluesky"

# Função para extrair o texto do RSS
def get_latest_news(rss_url):
    feed = feedparser.parse(rss_url)
    latest_entry = feed.entries[0]  # Pega a postagem mais recente
    title = latest_entry.title
    link = latest_entry.link
    description = latest_entry.description

    # Remove tags HTML da descrição (se houver)
    soup = BeautifulSoup(description, "html.parser")
    clean_description = soup.get_text()

    return title, link, clean_description

# Função para publicar no Bluesky
def post_to_bluesky(title, link, description):
    client = Client()
    client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)

    # Formata a mensagem
    post_text = f"{title}\n\n{description}\n\nLeia mais: {link}"

    # Publica no Bluesky
    client.send_post(text=post_text)
    print(f"Post publicado com sucesso no Bluesky: {title}")

# Executa o processo
if __name__ == "__main__":
    try:
        for rss_url in RSS_FEEDS:
            title, link, description = get_latest_news(rss_url)
            post_to_bluesky(title, link, description)
    except Exception as e:
        print(f"Erro ao publicar no Bluesky: {e}")