# 第6回 デバッグ報告

- 学籍番号：ｇ2432047
- 氏名：陳嘉欣
- 提出日：2026/10/18
- 提出方法：
  - WebClass： `lesson06_debug_report.md` を提出した。
  - Git：`DEBUG_REPORT.md` を `~/lesson06_debug` の直下に保存し、commitした。

> 各欄の例文や角括弧は、自分の実行結果と判断へ置き換えること。認証情報、password、tokenは記録しないこと。
> 配布code `lesson06_debug_starter` を `~/lesson06_debug` へcopyし、README.md の手順で準備してから作業する。`sample.png` と `sample_rgba.png` をそれぞれuploadして症状を確認する。`analysis.py` と `test_analysis.py` は変更しない。

---

## 0. 実習の前提

### 0.1 対象と調査方針

配布された `lesson06_debug_starter` を `~/lesson06_debug` に配置し、画像解析アプリで起こる不具合を調査した。アプリは、画像の読込を `image_io.py`、RGB平均値の計算を `analysis.py`、画面表示を `app.py` が担当する構成になっている。

今回の調査では、エラーが表示された箇所をすぐに書き換えるのではなく、まず入力条件を固定し、考えられる原因とその予測を整理した。その後、画像を読み込んだ直後のデータを確認し、原因に対応する部分だけを修正する方針とした。Copilot CLIには仮説や修正案の検討を依頼したが、提案の採否とテスト結果の判断は自分で行った。

### 0.2 実行環境と基準状態

| 項目 | 記録 |
|---|---|
| OS | Windows 11、WSL2上のUbuntu |
| 作業ディレクトリ | `~/lesson06_debug` |
| Python仮想環境 | `~/venvs/dla`（`/home/linyunru/venvs/dla/bin/python`） |
| 主なライブラリ・ツール | Pillow、NumPy、pytest、Streamlit、GitHub Copilot CLI |
| Gitブランチ | `main` |
| 修正前の基準commit | `85abeb9 Start lesson06 debug` |
| 修正前の既存test | `5 passed in 0.21s` |

使用ライブラリの詳細なバージョン番号は記録していないため、ここでは確認した範囲にとどめる。基準commitを作成した後、修正前の `git status --short` は空であり、作業ツリーに変更がないことを確認した。

最初の5件のテストが通っていても、今回の不具合は残っていた。このことから、既存テストが成功することと、アプリが受け付ける入力の種類を十分に検証できていることは別だと分かった。

---

## 1. 症状

- **入力：** Streamlitの画面から `sample.png` と `sample_rgba.png` をそれぞれアップロードした。どちらも640×480ピクセルのPNG画像である。
- **期待した結果：** アップロードした画像のプレビュー、幅と高さ、R・G・Bの平均値、各チャンネルのヒストグラムが表示される。
- **実際の結果：** `sample.png` は正常に解析できたが、`sample_rgba.png` は `ValueError: RGB image [H,W,3] required` を出して停止した。
- **正常に動く入力との比較：** `sample.png` は R=106.23、G=103.40、B=80.20 と表示され、ヒストグラムも描画された。一方、`sample_rgba.png` は修正前には同じ解析結果の表示まで進まなかった。
- **再現率：** 異常画面は複数回確認したが、独立したアップロード試行の回数を数えていなかったため「3回中3回」などの再現率は算出しない。その代わり、後述する関数の直接呼出しと自動テストで再現を確認した。
- **実行したcommand：** `python -m streamlit run app.py`。確認用のPythonスクリプトは `python - <<'PY' ... PY` という形式で実行した。
- **対象commit：** `85abeb9 Start lesson06 debug`。

画面に表示されたエラーの主要部分は次のとおりである。

```text
ValueError: RGB image [H,W,3] required
File "/home/linyunru/lesson06_debug/app.py", line 55, in main
    r_mean, g_mean, b_mean = mean_rgb(array)
File "/home/linyunru/lesson06_debug/analysis.py", line 9, in mean_rgb
    raise ValueError("RGB image [H,W,3] required")
```

この段階で分かるのは、`mean_rgb()` が入力を受け付けず、例外を発生させたという事実までである。エラーが `analysis.py` に表示されたからといって、計算関数自体に問題があるとは限らない。そこで、計算前の画像データを確認することにした。

---

## 2. 再現用test

### 2.1 修正前に失敗を確認したtest

最初に `test_image_io.py` を作成し、2×1ピクセルのRGBA画像をメモリ上で生成して、`load_rgb_image()` に渡した。完全に透明な画素と不透明な画素を含めたのは、RGBへの変換後に3チャンネルになるだけでなく、RGBの数値が保持されることも確認するためである。

