# Guia de Deploy em VPS

## Estrutura do Projeto

```
imoveis_project/
├── setup/            ← configurações Django
├── core/             ← home, sobre, contato + painel admin
├── imoveis/          ← cadastro e exibição de imóveis
├── leads/            ← captação de contatos
├── templates/        ← todos os templates HTML
├── static/           ← arquivos estáticos (CSS, JS)
├── media/            ← uploads de fotos (gerado em runtime)
├── manage.py
├── requirements.txt
└── .env.example
```

---

## 1. Rodando localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Criar o arquivo .env
cp .env.example .env
# Edite .env e ajuste as variáveis (em dev, mantenha DEBUG=True)

# Criar as tabelas do banco
python manage.py migrate

# Criar o superusuário (admin do painel)
python manage.py createsuperuser

# Rodar o servidor
python manage.py runserver
```

Acesse:
- Site: http://localhost:8000/
- Painel: http://localhost:8000/painel/
- Admin Django: http://localhost:8000/django-admin/

---

## 2. Deploy em VPS (Ubuntu 22.04)

### 2.1 Preparar o servidor

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx -y
```

### 2.2 Enviar o projeto

```bash
# Na sua máquina local — envie via SCP ou Git
scp -r imoveis_project/ usuario@ip_do_servidor:/home/usuario/
# ou: git clone https://github.com/seu_usuario/imoveis_project
```

### 2.3 Configurar o ambiente Python

```bash
cd /home/usuario/imoveis_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### 2.4 Configurar o .env

```bash
cp .env.example .env
nano .env
```

Edite o arquivo `.env`:
```
SECRET_KEY=gere-uma-chave-com-python-secrets-token-hex-50
DEBUG=False
ALLOWED_HOSTS=seudominio.com.br,www.seudominio.com.br
WHATSAPP_NUMBER=5511999999999
BROKER_NAME=Ferian e Tavares
BROKER_CRECI=123456-F
```

Para gerar a SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(50))"
```

### 2.5 Preparar arquivos estáticos e banco

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 2.6 Configurar Gunicorn como serviço

Crie o arquivo `/etc/systemd/system/imoveis.service`:

```ini
[Unit]
Description=Ferian e Tavares — Gunicorn
After=network.target

[Service]
User=usuario
Group=www-data
WorkingDirectory=/home/usuario/imoveis_project
ExecStart=/home/usuario/imoveis_project/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/usuario/imoveis_project/imoveis.sock \
    setup.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Ative o serviço:
```bash
sudo systemctl daemon-reload
sudo systemctl start imoveis
sudo systemctl enable imoveis
sudo systemctl status imoveis  # deve mostrar "active (running)"
```

### 2.7 Configurar Nginx

Crie `/etc/nginx/sites-available/imoveis`:

```nginx
server {
    listen 80;
    server_name seudominio.com.br www.seudominio.com.br;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/usuario/imoveis_project/staticfiles/;
    }

    location /media/ {
        alias /home/usuario/imoveis_project/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/usuario/imoveis_project/imoveis.sock;
    }
}
```

Ative o site:
```bash
sudo ln -s /etc/nginx/sites-available/imoveis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2.8 HTTPS com Certbot (SSL grátis)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d seudominio.com.br -d www.seudominio.com.br
```

---

## 3. Atualizar o projeto (após mudanças)

```bash
cd /home/usuario/imoveis_project
source venv/bin/activate
git pull  # ou envie os arquivos novamente
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart imoveis
```

---

## 4. Painel administrativo

| URL | Função |
|-----|--------|
| `/painel/` | Dashboard com métricas |
| `/painel/imoveis/` | Lista de imóveis |
| `/painel/imoveis/novo/` | Cadastrar imóvel |
| `/painel/imoveis/<id>/editar/` | Editar imóvel |
| `/painel/imoveis/<id>/fotos/` | Upload e gestão de fotos |
| `/painel/leads/` | Lista de leads recebidos |
| `/painel/leads/<id>/` | Detalhes e anotações do lead |

---

## 5. Permissões da pasta media

```bash
sudo chown -R usuario:www-data /home/usuario/imoveis_project/media
sudo chmod -R 775 /home/usuario/imoveis_project/media
```

---

## 6. Dicas de segurança

- Nunca coloque `DEBUG=True` em produção
- Use senhas fortes para o superusuário
- Faça backup regular do `db.sqlite3` (ou migre para PostgreSQL em produção)
- Configure um firewall: `sudo ufw allow 'Nginx Full'` e `sudo ufw enable`

---

## Suporte

Em caso de dúvidas, verifique os logs:
```bash
sudo journalctl -u imoveis -f      # logs do Gunicorn
sudo tail -f /var/log/nginx/error.log  # logs do Nginx
```
