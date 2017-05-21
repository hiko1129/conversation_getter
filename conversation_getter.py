from twitter import OAuth, OAuth2, oauth2_dance
from twitter import Twitter, TwitterStream, TwitterHTTPError
import os
import sqlite3
import time


class ConversationGetter:
    """ツイッター上での会話を取得する."""

    def prepare_db(self, db_name):
        """DBの準備."""
        if not os.path.exists(db_name):
            # ファイルが存在しない場合.
            self.conn = sqlite3.connect(db_name)
            self.c = self.conn.cursor()
            query = '''
            CREATE TABLE tweet_ids (
                conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tweet_id TEXT,
                in_reply_to_status_id TEXT
            )
            '''
            self.c.execute(query)
            query = '''
            CREATE TABLE conversations (
                conversation_id INTEGER primary key,
                tweet TEXT,
                reply TEXT,
                FOREIGN KEY (conversation_id)
                REFERENCES tweet_ids(conversation_id)
            )
            '''
            self.c.execute(query)
        else:
            # ファイルが存在する場合.
            self.conn = sqlite3.connect(db_name)
            self.c = self.conn.cursor()

    def fetch_tweet_ids(self):
        """ツイートに付与されたIDを取得する."""
        twitter_stream = TwitterStream(auth=self.__setting_oauth())
        iterator = twitter_stream.statuses.sample(language='ja')
        for index, msg in enumerate(iterator):
            print('fetch No.{0}'.format(index + 1))
            if 'in_reply_to_status_id' not in msg:
                continue
            if msg['in_reply_to_status_id']:
                try:
                    self.c.execute(
                        '''
                        INSERT INTO tweet_ids (tweet_id, in_reply_to_status_id)
                        VALUES (?, ?)
                        ''',
                        (msg['id'], msg['in_reply_to_status_id'])
                    )
                    self.conn.commit()
                except sqlite3.IntegrityError:
                    continue

    def fetch_conversations(self, limit_num, sleep_minute):
        """ツイッター上での会話を取得."""
        self.c.execute('SELECT * FROM tweet_ids')
        ids = self.c.fetchall()
        counter = 0
        for conversation_id, tweet_id, in_reply_to_status_id in ids:
            if self.__conversation_exists(conversation_id):
                print('skip. this conversation is already exists.')
                continue
            counter += 2
            # APIの制限への対応.
            if counter >= limit_num:
                print('--Wait 15 minutes--')
                counter = 0
                time.sleep(sleep_minute * 60)
            print("fetch conversation_id:{0}".format(conversation_id))
            try:
                twitter = Twitter(auth=self.__setting_oauth2())
                tweet = twitter.statuses.show(_id=in_reply_to_status_id)['text']
                reply = twitter.statuses.show(_id=tweet_id)['text']
                self.c.execute(
                    '''
                    INSERT INTO conversations (conversation_id, tweet, reply)
                    VALUES (?, ?, ?)
                    ''',
                    (conversation_id, tweet, reply)
                )
                self.conn.commit()
            except TwitterHTTPError as err:
                print('skip this conversation')
                self.c.execute(
                    'DELETE FROM tweet_ids WHERE conversation_id=?',
                    (conversation_id,)
                )
                continue
            except sqlite3.IntegrityError as err:
                print('skip this conversation')
                continue
        self.conn.close()

    def __conversation_exists(self, conversation_id):
        """既に取得した会話か否かを判断."""
        self.c.execute(
            'SELECT COUNT(*) FROM conversations WHERE conversation_id=?',
            (conversation_id,)
        )
        return self.c.fetchone()[0] == 1

    def __setting_oauth(self):
        """OAuthのための設定を行う."""
        api_key = os.environ['TWITTER_API_KEY']
        api_secret = os.environ['TWITTER_API_SECRET']
        access_token = os.environ['TWITTER_ACCESS_TOKEN']
        access_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

        return OAuth(
            consumer_key=api_key,
            consumer_secret=api_secret,
            token=access_token,
            token_secret=access_secret
        )

    def __setting_oauth2(self):
        """OAuth2のための設定を行う."""
        api_key = os.environ['TWITTER_API_KEY']
        api_secret = os.environ['TWITTER_API_SECRET']

        return OAuth2(
            bearer_token=oauth2_dance(
                api_key,
                api_secret,
            )
        )


if __name__ == '__main__':
    conversation_getter = ConversationGetter()
    conversation_getter.prepare_db('twitter_conversation.db')
    conversation_getter.fetch_tweet_ids()
    conversation_getter.fetch_conversations(450, 15)
