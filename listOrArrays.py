
points3D=[e.xyz for e in points]
colors=[e.color for e in points]




points=[]
class point():
    def __init__(xyz,color=[]):
        self.xyz=xyz
        self.color=color

for xyz,color in zip(points3D,colors):
    points.append(point(xyz,color))





class anonyme(): pass

for xyz,color in zip(points3D,colors):
    a = anonyme()
    a.xyz = xyz
    a.color = color
    points.append(a)

class anonyme():
    __init__(**argsDict):
        self.__dict__=argsDict
points =[anonyme(xyz=xyz,color=color) for xyz,color in zip(points3D,colors)]

#voir named tuples
    
def arraystolist(classe,**argsDict)

    # verifier que les tableaux font la meme taille
    
    for champ,values in argsDict:
        for i, value in interitems(values)
        #obj = classe
         objects[i].__dict__(key) = 
    # faire un version qui crée de properties pour garder le donnée in sync?

points=arraystolist(Point,xyz=point3D,color=colors)

a
