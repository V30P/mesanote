from mesanote.nodes import String, Text
from mesanote.tokens import StringStartToken, StringEndToken, TextToken

def string_of(text: str):
    return String([Text(text)])

def tokens_of(text: str):
    return [StringStartToken(), TextToken(text), StringEndToken()]