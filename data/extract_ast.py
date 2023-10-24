import clang.cindex
from clang.cindex import CursorKind


def extract_function_ast(filename, function_name):
    # Initialize the Clang Index
    # clang.cindex.Config.set_library_path("/usr/bin/clang")  # Replace with the actual path to your clang library
    index = clang.cindex.Index.create()

    # Parse the source file
    tu = index.parse(filename)

    if not tu:
        raise Exception("Failed to parse the source file")

    # Find the function declaration
    def find_function(cursor):
        if cursor.kind == CursorKind.FUNCTION_DECL and cursor.spelling == function_name:
            return cursor
        for child in cursor.get_children():
            result = find_function(child)
            if result:
                return result

    root = tu.cursor
    function_cursor = find_function(root)

    if function_cursor:
        # Get the AST of the function
        function_ast = function_cursor.get_children()
        return function_ast
    else:
        raise Exception(f"Function '{function_name}' not found in the source file")


def label_to_categorical(label, LABEL2CAT):
    if label not in LABEL2CAT:
        LABEL2CAT[label] = len(LABEL2CAT)
    return LABEL2CAT[label]


def spell_to_categorical(spell, SPELL2CAT):
    if spell not in SPELL2CAT:
        SPELL2CAT[spell] = len(SPELL2CAT)
    return 1 + SPELL2CAT[spell]


def print_function_ast(node, indent=""):
    if node.kind == clang.cindex.CursorKind.FLOATING_LITERAL:
        val = list(node.get_tokens())[0].spelling
        print(f"{indent}Constant Value: {val}")
    else:
        if len(list(node.get_arguments())) > 0:
            print_function_ast(list(node.get_arguments())[0], indent)
        print(f"{indent}{node.kind} - {node.spelling}")
    for child in node.get_children():
        print_function_ast(child, indent + "  ")


def traverse_function_ast(node, parent, graph, LABEL2CAT, SPELL2CAT):
    node_id = str(node.hash)
    node_label = node.kind
    node_spell = node.spelling

    if node.kind == clang.cindex.CursorKind.FLOATING_LITERAL:
        val = float(list(node.get_tokens())[0].spelling)
        graph.add_node(
            node_id,
            node_label=label_to_categorical(node_label, LABEL2CAT),
            node_spell=0,
            node_val=val,
        )
    else:
        if len(list(node.get_arguments())) > 0:
            traverse_function_ast(
                list(node.get_arguments())[0], node_id, graph, LABEL2CAT, SPELL2CAT
            )
        graph.add_node(
            node_id,
            node_label=label_to_categorical(node_label, LABEL2CAT),
            node_spell=spell_to_categorical(node_spell, SPELL2CAT),
            node_val=-1,
        )

    if parent is not None:
        graph.add_edge(node_id, parent)

    for child in node.get_children():
        traverse_function_ast(child, node_id, graph, LABEL2CAT, SPELL2CAT)
