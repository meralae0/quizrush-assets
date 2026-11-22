"""Crée questions.json + voice.json à partir de episodes/NN/spec.json.
spec : {"noun": "flag", "article": false, "q": "Which country does this flag belong to?",
        "intro": "...", "outro": "...", "items": [[answer, [w1, w2, w3], wiki_title_or_search, fact, {extra}], ... 40]}
Réponses réparties 10/10/10/10, lead-ins tous différents, débuts de réponse variés.
"""
import json, random, sys

LEAD = [
    "Kick-off! Here's your first {n}. Any idea?",
    "Take a good look. Which {n} is this?",
    "Easy one... or is it? Name this {n}!",
    "Eyes on the screen. What {n} do we have here?",
    "You've seen this one before. Which {n}?",
    "Quick! Which {n} is this?",
    "Trust your instinct. Name it!",
    "Don't overthink it. Which {n} is this?",
    "This one is a classic. Which {n}?",
    "Last easy one! Which {n} is this?",
    "Medium round! Things get trickier. Which {n} is this?",
    "Look closely at the details. Which {n}?",
    "Ten seconds on the clock. Name this {n}!",
    "This one fools a lot of people. Which {n} is it?",
    "Can you get this one right? Which {n}?",
    "Think carefully. What {n} is this?",
    "Here's a tricky one. Name it!",
    "Got it already? Which {n} is this?",
    "Keep that streak going! Which {n}?",
    "Last medium question! Which {n} is this?",
    "Hard round! Only the experts from here. Which {n} is this?",
    "Not so easy now. Which {n}?",
    "Here's one for the experts. Name this {n}!",
    "Take your time... but not too much. Which {n}?",
    "This one is a real head-scratcher. Which {n} is it?",
    "Big brain time! What {n} is this?",
    "Lock in your answer! Which {n}?",
    "Few people get this one. Do you?",
    "Are you still with me? Which {n} is this?",
    "Last hard one! Which {n}?",
    "Genius round! Only true masters get these. Which {n} is this?",
    "Seriously tough now. Name this {n}!",
    "If you know this one, you're a legend. Which {n}?",
    "Deep cut! Which {n} is this?",
    "Here's a rare one. What is it?",
    "No hints this time. Which {n}?",
    "Almost there! Which {n} is this?",
    "Only a handful of people will get this. Which {n}?",
    "Second to last! Name this {n}!",
    "Final question! Make it count. Which {n} is this?",
]
OPEN = ["Yes! It's", "That's", "It's", "Correct answer:", "Of course, it's", "Boom! It's", "Here it is:", "You got it, it's", "Spot on! It's", "The answer is"]
LVL = ['EASY'] * 10 + ['MEDIUM'] * 10 + ['HARD'] * 10 + ['GENIUS'] * 10


def art(name):
    return ('an ' if name[0].lower() in 'aeiou' else 'a ') + name


def main(ep):
    sp = json.load(open(f'{ep}/spec.json'))
    items = sp['items']; assert len(items) == 40, len(items)
    rnd = random.Random(ep)
    pos = []
    for blk in range(4):
        p = [0, 1, 2, 3, 0, 1, 2, 3, blk % 4, (blk + 2) % 4]; rnd.shuffle(p); pos += p
    qs, vq, va = [], [], []
    for i, it in enumerate(items):
        ans, wrong, wiki, fact = it[:4]; extra = it[4] if len(it) > 4 else {}
        opts = list(wrong); rnd.shuffle(opts); opts.insert(pos[i], ans)
        q = {'lvl': LVL[i], 'q': extra.get('q', sp['q']), 'o': opts, 'a': pos[i], 'f': fact, 'wiki': wiki}
        for k in ('search', 'focus', 'contain', 'hide'):
            if k in extra: q[k] = extra[k]
        if sp.get('contain'): q['contain'] = True
        qs.append(q)
        vq.append(LEAD[i].format(n=sp['noun']))
        say = extra.get('say', art(ans) if sp.get('article') else ans)
        va.append(f"{OPEN[i % 10]} {say}. {fact}")
    json.dump(qs, open(f'{ep}/questions.json', 'w'), ensure_ascii=False, indent=1)
    json.dump({'intro': sp['intro'], 'q': vq, 'a': va, 'outro': sp['outro']}, open(f'{ep}/voice.json', 'w'), ensure_ascii=False, indent=1)
    print(ep, 'ok', [sum(1 for q in qs if q['a'] == k) for k in range(4)])


if __name__ == '__main__':
    for e in sys.argv[1:]: main(e)
