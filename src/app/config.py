from advanced_alchemy.extensions.litestar import EngineConfig, SQLAlchemyAsyncConfig
from core.database.models import Base


class DatabaseConfig:
    connection_string = 'sqlite+aiosqlite:///../../db.sqlite3'
    create_all = True
    echo = False

    config = SQLAlchemyAsyncConfig(
        connection_string=connection_string,
        metadata=Base.metadata,
        create_all=create_all,
        before_send_handler='autocommit',
        engine_config=EngineConfig(echo=echo),
    )
