import javalang

def extract_method_texts(code):
    codelines = code.splitlines()
    tree = javalang.parse.parse(code)
    for _, method_node in tree.filter(javalang.tree.MethodDeclaration):
        # Find line of method declaration
        startline = method_node.position.line - 1
        # Find line of first brace
        for i, line in enumerate(codelines[startline:]):
            if line.count('{') > 0:
                break
        firstbraceline = startline + i
        # Find line of last brace
        braces = 0
        for i, line in enumerate(codelines[firstbraceline:]):
            braces += line.count('{') - line.count('}')
            if braces == 0: # use the fact that braces must be balanced
                break
        endline = firstbraceline + i + 1
        # Return the method texts one by one as generator
        yield '\n'.join(codelines[startline:endline])

if __name__ == "__main__":
    with open("./MyClass.java", 'r') as infile:
        code = infile.read()
    
    for method in extract_method_texts(code):
        print(method)