```python
import io

import numpy as np
from PIL import Image
from image_io import load_rgb_image


def test_load_rgb_image_converts_rgba_to_rgb():
    image = Image.new("RGBA", (2, 1))
    image.putdata([
        (10, 20, 30, 0),
        (40, 50, 60, 255),
    ])

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    result = load_rgb_image(buffer)
    expected = np.array(
        [[[10, 20, 30], [40, 50, 60]]],
        dtype=np.uint8,
    )

    assert result.shape == (1, 2, 3)
    np.testing.assert_array_equal(result, expected)
```

修正前の実行結果（実測）は次のとおりであった。

```text
$ python -m pytest -q test_image_io.py
>       assert result.shape == (1, 2, 3)
E       assert (1, 2, 4) == (1, 2, 3)
E         At index 2 diff: 4 != 3
FAILED test_image_io.py::test_load_rgb_image_converts_rgba_to_rgb
1 failed in 0.24s
```

期待値を `(1, 2, 3)` に固定したテストが、実際には `(1, 2, 4)` を受け取って失敗した。修正前の欠陥をこのテストで検出できることが分かった。

### 2.2 配布資料で指定された `tests/test_color.py`

配布資料では `tests/test_color.py` と `tests/data/red_1px.png` の使用が指定されていたため、後から指定のテストも追加した。まず画像を直接調べ、次の値を確認した。

```text
tests/data/red_1px.png
Exists: True
Mode: RGBA
Size: (1, 1)
Pixel: (255, 0, 0, 255)
```

実際に作成した `tests/test_color.py` は以下のとおりである。

```python
"""画像読込時のRGB変換に関する回帰テスト."""

import numpy as np
from pathlib import Path

from image_io import load_rgb_image
from analysis import mean_rgb


def test_rgba_red_pixel_is_converted_to_rgb():
    """RGBA画像を読み込んでもRGBの3チャンネル配列になる."""
    path = Path(__file__).parent / "data" / "red_1px.png"

    with path.open("rb") as uploaded_file:
        result = load_rgb_image(uploaded_file)

    expected = np.array([[[255, 0, 0]]], dtype=np.uint8)

    assert result.shape == (1, 1, 3)
    np.testing.assert_array_equal(result, expected)
    np.testing.assert_allclose(mean_rgb(result), [255, 0, 0])
```

このテストは、RGBAの1画素画像を読み込んだ結果がRGBの3チャンネルになり、その画素値と平均値が `[255, 0, 0]` であることを確認する。

**修正前の実行結果について：** `tests/test_color.py` は修正後に追加したため、このファイルそのものを修正前のコードで実行したログはない。修正前のFAILとして実際に記録できているのは2.1の `test_image_io.py` である。両者を混同せずに記載した。

**指定テストの修正後の実行結果（実測）：**

```text
$ python -m pytest -q tests/test_color.py
.                                                                               [100%]
1 passed in 0.19s
```

---

## 3. 仮説と予測（2件以上）

修正に入る前にCopilot CLIへ、原因候補を複数挙げ、それぞれが正しい場合に何が観察されるかを示すよう依頼した。この時点ではファイルの変更や修正案の実行を許可しなかった。検証に使った仮説は次の3件である。

| ID | 仮説 | 正しい場合に観察される結果 | 優先度 |
|---|---|---|---|
| H1 | `load_rgb_image()` でRGBA画像をRGBへ変換しておらず、alphaチャンネルが残っている。 | `sample.png` は `[480,640,3]`、`sample_rgba.png` は `[480,640,4]` のまま返される。 | 高 |
| H2 | 今回の画像がグレースケール（L）やパレット（P）など、別のモードとして読み込まれている。 | PILの `mode` がL/Pなどを示し、2次元または想定外の配列形状が観察される。 | 中 |
| H3 | 調査しているソースと、実行時に読み込まれるコード・モジュールが一致していない。 | コードの記述と実行時の挙動が食い違うか、想定外の場所のモジュールが読み込まれる。 | 低 |

H1は正常なRGB画像と異常なRGBA画像の違いを直接説明できるため、最初に調べる価値が高いと考えた。一方、H2は入力形式の取り違え、H3は実行環境の不一致を想定したものである。仮説を分けておくことで、一つの説明だけを信じて修正してしまうことを避けた。

---

## 4. 検証結果

### H1：支持

修正前に、Pillowで開いたときのモード、元の配列形状、`load_rgb_image()` の出力形状、dtypeを比較した。ファイル内容を `io.BytesIO` で渡して確認している。

