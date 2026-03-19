# データ蓄積・参照Webアプリケーション 設計書

## 1. 文書情報

| 項目 | 内容 |
| --- | --- |
| 文書名 | データ蓄積・参照Webアプリケーション 設計書 |
| 対象システム | FastAPI + SQLite によるオフライン運用向けデータ蓄積・参照Webアプリ |
| 作成日 | 2026-03-12 |
| 想定環境 | RHEL 7.9 / Python 3.9.10 |
| UI方針 | Bootstrap ベースのモダンな管理画面 |

## 2. システム概要

外部のWebシステムから POST された JSON データを受信し、SQLite に蓄積する。
蓄積したデータは Web ブラウザ上でテーブル形式で参照でき、必要に応じて CSV または JSON 形式で出力できる Web アプリケーションを FastAPI で構築する。

本システムはインターネット非接続サーバ上での稼働を前提とする。そのため、アプリケーション実行に必要な CSS、JavaScript、Python パッケージは事前配備し、外部 CDN や外部 API へ依存しない構成とする。

また、受信する JSON の項目名や構造が将来的に変更される可能性を考慮し、フロントエンドの設定画面から「どの JSON パスをどの表示項目として扱うか」を変更できるマッピング設定機能を設ける。

## 3. 目的

- 外部システムから送信される JSON データを安定して保存する
- 保存済みデータをブラウザから簡単に検索・閲覧できるようにする
- CSV / JSON 形式で業務データを持ち出せるようにする
- インターネット非接続環境でも自己完結して動作する構成とする
- JSON 項目変更時に、コード改修なしまたは最小限で追従できるようにする

## 4. 対象範囲

### 4.1 対象機能

- JSON データ受信 API
- SQLite へのデータ保存
- 一覧表示画面
- 詳細表示画面
- 条件検索機能
- CSV 出力機能
- JSON 出力機能
- 項目マッピング設定画面
- ヘルスチェック機能

### 4.2 対象外

- リアルタイム通知
- 複数サーバでの負荷分散構成
- 複雑なワークフロー
- 外部クラウドサービス連携

## 5. 前提条件

- OS は RHEL 7.9
- Python は 3.9.10 を利用可能
- Web フレームワークは FastAPI
- DB は SQLite
- UI は FastAPI + Jinja2 + Bootstrap で構成する
- Bootstrap の CSS/JavaScript はローカルファイルとして同梱し、CDN は使用しない
- 単一サーバ上での利用を前提とする
- サーバはインターネットに接続されていない

## 6. 想定利用者

| 利用者 | 用途 |
| --- | --- |
| 外部Webシステム | JSON データを HTTP POST で送信する |
| 業務担当者 | 画面でデータを参照・検索・出力する |
| 管理者 | 項目マッピング設定、稼働確認、ログ確認、バックアップ運用を行う |

## 7. 受信データ仕様

### 7.1 想定する初期JSON項目

初期導入時点では、以下のキーを持つ JSON を受信対象とする。

- `hostname`
- `ipaddress`
- `area`
- `building`
- `category`
- `model`
- `ping_test_result`
- `exec_result`

### 7.2 受信JSON例

```json
{
  "hostname": "sv-app-001",
  "ipaddress": "192.168.10.15",
  "area": "tokyo",
  "building": "dc-east",
  "category": "server",
  "model": "ProLiant DL360",
  "ping_test_result": "success",
  "exec_result": "ok"
}
```

### 7.3 項目変更への対応方針

- 受信 JSON の項目名および階層構造は変更される可能性がある
- そのため、画面表示や検索に使用する「標準項目」は固定しつつ、受信 JSON 上のどのパスを標準項目に対応づけるかを設定可能とする
- 例: `hostname` が将来 `device.host.name` に変わった場合でも、設定画面上で JSONPath 風のパスを変更することで対応可能とする
- 元の JSON 全体は常に保存し、マッピング設定変更後も再解釈できるようにする

## 8. 機能要件

### 8.1 JSON受信

