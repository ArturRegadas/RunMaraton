# qe vv/c(3.5 3, 3.6 4)
#qp pvv//qe
#cb(tira se qp < qe*0.1)
#cp < ct: resto
#
n, p = list(map(int, input().split()))
votos = []
for i in range(p):
    votos.append(int(input()))
vv = sum(votos)
qe = vv/n
#print(qe)
if qe % 0.5 ==0 and qe % 1 != 0:
    qe-=0.1
qe = f"{qe:.0f}"
qe = int(qe)
qp = []
#print(qe)
for i in votos:
    qp.append(i//qe)


l= sum(qp)
for i in range(n-l):
    miax = -1
    miai = -1
    for j in range(p):
        if(votos[j]/(qp[j]+1) > miax):
            miax = votos[i]/(qp[i]+1)
            miai = j
    qp[miai]+=1
for i in qp:
    print(i)