```python
import io
from pathlib import Path
import numpy as np
from PIL import Image
from image_io import load_rgb_image

for filename in ("sample.png", "sample_rgba.png"):
    data = Path(filename).read_bytes()
    image = Image.open(io.BytesIO(data))
    array = load_rgb_image(io.BytesIO(data))
    print(filename)
    print("PIL mode:", image.mode)
    print("Original shape:", np.asarray(image).shape)
    print("Loader output shape:", array.shape)
    print("dtype:", array.dtype)
    print("Valid RGB shape:", array.ndim == 3 and array.shape[2] == 3)
```

**実行結果（修正前）：**

```text
sample.png
PIL mode: RGB
Original shape: (480, 640, 3)
Loader output shape: (480, 640, 3)
dtype: uint8
Valid RGB shape: True

sample_rgba.png
PIL mode: RGBA
Original shape: (480, 640, 4)
Loader output shape: (480, 640, 4)
dtype: uint8
Valid RGB shape: False
```

`sample_rgba.png` はPILで読み込んだ時点でRGBAであり、読込関数を通った後も4チャンネルだった。H1の予測と一致する。

さらに、Streamlitを介さずに読込関数の出力を `mean_rgb()` に直接渡した。

```text
sample.png
mean_rgb result: [106.23259115 103.40480143  80.19984375]

sample_rgba.png
Exception: ValueError RGB image [H,W,3] required
```

**判定：支持。** UIを介さない呼出しでも同じ例外が起こることから、画像の4チャンネル出力が下流の入力条件に合っていないことが確認できた。

### H2：今回の入力については反証

**確認方法：** H1の確認と同じスクリプトでPILの `mode` を表示した。

```text
sample.png       PIL mode: RGB
sample_rgba.png  PIL mode: RGBA
```

**判定：今回の不具合の説明としては反証。** 問題のファイルはLやPではなく、明確にRGBAとして読み込まれていた。ただし、別のグレースケール画像やパレット画像を入力した場合の挙動まで調べたわけではない。

### H3：優先度は下がったが、独立した確認は未実施

**確認方法：** `image_io.py` の内容と、実行された読込関数の出力を照合した。修正前のコードは `return np.asarray(image)` であり、実際にRGBAの4チャンネル配列が返された。Streamlitを使わない場合にも同じエラーが出た。

**判定：H3を積極的に支持する証拠はない。** 観察結果は調査対象のコードの動作と整合している。ただし、`image_io.__file__` などを使ったモジュールの読込元の直接確認は実施していないため、完全に反証したとは書かない。今回の原因特定には、H1の実測結果とコードの対応で十分な根拠が得られた。

---

## 5. 確定した原因

- **原因：** `image_io.py` の `load_rgb_image()` が、Pillowで開いた画像をRGBへ変換せず、そのままNumPy配列にしていたこと。
- **根拠：** 修正前の `sample_rgba.png` は `RGBA`、出力shapeは `(480,640,4)` だった。修正前コードは `np.asarray(image)` をそのまま返しており、`mean_rgb()` に直接渡すと `[H,W,3]` という入力条件に違反して同じ `ValueError` が発生した。
- **errorが出た場所と原因の場所は同じか：** 同じではない。例外を投げたのは `analysis.py` の `mean_rgb()` だが、そこへ不適切な形状の配列を渡す原因を作ったのは上流の `image_io.py` である。

処理の流れは次のように整理できる。

```text
sample_rgba.png（RGBA）
  → Image.open()：RGBA
  → np.asarray(image)：shape (480,640,4)
  → mean_rgb()：必要なshapeは [H,W,3]
  → ValueError
```

`mean_rgb()` がRGBの3チャンネル入力を要求すること自体は、既存の関数の仕様と一致している。そこで、計算関数のチェックを外すのではなく、読込側でRGBの配列を返すように修正すると判断した。

---

## 6. 最小修正

Copilotに、修正対象を `image_io.py` のみに限定し、テストの実行やGitのcommitを行わずに最小の変更をするよう依頼した。提案された編集内容を人間が確認して許可し、変更後は `git diff -- image_io.py` で差分を確かめた。

```diff
diff --git a/image_io.py b/image_io.py
index 1ed4625..87dbf6c 100644
--- a/image_io.py
+++ b/image_io.py
@@ -6,5 +6,5 @@ from PIL import Image
 def load_rgb_image(uploaded_file) -> np.ndarray:
     """画像fileを読み込み、shape [H,W,3] のRGB配列を返す."""
-    image = Image.open(uploaded_file)
+    image = Image.open(uploaded_file).convert("RGB")
     return np.asarray(image)
```

