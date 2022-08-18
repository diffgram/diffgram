grammar_definition = """
    start: expr
    expr: term [OR term]
    term: factor [AND factor]
    factor: compare_expr
    ?quoted_string  : DOUBLE_QUOTED_STRING | SINGLE_QUOTED_STRING
    compare_expr: (NAME | array | quoted_string)  COMPARE_OP (NAME | array | quoted_string) 
    VALUE: NUMBER | CNAME | SINGLE_QUOTED_STRING | DOUBLE_QUOTED_STRING
    COMPARE_OP:  "!=" | ">=" | "<=" | ">" | "<" | "="  | "in"
    OR: "or"
    AND: "and"
    NAME: CNAME [DOT CNAME]+ | CNAME | NUMBER
    array: "[" [VALUE ("," VALUE)*] "]"
    DOT: "."
    AMPERSAND: "&"
    CNAME: ("_"|LETTER|"&") ("_"|LETTER|DIGIT|"&")*
    DOUBLE_QUOTED_STRING  : /"[^"]*"/
    SINGLE_QUOTED_STRING  : /'[^']*'/
    %import common.NUMBER
    %import common.LETTER
    %import common.DIGIT
    _WHITESPACE: /[ \t]+/ 
    %ignore _WHITESPACE
"""