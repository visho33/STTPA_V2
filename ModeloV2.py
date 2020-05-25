from gurobipy import Model, GRB, quicksum
from params import F, I, N, S, T, E, R, EL, EV, W, V, L, B, A, matches, FECHAINI
from output import parse_output

m = Model("STTPA_V2")

x = m.addVars(N, F, vtype=GRB.BINARY, name="x")
y = m.addVars(I, S, vtype=GRB.BINARY, name="y")
p = m.addVars(I, T, F, vtype=GRB.BINARY, name="p")
a = m.addVars(I, F, vtype=GRB.BINARY, name="a")
d = m.addVars(I, F, vtype=GRB.BINARY, name="d")

m.addConstrs((quicksum(x[n, f] for f in F) == 1 for n in N), name="R2")

m.addConstrs((quicksum(x[n, f] for n in N if EL[i][n] + EV[i][n] == 1) == 1 for i in I
                                                                            for f in F), name="R3")

m.addConstrs((quicksum(y[i, s] for s in S if W[i][s] == 1) == 1 for i in I), name="R4")

m.addConstrs((y[i, s] == 0 for i in I
                           for s in S
                           if W[i][s] == 0), name="R5")

m.addConstrs((quicksum(x[n, f] for n in N if EL[i][n] == 1) == quicksum(y[i, s] for s in S if L[s][f] == 1) for i in I
                                                                                                            for f in F), name="R6")

m.addConstrs((quicksum(x[n, f] for n in N if EV[i][n] == 1) == quicksum(y[i, s] for s in S if L[s][f] == 0) for i in I
                                                                                                            for f in F), name="R7")

m.addConstrs((quicksum(p[i, t, f] for t in T) == 1 for i in I
                                                   for f in F), name="R8")

m.addConstrs(( p[i, t, f-1] <= quicksum(R[i][n][v]*p[i, t+v, f] for v in A) + 1 - x[n, f] 	    for i in I
    																					        for n in N
																					            for t in T
																					            for f in F
																					            if f>FECHAINI and B[i][t][f] == 1), name="R9")

m.addConstrs((E[i][t]<= quicksum(R[i][n][v]*p[i,t+v,FECHAINI] for v in A) + 1 - x[n, FECHAINI] 	for i in I
																					            for n in N
																					            for t in T
																					            if B[i][t][FECHAINI] == 1), name="R10")

m.addConstrs((p[i, t, f] == 0 	for i in I
								for t in T
								for f in F
								if B[i][t][f] == 0), name= "R11")

m.addConstrs((a[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h <= t + 3 * (31 - f)) for i in I
                                                                                                           for j in I
                                                                                                           for t in T
                                                                                                           for f in F
                                                                                                           if f > F[0] and j != i), name="R12")

m.addConstrs((a[i, F[0]] <= 1 - E[i][t] + quicksum(E[j][h] for h in T if h <= t + 3 * (31 - F[0]))   for i in I
                                                                                                     for j in I
                                                                                                     for t in T
                                                                                                     if j != i), name="R13")

m.addConstrs((a[i, f] <= a[i, f - 1] for i in I
                                     for f in F
                                     if f > F[0]), name="R15")

m.addConstrs((d[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h >= t + 3 * (31 - f)) for i in I
                                                                                                           for j in I
                                                                                                           for t in T
                                                                                                           for f in F
                                                                                                           if f > F[0] and j != i), name="R16")

m.addConstrs((d[i, F[0]] <= 1 - E[i][t] + quicksum(E[j][h] for h in T if h >= t + 3 * (31 - F[0]))   for i in I
                                                                                                     for j in I
                                                                                                     for t in T
                                                                                                     if j != i), name="R17")

m.addConstrs((d[i, f] <= d[i, f - 1] for i in I
                                     for f in F
                                     if f > F[0]), name="R18")


m.setObjective(quicksum(quicksum(V[f] * (a[i, f] + d[i, f]) for i in I) for f in F), GRB.MAXIMIZE)

m.optimize()
parse_output(m.getVars(), matches)
