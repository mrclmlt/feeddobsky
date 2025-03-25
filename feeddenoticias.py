import feedparser
from bsup import BeautifulSoup
from atproto import Client
import os
import sys

# Configurações
RSS_URLS = [
    "https://www.vaticannews.va/pt.rss.xml",  # Feed principal
    # "https://siteficticio.xml",  # Feed fictício (descomente para adicionar)
]
MAX_POST_LENGTH = 300  # Limite do Bluesky
LINK_EMOJI = "🔗"      # Emoji para o link

def get_latest_news():
    """Obtém a última notícia dos feeds RSS"""
    try:
        print("\n=== INICIANDO LEITURA DOS FEEDS RSS ===")
        for url in RSS_URLS:
            print(f">> Verificando feed: {url}")
            feed = feedparser.parse(url)
            
            if feed.entries:
                latest = feed.entries[0]
                title = latest.title.strip()
                link = latest.link.strip()
                
                # Garante que o link tenha protocolo (https://)
                if not link.startswith(('http://', 'https://')):
                    link = f"https://{link}"
                
                print(f">> Notícia encontrada: {title[:60]}...")
                return title, link
        
        print(">> AVISO: Nenhuma notícia encontrada em nenhum feed")
        return None, None

    except Exception as e:
        print(f">> ERRO CRÍTICO AO LER RSS: {str(e)}")
        return None, None

def prepare_post(title, link):
    """Formata o post garantindo links clicáveis e limite de caracteres"""
    # Formato otimizado para clicabilidade:
    post_text = f"{title}\n\n{LINK_EMOJI} {link}"
    
    # Verificação de comprimento
    if len(post_text) > MAX_POST_LENGTH:
        # Calcula espaço disponível (reservando 23 chars para o link + emoji)
        max_title_length = MAX_POST_LENGTH - len(LINK_EMOJI) - len(link) - 4  # 4 = espaços e quebras
        title = f"{title[:max_title_length]}..."
        post_text = f"{title}\n\n{LINK_EMOJI} {link}"
    
    print(f">> Tamanho do post: {len(post_text)}/{MAX_POST_LENGTH} caracteres")
    return post_text

def post_to_bluesky(title, link):
    """Publica no Bluesky com tratamento robusto de erros"""
    try:
        client = Client()
        print("\n=== TENTANDO AUTENTICAÇÃO ===")
        client.login(os.environ['BLUESKY_USERNAME'], os.environ['BLUESKY_PASSWORD'])
        print(">> Autenticação bem-sucedida!")

        post_text = prepare_post(title, link)
        print(f"\n=== CONTEÚDO PRONTO ===\n{post_text}")

        response = client.send_post(text=post_text)
        print("\n>> Post publicado com sucesso!")
        print(f">> URL: bsky.app/profile/{response.uri.split('/')[-2]}/post/{response.uri.split('/')[-1]}")

    except Exception as e:
        print(f"\n>> ERRO NA PUBLICAÇÃO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Validação das credenciais
    required_vars = ['BLUESKY_USERNAME', 'BLUESKY_PASSWORD']
    if not all(var in os.environ for var in required_vars):
        print("ERRO: Configure os secrets no GitHub:")
        print("- BLUESKY_USERNAME: seu_handle.bsky.social")
        print("- BLUESKY_PASSWORD: sua_senha_ou_app_password")
        sys.exit(1)

    # Fluxo principal
    title, link = get_latest_news()
    
    if title and link:
        post_to_bluesky(title, link)
    else:
        print(">> Nenhum conteúdo válido para postar.")
        sys.exit(0)
