# realtime-data
Прототип сервиса по получению и предпросмотру торговых данных.
Стек - Django Rest Framework, PostgreSql, Celery, RabbitMQ, Nginx, Node.js, Docker

# Инструкция сборки и запуска

  1. Запустить сборку.

    docker-compose up --build
    
  2. Админпанель Джанго. Учетные данные в файле .env

    http://127.0.0.1/admin   - 
     
  3. Автодокументация.

    http://127.0.0.1/api/swagger/
    http://127.0.0.1/api/redoc/
   
  4. Веб-сервис.

    http://127.0.0.1:7070


 