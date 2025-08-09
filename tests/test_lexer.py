"""
AquaScript词法分析器测试
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'compiler'))

from lexer import Lexer, TokenType

def test_basic_tokens():
    """测试基本token"""
    print("Testing basic tokens...")
    
    code = "123 + 456 * 789"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    expected = [
        (TokenType.NUMBER, "123"),
        (TokenType.PLUS, "+"),
        (TokenType.NUMBER, "456"),
        (TokenType.MULTIPLY, "*"),
        (TokenType.NUMBER, "789"),
        (TokenType.EOF, "")
    ]
    
    for i, (expected_type, expected_value) in enumerate(expected):
        assert tokens[i].type == expected_type, f"Expected {expected_type}, got {tokens[i].type}"
        assert tokens[i].value == expected_value, f"Expected {expected_value}, got {tokens[i].value}"
    
    print("√ Basic tokens test passed")

def test_keywords():
    """测试关键字"""
    print("Testing keywords...")
    
    code = "def if else for while return True False None"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    expected_types = [
        TokenType.DEF, TokenType.IF, TokenType.ELSE, TokenType.FOR,
        TokenType.WHILE, TokenType.RETURN, TokenType.TRUE, TokenType.FALSE,
        TokenType.NONE, TokenType.EOF
    ]
    
    for i, expected_type in enumerate(expected_types):
        assert tokens[i].type == expected_type, f"Expected {expected_type}, got {tokens[i].type}"
    
    print("√ Keywords test passed")

def test_strings():
    """测试字符串"""
    print("Testing strings...")
    
    code = '"Hello, World!" \'AquaScript\' "Line\\nBreak"'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    expected = [
        (TokenType.STRING, "Hello, World!"),
        (TokenType.STRING, "AquaScript"),
        (TokenType.STRING, "Line\nBreak"),
        (TokenType.EOF, "")
    ]
    
    for i, (expected_type, expected_value) in enumerate(expected):
        assert tokens[i].type == expected_type, f"Expected {expected_type}, got {tokens[i].type}"
        assert tokens[i].value == expected_value, f"Expected {expected_value}, got {tokens[i].value}"
    
    print("√ Strings test passed")

def test_indentation():
    """测试缩进"""
    print("Testing indentation...")
    
    code = '''def test():
    if True:
        print("Hello")
    else:
        print("World")
'''
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    # 查找INDENT和DEDENT token
    indent_count = sum(1 for token in tokens if token.type == TokenType.INDENT)
    dedent_count = sum(1 for token in tokens if token.type == TokenType.DEDENT)
    
    assert indent_count == 3, f"Expected 3 INDENT tokens, got {indent_count}"
    assert dedent_count == 3, f"Expected 3 DEDENT tokens, got {dedent_count}"
    
    print("√ Indentation test passed")

def test_operators():
    """测试运算符"""
    print("Testing operators...")
    
    code = "== != <= >= ** and or not"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    expected_types = [
        TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_EQUAL,
        TokenType.GREATER_EQUAL, TokenType.POWER, TokenType.AND,
        TokenType.OR, TokenType.NOT, TokenType.EOF
    ]
    
    for i, expected_type in enumerate(expected_types):
        assert tokens[i].type == expected_type, f"Expected {expected_type}, got {tokens[i].type}"
    
    print("√ Operators test passed")

def test_comments():
    """测试注释"""
    print("Testing comments...")
    
    code = '''# This is a comment
x = 42  # Another comment
# Final comment'''
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    comment_tokens = [token for token in tokens if token.type == TokenType.COMMENT]
    assert len(comment_tokens) == 3, f"Expected 3 comment tokens, got {len(comment_tokens)}"
    
    print("√ Comments test passed")

def run_all_tests():
    """运行所有测试"""
    print("Running AquaScript Lexer Tests")
    print("=" * 40)
    
    try:
        test_basic_tokens()
        test_keywords()
        test_strings()
        test_indentation()
        test_operators()
        test_comments()
        
        print("=" * 40)
        print("All tests passed! √")
        
    except AssertionError as e:
        print(f"Test failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)