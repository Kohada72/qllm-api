import random
import time
from typing import Callable, Awaitable, Dict, Any



def execute_training(
    epochs: int,
    lr: float,
    model_name: str,
    on_step: Callable[[int, float, float, float], Awaitable[None]]
) -> Dict[str, Any]:
    """
    APIやDBに一切依存しない、純粋な学習（シミュレーション）ロジック
    """
    start_time = time.time()

    # 学習ループ
    for epoch in range(1, epochs + 1):
        time.sleep(2)  # 重い学習処理をシミュレート

        # メトリクスの計算
        loss = max(0.1, 4.0 - (epoch * 0.35) + random.uniform(-0.1, 0.1))
        current_lr = lr * (0.9 ** epoch)
        grad_norm = random.uniform(0.1, 0.5)

        # 💡 1エポック終わるごとに、外部から渡された「約束の関数（コールバック）」を呼ぶ
        # 自分が今どこにデータを送っているのか（PATCHなのかDBなのか）は知る必要がない
        on_step(epoch, loss, current_lr, grad_norm)

    # 最終結果の計算
    total_time_minutes = (time.time() - start_time) / 60.0
    final_loss = loss * 0.95
    ppl = 40.0 + random.uniform(-2.0, 2.0)

    # 最終結果を辞書として返す
    return {
        "eval_loss": final_loss,
        "total_time": total_time_minutes,
        "ppl": ppl
    }
