ConversationGetter
====

ツイッター上での会話を取得します。

## Description
Twitter APIのstatuses/sampleから会話を取得してDB（sqlite）に保存します。

sequence to sequenceの学習用データとして使えるかと思います。  
conversationsテーブルにtweetカラムとreplyカラムとして入ります。  
全ての会話を取得して来る機能はないので、コンテキストが読み取れないようなものが入ります。そのため、学習用データとしてはいまいちかもしれません。  

整形する機能はないので学習前に加工してください。

## Requirement
twitter  
https://github.com/sixohsix/twitter

## Usage
edit bash profile.  
export TWITTER_API_KEY='YOUR TWITTER API KEY'  
export TWITTER_API_SECRET='YOUR TWITTER API SECRET'  
export TWITTER_ACCESS_TOKEN='YOUR TWITTER ACCESS TOKEN'  
export TWITTER_ACCESS_TOKEN_SECRET='YOUR TWITTER ACCESS TOKEN SECRET'  

python conversation_getter.pyとすれば取得してくれるはずです。
