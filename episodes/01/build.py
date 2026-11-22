import sys; sys.path.insert(0,'tools'); import render_quiz as r
ep='episodes/01'
r.main(ep)
r.shorts(ep,[[3,17,10,26,33,37],[0,7,14,18,20,28],[2,19,32,39,27,35]],
 ['ONLY 2% GET ALL 6 RIGHT','CAN YOU NAME ALL 6 PLACES?','6 SPACE & SCIENCE QUESTIONS'])
