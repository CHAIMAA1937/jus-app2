#début massique du jus brut en (Kg/h)
m0=1000
#fraction de la m insoluble
x0=0.02
#fraction de la m soluble
y0=0.1
#fraction de l`eau
meau=0.88
#début massique du Particules insolubles filtrées : residus
mResidus=20
#début massique du Apport de jus concentré 
mR=100 #mR=m0*x0
#fraction des matières solubles dans jus concentré ajouté
xr=0.4
#Capacité calorifique constante en (kJ/Kg*K)
Cp=3.8
#température initiale du chaffage en °C
T2=20
#température aprés chauffage en °C
T3=80
#fraction massique final
x4=0.4
#température avant refroidissement en °C
T4=80
#température finale en °C
T5=25
#chaleur latente en (KJ/Kg)
lambda_v=2300
#opération unitaire 1 : filtration (m1 débit total aprés filtration)
m1=m0-mResidus
print("le débit aprés filtration c`est : ",m1)
 #fraction de soluble aprés filtration
y1=(y0*m0)/m1
print("la fraction de soluble aprés filtration c`est : ",y1)
#opération unitaire 2 : mélange
m2=m1+mR
print("le débit total aprés mélange c`est : ",m2)
 #fraction aprés mélange
y2=(m1*y1+mR*xr)/m2
print("la fraction de soluble aprés mélange c`est : ",y2)
#opération unitaire 3 : chauffage
Q3=m2*Cp*(T3-T2)/3600
print("Puissance chauffage c`est : ",Q3)
#opération unitaire 4 : évaporation
 #débit aprés évaporation
m4=(m2*y2)/x4
print("le débit aprés évaporation c`est : ",m4)
 #débit d`eau évaporée
mv=m2-m4
print("le débit d`eau évaporée c`est : ",mv)
 #puissance nécessaire à l`évaporation
Q4=(mv*lambda_v)/3600
#opération unitaire 5 : refroidissement
Q5=m4*Cp*(T4-T5)/3600
print("Puissance refroidissement c`est : ",Q5)
#verfication du bilan global de matière
 #débit total entrant en Kg/h
entrees=m0+mR
print("le débit total entrant en Kg/h c`est : ",entrees)
 #débit total sortant en Kg/h
sorties=mResidus+mv+m4
print("le débit total sortant en Kg/h c`est : ",sorties)
#vérification du bilan des matières solubles
 #quantité de matière solubles entrantes
solubles_entrantes=(m0*y0)+(mR*xr)
print("matière solubles entrantes c`est : ",solubles_entrantes)
 #quantité de matière solubles sortantes
solubles_sortantes=m4*x4
print("matière solubles sortantes c`est : ",solubles_sortantes)