- 外部システムは `POST /api/v1/records` に JSON を送信する
- リクエストボディは JSON 形式とする
- アプリは当時点のマッピング設定に基づいて標準項目を抽出する
- 元 JSON 全文は必ず保存する
- 保存時に受信日時をシステム側で付与する
- 保存成功時は HTTP 201 を返却する
- 不正な JSON の場合は HTTP 400 を返却する

### 8.2 データ一覧表示

- `GET /records` でブラウザ表示用の一覧画面を提供する
- Bootstrap ベースのレスポンシブなテーブルで表示する
- 1ページあたり一定件数を表示する
- ソート順は新しい受信日時順を基本とする
- ページネーションを提供する

### 8.3 条件検索

- 以下の標準項目で絞り込み可能とする
- 受信日時範囲
- hostname
- ipaddress
- area
- building
- category
- model
- ping_test_result
- exec_result
- フリーワード

### 8.4 データ詳細表示

- `GET /records/{id}` で1件の詳細を表示する
- 基本情報をカード形式で表示する
- 整形済み JSON をコード表示する
- 抽出済み標準項目と元 JSON を並べて確認できるようにする

### 8.5 CSV出力

- `GET /api/v1/records/export.csv` で CSV をダウンロード可能とする
- 検索条件を引き継いで出力できるようにする
- 標準項目と受信日時を出力対象に含める
- 必要に応じて元 JSON 全文も最終列に出力する

### 8.6 JSON出力

- `GET /api/v1/records/export.json` で JSON をダウンロード可能とする
- 検索条件を引き継いで出力できるようにする
- 標準項目、管理項目、元 JSON を含む配列形式で返却する

### 8.7 項目マッピング設定

- `GET /settings/mappings` で項目マッピング設定画面を表示する
- 管理者は標準項目ごとに JSON パスを設定できる
- 項目の表示名、一覧表示有無、検索対象有無、CSV 出力有無を設定できる
- 設定変更後、新規受信データには新設定を適用する
- 既存データに対して再抽出を行う再同期機能を任意で提供する

### 8.8 ヘルスチェック

- `GET /health` で稼働状態を返却する
- SQLite 接続確認を実施する

## 9. 非機能要件

### 9.1 性能

- 数万件規模のデータ蓄積を想定する
- 一覧表示はページネーションにより応答性能を維持する
- 検索対象カラムに必要なインデックスを付与する
- JSON 全文検索は補助的機能とし、主検索は標準項目に対して行う

### 9.2 可用性

- 単一サーバ構成とする
- プロセス監視は systemd を基本とする
- 障害時はログ確認と DB ファイル復旧で対応可能とする

### 9.3 保守性

- FastAPI のルータ、サービス、リポジトリ、テンプレートを分離する
- Pydantic モデルで入出力仕様を明確化する
- 設定値は環境変数または `.env` で管理する
- Bootstrap の静的ファイルをアプリ内に保持し、外部取得を不要とする

### 9.4 セキュリティ

- 入力値バリデーションを実施する
- SQLAlchemy 経由で SQL インジェクションを防止する
- 管理画面には Basic 認証またはリバースプロキシ認証を付与する
- 項目マッピング設定変更は管理者のみ実施可能とする
- 個人情報や機密情報をログへ出力しない

### 9.5 オフライン運用

- アプリケーションの稼働時に外部ネットワーク接続を必要としない
- Python パッケージはオフラインインストール可能な形で事前準備する
- Bootstrap の資材は `static/vendor/bootstrap/` 配下に同梱する
- アイコンを利用する場合もローカル配備とする
- 時刻同期や証明書更新など OS 外部運用は別途管理対象とする

## 10. システム構成

### 10.1 論理構成

```text
[外部Webシステム]
        |
     HTTP/JSON
        |
[Nginx または Apache]
        |
[FastAPI アプリケーション]
  |- API Router
  |- Web Router
  |- Mapping Service
  |- Record Service
  |- Repository
  |- SQLAlchemy
  |- Jinja2 Templates
  |- Bootstrap Static Files
        |
     SQLite
        |
   DBファイル
```

