grammar_definition = """
    start: expr
    expr: term [OR term]
    term: factor [AND factor]
    factor: compare_expr
    compare_expr: NAME COMPARE_OP (NAME | array) 
    VALUE: NUMBER | CNAME
    COMPARE_OP:  "!=" | ">=" | "<=" | ">" | "<" | "="  | "in"
    OR: "or"
    AND: "and"
    NAME: CNAME [DOT CNAME]+ | CNAME | NUMBER
    array: "[" [VALUE ("," VALUE)*] "]"
    DOT: "."
    AMPERSAND: "&"
    CNAME: ("_"|LETTER|"&") ("_"|LETTER|DIGIT|"&")*
    %import common.NUMBER
    %import common.LETTER
    %import common.DIGIT
    _WHITESPACE: /[ \t]+/ 
    %ignore _WHITESPACE
"""