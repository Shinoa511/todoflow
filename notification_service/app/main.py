from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
from .database import init_db
from .consumer import start_consumer_background
from .monitoring import router as monitoring_router

app = FastAPI(title='Notification Service')
app.include_router(monitoring_router)

@app.on_event('startup')
def startup():
    init_db()
    start_consumer_background()

@app.get('/')
def root():
    return {'ok': True, 'service': 'notification'}

# Добавляем HTML страницу
@app.get('/monitoring-ui', response_class=HTMLResponse)
def monitoring_ui():
    """Веб-интерфейс для мониторинга"""
    html_path = os.path.join(os.path.dirname(__file__), 'templates', 'monitoring.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())