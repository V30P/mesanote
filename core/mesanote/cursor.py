from typing import Sequence, Iterable, cast


class CursorError(Exception):
    pass


class Cursor[T]:
    def __init__(self, sequence: Sequence[T]) -> None:
        self.sequence = sequence
        self.pos = 0

    def is_at_end(self) -> bool:
        return self.pos >= len(self.sequence)

# region Single element methods
    def peek(self) -> T:
        if self.is_at_end():
            raise CursorError("Cannot peek past the end of the sequence.")
        
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
            self.pos += 1
            return True
        
        return False
# endregion

# region Multiple element methods
    def peek_many(self, n: int) -> Sequence[T]:
        if self.pos + n > len(self.sequence):
            raise CursorError("Cannot peek past the end of the sequence.")
        return self.sequence[self.pos : self.pos + n]

    def advance_many(self, n: int) -> Sequence[T]:
        if self.pos + n > len(self.sequence):
            raise CursorError("Cannot advance past the end of the sequence.")
        
        elements = self.sequence[self.pos : self.pos + n]
        self.pos += n
        return elements

    def check_many(self, sequence: Sequence[T]) -> bool:
        n = len(sequence)
        if self.pos + n > len(self.sequence):
            return False
        
        return self.peek_many(n) == sequence

    def match_many(self, sequence: Sequence[T]) -> bool:
        if self.check_many(sequence):
            self.pos += len(sequence)
            return True
        
        return False
# endregion

# region Multiple sequence methods
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
# endregion
