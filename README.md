# nanaco ANA キャンペーン監視アプリの使い方

このガイドは、nanacoポイントとANAのキャンペーン開始を監視し、LINEで通知するPythonスクリプトをGitHub Actionsで自動実行する方法を説明します。所要時間は約15-20分です。前提として、GitHubアカウントとLINE Developers Consoleのアカウントが必要です。

## 1. 準備するもの
- **GitHubアカウント**: 無料で新規リポジトリを作成。
- **LINE Developers Console**:
  - [LINE Developers Console](https://developers.line.biz/console/)でMessaging APIチャネルを作成。
  - チャネルアクセストークンを発行（長期用）。
  - ユーザーIDを取得（Botを友達追加後、Webhookやテストで確認。例: `Uxxxxxxxx`）。
- **Python知識**: 基本的なGit操作（クローン、プッシュ）のみ。

## 2. リポジトリのセットアップ
1. GitHubで新しいリポジトリを作成（例: `nanaco-ana-monitor`）。
2. ローカルでリポジトリをクローン:
   ```
   git clone https://github.com/あなたのユーザー名/nanaco-ana-monitor.git
   cd nanaco-ana-monitor
   ```
3. 以下のファイルを追加:
   - **`monitor.py`**: 監視スクリプト（前のメッセージからコピー）。
     ```python
     # (ここに前のスクリプトのコードを貼り付け)
     ```
   - **`requirements.txt`**: 依存ライブラリ。
     ```
     requests
     beautifulsoup4
     line-bot-sdk
     ```

4. GitHub Secretsを設定（機密情報保護）:
   - リポジトリの「Settings」 > 「Secrets and variables」 > 「Actions」。
   - 新規追加:
     - `LINE_ACCESS_TOKEN`: LINEのチャネルアクセストークン。
     - `USER_ID`: あなたのLINEユーザーID。

5. ファイルをプッシュ:
   ```
   git add .
   git commit -m "Initial setup"
   git push origin main
   ```

## 3. GitHub Actionsの設定
1. リポジトリのルートに`.github/workflows/monitor.yml`を作成し、以下のYAMLを貼り付け（毎日日本時間9時に実行例）。
   ```yaml
   name: Nanaco ANA Monitor

   on:
     schedule:
       - cron: '0 0 * * *'  # 毎日UTC 0時（日本時間9時）
     workflow_dispatch:  # 手動実行可能

   jobs:
     monitor:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout code
           uses: actions/checkout@v4

         - name: Set up Python
           uses: actions/setup-python@v5
           with:
             python-version: '3.12'

         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt

         - name: Run monitor script
           env:
             LINE_ACCESS_TOKEN: ${{ secrets.LINE_ACCESS_TOKEN }}
             USER_ID: ${{ secrets.USER_ID }}
           run: python monitor.py

         - name: Commit state changes
           run: |
             git config --local user.email "action@github.com"
             git config --local user.name "GitHub Action"
             git add state.json
             if git diff --staged --quiet; then
               echo "No changes to commit"
             else
               git commit -m "Update state [$(date)]"
               git push
             fi
   ```
2. ファイルをプッシュ:
   ```
   git add .github/workflows/monitor.yml
   git commit -m "Add workflow"
   git push origin main
   ```

## 4. テスト実行
1. GitHubリポジトリの「Actions」タブを選択。
2. 「Nanaco ANA Monitor」ワークフローをクリック。
3. 「Run workflow」ボタンで手動実行（初回はこれでテスト）。
4. 実行ログを確認:
   - 成功: 「No changes detected.」や「Initial state saved...」が表示。
   - エラー時: ログをチェック（例: トークン無効ならSecrets再確認）。
5. LINEでテストメッセージが届くか確認（初回は状態保存のみで通知なし。変更シミュレーションでテスト）。

## 5. 自動実行の確認
- スケジュール通り毎日実行される（無料プランで月2000分以内）。
- キャンペーン変更検知時: LINEに「【nanaco ANAキャンペーン検知】」メッセージが届く。
- 状態ファイル(`state.json`)はGitHubに自動保存（変更時コミット）。

## トラブルシューティング
| 問題 | 原因と解決 |
|------|------------|
| LINE通知が届かない | - トークン/ユーザーIDのSecretsを確認。<br>- Botを友達追加済みか？<br>- ログで`LINE通知エラー`を探す。 |
| ページ取得エラー | - ネットワーク問題: タイムアウトを調整（スクリプトの`timeout=10`を増やす）。<br>- 初回実行で状態保存を確認。 |
| 偽陽性（不要通知） | - キーワードをスクリプトの`['ana', 'マイル', '交換', 'レートアップ']`で調整。 |
| 実行制限 | - 頻度を減らす（cronを週1に）。GitHub無料プランを確認。 |

## カスタマイズ例
- **通知頻度変更**: YAMLの`cron`を編集（例: `0 0 * * 1`で月曜のみ）。
- **監視URL追加**: `monitor.py`の`URLS`リストに追加。
- **メッセージカスタム**: `my_text`で絵文字や詳細を追加（例: `my_text = f"🚀 {subject}\n{body}"`）。

これでセットアップ完了！ 質問があればいつでもどうぞ。キャンペーン開始を逃さないようにがんばりましょう！
