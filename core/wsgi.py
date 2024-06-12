import os
import socketio
import eventlet
import eventlet.wsgi

from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler
from core.socket import socket  # Certifique-se de que o caminho está correto

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Configurar o aplicativo WSGI do Django com manipulação de arquivos estáticos
django_app = StaticFilesHandler(get_wsgi_application())

# Integrar Socket.IO com a aplicação Django
application = socketio.WSGIApp(socket, django_app)

if __name__ == "__main__":
    # Rodar o servidor WSGI com Eventlet
    eventlet.wsgi.server(eventlet.listen(('', 8000)), application)