### 10.2 使用技術

| 区分 | 技術 |
| --- | --- |
| 言語 | Python 3.9.10 |
| Web | FastAPI |
| ASGI Server | Uvicorn |
| ORM | SQLAlchemy |
| バリデーション | Pydantic |
| DB | SQLite |
| テンプレート | Jinja2 |
| UI | Bootstrap |
| フロント | HTML / CSS / 最小限の JavaScript |

## 11. アプリケーション構成案

```text
app/
  main.py
  core/
    config.py
    database.py
    auth.py
  models/
    record.py
    field_mapping.py
    setting_history.py
  schemas/
    record.py
    field_mapping.py
  repositories/
    record_repository.py
    field_mapping_repository.py
  services/
    record_service.py
    mapping_service.py
    export_service.py
  routers/
    api_records.py
    web_records.py
    web_settings.py
    health.py
  templates/
    base.html
    dashboard.html
    records.html
    record_detail.html
    settings_mappings.html
  static/
    css/
      app.css
    js/
      app.js
    vendor/
      bootstrap/
```

## 12. データ設計

### 12.1 保存方針

JSON の構造変動に対応するため、以下の方針で保存する。

- 元の JSON 全体を文字列として保存する
- 検索・一覧表示に使う標準項目は個別カラムに保持する
- 標準項目と受信 JSON の対応関係は別テーブルで管理する

### 12.2 標準項目定義

初期実装では以下を標準項目とする。

| 標準項目ID | 初期表示名 | 説明 |
| --- | --- | --- |
| hostname | Hostname | ホスト名 |
| ipaddress | IP Address | IP アドレス |
| area | Area | エリア |
| building | Building | 建屋 |
| category | Category | カテゴリ |
| model | Model | 機種 |
| ping_test_result | Ping Test Result | Ping試験結果 |
| exec_result | Exec Result | 実行結果 |

### 12.3 テーブル定義案

#### テーブル名: `records`

| カラム名 | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| id | INTEGER | ○ | 主キー、自動採番 |
| hostname | TEXT | △ | 抽出済みホスト名 |
| ipaddress | TEXT | △ | 抽出済みIPアドレス |
| area | TEXT | △ | 抽出済みエリア |
| building | TEXT | △ | 抽出済み建屋 |
| category | TEXT | △ | 抽出済みカテゴリ |
| model | TEXT | △ | 抽出済み機種 |
| ping_test_result | TEXT | △ | 抽出済みPing結果 |
| exec_result | TEXT | △ | 抽出済み実行結果 |
| payload_json | TEXT | ○ | 元JSON文字列 |
| mapping_version | INTEGER | ○ | 適用したマッピング定義の版数 |
| received_at | DATETIME | ○ | 受信日時 |
| created_at | DATETIME | ○ | 作成日時 |
| updated_at | DATETIME | ○ | 更新日時 |

#### テーブル名: `field_mappings`

| カラム名 | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| id | INTEGER | ○ | 主キー |
| field_key | TEXT | ○ | 標準項目ID |
| display_name | TEXT | ○ | 画面表示名 |
| json_path | TEXT | ○ | JSON 上の取得パス |
| is_visible | BOOLEAN | ○ | 一覧表示対象フラグ |
| is_searchable | BOOLEAN | ○ | 検索対象フラグ |
| is_exportable | BOOLEAN | ○ | CSV/JSON 出力対象フラグ |
| sort_order | INTEGER | ○ | 表示順 |
| version | INTEGER | ○ | マッピング版数 |
| is_active | BOOLEAN | ○ | 現行版フラグ |
| created_at | DATETIME | ○ | 作成日時 |
| updated_at | DATETIME | ○ | 更新日時 |

#### テーブル名: `setting_histories`

| カラム名 | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| id | INTEGER | ○ | 主キー |
| setting_type | TEXT | ○ | 設定種別 |
| version | INTEGER | ○ | 版数 |
| changed_by | TEXT | △ | 変更者 |
| change_summary | TEXT | △ | 変更概要 |
| created_at | DATETIME | ○ | 作成日時 |

