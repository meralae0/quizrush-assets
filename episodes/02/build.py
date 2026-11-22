import sys; sys.path.insert(0,'tools'); import render_quiz as r
ep='episodes/02'
r.main_voice(ep, TQ=10)
r.shorts(ep,[[0,4,12,18,25,35],[2,10,15,21,27,37],[30,31,32,34,36,39]],
 ['ONLY 3% GUESS ALL 6 COUNTRIES','GUESS THE COUNTRY IN 5 SECONDS','THE HARDEST COUNTRY QUIZ'])
