"""Module description."""
from uuid import UUID
import pytest
from redis.exceptions import ConnectionError, AuthenticationError
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from services.storage.chat_redis import get_chat_memory_celery, RedisChatMemoryCelery
from services.storage.helpers.async_redis_manager import RedisChatMemoryFastAPI
from services.chat_session.helpers.db_loaders import load_with_logging


class TestRedisExceptionCatcher:
    """Test suite for redis exception catcher."""

    @pytest.mark.asyncio
    async def test_redis_retry_recovers(self, fake_memory: RedisChatMemoryFastAPI):
        """Test redis retry recovers."""
        fake_memory.redis.set = AsyncMock(
            side_effect=[
                ConnectionError("temporary down"),
                ConnectionError("temporary down"),
                True,
            ]
        )

        inbox_lock_acquired = await fake_memory.lock.try_start_processing_inbox()

        assert fake_memory.redis.set.call_count == 3

        assert inbox_lock_acquired is True

    @pytest.mark.asyncio
    async def test_redis_retry_fails_after_3_attempts(
        self,
        fake_memory: RedisChatMemoryFastAPI,
        valid_chat_passport_id: UUID,
    ):
        """Test redis retry fails after 3 attempts."""
        fake_memory.redis.set = AsyncMock(
            side_effect=[
                ConnectionError("temporary down"),
                ConnectionError("temporary down"),
                ConnectionError("temporary down"),
            ]
        )

        with pytest.raises(ConnectionError):
            await fake_memory.lock.try_start_processing_inbox()

        assert fake_memory.redis.set.call_count == 3

        inbox_lock_acquired = await fake_memory.redis.get(f"chat:{valid_chat_passport_id}:lock")
        assert inbox_lock_acquired is None

    @pytest.mark.asyncio
    async def test_redis_critical_error_no_retry(self, fake_memory: RedisChatMemoryFastAPI):
        """Test redis critical error no retry."""
        fake_memory.redis.set = AsyncMock(
            side_effect=AuthenticationError("bad password")
        )

        with pytest.raises(ConnectionError):
            await fake_memory.lock.try_start_processing_inbox()

        assert fake_memory.redis.set.call_count == 1


class TestRedisDecoratorsAsync:
    """Test suite for redis decorators async."""

    @pytest.mark.asyncio
    async def test_decorator_orders_transient_2_attempts(self, fake_memory: RedisChatMemoryFastAPI):
        """Test decorator orders transient 2 attempts."""

        fake_memory.redis.set = AsyncMock(
            side_effect=[
                ConnectionError("temp1"),
                ConnectionError("temp2"),
                None
            ]
        )

        import services.storage.helpers.storage_decorators as loc
        logger_call_location = f"{loc.__name__}.logger.warning"
        func_call_location = f"{loc.__name__}.log_and_raise_exception"

        with patch(logger_call_location) as mock_warning, \
                patch(func_call_location) as mock_critical:

            await fake_memory.classify.set_bot_shortname(
                bot_shortname="bot",
            )

            assert mock_warning.call_count == 2

            mock_critical.assert_not_called()

    @pytest.mark.asyncio
    async def test_decorator_orders_transient_3_attempts(self, fake_memory: RedisChatMemoryFastAPI):
        """Test decorator orders transient 3 attempts."""

        fake_memory.redis.set = AsyncMock(
            side_effect=ConnectionError("redis down")
        )

        import services.storage.helpers.storage_decorators as loc
        logger_call_location = f"{loc.__name__}.logger.warning"
        func_call_location = f"{loc.__name__}.log_and_raise_exception"

        with patch(logger_call_location) as mock_warning, \
                patch(func_call_location) as mock_critical:

            with pytest.raises(ConnectionError):
                await fake_memory.classify.set_bot_shortname(
                    bot_shortname="bot",
                )

            assert fake_memory.redis.set.call_count == 3

            assert mock_warning.call_count == 2

            assert mock_critical.call_count == 0

    @pytest.mark.asyncio
    async def test_retry_log_text(self,
                                  fake_memory: RedisChatMemoryFastAPI,
                                  valid_chat_passport_id: UUID):
        """Test retry log text."""
        fake_memory.redis.set = AsyncMock(
            side_effect=[
                ConnectionError("temp_error"),
                None
            ]
        )

        import services.storage.helpers.storage_decorators as loc
        logger_call_location = f"{loc.__name__}.logger.warning"

        with patch(logger_call_location) as mock_warning:

            await fake_memory.context.set_user_context(
                "fake context",
            )

            assert mock_warning.call_count == 1

            args, kwargs = mock_warning.call_args

            assert "temp_error" in args[0]

            assert "extra" in kwargs
            assert kwargs["extra"]["caller_name"] == "test_logging.test_retry_log_text"
            assert kwargs["extra"]["callee_name"] == "set_user_context"
            assert str(
                kwargs["extra"]["chat_passport_id"]) == valid_chat_passport_id


