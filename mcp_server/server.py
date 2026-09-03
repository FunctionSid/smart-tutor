import ast
import json
import operator
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STUDY_DIR = PROJECT_ROOT / "study_materials"
STUDY_DIR.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("SmartTutorMCP", host="127.0.0.1", port=8765)

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _eval_ast_node(node):
    if isinstance(node, ast.Expression):
        return _eval_ast_node(node.body)
    elif isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _eval_ast_node(node.left)
        right = _eval_ast_node(node.right)
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Operator {op_type.__name__} is not allowed.")
        return SAFE_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_ast_node(node.operand)
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unary operator {op_type.__name__} is not allowed.")
        return SAFE_OPERATORS[op_type](operand)
    else:
        raise ValueError(f"Syntax element {type(node).__name__} is not supported in simple math.")

@mcp.tool()
def list_study_files() -> str:
    files = []
    for entry in STUDY_DIR.iterdir():
        if entry.is_file():
            stat = entry.stat()
            files.append({
                "name": entry.name,
                "size_bytes": stat.st_size,
            })
    return json.dumps(files, indent=2)

@mcp.tool()
def read_study_file(filename: str) -> str:
    clean_name = Path(filename).name
    target = (STUDY_DIR / clean_name).resolve()
    if not str(target).startswith(str(STUDY_DIR.resolve())):
        return "Error: Access denied. Cannot read files outside study_materials."
    if not target.exists() or not target.is_file():
        return f"Error: File '{clean_name}' not found in study_materials."
    try:
        return target.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"

@mcp.tool()
def calculate(expression: str) -> str:
    try:
        parsed = ast.parse(expression.strip(), mode="eval")
        result = _eval_ast_node(parsed)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

if __name__ == "__main__":
    print(f"Starting Smart Tutor MCP server on http://127.0.0.1:8765/sse")
    print(f"Study materials folder: {STUDY_DIR}")
    mcp.run(transport="sse")
