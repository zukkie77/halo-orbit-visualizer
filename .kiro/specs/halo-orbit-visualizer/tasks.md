# Implementation Plan

- [x] 1. Foundation — 共有型定義とプロジェクト構造のセットアップ
- [x] 1.1 共有データ型と初期ファイル構造の実装
  - `main.py`, `types.py`, `physics.py`, `time_manager.py`, `animation.py`, `ui.py` の6ファイルを作成
  - `types.py` に `Vector2D`, `LagrangePointData`, `OrbitParameters`, `AnimationState` を型ヒント付きデータクラスとして実装
  - 各モジュールは空のクラス定義（スタブ）で初期化し、`python main.py` が ImportError なく起動できる状態にする
  - `python main.py` が正常終了（エラーなし）することで完了を確認できる
  - _Requirements: 4.1, 4.3_

- [x] 2. 物理計算層の実装
- [x] 2.1 ラグランジュポイント位置計算の実装
  - 太陽-地球系の質量比パラメータ μ ≈ 3.003×10⁻⁶ を定数として定義する
  - L1・L2 を Hill sphere 近似、L3 を太陽反対側近似、L4・L5 を正三角形配置（60°/−60°）で位置を算出する
  - 5点すべての位置が正しい象限（L1は太陽側、L2は反太陽側、L4はY正方向、L5はY負方向）に収まることを確認できる
  - _Requirements: 1.1_

- [x] 2.2 軌道パラメータと軌道位置計算の実装
  - L1・L2・L3 に対して CR3BP 線形化の解析近似（楕円軌道、固有振動数 ω ≈ 2.09 × ω_earth）を実装する
  - L4・L5 に対して地球と同周期（T = 365.25日）の円軌道近似を実装する
  - 軌道サイズに視覚的誇張係数を適用し、画面上で各軌道が識別できる大きさにする
  - エポックオフセット秒から各軌道の初期位相（rad）を算出するロジックを組み込む
  - `compute_position(params, t)` と `compute_position(params, t + period)` が同一位置を返すことで完了を確認できる
  - _Requirements: 1.2, 1.3, 1.4, 3.2_

- [x] 3. (P) 時刻管理の実装
  - `datetime.now(timezone.utc)` で現在 UTC を取得し J2000 エポック（2000-01-01 12:00 UTC）起算秒を算出する
  - 時刻取得に失敗した場合は `epoch_offset_seconds = 0.0` でフォールバックし stderr に警告を出力する
  - `advance(real_delta_ms, multiplier)` を呼ぶと `sim_time_seconds` が `(real_delta_ms / 1000) × multiplier` だけ増加する
  - `advance(1000, 1_000_000)` 後に `sim_time_seconds` が 10⁶ 秒増加していることで完了を確認できる
  - _Requirements: 3.1, 3.3_
  - _Boundary: TimeManager_

- [x] 4. (P) UI 描画層の実装
- [x] 4.1 VisualizationView の静的描画実装
  - matplotlib Figure/Axes を生成し、太陽・地球・L1〜L5 を異なるマーカーでプロットする
  - 各ラグランジュポイントの軌道パスを楕円または円として背景に描画する
  - ラベルと凡例を追加し、すべての要素が視覚的に識別できる状態にする
  - スライダー用の余白（`subplots_adjust(bottom=0.2)`）を確保し、ウィンドウクローズ時に `plt.close('all')` が呼ばれるイベントを登録する
  - `setup()` を呼び出すと Figure が開き軌道パスとラベルが表示された静止画が確認できる
  - _Requirements: 2.1, 2.2, 2.3, 2.5, 4.2_
  - _Boundary: VisualizationView_

- [x] 4.2 SpeedControlUI スライダーウィジェットの実装
  - Figure 下部に専用 Axes を配置し、log10 スケール（範囲 0〜9、デフォルト 6）の Slider を生成する
  - `get_multiplier(slider_value)` が `10 ** slider_value` を正確に返す
  - `update_label(slider, multiplier)` がスライダーラベルに現在の実倍率を表示する
  - デフォルト値 6（×10⁶）の状態で Slider が正しく表示されることで完了を確認できる
  - _Requirements: 5.1, 5.2, 5.4, 5.5_
  - _Boundary: SpeedControlUI_

- [x] 5. 統合 — アニメーションコントローラーとアプリ起動の実装
- [x] 5.1 AnimationController の実装
  - `FuncAnimation(fig, update_func, interval=50, blit=True)` でアニメーションループを構築する
  - フレームごとに `TimeManager.advance()` → `OrbitCalculator.compute_position() × 5` → `VisualizationView.update_markers()` を呼び出す
  - `SpeedControlUI.on_changed` コールバックを登録し、スライダー変更が倍率へ即時反映されるようにする
  - `update_markers()` が返す Artist リストのみ再描画（blit=True）されることを確認する
  - `start()` を呼び出して `plt.show()` を実行するとマーカーが継続的に動くアニメーションが動作することで完了を確認できる
  - _Requirements: 2.4, 2.6, 5.3_
  - _Depends: 2.2, 3, 4.1, 4.2_

- [x] 5.2 main.py でのコンポーネント統合と起動確認
  - 全コンポーネント（LagrangePointCalculator, OrbitCalculator, TimeManager, VisualizationView, SpeedControlUI, AnimationController）を生成・接続する
  - `if __name__ == "__main__":` ブロックで起動シーケンスを実装する
  - `python main.py` でアニメーションウィンドウが開き、L1〜L5 の軌道マーカーすべてが動作することを目視確認できる
  - _Requirements: 4.3_

- [x] 6. 検証 — ユニットテストと動作確認
- [x] 6.1 (P) 物理計算のユニットテスト
  - `LagrangePointCalculator`: L4・L5 が太陽・地球それぞれから 1 AU 離れた正三角形配置であることを検証する
  - `OrbitCalculator.compute_position`: `sim_time = 0` と `sim_time = period` で同一位置が返ること（周期性）を検証する
  - `pytest` で全テストがパスすることで完了を確認できる
  - _Requirements: 1.1, 1.2, 1.3_
  - _Boundary: LagrangePointCalculator, OrbitCalculator_

- [x] 6.2 (P) 時刻管理と速度制御のユニットテスト
  - `TimeManager.advance(1000, 1_000_000)` で `sim_time_seconds` が正確に 10⁶ 秒増加することを検証する
  - `SpeedControlUI.get_multiplier`: 入力 0 → 1.0、入力 9 → 1e9 を検証する
  - フォールバック時に `epoch_offset_seconds == 0.0` となることを検証する
  - `pytest` で全テストがパスすることで完了を確認できる
  - _Requirements: 3.1, 3.3, 5.4_
  - _Boundary: TimeManager, SpeedControlUI_
