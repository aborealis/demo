FROM nginx:alpine3.22-perl

# Перезаписываем дефолтную конфигурацию
COPY configs/nginx.conf /etc/nginx/nginx.conf

# Запускаеи сервер
CMD ["nginx", "-g", "daemon off;"]