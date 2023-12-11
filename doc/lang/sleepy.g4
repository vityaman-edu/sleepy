grammar sleepy;

WS
    : [ \r\n\t]+ -> skip
    ;

program
    : expression+ EOF
    ;

expression
    : atomic
    | lambda
    | ifExpression
    | variableDefinition
    | application
    ;

atomic
    : SYMBOL
    | INTEGER
    | STRING
    | BOOLEAN
    ;

application
    : LCURL expression expression* RCURL
    ;

ifExpression
    : LCURL IF expression expression expression RCURL
    ;

variableDefinition
    : LCURL DEF SYMBOL expression RCURL
    ;

lambda
    : LCURL LAMBDA LCURL lambdaParameter* RCURL expression+ RCURL
    ;

lambdaParameter
    : SYMBOL SYMBOL
    ;

BOOLEAN
    : TRUE
    | FALSE
    ;

SYMBOL
    : LETTER+
    ;

INTEGER
    : ZERO
    | SIGN? NON_ZERO_DIGIT DIGIT*
    ;

STRING
    : QUOTE STRING_ATOM* QUOTE
    ;

STRING_ATOM
    : [a-zA-Z0-9 .,!?]
    ;

SIGN
    : MINUS
    | PLUS
    ;

LETTER
    : [a-z]
    ;

DIGIT
    : ZERO
    | NON_ZERO_DIGIT
    ;

NON_ZERO_DIGIT
    : [1-9]
    ;

ZERO
    : '0'
    ;

QUOTE
    : '"'
    ;

LAMBDA
    : 'lambda'
    ;

IF
    : 'if'
    ;

DEF
    : 'def'
    ;

LCURL
    : '('
    ;

RCURL
    : ')'
    ;

MINUS
    : '-'
    ;

PLUS
    : '+'
    ;

SPACE
    : ' '
    ;

COMMA
    : ','
    ;

DOT
    : '.'
    ;

COMMENT_OUT
    : ';'
    ;

SELF
    : 'self'
    ;

TRUE
    : 'true'
    ;

FALSE
    : 'false'
    ;