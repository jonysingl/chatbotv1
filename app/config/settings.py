TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "123456",
                "database": "chatsql",
                "minsize": 1,
                "maxsize": 5,
                "charset": "utf8mb4",
                "echo": True
            }
        }
    },
    "apps": {
        "models": {
            "models": ["app.models.orm.user", "app.models.orm.chat", "aerich.models"],
            "default_connection": "default"
        }
    },
    "use_tz": False,  # 应该放在顶层，而不是 apps 里
    "timezone": "Asia/Shanghai"  # 时区建议用 "Asia/Shanghai"（云南时区可能不支持）
}