- **変更file・行数：** 既存のプログラムについては `image_io.py` の1行を置換した。
- **変えなかったもの：** `analysis.py`、`app.py`、既存の `test_analysis.py`、および `mean_rgb()` の入力条件。テストは `test_image_io.py` と `tests/test_color.py` を新規追加したが、既存テストの期待値は変更していない。

`convert("RGB")` を配列化の前に置くことで、RGBA画像を読み込んだ場合も3チャンネルにそろえられる。問題となった入力形式の差を読込部分で処理できるため、計算や表示の処理を変更する必要がなかった。

---

## 7. 再テスト

### 7.1 自動テスト：修正前後の比較

まず、修正前に失敗を確認した `test_image_io.py` を、修正後に同じ条件で実行した。

```text
修正前：
$ python -m pytest -q test_image_io.py
1 failed in 0.24s

修正後：
$ python -m pytest -q test_image_io.py
.                                                                               [100%]
1 passed in 0.22s
```

その後、当時のテスト全体を実行した結果は次のとおりである。

```text
$ python -m pytest -q
......                                                                          [100%]
6 passed in 0.09s
```

さらに、指定された `tests/test_color.py` を追加した後、次の結果を得た。

```text
$ python -m pytest -q tests/test_color.py
.                                                                               [100%]
1 passed in 0.19s

$ python -m pytest -q
.......                                                                         [100%]
```

最後の全テスト実行では、pytestの進捗表示で7件とも `.` となり、100%まで終了した。コピーしたログには実行時間を含む最終集計行がないため、ここでは記録のある表示だけを載せた。

### 7.2 配布画像での直接確認

修正後、`sample.png` と `sample_rgba.png` をそれぞれ読み込み、`mean_rgb()` に渡して結果を比較した。

```text
sample.png
Shape: (480, 640, 3)
dtype: uint8
RGB mean: [106.23259115 103.40480143  80.19984375]

sample_rgba.png
Shape: (480, 640, 3)
dtype: uint8
RGB mean: [106.23259115 103.40480143  80.19984375]
```

修正前に正常だった `sample.png` の平均値は変わらず、エラーになっていた `sample_rgba.png` も3チャンネルになって平均値を計算できた。

### 7.3 Streamlit画面での確認

修正後にアプリを起動して `sample_rgba.png` をアップロードすると、画像プレビュー、幅640px・高さ480px、R=106.23・G=103.40・B=80.20の平均値、RGBヒストグラムが正常に表示され、以前の `ValueError` は出なかった。`sample.png` でも同様に解析結果を確認した。

このように、回帰テストだけでなく、実際の画像ファイルとユーザー画面の両方で元の症状が解消したことを確認した。

---

## 8. AI提案の評価

| AIの提案・行動 | 採用 / 保留 / 却下 | 理由 |
|---|---|---|
| RGBAのalphaチャンネルが読込後も残るというH1を提示 | 採用 | modeとshapeを実際に測定し、予測と一致したため。 |
| 読込関数だけを `convert("RGB")` で修正する案 | 採用 | エラーを起こしたデータ形式の違いに直接対応し、既存の計算関数を変えずに済むため。 |
| `mean_rgb()` の入力チェックを維持する方針 | 採用 | RGB入力という契約を変更せず、上流側の問題を修正できるため。 |
| テストでファイルパスを渡す例 | 修正して採用 | 実際のアップロード処理に合わせ、独自テストでは `io.BytesIO` を使った。 |
| 新しい会話でH2/H3を別の内容に置き換えた説明 | 却下 | もとの仮説を変えてしまうと、予測と検証結果を対応付けられなくなるため。 |
| 透明部分の背景合成まで考慮する可能性 | 保留 | 今回の要求はRGB配列への正規化であり、合成する背景色についての指定がないため。 |

途中でCopilotの会話を開き直した際、AIはもとの仮説の定義を保持しておらず、H2を「`mean_rgb()` の処理」、H3を「Streamlit経由の処理」と解釈した。しかし、最初に立てたH2は別モードの読込、H3は実行コードの不一致であり、内容が違う。この説明はそのまま採用せず、最初の仮説を維持した。

また、Copilotには修正前に「説明のみ、ファイル変更とコマンド実行は禁止」と指示し、修正段階では `image_io.py` のみを変更するよう範囲を限定した。編集の許可を求められた際は差分を確認してから承認し、テストは自分で実行した。

---

## 9. 人間が行った判断

今回、特に重要だったのは、エラーが出た関数をそのまま修正対象にしなかったことである。`mean_rgb()` の入力チェックを緩めれば例外は見えなくなるかもしれないが、読込関数が返すデータの形式が揃っていない問題は残る。そこで、画像の読込直後のmodeとshapeを確認し、関数の入出力の境界で何が起きているかを調べた。

