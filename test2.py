import json

demo = {
    1: 'hi',
    2: 'hey',
    3: 'hello'
}

while True:
    with open('test.json', 'w') as f:
        json.dump(demo, f)