### 12.4 インデックス

| インデックス名 | 対象 |
| --- | --- |
| idx_records_received_at | received_at |
| idx_records_hostname | hostname |
| idx_records_ipaddress | ipaddress |
| idx_records_area | area |
| idx_records_building | building |
| idx_records_category | category |
| idx_records_model | model |
| idx_records_ping_test_result | ping_test_result |
| idx_records_exec_result | exec_result |
| idx_field_mappings_field_key | field_key |
| idx_field_mappings_active | is_active |

## 13. JSONマッピング設計

### 13.1 マッピング方式

- 標準項目ごとに JSON パスを1件設定する
- パス指定形式は `hostname` や `device.network.ipaddress` のようなドット区切りを基本とする
- 配列対応が必要な場合は将来拡張として `items[0].name` 形式を許容する
- パスが見つからない場合は `NULL` 保存とする

### 13.2 初期マッピング定義

| 標準項目 | 初期 JSON パス |
| --- | --- |
| hostname | hostname |
| ipaddress | ipaddress |
| area | area |
| building | building |
| category | category |
| model | model |
| ping_test_result | ping_test_result |
| exec_result | exec_result |

### 13.3 再同期方針

- マッピング変更後、既存 `records.payload_json` を再解析して標準項目列へ再反映できるようにする
- 再同期は管理者操作で明示実行とする
- 再同期処理中は対象件数に応じてバッチ更新する

## 14. JSON入出力仕様

### 14.1 登録成功レスポンス例

```json
{
  "id": 101,
  "message": "created",
  "mapping_version": 3
}
```

### 14.2 一覧取得レスポンス例