また、修正する前に回帰テストを実行し、意図した条件で失敗することを確かめた。修正後に同じテストが通ったことは、今回の変更が欠陥に対応している根拠になる。既存のテスト5件が通っていたにもかかわらずRGBA画像で不具合が起きていた点から、正常な入力だけを確かめてもテストとしては十分でないと分かった。

Copilotの提案は原因を考える助けになった一方、会話を再開すると仮説の定義が変わることもあった。AIの文章がもっともらしくても、実際の記録と矛盾していないかを確認する必要がある。今回のように、AIには候補や変更案を出してもらい、人間が観察結果を基準に判断する進め方が有効だと感じた。

### 今後の再発防止

今後は画像読込の部分に、RGBだけでなくRGBAなどの入力形式も含めたテストを残し、関数の出力が常に `[H,W,3]` になることを確認したい。`analysis.py` 側の入力チェックは、契約違反に気付くための仕組みとして残す。ほかの画像形式（L、P、CMYKなど）については今回個別に検証していないため、必要になった時点で期待値を決めてテストを追加する。

---

## 補足A. 追加で考察した点

### A.1 平均値が一致しても、全画素が一致するとは限らない

修正後、`sample.png` と `sample_rgba.png` のRGB平均値はともに `[106.23259115, 103.40480143, 80.19984375]` だった。しかし、平均値は画素の値をまとめた統計量なので、異なる画素配置や異なる画素値の組合せでも同じ平均値になる場合がある。今回は両画像の全画素を直接比較する実験は行っていないため、「同じ平均値を得た」と「全画素が同一である」は区別した。

### A.2 alphaチャンネルの扱い

今回採用した `convert("RGB")` はalphaチャンネルを削除する処理であり、透明な画素を自動的に白い背景へ合成する処理ではない。独自テストにはalphaが0の画素 `(10,20,30,0)` を含め、RGB変換後に `[10,20,30]` が残ることを期待値として設定した。この仕様はRGBの色成分を解析する今回の課題には合うが、画面に見える色を背景込みで解析したいアプリでは別の扱いを検討する必要がある。

### A.3 テストの役割分担

今回のテストにはそれぞれ異なる役割があった。`test_analysis.py` は平均値の計算と不正な入力の拒否を確認する。`test_image_io.py` はalphaを含む画像を読込関数がRGB化できるかを確認する。`tests/test_color.py` は配布された1画素のPNGを使い、RGB値と平均値まで具体的に確かめる。これらを分けておくと、不具合が再発した場合にも、どの処理で期待と違う結果が出たかを調べやすい。

---

## 補足B. 記録上の制約

- Streamlitの異常画面は複数回観察したが、独立した試行回数を記録していないため、再現率を数値で示していない。
- `tests/test_color.py` は修正後に作成したため、同ファイルを使った修正前のFAILログはない。修正前のFAILを確認したのは `test_image_io.py` である。
- H3について、モジュールの実際のimport元を表示する独立した確認はしていない。
- Pythonや各ライブラリの詳細バージョン、および7件全体テストの最終実行時間は手元の記録に残っていない。

検証していない内容を結果として書かないことも、今回の報告では意識した。

---

## 提出前の確認

- [x] 症状を期待値と実際値で記録した。
- [x] 修正前に失敗した回帰テストと、その実行結果を記録した。
- [x] 指定の `tests/test_color.py` を作成し、`tests/data/red_1px.png` を使用して確認した。
- [x] 仮説を3件挙げ、予測と優先度を示した。
- [x] 検証結果について支持・反証・未確認を区別した。
- [x] 最小修正のdiff、再テスト、AI案の採否を記録した。
- [x] `git status --short` の表示に `analysis.py` と `test_analysis.py` の変更はなかった。
- [x] 学籍番号・氏名を記入する。
- [x] `DEBUG_REPORT.md` を `~/lesson06_debug` の直下に置き、最終確認後にcommitする。

## 10. 感想

今回の実習で特に印象に残ったのは、エラーが発生した場所と実際の原因が異なっていたことである。最初は `mean_rgb()` に問題があるように見えたが、画像のmodeやshapeを確認することで、原因は画像の読込処理にあると分かった。この経験から、エラーメッセージだけで判断せず、データがどの段階で期待と異なる状態になったのかを調べることが重要だと学んだ。

また、Copilotの提案も実際の結果と照らし合わせて判断する必要があると感じた。今後は、修正方法を探す前に仮説と検証方法を整理し、原因を理解した上で修正できるようになりたい。

