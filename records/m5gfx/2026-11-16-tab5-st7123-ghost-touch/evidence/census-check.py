# Arithmetic check over huntson's 44-line table (issue #418, 2026-11-17T21:53Z).
# No runtime data; verifies counts, episode grouping and rail coherence.
rows = [
 (1,21,5.530,1,719,11),(2,25,1051.179,1,0,24),(3,26,236.756,1,719,10),
 (4,26,236.780,1,719,10),(5,27,69.333,1,719,10),(6,31,4.716,8,None,None),
 (7,31,10.930,1,719,10),(8,33,5.666,1,0,10),(9,40,396.336,1,0,11),
 (10,42,13511.052,1,0,10),(11,56,480.142,1,0,10),(12,56,480.167,1,0,10),
 (13,126,3.904,1,719,17),(14,127,125.999,1,0,12),(15,127,126.023,1,0,12),
 (16,128,1105.288,1,0,10),(17,128,7491.623,1,719,10),(18,128,7491.647,1,719,10),
 (19,128,13137.610,9,None,None),(20,128,13137.635,9,None,None),
 (21,128,17381.405,1,0,10),(22,128,17381.429,1,0,10),
 (23,128,19657.298,10,None,None),(24,128,19657.322,10,None,None),
 (25,128,19684.146,1,0,10),(26,128,19684.169,1,0,10),
 (27,129,39.029,1,0,10),(28,129,39.052,1,0,9),
 (29,130,278.250,10,None,None),(30,130,278.274,10,None,None),
 (31,131,202.851,1,0,10),(32,131,202.874,1,0,10),
 (33,132,326.252,1,719,10),(34,132,326.275,1,719,10),
 (35,132,380.650,10,None,None),(36,132,380.673,10,None,None),
 (37,137,465.182,1,719,10),(38,137,465.206,1,719,10),
 (39,148,919.359,10,None,None),(40,148,919.383,10,None,None),
 (41,151,204.495,10,None,None),(42,151,204.519,10,None,None),
 (43,158,260.046,10,None,None),(44,158,260.070,10,None,None),
]
assert len(rows)==44
whole=[r for r in rows if r[3]==1]
cut=[r for r in rows if r[3]>1]
print("total",len(rows),"whole",len(whole),"cut",len(cut))

# episodes: consecutive whole reads on same boot within 40 ms
eps=[]
for r in whole:
    if eps and eps[-1][-1][1]==r[1] and r[2]-eps[-1][-1][2] <= 0.040:
        eps[-1].append(r)
    else:
        eps.append([r])
print("episodes",len(eps),"sizes",{s:sum(1 for e in eps if len(e)==s) for s in (1,2,3)})
pairs=[e for e in eps if len(e)==2]
print("pairs",len(pairs))
for e in pairs:
    same = e[0][4]==e[1][4]
    print("  boot %3d dt=%.3fs x=%s/%s rail_coherent=%s" % (e[0][1], e[1][2]-e[0][2], e[0][4], e[1][4], same))
print("rail coherent pairs",sum(1 for e in pairs if e[0][4]==e[1][4]),"/",len(pairs))

ints=[r[5] for r in whole]
print("intensity whole: min",min(ints),"max",max(ints),
      "count<=22",sum(1 for i in ints if i<=22),
      "values>22",sorted(i for i in ints if i>22),
      "9-12",sum(1 for i in ints if 9<=i<=12))
print("rails: x=0",sum(1 for r in whole if r[4]==0),"x=719",sum(1 for r in whole if r[4]==719))
print("cut n:",sorted(r[3] for r in cut))