```json
{
  "items": [
    {
      "id": 101,
      "hostname": "sv-app-001",
      "ipaddress": "192.168.10.15",
      "area": "tokyo",
      "building": "dc-east",
      "category": "server",
      "model": "ProLiant DL360",
      "ping_test_result": "success",
      "exec_result": "ok",
      "received_at": "2026-03-12T09:30:00"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

## 15. API設計

| メソッド | パス | 用途 |
| --- | --- | --- |
| POST | `/api/v1/records` | JSON データ登録 |
| GET | `/api/v1/records` | JSON 形式で一覧取得 |
| GET | `/api/v1/records/{id}` | JSON 形式で詳細取得 |
| GET | `/api/v1/records/export.csv` | CSV ダウンロード |
| GET | `/api/v1/records/export.json` | JSON ダウンロード |
| GET | `/api/v1/settings/mappings` | マッピング設定一覧取得 |
| PUT | `/api/v1/settings/mappings` | マッピング設定更新 |
| POST | `/api/v1/settings/mappings/resync` | 既存データ再同期 |
| GET | `/records` | ブラウザ用一覧画面 |
| GET | `/records/{id}` | ブラウザ用詳細画面 |
| GET | `/settings/mappings` | ブラウザ用設定画面 |
| GET | `/health` | ヘルスチェック |

### 15.1 POST `/api/v1/records`

#### リクエスト

- Content-Type: `application/json`
- 任意の JSON オブジェクトを受信対象とする

#### 処理概要

1. JSON ボディを受信
2. JSON 形式を検証
3. 現行マッピング設定を取得
4. 標準項目を抽出
5. SQLite に保存
6. 採番 ID と適用マッピング版数を返却

#### レスポンス

| HTTP | 内容 |
| --- | --- |
| 201 | 登録成功 |
| 400 | JSON 不正 |
| 500 | サーバ内部エラー |

### 15.2 GET `/api/v1/records`

#### クエリパラメータ

| パラメータ | 説明 |
| --- | --- |
| page | ページ番号 |
| page_size | 取得件数 |
| hostname | ホスト名絞り込み |
| ipaddress | IPアドレス絞り込み |
| area | エリア絞り込み |
| building | 建屋絞り込み |
| category | カテゴリ絞り込み |
| model | 機種絞り込み |
| ping_test_result | Ping結果絞り込み |
| exec_result | 実行結果絞り込み |
| date_from | 受信日時From |
| date_to | 受信日時To |
| keyword | JSON 全文のフリーワード検索 |

### 15.3 PUT `/api/v1/settings/mappings`

#### 処理概要

1. 画面または API からマッピング定義を受け取る
2. 入力内容を検証する
3. 版数を採番する
4. `field_mappings` に新現行版として保存する
5. 設定変更履歴を記録する

### 15.4 POST `/api/v1/settings/mappings/resync`

#### 処理概要

1. 現行マッピング設定を取得
2. 既存 `records.payload_json` を順次再解析する
3. 標準項目列を更新する
4. `mapping_version` を最新化する

## 16. 画面設計

### 16.1 UIデザイン方針

- Bootstrap をベースとしたクリーンでモダンな管理画面とする
- ナビゲーションバー、カード、テーブル、フォーム、バッジを活用する
- PC とタブレットを主対象にしつつ、モバイルでも閲覧可能なレスポンシブ構成とする
- CDN は使用せず、Bootstrap の配布ファイルをローカル参照する
- 独自 CSS で配色や余白を調整し、業務画面として視認性を高める

### 16.2 共通レイアウト

- ヘッダ: システム名、ナビゲーション、現在時刻帯表示
- サイドまたは上部メニュー: 一覧、設定、ヘルス確認
- メインコンテンツ: カードとテーブル主体
- フッタ: バージョン、最終更新日時

### 16.3 一覧画面

#### 表示項目

- ID
- 受信日時
- hostname
- ipaddress
- area
- building
- category
- model
- ping_test_result
- exec_result
- 詳細リンク

#### 操作項目

- 検索条件入力フォーム
- 検索実行
- 条件クリア
- CSV ダウンロード
- JSON ダウンロード
- ページ移動

#### 画面イメージ方針

- 上部に絞り込みフォームをカード表示
- 中央に Bootstrap の `table`, `table-striped`, `table-hover` を用いた一覧
- 試験結果項目は `badge` で視覚的に区別する

### 16.4 詳細画面

- 基本情報をカードで表示
- 標準項目一覧を定義リストまたはテーブルで表示
- 元 JSON を整形表示
- 一覧へ戻るボタンを配置

### 16.5 項目マッピング設定画面

- 標準項目ごとの設定テーブルを表示する
- 管理者は以下を編集できる
- 表示名
- JSON パス
- 一覧表示可否
- 検索可否
- 出力可否
- 表示順
- 保存ボタン、初期値復元ボタン、再同期実行ボタンを配置する
- 保存前に簡易バリデーションを実施する

## 17. 処理方式

### 17.1 登録処理

```text
外部システム
  -> POST /api/v1/records
  -> FastAPI Router
  -> JSON Validation
  -> Mapping Service
  -> Record Service
  -> Repository
  -> SQLite 保存
  -> 201 Response
```

### 17.2 一覧表示処理

```text
ブラウザ
  -> GET /records
  -> Web Router
  -> Record Service
  -> Repository
  -> SQLite 検索
  -> Jinja2 + Bootstrap Rendering
  -> HTML Response
```

### 17.3 マッピング更新処理

```text
管理者
  -> GET /settings/mappings
  -> 編集
  -> PUT /api/v1/settings/mappings
  -> Validation
  -> Mapping Repository
  -> field_mappings 保存
  -> setting_histories 保存
