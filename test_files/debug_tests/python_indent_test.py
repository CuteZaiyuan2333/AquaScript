"""
测试Python的缩进行为
"""

import token
import tokenize
import io

def test_python_indentation():
    code = '''def test():
    if True:
        print("Hello")
    else:
        print("World")
'''
    
    print("Python tokenization:")
    tokens = tokenize.generate_tokens(io.StringIO(code).readline)
    
    indent_count = 0
    dedent_count = 0
    
    for tok in tokens:
        if tok.type in [token.INDENT, token.DEDENT, token.NEWLINE] or (tok.type == token.NAME and tok.string in ['def', 'if', 'else']):
            print(f"{token.tok_name[tok.type]:15} '{tok.string}' Line: {tok.start[0]}")
            
            if tok.type == token.INDENT:
                indent_count += 1
            elif tok.type == token.DEDENT:
                dedent_count += 1
    
    print(f"\nPython INDENT count: {indent_count}")
    print(f"Python DEDENT count: {dedent_count}")

if __name__ == "__main__":
    test_python_indentation()