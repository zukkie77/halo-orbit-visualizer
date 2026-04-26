# Research & Design Decisions

---
**Purpose**: Discovery findings and design rationale for halo-orbit-visualizer.

---

## Summary

- **Feature**: `halo-orbit-visualizer`
- **Discovery Scope**: New Feature (Greenfield)
- **Key Findings**:
  - `matplotlib.animation.FuncAnimation` + `matplotlib.widgets.Slider` はデスクトップ単体アプリとして十分な機能を持ち、追加GUIフレームワーク不要
  - L1/L2/L3のハロー軌道は CR3BP の線形化から導く解析近似（Lindstedt-Poincaré 展開の1次近似）で実用的な精度が得られる
  - 速度倍率はlog10スケールのスライダーで表現するのが適切（×1〜×10⁹という広いレンジをカバーするため）

---

## Research Log

### matplotlib FuncAnimation および Slider

- **Context**: アニメーションと速度制御UIをmatplotlibだけで実現できるか検証
- **Findings**:
  - `FuncAnimation(fig, update_func, interval=50, blit=True)` でフレームレート20FPSのアニメーションが可能
  - `interval`（ms）× `time_multiplier` = 1フレームあたりの仮想時間進行量（秒）
  - `matplotlib.widgets.Slider(ax, label, valmin, valmax, valinit)` でスライダーUI実現
  - `blit=True` にするとフレームごとに変化する Artist のみ再描画されパフォーマンス向上
  - Slider 用に専用の `Axes` を確保する必要がある（`plt.axes([left, bottom, width, height])`）
  - `Slider.on_changed(callback)` でリアルタイム反映が可能
- **Implications**: 追加ライブラリ不要。Slider は log10 スケールで実装し表示ラベルに実倍率を表示する

### ハロー軌道の近似モデル

- **Context**: 教育目的の近似でよいが、L1〜L5を視覚的に正しく表現する必要がある
- **Findings**:
  - **太陽-地球系パラメータ**: μ = m_E/(m_S + m_E) ≈ 3.003×10⁻⁶、地球公転周期 T = 365.25日
  - **L1/L2/L3（共線ラグランジュポイント）**: CR3BP の線形化による周期軌道が「ハロー軌道」。1次近似では楕円軌道として近似可能。固有振動数 ωₓ ≈ 2.09 × ωₑₐᵣₜₕ（約6ヶ月周期）、軌道形状比 κ ≈ 2.36（L1/L2付近）
  - **L4/L5（三角ラグランジュポイント）**: 安定な平衡点。周辺の軌道は蝌蚪型（tadpole）軌道だが近似では地球と同周期の小円として表現可能
  - 正規化座標（AU）で計算し表示は AU のまま（太陽=原点、地球=(1,0)）
- **Implications**: physics.py で解析式のみを使い scipy 等の数値積分ライブラリは不要

### 時刻管理と初期位相

- **Context**: 現在時刻（UTC）から各軌道の初期位相を求める方法
- **Findings**:
  - J2000.0（2000-01-01 12:00 UTC）をエポック基準とする
  - `datetime.utcnow()` で現在UTCを取得し、エポックからの経過秒数を算出
  - 各軌道の初期位相 φ₀ = ω × Δt_since_epoch (mod 2π)
  - `datetime.utcnow()` は Python 3.12で非推奨のため `datetime.now(timezone.utc)` を使用
- **Implications**: TimeManager が J2000 エポックからの経過秒を管理

---

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| **シンプル階層アーキテクチャ（採用）** | Physics → Time → Animation → UI の一方向依存 | 単純・実装が速い・小規模アプリに最適 | 大規模化には向かない | 本アプリの規模に適切 |
| MVC | Model/View/Controller分離 | テスト容易・責務明確 | このサイズでは過剰 | 却下 |
| イベント駆動 | コンポーネント間をイベントバスで接続 | 疎結合 | Reactiveフレームワーク不要。複雑すぎる | 却下 |

---

## Design Decisions

### Decision: ファイル分割粒度

- **Context**: 単一ファイル vs 複数ファイル
- **Alternatives Considered**:
  1. `main.py` 単一ファイル — シンプルだが500行超になりメンテナンス困難
  2. 4ファイル分割（`main.py`, `physics.py`, `animation.py`, `ui.py`）— 責務分離が明確
- **Selected Approach**: 4ファイル分割
- **Rationale**: テスト可能性と単一責任の原則を両立
- **Trade-offs**: ファイル間のインポートが増えるが許容範囲

### Decision: 速度スライダーのスケール

- **Context**: ×1〜×10⁹ という9桁のレンジをどう表現するか
- **Alternatives Considered**:
  1. 線形スケール — 高倍率に偏りすぎてlow端が操作不能
  2. log10スケール（採用）— 各桁を均等に操作可能
- **Selected Approach**: スライダー値 = log10(multiplier)、範囲 [0, 9]、ラベルに `10^n × (実値)` を表示
- **Trade-offs**: 実装にlog変換が入るが直感的なUI

### Decision: 座標系と表示スケール

- **Context**: 太陽-地球-L1/L2はスケール差が大きい（AU vs 0.01 AU）
- **Alternatives Considered**:
  1. 物理スケール通りに表示 — L1/L2/L3 の軌道が小さすぎて見えない
  2. 軌道サイズを誇張表示（採用）— 視認性を優先
- **Selected Approach**: ラグランジュポイントの軌道サイズを誇張係数で拡大表示（物理的正確さよりも教育的可視性を優先）
- **Trade-offs**: 物理的スケールと異なるが要件（近似モデル）の範囲内

---

## Risks & Mitigations

- matplotlib の Slider と FuncAnimation を同一 figure で共存させる際、レイアウト調整が必要 — `plt.subplots_adjust(bottom=0.2)` でスライダー用スペースを確保
- `blit=True` 時に Slider などの静的Widgetがちらつく可能性 — Slider の Axes を animation の blit 対象外にする
- L3の軌道周期は L1/L2 と異なる（L3は太陽の反対側で周期≒1年）— OrbitParameters に各ポイント固有の周波数を持たせることで対応

---

## References

- matplotlib FuncAnimation: https://matplotlib.org/stable/api/animation_api.html
- matplotlib Slider: https://matplotlib.org/stable/api/widgets_api.html
- CR3BP Lagrange point approximation: Szebehely (1967), Theory of Orbits
- J2000 epoch: IAU standard, 2000 January 1, 12:00 TT
