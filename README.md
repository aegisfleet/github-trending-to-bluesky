# GitHub Trending to Bluesky

GitHub Trending to Blueskyは、[GitHubのトレンド](https://github.com/trending)にある最も人気のあるリポジトリの内容を要約し、Blueskyに投稿するPython製のアプリケーションです。  
このアプリケーションは、技術トレンドに迅速に反応し、Blueskyのフォロワーに価値ある情報を提供することを目的としています。

## 関連記事

- [Webスクレイピング×生成AI×SNSで新しい価値が生まれる？すべて無料でBOTを作った話](https://note.com/aegisfleet/n/nc8362f717cd9)

## 機能

- GitHubトレンドの最上位リポジトリを自動検出
- リポジトリの内容を要約
- 要約をBlueskyに自動投稿

このリポジトリで実行された結果はBlueskyの [デイリーGitHubトレンド](https://bsky.app/profile/dailygithubtrends.bsky.social) に投稿されます。

## インストール方法

このプロジェクトをローカル環境で動かすには、次の手順を実行してください。

```bash
git clone https://github.com/aegisfleet/github-trending-to-bluesky.git
cd github-trending-to-bluesky
pip install -r requirements.txt
```

## 使用方法

アプリケーションを実行するには、以下のコマンドを使用します。

```text
python main.py <BlueSkyのユーザーハンドル> <BlueSkyのパスワード> <GeminiのAPIキー>
```

プログラムは、GitHubのトレンドから最も人気のあるリポジトリを検出し、その内容を要約してBlueskyに投稿します。  
コマンドライン引数としてBlueskyのユーザーハンドルとパスワードが必要です。

## 技術要素

このアプリケーションは以下の技術を使用しています。

- Python: メインのプログラミング言語
- beautifulsoup4: HTMLの解析
- requests: HTTPリクエスト
- google-generativeai: Gemini
- atproto: BlueskyのAPIクライアント

また、開発には以下を使用しています。

- [Gemini](https://ai.google.dev/gemini-api?hl=ja): Googleの生成AI API
- [リートン](https://wrtn.jp/): コード生成やテキスト生成に利用しているAIサービス
- [AWS CodeWhisperer](https://aws.amazon.com/jp/codewhisperer/): コード生成に使用しているAIツール

## マスコット

リートンで生成したマスコット画像。  
名前はまだ無い。

<img src="images\mascot.png" width="50%">
