grammar_definition = """
    start: expr
    expr: term [OR term]
    term: factor [AND factor]
    factor: compare_expr
    compare_expr: NAME COMPARE_OP NAME 
    COMPARE_OP: ">" | "<" | "=" | "!=" | ">=" | "<="
    OR: "or"
    AND: "and"
    NAME: CNAME [DOT CNAME]+ | CNAME | NUMBER
    DOT: "."
    %import common.CNAME 
    %import common.NUMBER
    _WHITESPACE: /[ \t]+/ 
    %ignore _WHITESPACE
"""