# フロントエンド実装で学んでいること

## リクエストの送り方

## エラー対処(記述できるところまで)

`'Signup' cannot be used as a JSX component.
  Its return type 'void' is not a valid JSX element.`
というエラーが出た時の対処法

- このエラーは、JSX を返すはずのコンポーネントが何も返していないとき、表示するものがなくて出るエラー
- 今回は、handleCick のの閉じカッコの位置が間違っており、大本のコンポーネントの return を handleClick が含んでしまっていたことが原因だった
