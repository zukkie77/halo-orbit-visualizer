# Requirements Document

## Introduction

ハロー軌道ビジュアライザーは、太陽-地球系のラグランジュポイント（L1〜L5）周辺を周回する物体のハロー軌道を、Pythonとmatplotlibを使ったLinux（Ubuntu）デスクトップ上の2Dアニメーションとして表示するアプリケーションである。近似モデルを用いた教育・概念把握向けのビジュアライゼーションを提供する。

## Boundary Context

- **In scope**: L1〜L5各ラグランジュポイント周辺の軌道計算・2Dアニメーション表示・現実時刻に基づいたアニメーション開始・時間進行速度の倍率指定UI
- **Out of scope**: 倍率以外のパラメータ変更UI、数値データのエクスポート、リサジュー軌道等の他軌道種別、3D表示、高精度数値積分
- **Adjacent expectations**: アプリは単体のPythonスクリプトとして動作し、外部サービスや他システムとの連携は不要

## Requirements

### 1. ラグランジュポイントと軌道の計算

**Objective:** As a ユーザー, I want 太陽-地球系のL1〜L5各ラグランジュポイントの位置と、各ポイント周辺の代表的な軌道を近似計算できること, so that 正確なシミュレーター不要でハロー軌道の概念を視覚的に把握できる。

#### Acceptance Criteria

1. The Halo Orbit Visualizer shall 太陽-地球系の回転座標系（共回転座標系）においてL1〜L5の5つのラグランジュポイントの近似位置を計算する。
2. The Halo Orbit Visualizer shall L1・L2・L3の各ポイントに対して、円制限三体問題に基づく近似ハロー軌道（周期軌道）のパラメータを算出する。
3. The Halo Orbit Visualizer shall L4・L5の各ポイントに対して、三角ラグランジュポイント周辺のトロヤン型近似軌道のパラメータを算出する。
4. The Halo Orbit Visualizer shall 軌道計算に解析的近似式を用い、数値積分ライブラリへの依存を不要とする。

### 2. 2Dアニメーション表示

**Objective:** As a ユーザー, I want 軌道をmatplotlibの2Dアニメーションとして見られること, so that ハロー軌道上の物体の動きを直感的に理解できる。

#### Acceptance Criteria

1. When アプリケーションが起動する, the Halo Orbit Visualizer shall matplotlibのGUIウィンドウを開き、2D軌道アニメーションを表示する。
2. The Halo Orbit Visualizer shall 太陽・地球・L1〜L5の各ラグランジュポイントを2D平面上に図示する。
3. The Halo Orbit Visualizer shall L1〜L5の各ラグランジュポイントに対応した軌道パスを描画する。
4. The Halo Orbit Visualizer shall 各軌道上を動く物体（マーカー）をアニメーションとして継続的に表示する。
5. The Halo Orbit Visualizer shall 太陽・地球・各ラグランジュポイント・軌道オブジェクトをラベルまたは凡例で識別できるよう表示する。
6. While アニメーションが動作している, the Halo Orbit Visualizer shall フレームを定期的に更新し滑らかな動きを維持する。

### 3. 現実時刻に基づくアニメーション開始

**Objective:** As a ユーザー, I want アニメーションが現在時刻を起点として開始されること, so that 実際の軌道位相に対応した表示から始められる。

#### Acceptance Criteria

1. When アプリケーションが起動する, the Halo Orbit Visualizer shall システムの現在日時（UTC）を取得し、アニメーションの初期位相として使用する。
2. The Halo Orbit Visualizer shall 各軌道オブジェクトの初期位置を、現在時刻に対応した軌道位相から算出する。
3. If システム時刻の取得に失敗した場合, the Halo Orbit Visualizer shall 位相ゼロ（デフォルト基準点）からアニメーションを開始する。

### 5. 時間進行速度の倍率指定UI

**Objective:** As a ユーザー, I want アニメーションの時間進行速度を倍率で変更できること, so that 実時間では視認できないほど遅い軌道運動を任意の速さで確認できる。

#### Acceptance Criteria

1. The Halo Orbit Visualizer shall ウィンドウ内にスライダーまたは入力欄による時間倍率コントロールを表示する。
2. The Halo Orbit Visualizer shall デフォルトの時間倍率として実用的な値（例：×1,000,000 程度）を設定し、起動直後からアニメーションが視認可能な速度で動く状態にする。
3. When ユーザーが時間倍率を変更する, the Halo Orbit Visualizer shall 変更後の倍率をただちにアニメーションの進行速度へ反映する。
4. The Halo Orbit Visualizer shall 設定可能な倍率の範囲を、×1（実時間）から×1,000,000,000（10億倍）程度までとする。
5. The Halo Orbit Visualizer shall 現在設定されている倍率の値をUI上に表示する。

### 4. アプリケーション動作要件

**Objective:** As a ユーザー, I want アプリがLinux（Ubuntu）上で単体Pythonスクリプトとして起動できること, so that 追加のインフラなしに手軽に実行できる。

#### Acceptance Criteria

1. The Halo Orbit Visualizer shall Python 3.8以降とmatplotlibのみに依存し、標準的なUbuntu環境で動作する。
2. When ウィンドウのクローズ操作が行われる, the Halo Orbit Visualizer shall アニメーションを停止しアプリケーションを正常終了する。
3. The Halo Orbit Visualizer shall 単一のエントリーポイント（`python main.py` 等）で起動できる。
