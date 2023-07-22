# AIWolf Contest's Agent for Natural Language Division
人狼知能大会自然言語部門向けのPythonエージェントコードです。
OpenAIのGPT-4およびGPT-3.5-turboを用いて、人狼ゲームをプレイします。

大会公式サイト: http://aiwolf.org/

Forked from: [aiwolfdial/AIWolfNLAgentPython](https://github.com/aiwolfdial/AIWolfNLAgentPython)

Server code: [aiwolfdial/RandomTalkAgent](https://github.com/aiwolfdial/RandomTalkAgent)

# Usage

## Run a Single Agent
1. Please fill `host` ,`port` ,`name1` in `res/config.ini`.
host and port should be set to specified locations of the contest server, or your own server if any.
name1 should be a unique name within other agents.

Example
```
[connection]
host = localhost
port = 10000
buffer = 2048

[agent]
name1 = kanolab1
```
2.After running the server program, execute ```python3 main.py```.


<br>

## Run Multiple Agents
1. Please fill `host` , `port`, `num` (number of agents), num lines of `name`s in config.ini.

Example
```
[connection]
host = localhost
port = 10000
buffer = 2048

[agent]
num = 5
name1 = kanolab1
name2 = kanolab2
name3 = kanolab3
name4 = kanolab4
name5 = kanolab5
```

2.After running the server program, execute ```python3 multiprocess.py```.

# 使い方

## Agent 1体を使用して実行する場合
1. `res/config.ini`の `host` ,`port` ,`name1`を埋めてください。
host, port は対戦サーバに合わせます。自分でサーバを建てている場合はその設定に、
大会用対戦サーバであれば指定されたIPアドレスとポートを記入してください。
name1 にはほかのエージェントと重複しない名前（英数字）を使用してください。

例
```
[connection]
host = localhost
port = 10000
buffer = 2048

[agent]
name1 = kanolab1
```
2. サーバプログラム実行後、```python3 main.py```で動作します。


<br>

## Agent 複数体を同時に使用して実行する場合
1. config.iniの`host` ,`port` とエージェントの人数`num`、人数分の`name`を埋めてください。

例
```
[connection]
host = localhost
port = 10000
buffer = 2048

[agent]
num = 5
name1 = kanolab1
name2 = kanolab2
name3 = kanolab3
name4 = kanolab4
name5 = kanolab5
```

2.サーバプログラム実行後、```python3 multiprocess.py```で動作します。
