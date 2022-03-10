from ply import lex as lex


TYPE_LABEL = "LABEL"
TYPE_WORD = "WORD"
TYPE_NUMBER = "NUMBER"
TYPE_APOSTROPHIZED = "APOSTROPHIZED"
TYPE_APOSTROPHE_CARRY = "APOSTROPHE_CARRY"
TYPE_HYPHENATED = "HYPHENATED"
TYPE_DELIMITER = "DELIMITER"
TYPE_PUNCTUATION = "PUNCTUATION"


class _Lexer:
    def __init__(self):
        self.lexer = None

    tokens = [
        TYPE_LABEL,
        TYPE_WORD,
        TYPE_NUMBER,
        TYPE_APOSTROPHIZED,
        TYPE_APOSTROPHE_CARRY,
        TYPE_HYPHENATED,
        TYPE_DELIMITER,
        TYPE_PUNCTUATION
    ]

    def t_LABEL(self, t):
        r'\$DOC|\$TITLE|\$TEXT'
        return t

    def t_NUMBER(self, t):
        # Using negative lookahead to drop number match if we find any word characters immediately
        # following the number (i.e. we'll let it get matched as a word instead)
        r'([\+\-]?\d*\.\d+(?!\d*[a-zA-Z]))|([\+\-]?\d+(?!\d*[a-zA-Z]))'
        return t

    # Can be either:
    # - 2 parts; 1'3+
    # - 2 parts; 1+'s
    # - 3 parts; 1'1+'s
    def t_APOSTROPHIZED(self, t):
        # Use negative look-ahead and look-behind to ensure we don't end or start in an
        # apostrophe or more word characters (in the case of 's endings)
        r"(?<!['\w])((\w{1}'\w{3,})|(\w+'[sS])|(\w{1}'\w+'[sS]))(?!['\w])"
        return t

    # If we have a two part apostrophized text (a'b) that fails to match t_APOSTROPHE,
    # and if the second part is 1 or 2 characters long, then we catch the text here
    def t_APOSTROPHE_CARRY(self, t):
        # Use negative look-behind to ensure we don't start with an extra '.
        # Ply won't let us perform variable length look-behind, so we can't search for text that matches only
        # the second half of this pattern.  I.e. we can't catch and match just the 'b component.  We have to
        # catch and match a'b.  We could catch just the 'b component if we could do a (?<!'\w+)
        r"(?<!')\w+'\w{1,2}(?!['\w])"
        t.value = t.value.replace("'", " '")
        return t

    # Either 2 parts, or 3 parts with 1 or 2 character middle.
    # The last part can be apostrophized, following the t_APOSTROPHIZED rules.
    def t_HYPHENATED(self, t):
        # The pattern uses negative look-behind and look-ahead to cancel a match if it starts with
        # or ends with an extra hyphen, apostrophe, or for 's endings, any extra word characters.
        r"(?<![\-'])"\
         "((\w+\-)|(\w+\-\w{1,2}\-))"\
         "((\w+)|(\w{1}'\w{3,})|(\w+'[sS])|(\w{1}'\w+'[sS]))"\
         "(?![\-'\w])"
        return t

    def t_WORD(self, t):
        r'\d*[a-zA-Z]+[\da-zA-Z]*'
        return t

    t_DELIMITER = r'\s'
    t_PUNCTUATION = r'.'

    def t_error(self, t):
        print("Uncaptured token {}".format(t))

    def build(self):
        self.lexer = lex.lex(module=self)


_m = _Lexer()
_m.build()
lexer = _m.lexer
