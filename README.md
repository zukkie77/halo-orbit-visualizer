# Halo Orbit Visualizer

太陽-地球系・地球-月系のラグランジュポイント（L1〜L5）周辺のハロー軌道を2Dアニメーションで表示するPythonデスクトップアプリケーション。

## 概要

| 項目 | 内容 |
|------|------|
| 対象天体系 | 太陽-地球系 / 地球-月系（切り替え可能） |
| 表示軌道 | L1〜L5 各ラグランジュポイント周辺のハロー軌道（L1/L2/L3）・トロヤン型軌道（L4/L5） |
| 物理モデル | CR3BP 解析近似（教育目的） |
| 初期位相 | 起動時のシステム時刻（UTC）を J2000 エポック起算で使用 |
| プラットフォーム | Linux (Ubuntu) デスクトップ |

## スクリーンショット

```
[Sun-Earth System]                  [Earth-Moon System]
  太陽を中心に地球が公転               地球を中心に月が公転
  L1〜L5 の軌道マーカーが周回          L1〜L5 の軌道マーカーが周回
  下部スライダーで速度調整             左下ラジオボタンで系を切り替え
```

## 必要環境

- Python 3.8 以上
- matplotlib ≥ 3.5
- numpy ≥ 1.21

## セットアップ

```bash
git clone https://github.com/zukkie77/halo-orbit-visualizer.git
cd halo-orbit-visualizer
python3 -m venv .venv
source .venv/bin/activate
pip install matplotlib numpy
```

## 起動

```bash
python -m halo_orbit_visualizer.main
```

## 操作方法

| 操作 | 内容 |
|------|------|
| キー `1` | 太陽-地球系に切り替え |
| キー `2` | 地球-月系に切り替え |
| 左下 RadioButtons クリック | 系を切り替え |
| 下部スライダー | 時間進行速度の倍率を調整（×1 〜 ×10⁹、log スケール） |

デフォルトの時間倍率は **×10⁶**（起動直後から軌道運動が視認できる速度）。

## アーキテクチャ

```
types.py          共有データクラス・CelestialSystem enum
physics.py        ラグランジュポイント位置計算・軌道パラメータ計算
time_manager.py   J2000 エポック起算のシミュレーション時刻管理
animation.py      FuncAnimation ループ・系切り替えコールバック
ui.py             matplotlib 描画・Slider・RadioButtons
main.py           エントリーポイント
```

依存方向: `types → physics → time_manager → animation → ui`

## テスト

```bash
pip install pytest
python -m pytest tests/ -v
```

39 テストケース（物理計算・時刻管理・UI・統合テスト）。

## ライセンス

MIT
