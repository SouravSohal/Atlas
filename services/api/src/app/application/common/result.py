class Result[T]:
    """A generic wrapper representing the result of an application or domain operation."""

    def __init__(
        self,
        success: bool,
        value: T | None = None,
        error: str | None = None,
    ) -> None:
        if success and error:
            raise ValueError("A successful result cannot have an error.")
        if not success and not error:
            raise ValueError("A failed result must have an error.")

        self._success = success
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._success

    @property
    def is_failure(self) -> bool:
        return not self._success

    @property
    def value(self) -> T:
        if not self._success:
            raise ValueError("Cannot access value of a failed result.")
        return self._value  # type: ignore[return-value]

    @property
    def error(self) -> str:
        if self._success:
            raise ValueError("Cannot access error of a successful result.")
        assert self._error is not None
        return self._error

    @classmethod
    def ok(cls, value: T | None = None) -> "Result[T]":
        """Creates a successful Result instance."""
        return cls(success=True, value=value)

    @classmethod
    def fail(cls, error: str) -> "Result[T]":
        """Creates a failed Result instance with an error message."""
        return cls(success=False, error=error)
