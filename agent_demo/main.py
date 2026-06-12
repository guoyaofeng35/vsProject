from pathlib import Path

from agent import MiniMaxAgent


def main():
    project_root = Path(__file__).resolve().parents[1]
    agent = MiniMaxAgent(project_root)

    print("MiniMax Agent demo started.")
    print("Set MINIMAX_API_KEY to use the real model; without it, local rule mode is used.")
    print("Try: 时间 / 计算 12 * (8 + 3) / 计划 做一个天气查询 agent / 查看记忆")

    while True:
        try:
            user_input = input("\n你: ").strip()
        except EOFError:
            print("\nAgent: 输入结束，已退出。")
            break

        if user_input in {"退出", "exit", "quit"}:
            print("Agent: 下次继续。")
            break

        print(f"\nAgent:\n{agent.run(user_input)}")


if __name__ == "__main__":
    main()
