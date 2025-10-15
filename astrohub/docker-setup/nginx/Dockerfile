FROM nginx:1.26.0-alpine

# Перезаписываем дефолтную конфигурацию
COPY configs/nginx.conf /etc/nginx/nginx.conf
COPY configs/uwsgi_params /etc/nginx/uwsgi_params

# Запускаеи сервер
CMD ["nginx", "-g", "daemon off;"]