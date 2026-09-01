"""Tool implementations the agent can call."""
import ast
import operator as op


_ALLOWED_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.USub: op.neg,
}


def calculator(expression: str) -> str:
    """Safely evaluate a basic arithmetic expression (no eval())."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except Exception as e:
        return f"error: could not evaluate '{expression}' ({e})"


def _safe_eval(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("unsupported expression")


TOOL_SCHEMAS = [
    {"name": "calculator", "description": "Evaluate a basic arithmetic expression."},
    {"name": "retriever", "description": "Retrieve relevant document chunks for a query."},
]
