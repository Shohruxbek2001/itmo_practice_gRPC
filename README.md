# Практика 8. gRPC

# Выполнил: Бабаев Шохрухбек

1. Клонируйте репозиторий

2. Установите зависимости

```bash
pip install -r requirements.txt
```

3. Сгенерируйте файлы proto

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. glossary.proto
```

4. Соберите и запустите контейнер

```bash
docker-compose up --build
```