class TestRedisDecoratorsSync:
    """Test suite for redis decorators sync."""

    def test_decorator_orders_transient_2_attempts(self):
        """Test decorator orders transient 2 attempts."""
        chat_passport_id = uuid4()
        fake_memory: RedisChatMemoryCelery = get_chat_memory_celery(
            chat_passport_id)

        fake_memory.redis.set = Mock(
            side_effect=[
                ConnectionError("temp1"),
                ConnectionError("temp2"),
                None
            ]
        )

        import services.storage.helpers.storage_decorators as loc
        logger_call_location = f"{loc.__name__}.logger.warning"
        func_call_location = f"{loc.__name__}.log_and_raise_exception"

        with patch(logger_call_location) as mock_warning, \
                patch(func_call_location) as mock_critical:

            fake_memory.set_user_context(
                message="fake context",
            )

            assert mock_warning.call_count == 2

            mock_critical.assert_not_called()

    def test_decorator_orders_transient_3_attempts(self):
        """Test decorator orders transient 3 attempts."""
        chat_passport_id = uuid4()
        fake_memory: RedisChatMemoryCelery = get_chat_memory_celery(
            chat_passport_id)

        fake_memory.redis.set = Mock(
            side_effect=ConnectionError("redis down")
        )

        import services.storage.helpers.storage_decorators as loc
        logger_call_location = f"{loc.__name__}.logger.warning"
        func_call_location = f"{loc.__name__}.log_and_raise_exception"

        with patch(logger_call_location) as mock_warning, \
                patch(func_call_location) as mock_critical:

            with pytest.raises(ConnectionError):
                fake_memory.set_user_context(
                    message="fake context",
                )

            assert fake_memory.redis.set.call_count == 3

            assert mock_warning.call_count == 2

            assert mock_critical.call_count == 0

    def test_retry_log_text(self):
        """Test retry log text."""
        chat_passport_id = uuid4()
        fake_memory: RedisChatMemoryCelery = get_chat_memory_celery(
            chat_passport_id)

        fake_memory.redis.set = Mock(
            side_effect=[
                ConnectionError("temp_error"),
                None
            ]
        )

        import services.storage.helpers.storage_decorators as loc
        logger_call_location = f"{loc.__name__}.logger.warning"

        with patch(logger_call_location) as mock_warning:

            fake_memory.set_user_context("context")

            assert mock_warning.call_count == 1

            args, kwargs = mock_warning.call_args

            assert "temp_error" in args[0]

            assert "extra" in kwargs
            assert kwargs["extra"]["caller_name"] == 'test_logging.test_retry_log_text'
            assert kwargs["extra"]["callee_name"] == 'set_user_context'
            assert kwargs["extra"]["chat_passport_id"] == chat_passport_id


class TestSQLDecorators:
    @pytest.mark.asyncio
    async def test_logging_on_sql_err(self):
        """Test logging on sql err."""
        import services.chat_session.helpers.db_loaders as loc
        logger_call_location = f"{loc.__name__}.logger.exception"
        passport_id = uuid4()

        class FakeChatSession(BaseModel):
            chat_passport_id: UUID = passport_id

        fake_obj = FakeChatSession()

        @load_with_logging()
        async def load_user_by_id_for_tests(obj: FakeChatSession):
            raise SQLAlchemyError("Test error")

        with patch(logger_call_location) as mock_error:
            with pytest.raises(SQLAlchemyError):
                await load_user_by_id_for_tests(fake_obj)

            assert mock_error.call_count == 1

            args, kwargs = mock_error.call_args

            assert 'placeholder SQL' in args[0]

            assert "extra" in kwargs
            assert kwargs["extra"]["caller_name"] == 'test_logging.test_logging_on_sql_err'
            assert kwargs["extra"]["callee_name"] == 'load_user_by_id_for_tests'
            assert kwargs["extra"]["chat_passport_id"] == passport_id