```

## 18. エラーハンドリング

| ケース | 対応 |
| --- | --- |
| JSON 形式不正 | 400 を返却しエラー内容を通知 |
| JSON パスに該当項目なし | 該当標準項目を NULL として保存 |
| 設定値不正 | 400 を返却し入力項目を明示 |
| 対象データなし | 画面では0件表示、APIでは空配列返却 |
| DB 接続不可 | 500 を返却しログ出力 |
| 想定外例外 | 500 を返却しログ出力 |

## 19. ログ設計

### 19.1 出力対象

- アクセスログ
- アプリケーションログ
- 例外ログ
- 設定変更ログ

### 19.2 ログ項目

- リクエスト日時
- HTTP メソッド
- パス
- ステータスコード
- 処理時間
- 設定変更版数
- エラーメッセージ

注意:

- 元 JSON 全文は原則ログへ出力しない
- 設定変更時は変更者と変更対象を記録する

## 20. バックアップ・運用

### 20.1 バックアップ

- SQLite DB ファイルを定期バックアップする
- マッピング設定も DB 内に保持するため、DB バックアップで一括保全する
- 出力ファイルを永続保存対象とする場合は専用ディレクトリに保存する

### 20.2 オフライン運用上の注意

- Python パッケージ群は wheel またはローカルリポジトリから導入可能とする
- Bootstrap 資材更新は管理端末で取得後、手動配備する
- OS パッチ、ミドルウェア更新、証明書更新は別途運用手順化する

### 20.3 監視

- `GET /health` による死活監視
- systemd によるプロセス再起動
- ディスク使用量監視
- SQLite ファイルサイズ監視

## 21. セキュリティ設計方針

- API 公開先は業務ネットワーク内に制限する
- 管理画面は認証付きとする
- POST 元システムに対し、必要に応じて API キー認証を付与する
- HTTPS 終端は Nginx / Apache で行う
- 設定変更操作は監査対象とする
- 外部 CDN や外部スクリプトを読み込まない

## 22. デプロイ構成案

### 22.1 実行方式

- `Nginx + Uvicorn` または `Nginx + Gunicorn + UvicornWorker`
- RHEL 7.9 上で systemd 管理する

### 22.2 配備資材

- Python アプリケーション一式
- `requirements.txt` またはオフライン配備用 wheel 群
- `static/vendor/bootstrap/` 配下の Bootstrap 資材
- SQLite DB 初期化スクリプト
- systemd サービス定義
- Nginx 設定ファイル

### 22.3 環境変数例

| 変数名 | 内容 |
| --- | --- |
| APP_NAME | アプリ名 |
| APP_ENV | 実行環境 |
| DATABASE_URL | SQLite 接続文字列 |
| PAGE_SIZE_DEFAULT | 一覧画面のデフォルト件数 |
| EXPORT_MAX_ROWS | 1回の最大出力件数 |
| ADMIN_USERNAME | 管理画面ユーザ名 |
| ADMIN_PASSWORD | 管理画面パスワード |
| API_KEY | POST API 認証キー |

例:

```env
APP_NAME=data-connect-viewer
APP_ENV=production
DATABASE_URL=sqlite:///./data/app.db
PAGE_SIZE_DEFAULT=20
EXPORT_MAX_ROWS=10000
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_me
API_KEY=local-secure-key
```

## 23. テスト方針

### 23.1 単体テスト

- JSON パス抽出ロジック確認
- マッピング設定バリデーション確認
- Service 層の登録・検索ロジック確認
- Repository 層の CRUD 確認

### 23.2 結合テスト

- JSON POST から DB 保存までの疎通確認
- 一覧画面表示確認
- Bootstrap 適用済みテンプレート表示確認
- CSV / JSON 出力確認
- マッピング変更後の新規登録確認
- 再同期処理確認

### 23.3 受入観点

- 受信 JSON が保存されること
- 一覧画面で標準項目が参照できること
- 設定画面から JSON パスを変更できること
- 項目変更後も新規受信データに反映されること
- CSV / JSON のダウンロードができること
- インターネット未接続環境で動作すること

## 24. 今後の拡張候補

- JSONPath 互換レベルの向上
- 設定変更の承認ワークフロー
- 削除・更新機能の追加
- 監査ログ強化
- SQLite から PostgreSQL への移行

## 25. 実装上の補足方針

- 初期実装では標準項目を8項目に固定し、マッピングのみ変更可能とする
- 将来的に標準項目そのものを追加できる設計へ拡張可能とする
- UI はサーバサイドレンダリング中心とし、JavaScript は設定画面の補助に限定する
- オフライン環境のため、外部依存を最小限とする

