```
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
```

- Эта команда устанавливает переменную окружения `SSL_CERT_FILE`, указывающую на файл сертификатов, предоставляемый библиотекой `certifi`.
- Фикс для MacOS и, возможно Linux.