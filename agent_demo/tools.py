import ast
import operator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class ToolResult:
    name: str
    output: str


class SafeCalculator(ast.NodeVisitor):
    OPERATORS = {
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

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers are supported.")

    def visit_BinOp(self, node):
        op_type = type(node.op)
        if op_type not in self.OPERATORS:
            raise ValueError("Unsupported operator.")
        return self.OPERATORS[op_type](self.visit(node.left), self.visit(node.right))

    def visit_UnaryOp(self, node):
        op_type = type(node.op)
        if op_type not in self.OPERATORS:
            raise ValueError("Unsupported operator.")
        return self.OPERATORS[op_type](self.visit(node.operand))

    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression: {type(node).__name__}")


def calculate(expression: str) -> ToolResult:
    try:
        tree = ast.parse(expression, mode="eval")
        value = SafeCalculator().visit(tree)
        return ToolResult("calculator", f"{expression} = {value}")
    except Exception as exc:
        return ToolResult("calculator", f"Calculation failed: {exc}")


def current_time() -> ToolResult:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return ToolResult("clock", f"Current time: {now}")


def search_files(keyword: str, root: Path) -> ToolResult:
    matches = []
    for path in root.rglob("*"):
        if path.is_file() and keyword.lower() in path.name.lower():
            matches.append(str(path.relative_to(root)))

    if not matches:
        return ToolResult("file_search", f"No file name contains `{keyword}`.")

    preview = "\n".join(f"- {item}" for item in matches[:10])
    extra = "" if len(matches) <= 10 else f"\n... and {len(matches) - 10} more"
    return ToolResult("file_search", preview + extra)


def make_plan(goal: str) -> ToolResult:
    target = goal.strip() or "finish a small agent task"
    steps = [
        f"Clarify the goal: {target}",
        "List the tools and data the agent needs.",
        "Build the smallest runnable loop.",
        "Test with simple inputs first.",
        "Improve prompts, tools, and memory after observing failures.",
    ]
    return ToolResult("planner", "\n".join(f"{index}. {step}" for index, step in enumerate(steps, 1)))
