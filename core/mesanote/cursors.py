from typing import Sequence, Iterable, cast


class CursorDepletedError(Exception):
    pass


class Cursor[T]:
    def __init__(self, sequence: Sequence[T]) -> None:
        self.sequence = sequence
        self.pos = 0

    def is_at_end(self) -> bool:
        return self.pos >= len(self.sequence)

    def peek(self) -> T:
        if self.is_at_end():
            raise CursorDepletedError("Cannot peek past the end of the sequence.")

        return self.sequence[self.pos]

    def advance(self) -> T:
        element = self.peek()
        self.pos += 1
        return element

    def check(self, element: T) -> bool:
        if self.is_at_end():
            return False

        return self.sequence[self.pos] == element

    def match(self, element: T) -> bool:
        if self.check(element):
            self.advance()
            return True

        return False

    def previous(self) -> T:
        if self.pos != 0:
            return self.sequence[self.pos - 1]

    def check_type(self, type: type) -> bool:
        return isinstance(self.peek(), type)

    def match_type(self, type: type) -> bool:
        matched = self.check_type(type)
        if matched:
            self.advance()
        return matched

    def peek_many(self, n: int) -> Sequence[T]:
        if self.pos + n > len(self.sequence):
            raise CursorDepletedError("Cannot peek past the end of the sequence.")
        return self.sequence[self.pos : self.pos + n]

    def advance_many(self, n: int) -> Sequence[T]:
        if self.pos + n > len(self.sequence):
            raise CursorDepletedError("Cannot advance past the end of the sequence.")

        elements = self.sequence[self.pos : self.pos + n]
        for _ in range(n):
            self.advance()
        return elements

    def check_many(self, sequence: Sequence[T]) -> bool:
        n = len(sequence)
        if self.pos + n > len(self.sequence):
            return False

        return self.peek_many(n) == sequence

    def match_many(self, sequence: Sequence[T]) -> bool:
        if self.check_many(sequence):
            for _ in range(len(sequence)):
                self.advance()
            return True

        return False

    def check_any_of(self, values: Iterable[T | Sequence[T]]) -> bool:
        for value in values:
            if isinstance(value, Sequence) and (
                not isinstance(value, str) or len(value) > 1
            ):
                if self.check_many(cast(Sequence[T], value)):
                    return True
            else:
                if self.check(cast(T, value)):
                    return True

        return False

    def match_any_of(self, values: Iterable[T | Sequence[T]]) -> bool:
        for value in values:
            if isinstance(value, Sequence) and (
                not isinstance(value, str) or len(value) > 1
            ):
                if self.match_many(cast(Sequence[T], value)):
                    return True
            else:
                if self.match(cast(T, value)):
                    return True

        return False


class StrCursor(Cursor[str]):
    char_pos = property(lambda self: (self.line_number, self.char_number))

    def __init__(self, sequence):
        super().__init__(sequence)

        self.line_number = self.char_number = 1

    def advance(self) -> str:
        char = super().advance()
        if char == "\n":
            self.char_number = 1
            self.line_number += 1
        else:
            self.char_number += 1

        return char
