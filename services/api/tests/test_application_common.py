from types import TracebackType
from typing import Self

import pytest

from app.application.common import (
    BaseUseCase,
    Command,
    CommandHandler,
    Query,
    QueryHandler,
    Result,
    UnitOfWork,
)


def test_result_success() -> None:
    # Act
    res: Result[str] = Result.ok("Hello")

    # Assert
    assert res.is_success is True
    assert res.is_failure is False
    assert res.value == "Hello"
    
    with pytest.raises(ValueError, match="Cannot access error"):
        _ = res.error

def test_result_failure() -> None:
    # Act
    res: Result[str] = Result.fail("Something went wrong")

    # Assert
    assert res.is_success is False
    assert res.is_failure is True
    assert res.error == "Something went wrong"

    with pytest.raises(ValueError, match="Cannot access value"):
        _ = res.value

def test_result_validation() -> None:
    with pytest.raises(ValueError, match="cannot have an error"):
        Result(success=True, value="ok", error="err")

    with pytest.raises(ValueError, match="must have an error"):
        Result(success=False, value=None, error=None)

@pytest.mark.asyncio
async def test_base_use_case() -> None:
    # Arrange
    class MockUseCase(BaseUseCase[str, int]):
        async def execute(self, request: str) -> int:
            return len(request)

    use_case = MockUseCase()

    # Act
    val = await use_case.execute("test")

    # Assert
    assert val == 4

@pytest.mark.asyncio
async def test_command_handler() -> None:
    # Arrange
    class MockCommand(Command):
        def __init__(self, data: str) -> None:
            self.data = data

    class MockCommandHandler(CommandHandler[MockCommand, str]):
        async def handle(self, command: MockCommand) -> Result[str]:
            return Result.ok(command.data.upper())

    handler = MockCommandHandler()
    cmd = MockCommand("hello")

    # Act
    res = await handler.handle(cmd)

    # Assert
    assert res.is_success is True
    assert res.value == "HELLO"

@pytest.mark.asyncio
async def test_query_handler() -> None:
    # Arrange
    class MockQuery(Query):
        def __init__(self, key: int) -> None:
            self.key = key

    class MockQueryHandler(QueryHandler[MockQuery, int]):
        async def handle(self, query: MockQuery) -> Result[int]:
            return Result.ok(query.key * 2)

    handler = MockQueryHandler()
    qry = MockQuery(5)

    # Act
    res = await handler.handle(qry)

    # Assert
    assert res.is_success is True
    assert res.value == 10

@pytest.mark.asyncio
async def test_unit_of_work_interface() -> None:
    # Arrange
    class MockUnitOfWork(UnitOfWork):
        def __init__(self) -> None:
            self.committed = False
            self.rolled_back = False

        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
        ) -> bool | None:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
            return None

        async def commit(self) -> None:
            self.committed = True

        async def rollback(self) -> None:
            self.rolled_back = True

    # Act & Assert (Success flow)
    async with MockUnitOfWork() as uow:
        pass
    assert uow.committed is True
    assert uow.rolled_back is False

    # Act & Assert (Failure flow)
    uow2 = MockUnitOfWork()
    with pytest.raises(RuntimeError):
        async with uow2:
            raise RuntimeError("Error")
    assert uow2.committed is False
    assert uow2.rolled_back is True
