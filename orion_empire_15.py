# -*- coding: utf-8 -*-
from tkinter import *
from PIL import Image,ImageDraw, ImageTk
import os,os.path
import sys
import Pyro4
import socket
import random
from subprocess import Popen 
from helper import Helper as hlp
import math

""" ORION EMPIRE ******************

VERSION 01
- changer controleur.prochaintour pour appliquer la suggestion de Miguel - FAIT !
- taille de la map - FAIT !
    et canvas size  - FAIT !
    et scrollbar - FAIT !
- taille 8000x8000  - FAIT
- 200 etoiles  - FAIT

VERSION 02
-  Minimap  - FAIT
    et clickable  - FAIT

VERSION 03
- Vision systeme solaire
    - changer cadrejeu pour cadregalactique - FAIT !
    - changer Systeme et systeme pour Systeme et systeme - FAIT !
    
VERSION 04-10
- construction des cadres de base - Refactoring
- rapporter les modes en objets inbdependants pour .la representation
    - ajout planetes autour de systeme
    - creer cadresysteme 
    - boutons niveaux dans info, au dessus de minimap
        NOTE ces boutons sont pour le developement SEULEMENT
             les changements de niveaux se feront en game play
    - choisir cadresysteme, le bouton
    - changer vision pour cadresysteme
    - revenir a cadregalactique
    
- Modifier minimap
    - ajouter visualisation d'effectifs  vaisseaux, autres ???


"""

modeauto=3

class Id():
    id=0
    def prochainid():
        Id.id+=1
        str_id="id_"+str(Id.id)
        return str_id # Id.id

class Vue():
    def __init__(self,parent,ip,nom,largeur=800,hauteur=600):
        self.root=Tk()
        self.root.title(os.path.basename(sys.argv[0]))
        self.root.protocol("WM_DELETE_WINDOW", self.fermerfenetre)
        self.parent=parent
        self.modele=None
        self.nom=None
        self.largeur=largeur
        self.hauteur=hauteur
        self.images={}
        self.modes={}
        self.modecourant=None
        self.cadreactif=None
        self.creercadres(ip,nom)
        self.changecadre(self.cadresplash)
        
    def changemode(self,cadre):
        if self.modecourant:
            self.modecourant.pack_forget()
        self.modecourant=cadre
        self.modecourant.pack(expand=1,fill=BOTH)            

    def changecadre(self,cadre,etend=0):
        if self.cadreactif:
            self.cadreactif.pack_forget()
        self.cadreactif=cadre
        if etend:
            self.cadreactif.pack(expand=1,fill=BOTH)
        else:
            self.cadreactif.pack()
    
    def creercadres(self,ip,nom):
        self.creercadresplash(ip, nom)
        self.creercadrelobby()
        self.cadrejeu=Frame(self.root,bg="blue")
        self.modecourant=None
                
    def creercadresplash(self,ip,nom):
        self.cadresplash=Frame(self.root)
        self.canevasplash=Canvas(self.cadresplash,width=640,height=480,bg="red")
        self.canevasplash.pack()
        self.nomsplash=Entry(bg="pink")
        self.nomsplash.insert(0, nom)
        self.ipsplash=Entry(bg="pink")
        self.ipsplash.insert(0, ip)
        labip=Label(text=ip,bg="red",borderwidth=0,relief=RIDGE)
        btncreerpartie=Button(text="Creer partie",bg="pink",command=self.creerpartie)
        btnconnecterpartie=Button(text="Connecter partie",bg="pink",command=self.connecterpartie)
        self.canevasplash.create_window(200,200,window=self.nomsplash,width=100,height=30)
        self.canevasplash.create_window(200,250,window=self.ipsplash,width=100,height=30)
        self.canevasplash.create_window(200,300,window=labip,width=100,height=30)
        self.canevasplash.create_window(200,350,window=btncreerpartie,width=100,height=30)
        self.canevasplash.create_window(200,400,window=btnconnecterpartie,width=100,height=30) 
        
    def creercadrelobby(self):
        self.cadrelobby=Frame(self.root)
        self.canevaslobby=Canvas(self.cadrelobby,width=640,height=480,bg="lightblue")
        self.canevaslobby.pack()
        self.listelobby=Listbox(bg="red",borderwidth=0,relief=FLAT)
        self.modeauto=Entry(bg="lightgreen")
        self.modeauto.insert(0,0)
        self.diametre=Entry(bg="pink")
        self.diametre.insert(0, 50)
        self.densitestellaire=Entry(bg="pink")
        self.densitestellaire.insert(0, 25)
        self.btnlancerpartie=Button(text="Lancer partie",bg="pink",command=self.lancerpartie,state=DISABLED)
        self.canevaslobby.create_window(440,240,window=self.listelobby,width=200,height=400)
        self.canevaslobby.create_window(200,200,window=self.diametre,width=100,height=30)
        self.canevaslobby.create_window(200,250,window=self.densitestellaire,width=100,height=30)
        self.canevaslobby.create_window(100,300,window=self.modeauto,width=100,height=30)
        self.canevaslobby.create_window(200,400,window=self.btnlancerpartie,width=100,height=30)

    def voirgalaxie(self):
        # A FAIRE comme pour voirsysteme et voirplanete, tester si on a deja la vuegalaxie
        #         sinon si on la cree en centrant la vue sur le systeme d'ou on vient
        s=self.modes["galaxie"]
        self.changemode(s) 
       
    def voirsysteme(self,systeme=None):
        if systeme:
            sid=systeme.id
            if sid in self.modes["systemes"].keys():
                s=self.modes["systemes"][sid]
            else:
                s=VueSysteme(self)
                self.modes["systemes"][sid]=s
                s.initsysteme(systeme)
            self.changemode(s)
        
    def voirplanete(self,maselection=None):
        s=self.modes["planetes"]
        
        if maselection:
            sysid=maselection[5]
            planeid=maselection[2]
            if planeid in self.modes["planetes"].keys():
                s=self.modes["planetes"][planeid]
            else:
                s=VuePlanete(self,sysid,planeid)
                self.modes["planetes"][planeid]=s
                s.initplanete(sysid,planeid)
            self.changemode(s)
        else:
            print("aucune planete selectionnee pour atterrissage")
        
    def creerpartie(self):
        nom=self.nomsplash.get()
        ip=self.ipsplash.get()
        if nom and ip:
            self.parent.creerpartie()
            self.btnlancerpartie.config(state=NORMAL)
            self.connecterpartie()
          
    def connecterpartie(self):
        nom=self.nomsplash.get()
        ip=self.ipsplash.get()
        if nom and ip:
            self.parent.inscrirejoueur()
            self.changecadre(self.cadrelobby)
            self.parent.boucleattente()
            
    def lancerpartie(self):
        global modeauto
        diametre=self.diametre.get()
        densitestellaire=self.densitestellaire.get()
        modeauto=int(self.modeauto.get())
        if diametre :
            diametre=int(diametre)
        else:
            largeurjeu=None
        if densitestellaire :
            densitestellaire=int(densitestellaire)
        else:
            densitestellaire=None
        self.parent.lancerpartie(diametre,densitestellaire,modeauto)
        
    def affichelisteparticipants(self,lj):
        self.listelobby.delete(0,END)
        for i in lj:
            self.listelobby.insert(END,i)

    def afficherinitpartie(self,mod):
        self.nom=self.parent.monnom
        self.modele=mod
        
        self.modes["galaxie"]=VueGalaxie(self)
        self.modes["systemes"]={}
        self.modes["planetes"]={}
        
        g=self.modes["galaxie"]
        g.labid.config(text=self.nom)
        g.labid.config(fg=mod.joueurs[self.nom].couleur)
        
        g.chargeimages()
        g.afficherdecor() #pourrait etre remplace par une image fait avec PIL -> moins d'objets
        self.changecadre(self.cadrejeu,1)
        self.changemode(self.modes["galaxie"])
        
    def affichermine(self,joueur,systemeid,planeteid,x,y):
        for i in self.modes["planetes"].keys():
            if i == planeteid:
                im=self.modes["planetes"][i].images["mine"]
                self.modes["planetes"][i].canevas.create_image(x,y,image=im)
                
    def fermerfenetre(self):
        # Ici, on pourrait mettre des actions a faire avant de fermer (sauvegarder, avertir etc)
        self.parent.fermefenetre()
        
class Perspective(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent.cadrejeu)
        self.parent=parent
        self.modele=None
        self.cadreetatactif=None
        self.images={}
        self.cadrevue=Frame(self,width=400,height=400, bg="lightgreen")
        self.cadrevue.pack(side=LEFT,expand=1,fill=BOTH)
        
        self.cadreinfo=Frame(self,width=200,height=200,bg="darkgrey")
        self.cadreinfo.pack(side=LEFT,fill=Y)
        self.cadreinfo.pack_propagate(0)
        self.cadreetat=Frame(self.cadreinfo,width=200,height=200,bg="grey20")
        self.cadreetat.pack()
        
        self.scrollX=Scrollbar(self.cadrevue,orient=HORIZONTAL)
        self.scrollY=Scrollbar(self.cadrevue)
        self.canevas=Canvas(self.cadrevue,width=800,height=600,bg="grey11",
                             xscrollcommand=self.scrollX.set,
                             yscrollcommand=self.scrollY.set)
        
        self.canevas.bind("<Button>",self.cliquervue)
        
        self.scrollX.config(command=self.canevas.xview)
        self.scrollY.config(command=self.canevas.yview)
        self.canevas.grid(column=0,row=0,sticky=N+E+W+S)
        self.cadrevue.columnconfigure(0,weight=1)
        self.cadrevue.rowconfigure(0,weight=1)
        self.scrollX.grid(column=0,row=1,sticky=E+W)
        self.scrollY.grid(column=1,row=0,sticky=N+S)
        
        self.labid=Label(self.cadreinfo,text=self.parent.nom)
        self.labid.pack()
        
        self.cadreetataction=Frame(self.cadreetat,width=200,height=200,bg="grey20")
        
        self.cadreetatmsg=Frame(self.cadreetat,width=200,height=200,bg="grey20")
        
        self.cadreminimap=Frame(self.cadreinfo,width=200,height=200,bg="grey20")
        self.cadreminimap.pack(side=BOTTOM)
        self.minimap=Canvas(self.cadreminimap,width=200,height=200,bg="grey11")
        self.minimap.bind("<Button>",self.cliquerminimap)
        self.minimap.pack()
        
    def cliquervue(self,evt):
        pass
    
    def cliquerminimap(self,evt):
        pass
    
    def changecadreetat(self,cadre):
        if self.cadreetatactif:
            self.cadreetatactif.pack_forget()
            self.cadreetatactif=None
        if cadre:
            self.cadreetatactif=cadre
            self.cadreetatactif.pack()
        
class VueGalaxie(Perspective):
    def __init__(self,parent):
        Perspective.__init__(self,parent)
        self.modele=self.parent.modele
        self.maselection=None
        self.AL2pixel=100
        
        self.largeur=self.modele.diametre*self.AL2pixel
        self.hauteur=self.largeur
        
        self.canevas.config(scrollregion=(0,0,self.largeur,self.hauteur))
        
        self.labid.bind("<Button>",self.identifierplanetemere)
        self.btncreervaisseau=Button(self.cadreetataction,text="Creer Vaisseau",command=self.creervaisseau)
        self.btncreervaisseau.pack()
        
        self.btncreerstation=Button(self.cadreetataction,text="Creer Station",command=self.creerstation)
        self.btncreerstation.pack()
        self.btnvuesysteme=Button(self.cadreetataction,text="Voir systeme",command=self.voirsysteme)
        self.btnvuesysteme.pack(side=BOTTOM)
        
        self.lbselectecible=Label(self.cadreetatmsg,text="Choisir cible",bg="darkgrey")
        self.lbselectecible.pack()
    
    def voirsysteme(self,systeme=None):
        if systeme==None:
            if self.maselection and self.maselection[0]==self.parent.nom and self.maselection[1]=="systeme":
                sid=self.maselection[2]
                for i in self.modele.joueurs[self.parent.nom].systemesvisites:
                    if i.id==sid:
                        s=i
                        break
                
                self.parent.parent.visitersysteme(sid)
                self.parent.voirsysteme(s) #normalement devrait pas planter
        else:                
            sid=systeme.id
            for i in self.modele.joueurs[self.parent.nom].systemesvisites:
                if i.id==sid:
                    s=i
                    break
            # NOTE passer par le serveur est-il requis ????????????
            self.parent.parent.visitersysteme(sid)
            self.parent.voirsysteme(s) #normalement devrait pas planter
            
    def chargeimages(self):
        im = Image.open("./images/chasseur.png")
        self.images["chasseur"] = ImageTk.PhotoImage(im)
        
    def afficherdecor(self):
        self.creerimagefond()
        self.affichermodelestatique()

    def creerimagefond(self): #NOTE - au lieu de la creer a chaque fois on aurait pu utiliser une meme image de fond cree avec PIL
        imgfondpil = Image.new("RGBA", (self.largeur,self.hauteur),"black")
        draw = ImageDraw.Draw(imgfondpil) 
        for i in range(self.largeur*2):
            x=random.randrange(self.largeur)
            y=random.randrange(self.hauteur)
            #draw.ellipse((x,y,x+1,y+1), fill="white")
            draw.ellipse((x,y,x+0.1,y+0.11), fill="white")
        self.images["fond"] = ImageTk.PhotoImage(imgfondpil)
        self.canevas.create_image(self.largeur/2,self.hauteur/2,image=self.images["fond"])
            
    def affichermodelestatique(self): 
        mini=self.largeur/200
        e=self.AL2pixel
        me=200/self.modele.diametre
        for i in self.modele.systemes:
            t=i.etoile.taille*3
            if t<3:
                t=3
            self.canevas.create_oval((i.x*e)-t,(i.y*e)-t,(i.x*e)+t,(i.y*e)+t,fill="grey80",
                                     tags=("inconnu","systeme",i.id,str(i.x),str(i.y)))
            # NOTE pour voir les id des objets systeme, decommentez la ligne suivantes
            #self.canevas.create_text((i.x*e)-t,(i.y*e)-(t*2),text=str(i.id),fill="white")
            
        for i in self.modele.joueurscles:
            couleur=self.modele.joueurs[i].couleur
            m=2
            for j in self.modele.joueurs[i].systemesvisites:
                s=self.canevas.find_withtag(j.id)
                self.canevas.addtag_withtag(i, s)
                self.canevas.itemconfig(s,fill=couleur)
                
                self.minimap.create_oval((j.x*me)-m,(j.y*me)-m,(j.x*me)+m,(j.y*me)+m,fill=couleur)
                
    # ************************ FIN DE LA SECTION D'AMORCE DE LA PARTIE
                
    def identifierplanetemere(self,evt): 
        j=self.modele.joueurs[self.parent.nom]
        couleur=j.couleur
        x=j.systemeorigine.x*self.AL2pixel
        y=j.systemeorigine.y*self.AL2pixel
        id=j.systemeorigine.id
        t=10
        self.canevas.create_oval(x-t,y-t,x+t,y+t,dash=(3,3),width=2,outline=couleur,
                                 tags=(self.parent.nom,"selecteur",id,""))
        xx=x/self.largeur
        yy=y/self.hauteur
        ee=self.canevas.winfo_width()
        ii=self.canevas.winfo_height()
        eex=int(ee)/self.largeur/2
        self.canevas.xview(MOVETO, xx-eex)
        eey=int(ii)/self.hauteur/2
        self.canevas.yview(MOVETO, yy-eey)
        
    def creervaisseau(self): 
        if self.maselection:
            self.parent.parent.creervaisseau(self.maselection[2])
            self.maselection=None
            self.canevas.delete("selecteur")
    
    def creerstation(self):
        print("Creer station EN CONSTRUCTION")
        
    def afficherpartie(self,mod):
        self.canevas.delete("artefact")
        self.canevas.delete("pulsar")
        self.afficherselection()
        
        e=self.AL2pixel
        for i in mod.joueurscles:
            i=mod.joueurs[i]
            for j in i.vaisseauxinterstellaires:
                jx=j.x*e
                jy=j.y*e
                x2,y2=hlp.getAngledPoint(j.angletrajet,8,jx,jy)
                x1,y1=hlp.getAngledPoint(j.angletrajet,4,jx,jy)
                x0,y0=hlp.getAngledPoint(j.angleinverse,4,jx,jy)
                x,y=hlp.getAngledPoint(j.angleinverse,7,jx,jy)
                self.canevas.create_line(x,y,x0,y0,fill="yellow",width=3,
                                         tags=(j.proprietaire,"vaisseauinterstellaire",j.id,"artefact"))
                self.canevas.create_line(x0,y0,x1,y1,fill=i.couleur,width=4,
                                         tags=(j.proprietaire,"vaisseauinterstellaire",j.id,"artefact"))
                self.canevas.create_line(x1,y1,x2,y2,fill="red",width=2,
                                         tags=(j.proprietaire,"vaisseauinterstellaire",j.id,"artefact"))
                
        for i in mod.pulsars:
            t=i.taille
            self.canevas.create_oval((i.x*e)-t,(i.y*e)-t,(i.x*e)+t,(i.y*e)+t,fill="orchid3",dash=(1,1),
                                                 outline="maroon1",width=2,
                                     tags=("inconnu","pulsar",i.id))
                
    def changerproprietaire(self,prop,couleur,systeme):
        #lp=self.canevas.find_withtag(systeme.id) 
        self.canevas.addtag_withtag(prop,systeme.id)
        
        
    def changerproprietaire1(self,prop,couleur,systeme): 
        id=str(systeme.id)
        lp=self.canevas.find_withtag(id)
        self.canevas.itemconfig(lp[0],fill=couleur)
        t=(prop,"systeme",id,"systemevisite",str(len(systeme.planetes)),systeme.etoile.type)
        self.canevas.itemconfig(lp[0],tags=t)
               
    def afficherselection(self):
        self.canevas.delete("selecteur")
        if self.maselection!=None:
            joueur=self.modele.joueurs[self.parent.nom]
            
            e=self.AL2pixel
            if self.maselection[1]=="systeme":
                for i in joueur.systemesvisites:
                    if i.id == self.maselection[2]:
                        x=i.x
                        y=i.y
                        t=10
                        self.canevas.create_oval((x*e)-t,(y*e)-t,(x*e)+t,(y*e)+t,dash=(2,2),
                                                 outline=joueur.couleur,
                                                 tags=("select","selecteur"))
            elif self.maselection[1]=="vaisseauinterstellaire":
                for i in joueur.vaisseauxinterstellaires:
                    if i.id == self.maselection[2]:
                        x=i.x
                        y=i.y
                        t=10
                        self.canevas.create_rectangle((x*e)-t,(y*e)-t,(x*e)+t,(y*e)+t,dash=(2,2),
                                                      outline=joueur.couleur,
                                                      tags=("select","selecteur"))
      
    def cliquervue(self,evt):
        self.changecadreetat(None)
        t=self.canevas.gettags("current")
        if t and t[0]!="current":
            
            if t[1]=="vaisseauinterstellaire":
                print("IN VAISSEAUINTERSTELLAIRE",t)
                self.maselection=[self.parent.nom,t[1],t[2]]
                self.montrevaisseauxselection()
            
            elif t[1]=="systeme":
                print("IN SYSTEME",t)
                if self.maselection and self.maselection[1]=="vaisseauinterstellaire":
                    print("IN systeme + select VAISSEAUINTERSTELLAIRE")
                    self.parent.parent.ciblerdestination(self.maselection[2],t[2])
                elif self.parent.nom in t:
                    print("IN systeme  PAS SELECTION")
                    self.maselection=[self.parent.nom,t[1],t[2]]
                    self.montresystemeselection()
                else:    
                    print("IN systeme + RIEN")
                    self.maselection=None
                    self.lbselectecible.pack_forget()
                    self.canevas.delete("selecteur")
            else:
                print("Objet inconnu")
        else:
            print("Region inconnue")
            self.maselection=None
            self.lbselectecible.pack_forget()
            self.canevas.delete("selecteur")
            
    def montresystemeselection(self):
        self.changecadreetat(self.cadreetataction)
        
    def montrevaisseauxselection(self):
        self.changecadreetat(self.cadreetatmsg)
    
    def afficherartefacts(self,joueurs):
        pass #print("ARTEFACTS de ",self.nom)
    
    def cliquerminimap(self,evt):
        x=evt.x
        y=evt.y
        xn=self.largeur/int(self.minimap.winfo_width())
        yn=self.hauteur/int(self.minimap.winfo_height())
        
        ee=self.canevas.winfo_width()
        ii=self.canevas.winfo_height()
        eex=int(ee)/self.largeur/2
        eey=int(ii)/self.hauteur/2
        
        self.canevas.xview(MOVETO, (x*xn/self.largeur)-eex)
        self.canevas.yview(MOVETO, (y*yn/self.hauteur)-eey)
        
class VueSysteme(Perspective):
    def __init__(self,parent):
        Perspective.__init__(self,parent)
        self.modele=self.parent.modele
        self.planetes={}
        self.systeme=None
        self.maselection=None
        
        self.UA2pixel=100 # ainsi la terre serait a 100 pixels du soleil et Uranus a 19 Unites Astronomiques       
        self.largeur=self.modele.diametre*self.UA2pixel
        self.hauteur=self.largeur
        
        self.canevas.config(scrollregion=(0,0,self.largeur,self.hauteur))
        
        self.btncreervaisseau=Button(self.cadreetataction,text="Creer Vaisseau",command=self.creervaisseau)
        self.btncreervaisseau.pack()
        
        self.btncreerstation=Button(self.cadreetataction,text="Creer Station",command=self.creerstation)
        self.btncreerstation.pack()
        self.btnvuesysteme=Button(self.cadreetataction,text="Voir planete",command=self.voirplanete)
        self.btnvuesysteme.pack(side=BOTTOM)
        self.btnvuesysteme=Button(self.cadreetataction,text="Voir galaxie",command=self.voirgalaxie)
        self.btnvuesysteme.pack(side=BOTTOM)
        
        self.lbselectecible=Label(self.cadreetatmsg,text="Choisir cible",bg="darkgrey")
        self.lbselectecible.pack()
        self.changecadreetat(self.cadreetataction)
    
    def voirplanete(self):
        self.parent.voirplanete(self.maselection)

    def voirgalaxie(self):
        self.parent.voirgalaxie()
            
    def initsysteme(self,i):
        self.systeme=i
        self.affichermodelestatique(i)
    
    def affichermodelestatique(self,i):
        xl=self.largeur/2
        yl=self.hauteur/2
        n=i.etoile.taille*self.UA2pixel/2
        mini=2
        UAmini=4
        self.canevas.create_oval(xl-n,yl-n,xl+n,yl+n,fill="yellow",dash=(1,2),width=4,outline="white",
                                 tags=("systeme",i.id,"etoile",str(n),))
        self.minimap.create_oval(100-mini,100-mini,100+mini,100+mini,fill="yellow")
        for p in i.planetes:
            x,y=hlp.getAngledPoint(math.radians(p.angle),p.distance*self.UA2pixel,xl,yl)
            n=p.taille*self.UA2pixel
            self.canevas.create_oval(x-n,y-n,x+n,y+n,fill="red",tags=(i.proprietaire,"planete",p.id,"inconnu",i.id,int(x),int(y)))
            x,y=hlp.getAngledPoint(math.radians(p.angle),p.distance*UAmini,100,100)
            self.minimap.create_oval(x-mini,y-mini,x+mini,y+mini,fill="red",tags=())
        
        # NOTE Il y a un probleme ici je ne parviens pas a centrer l'objet convenablement comme dans la fonction 'identifierplanetemere'
        canl=int(self.canevas.cget("width"))/2
        canh=int(self.canevas.cget("height"))/2
        self.canevas.xview(MOVETO, ((self.largeur/2)-canl)/self.largeur)
        self.canevas.yview(MOVETO, ((self.hauteur/2)-canh)/self.hauteur)
                 
    def creerimagefond(self): 
        pass  # on pourrait creer un fond particulier pour un systeme
    
    def afficherdecor(self):
        pass
                
    def creervaisseau(self): 
        pass
    
    def creerstation(self):
        pass
         
    def afficherpartie(self,mod):
        self.canevas.delete("artefact")
        self.canevas.delete("pulsar")
        self.afficherselection()
        
        for i in mod.joueurscles:
            i=mod.joueurs[i]
            for j in i.vaisseauxinterplanetaires:
                x2,y2=hlp.getAngledPoint(j.angletrajet,8,j.x,j.y)
                x1,y1=hlp.getAngledPoint(j.angletrajet,4,j.x,j.y)
                x0,y0=hlp.getAngledPoint(j.angleinverse,4,j.x,j.y)
                x,y=hlp.getAngledPoint(j.angleinverse,7,j.x,j.y)
                self.canevas.create_line(x,y,x0,y0,fill="yellow",width=3,
                                         tags=(j.proprietaire,"vaisseauinter",j.id,"artefact"))
                self.canevas.create_line(x0,y0,x1,y1,fill=i.couleur,width=4,
                                         tags=(j.proprietaire,"vaisseauinter",j.id,"artefact"))
                self.canevas.create_line(x1,y1,x2,y2,fill="red",width=2,
                                         tags=(j.proprietaire,"vaisseauinter",j.id,"artefact"))
            
    def changerproprietaire(self,prop,couleur,systeme): 
        pass
               
    def afficherselection(self):
        if self.maselection!=None:
            joueur=self.modele.joueurs[self.parent.nom]
            if self.maselection[1]=="planete":
                for i in self.systeme.planetes:
                    if i.id == self.maselection[2]:
                        x=int(self.maselection[3])
                        y=int(self.maselection[4])
                        t=20
                        self.canevas.create_oval(x-t,y-t,x+t,y+t,dash=(2,2),
                                                 outline=joueur.couleur,
                                                 tags=("select","selecteur"))
      
    def cliquervue(self,evt):
        self.changecadreetat(None)
        
        t=self.canevas.gettags("current")
        if t and t[0]!="current":
            nom=t[0]
            idplanete=t[2]
            idsysteme=t[4]
            self.maselection=[self.parent.nom,t[1],t[2],t[5],t[6],t[4]]  # prop, type, id; self.canevas.find_withtag(CURRENT)#[0]
            if t[1] == "planete" and t[3]=="inconnu":
                self.montreplaneteselection()
                
            # ici je veux envoyer un message comme quoi je visite cette planete
            # et me mettre en mode planete sur cette planete, d'une shot
            # ou est-ce que je fais selection seulement pour etre enteriner par un autre bouton
            
            #self.parent.parent.atterrirdestination(nom,idsysteme,idplanete)
        else:
            print("Region inconnue")
            self.maselection=None
            self.lbselectecible.pack_forget()
            self.canevas.delete("selecteur")
            
    def montreplaneteselection(self):
        self.changecadreetat(self.cadreetataction)
    
    def afficherartefacts(self,joueurs):
        pass #print("ARTEFACTS de ",self.nom)
    
    def cliquerminimap(self,evt):
        x=evt.x
        y=evt.y
        xn=self.largeur/int(self.minimap.winfo_width())
        yn=self.hauteur/int(self.minimap.winfo_height())
        
        ee=self.canevas.winfo_width()
        ii=self.canevas.winfo_height()
        eex=int(ee)/self.largeur/2
        eey=int(ii)/self.hauteur/2
        
        self.canevas.xview(MOVETO, (x*xn/self.largeur)-eex)
        self.canevas.yview(MOVETO, (y*yn/self.hauteur)-eey)
        
class VuePlanete(Perspective):
    def __init__(self,parent,syste,plane):
        Perspective.__init__(self,parent)
        self.modele=self.parent.modele
        self.planete=plane
        self.systeme=syste
        self.infrastructures={}
        self.maselection=None
        self.macommande=None
        
        self.KM2pixel=100 # ainsi la terre serait a 100 pixels du soleil et Uranus a 19 Unites Astronomique       
        self.largeur=self.modele.diametre*self.KM2pixel
        self.hauteur=self.largeur
        
        self.canevas.config(scrollregion=(0,0,self.largeur,self.hauteur))
        self.canevas.config(bg="sandy brown")
        
        self.btncreervaisseau=Button(self.cadreetataction,text="Creer Mine",command=self.creermine)
        self.btncreervaisseau.pack()
        
        self.btncreerstation=Button(self.cadreetataction,text="Creer Manufacture",command=self.creermanufacture)
        self.btncreerstation.pack()
        self.btnvuesysteme=Button(self.cadreetataction,text="Voir System",command=self.voirsysteme)
        self.btnvuesysteme.pack(side=BOTTOM)
        
        self.changecadreetat(self.cadreetataction)
    
    def creermine(self):
        self.macommande="mine"
    
    def creermanufacture(self):
        pass
    
    def voirsysteme(self):
        for i in self.modele.joueurs[self.parent.nom].systemesvisites:
            if i.id==self.systeme:
                self.parent.voirsysteme(i)
            
    def initplanete(self,sys,plane):
        s=None
        p=None
        for i in self.modele.joueurs[self.parent.nom].systemesvisites:
            if i.id==sys:
                s=i
                for j in i.planetes:
                    if j.id==plane:
                        p=j
                        break
        self.systemeid=sys
        self.planeteid=plane
        self.affichermodelestatique(s,p)
    
    def affichermodelestatique(self,s,p):
        # NOTE: DANGER pas le bon mode d'acces aux objets
        self.chargeimages()
        xl=self.largeur/2
        yl=self.hauteur/2
        mini=2
        UAmini=4
        for i in p.infrastructures:
            pass
        
        self.canevas.create_image(p.posXatterrissage,p.posYatterrissage,image=self.images["ville"])
        
        canl=int(p.posXatterrissage-100)/self.largeur
        canh=int(p.posYatterrissage-100)/self.hauteur
        self.canevas.xview(MOVETO,canl)
        self.canevas.yview(MOVETO, canh)  
            
    def chargeimages(self):
        im = Image.open("./images/ville_100.png")
        self.images["ville"] = ImageTk.PhotoImage(im)
        im = Image.open("./images/mine_100.png")
        self.images["mine"] = ImageTk.PhotoImage(im)
        
    def afficherdecor(self):
        pass
                
    def creervaisseau(self): 
        pass
    
    def creerstation(self):
        pass
         
    def afficherpartie(self,mod):
        pass
            
    def changerproprietaire(self,prop,couleur,systeme): 
        pass
               
    def afficherselection(self):
        pass
      
    def cliquervue(self,evt):
        #self.changecadreetat(None)
        
        t=self.canevas.gettags("current")
        if t and t[0]!="current":
            if t[0]==self.parent.nom:
                pass
            elif t[1]=="systeme":
                pass
        else:
            if self.macommande:
                x=self.canevas.canvasx(evt.x)
                y=self.canevas.canvasy(evt.y)
                self.parent.parent.creermine(self.parent.nom,self.systemeid,self.planeteid,x,y)
                self.macommande=None
            
    def montreinfrastructuresselection(self):
        pass
        
    def montrevaisseauxselection(self):
        pass
    
    def afficherartefacts(self,joueurs):
        pass #print("ARTEFACTS de ",self.nom)
    
    def cliquerminimap(self,evt):
        x=evt.x
        y=evt.y
        xn=self.largeur/int(self.minimap.winfo_width())
        yn=self.hauteur/int(self.minimap.winfo_height())
        
        ee=self.canevas.winfo_width()
        ii=self.canevas.winfo_height()
        eex=int(ee)/self.largeur/2
        eey=int(ii)/self.hauteur/2
        
        self.canevas.xview(MOVETO, (x*xn/self.largeur)-eex)
        self.canevas.yview(MOVETO, (y*yn/self.hauteur)-eey)
        
class Pulsar():
    def __init__(self,x,y):
        self.id=Id.prochainid()
        self.proprietaire="inconnu"
        self.x=x
        self.y=y
        self.periode=random.randrange(20,50,5)
        self.moment=0
        self.phase=1 
        self.mintaille=self.taille=random.randrange(2,4)
        self.maxtaille=self.mintaille++random.randrange(1,3)
        self.pas=self.maxtaille/self.periode
        self.taille=self.mintaille
        
    def evoluer(self):
        self.moment=self.moment+self.phase
        if self.moment==0:
            self.taille=self.mintaille
            self.phase=1
        elif self.moment==self.periode:
            self.taille=self.mintaille+self.maxtaille
            self.phase=-1
        else:
            self.taille=self.mintaille+(self.moment*self.pas)
 
class Ville():
    def __init__(self,parent,proprio="inconnu",x=2500,y=2500):
        self.id=Id.prochainid()
        self.parent=parent
        self.x=x
        self.y=y
        self.proprietaire=proprio
        self.taille=20
               
class Mine():
    def __init__(self,parent,nom,systemeid,planeteid,x,y):
        self.id=Id.prochainid()
        self.parent=parent
        self.x=x
        self.y=y
        self.systemeid=systemeid
        self.planeteid=planeteid
        self.entrepot=0
                
class Planete():
    def __init__(self,parent,type,dist,taille,angle):
        self.id=Id.prochainid()
        self.parent=parent
        self.posXatterrissage=random.randrange(5000)
        self.posYatterrissage=random.randrange(5000)
        self.infrastructures=[Ville(self)]
        self.proprietaire="inconnu"
        self.visiteurs={}
        self.distance=dist
        self.type=type
        self.taille=taille
        self.angle=angle
        
class Etoile():
    def __init__(self,parent,x,y):
        self.id=Id.prochainid()
        self.parent=parent
        self.type=random.choice(["rouge","rouge","rouge",
                                 "jaune","jaune",
                                 "bleu"])
        self.taille=random.randrange(25)/10 +0.1   # en masse solaire
        
class Systeme():
    def __init__(self,x,y):
        self.id=Id.prochainid()
        self.proprietaire="inconnu"
        self.visiteurs={}
        self.diametre=50 # UA unite astronomique = 150000000km
        self.x=x
        self.y=y
        self.etoile=Etoile(self,x,y)
        self.planetes=[]
        self.planetesvisites=[]
        self.creerplanetes()
        
    def creerplanetes(self):
        systemeplanetaire=random.randrange(5) # 4 chance sur 5 d'avoir des planetes
        if systemeplanetaire:
            nbplanetes=random.randrange(12)+1
            for i in range(nbplanetes):
                type=random.choice(["roc","gaz","glace"])
                distsol=random.randrange(250)/10 #distance en unite astronomique 150000000km
                taille=random.randrange(50)/100 # en masse solaire
                angle=random.randrange(360)
                self.planetes.append(Planete(self,type,distsol,taille,angle))
                
class Vaisseau():
    def __init__(self,nom,systeme):
        self.id=Id.prochainid()
        self.proprietaire=nom
        self.taille=16
        self.base=systeme
        self.angletrajet=0
        self.angleinverse=0
        self.x=self.base.x
        self.y=self.base.y
        self.taille=16
        self.cargo=0
        self.energie=100
        self.vitesse=random.choice([0.001,0.003,0.005,0.01])*5 #0.5
        self.cible=None 
        
    def avancer(self):
        rep=None
        if self.cible:
            x=self.cible.x
            y=self.cible.y
            self.x,self.y=hlp.getAngledPoint(self.angletrajet,self.vitesse,self.x,self.y)
            if hlp.calcDistance(self.x,self.y,x,y) <=self.vitesse:
                rep=self.cible
                self.base=self.cible
                self.cible=None
            return rep
        
    def ciblerdestination(self,p):
        self.cible=p
        self.angletrajet=hlp.calcAngle(self.x,self.y,p.x,p.y)
        self.angleinverse=math.radians(math.degrees(self.angletrajet)+180)
        dist=hlp.calcDistance(self.x,self.y,p.x,p.y)
        #print("Distance",dist," en ", int(dist/self.vitesse))
    
class Joueur():
    def __init__(self,parent,nom,systemeorigine,couleur):
        self.id=Id.prochainid()
        self.parent=parent
        self.nom=nom
        self.systemeorigine=systemeorigine
        self.couleur=couleur
        self.systemesvisites=[systemeorigine]
        self.vaisseauxinterstellaires=[]
        self.vaisseauxinterplanetaires=[]
        self.actions={"creervaisseau":self.creervaisseau,
                      "ciblerdestination":self.ciblerdestination,
                      "atterrirplanete":self.atterrirplanete,
                      "visitersysteme":self.visitersysteme,
                      "creermine":self.creermine}
        
    def creermine(self,listeparams):
        nom,systemeid,planeteid,x,y=listeparams
        for i in self.systemesvisites:
            if i.id==systemeid:
                for j in i.planetes:
                    if j.id==planeteid:
                        mine=Mine(self,nom,systemeid,planeteid,x,y)
                        j.infrastructures.append(mine)
                        self.parent.parent.affichermine(nom,systemeid,planeteid,x,y)
                        
        
        
                
    def atterrirplanete(self,d):
        nom,systeid,planeid=d
        for i in self.systemesvisites:
            if i.id==systeid:
                for j in i.planetes:
                    if j.id==planeid:
                        i.planetesvisites.append(j)
                        if nom==self.parent.parent.monnom:
                            self.parent.parent.voirplanete(i.id,j.id)
                        return 1
        
    
    def visitersysteme(self,systeme_id):
        for i in self.parent.systemes:
            if i.id==systeme_id:
                self.systemesvisites.append(i)
                
    def creervaisseau(self,id):
        for i in self.systemesvisites:
            if i.id==id:
                v=Vaisseau(self.nom,i)
                self.vaisseauxinterstellaires.append(v)
                return 1
        
    def ciblerdestination(self,ids):
        idori,iddesti=ids
        for i in self.vaisseauxinterstellaires:
            if i.id== idori:
                for j in self.parent.systemes:
                    if j.id== iddesti:
                        #i.cible=j
                        i.ciblerdestination(j)
                        return
                for j in self.systemesvisites:
                    if j.id== iddesti:
                        #i.cible=j
                        i.ciblerdestination(j)
                        return
        
    def prochaineaction(self): # NOTE : cette fonction sera au coeur de votre developpement
        global modeauto
        for i in self.vaisseauxinterstellaires:
            if i.cible:
                rep=i.avancer()
                if rep:
                    if rep.proprietaire=="inconnu":
                        rep.proprietaire=self.nom
                        if rep not in self.systemesvisites:
                            self.systemesvisites.append(rep)
                            self.parent.changerproprietaire(self.nom,self.couleur,rep)
            
            elif modeauto:
                p=random.choice(self.parent.systemes)
                i.ciblerdestination(p)
                
        if len(self.vaisseauxinterstellaires)<modeauto:
            print("DEMANDE AUTO ",self.parent.parent.cadre,self.nom,len(self.vaisseauxinterstellaires))
            self.creervaisseau(str(self.systemeorigine.id))   
    
class Modele():
    def __init__(self,parent,joueurs,dd):
        self.parent=parent
        self.diametre,self.densitestellaire=dd
        self.nbsystemes=int(self.diametre**2/self.densitestellaire)
        print(self.nbsystemes)
        
        self.joueurs={}
        self.joueurscles=joueurs
        self.actionsafaire={}
        self.pulsars=[]
        self.systemes=[]
        self.terrain=[]
        self.creersystemes()
        
    def creersystemes(self):
        
        for i in range(self.nbsystemes):
            x=random.randrange(self.diametre*10)/10
            y=random.randrange(self.diametre*10)/10
            self.systemes.append(Systeme(x,y))
        
        
        for i in range(20):
            x=random.randrange(self.diametre*10)/10
            y=random.randrange(self.diametre*10)/10
            self.pulsars.append(Pulsar(x,y))
            
        np=len(self.joueurscles)
        planes=[]
        systemetemp=self.systemes[:]
        while np:
            p=random.choice(systemetemp)
            if p not in planes and len(p.planetes)>0:
                planes.append(p)
                systemetemp.remove(p)
                np-=1
        couleurs=["cyan","goldenrod","orangered","greenyellow",
                  "dodgerblue","yellow2","maroon1","chartreuse3"]
        
        for i in self.joueurscles:
            self.joueurs[i]=Joueur(self,i,planes.pop(0),couleurs.pop(0))
            
    def creervaisseau(self,systeme):
        self.parent.actions.append([self.parent.monnom,"creervaisseau",systeme])
            
    def prochaineaction(self,cadre):
        if cadre in self.actionsafaire:
            for i in self.actionsafaire[cadre]:
                self.joueurs[i[0]].actions[i[1]](i[2])
            del self.actionsafaire[cadre]
                
        for i in self.joueurscles:
            self.joueurs[i].prochaineaction()
            
        for i in self.pulsars:
            i.evoluer()
            
    def changerproprietaire(self,nom,couleur,syst):
        self.parent.changerproprietaire(nom,couleur,syst)
                
class Controleur():
    def __init__(self):
        print("IN CONTROLEUR")
        self.attente=0
        self.cadre=0 # le no de cadre pour assurer la syncronisation avec les autres participants
        self.egoserveur=0 
        self.actions=[]    # la liste de mes actions a envoyer au serveur pour qu'il les redistribue a tous les participants
        self.monip=self.trouverIP() # la fonction pour retourner mon ip
        self.monnom=self.generernom() # un generateur de nom pour faciliter le deboggage (comme il genere un nom quasi aleatoire et on peut demarrer plusieurs 'participants' sur une meme machine pour tester)
        self.modele=None
        self.serveur=None
        self.vue=Vue(self,self.monip,self.monnom)
        self.vue.root.mainloop()
        
    def trouverIP(self): # fonction pour trouver le IP en 'pignant' gmail
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # on cree un socket
        s.connect(("gmail.com",80))    # on envoie le ping
        monip=s.getsockname()[0] # on analyse la reponse qui contient l'IP en position 0 
        s.close() # ferme le socket
        return monip
    
    def generernom(self):  # generateur de nouveau nom - accelere l'entree de nom pour les tests - parfois a peut generer le meme nom mais c'est rare
        monnom="jmd_"+str(random.randrange(1000))
        return monnom

    def creerpartie(self):
        if self.egoserveur==0:
            pid = Popen(["C:\\Python34\\Python.exe", "./orion_empire_serveur.py"],shell=1).pid # on lance l'application serveur
            self.egoserveur=1 # on note que c'est soi qui, ayant demarre le serveur, aura le privilege de lancer la simulation

    ## ----------- FONCTION POUR CELUI QUI A CREE LA PARTIE SEULEMENT
    def lancerpartie(self,diametre,densitestellaire,mode): # reponse du bouton de lancement de simulation (pour celui qui a parti le serveur seulement)
        rep=self.serveur.lancerpartie(diametre,densitestellaire,mode) 
   ## ----------- FIN --

    def inscrirejoueur(self):
        ipserveur=self.vue.ipsplash.get() # lire le IP dans le champ du layout
        nom=self.vue.nomsplash.get() # noter notre nom
        if ipserveur and nom:
            ad="PYRO:controleurServeur@"+ipserveur+":9999" # construire la chaine de connection
            self.serveur=Pyro4.core.Proxy(ad) # se connecter au serveur
            self.monnom=nom
            rep=self.serveur.inscrireclient(self.monnom)    # on averti le serveur de nous inscrire
            #tester retour pour erreur de nom
            random.seed(rep[2])

    def boucleattente(self):
        rep=self.serveur.faireaction([self.monnom,0,0])
        if rep[0]:
            print("Recu ORDRE de DEMARRER")
            self.initierpartie(rep[2])
        elif rep[0]==0:
            self.vue.affichelisteparticipants(rep[2])
            self.vue.root.after(50,self.boucleattente)
        
    def initierpartie(self,rep):  # initalisation locale de la simulation, creation du modele, generation des assets et suppression du layout de lobby
        global modeauto
        if rep[1][0][0]=="lancerpartie":
            #print("REP",rep)
            self.modele=Modele(self,rep[1][0][1],rep[1][0][2]) # on cree le modele
            modeauto=int(rep[1][0][3])
            self.vue.afficherinitpartie(self.modele)
            #print(self.monnom,"LANCE PROCHAINTOUR")
            self.prochaintour()
        
    def prochaintour(self): # la boucle de jeu principale, qui sera appelle par la fonction bouclejeu du timer
        if self.serveur: # s'il existe un serveur
            self.cadre=self.cadre+1 # increment du compteur de cadre
            if self.actions: # si on a des actions a partager 
                rep=self.serveur.faireaction([self.monnom,self.cadre,self.actions]) # on les envoie 
            else:
                rep=self.serveur.faireaction([self.monnom,self.cadre,0]) # sinon on envoie rien au serveur on ne fait que le pigner 
                                                                        # (HTTP requiert une requete du client pour envoyer une reponse)
            self.actions=[] # on s'assure que les actions a envoyer sont maintenant supprimer (on ne veut pas les envoyer 2 fois)
            if rep[1]=="attend":
                self.cadre=self.cadre-1 # increment du compteur de cadre
                print("J'attends")
            else:
                self.modele.prochaineaction(self.cadre)    # mise a jour du modele
                self.vue.modecourant.afficherpartie(self.modele) # mise a jour de la vue
            if rep[0]: # si le premier element de reponse n'est pas vide
                for i in rep[2]:   # pour chaque action a faire (rep[2] est dictionnaire d'actions en provenance des participants
                                   # dont les cles sont les cadres durant lesquels ses actions devront etre effectuees
                    if i not in self.modele.actionsafaire.keys(): # si la cle i n'existe pas
                        self.modele.actionsafaire[i]=[] #faire une entree dans le dictonnaire
                    for k in rep[2][i]: # pour toutes les actions lies a une cle du dictionnaire d'actions recu
                        self.modele.actionsafaire[i].append(k) # ajouter cet action au dictionnaire sous l'entree dont la cle correspond a i
            self.vue.root.after(50,self.prochaintour)
        else:
            print("Aucun serveur connu")
            
    def prochaintour1(self): # la boucle de jeu principale, qui sera appelle par la fonction bouclejeu du timer
        if self.serveur: # s'il existe un serveur
            if self.attente==0:
                self.cadre=self.cadre+1 # increment du compteur de cadre
                self.modele.prochaineaction(self.cadre)    # mise a jour du modele
                self.vue.afficherpartie(self.modele) # mise a jour de la vue
            if self.actions: # si on a des actions a partager 
                rep=self.serveur.faireaction([self.monnom,self.cadre,self.actions]) # on les envoie 
            else:
                rep=self.serveur.faireaction([self.monnom,self.cadre,0]) # sinon on envoie rien au serveur on ne fait que le pigner 
                                                                        # (HTTP requiert une requete du client pour envoyer une reponse)
            self.actions=[] # on s'assure que les actions a envoyer sont maintenant supprimer (on ne veut pas les envoyer 2 fois)
            if rep[0]: # si le premier element de reponse n'est pas vide
                for i in rep[2]:   # pour chaque action a faire (rep[2] est dictionnaire d'actions en provenance des participants
                                   # dont les cles sont les cadres durant lesquels ses actions devront etre effectuees
                    if i not in self.modele.actionsafaire.keys(): # si la cle i n'existe pas
                        self.modele.actionsafaire[i]=[] #faire une entree dans le dictonnaire
                    for k in rep[2][i]: # pour toutes les actions lies a une cle du dictionnaire d'actions recu
                        self.modele.actionsafaire[i].append(k) # ajouter cet action au dictionnaire sous l'entree dont la cle correspond a i
            if rep[1]=="attend": # si jamais rep[0] est vide MAIS que rep[1] == 'attend', on veut alors patienter
                if self.attente==0:
                    #self.cadre=self.cadre-1  # donc on revient au cadre initial
                    self.attente=1
                print("ALERTE EN ATTENTE",self.monnom,self.cadre)
            else:
                self.attente=0
                #print(self.cadre)
            self.vue.root.after(50,self.prochaintour)
        else:
            print("Aucun serveur connu")
            
    def fermefenetre(self):
        if self.serveur:
            self.serveur.jequitte(self.monnom)
        self.vue.root.destroy()
        
    # FONCTIONS DE COUP DU JOUEUR A ENVOYER AU SERVEUR
    def creervaisseau(self,systeme):
        self.modele.creervaisseau(systeme)
        #self.actions.append([self.monnom,"creervaisseau",""])
        
    def ciblerdestination(self,idorigine,iddestination):
        self.actions.append([self.monnom,"ciblerdestination",[idorigine,iddestination]])
        
    def visitersysteme(self,systeme_id):
        self.actions.append([self.monnom,"visitersysteme",[systeme_id]])
        
    def atterrirdestination(self,joueur,systeme,planete):
        self.actions.append([self.monnom,"atterrirplanete",[self.monnom,systeme,planete]])
        
    
    def creermine(self,joueur,systeme,planete,x,y):
        self.actions.append([self.monnom,"creermine",[self.monnom,systeme,planete,x,y]])
        
    def affichermine(self,joueur,systemeid,planeteid,x,y):
        self.vue.affichermine(joueur,systemeid,planeteid,x,y)
        
    def voirplanete(self,idsysteme,idplanete):
        pass
    
    def changerproprietaire(self,nom,couleur,systeme):
        self.vue.modes["galaxie"].changerproprietaire(nom,couleur,systeme)
        
if __name__=="__main__":
    c=Controleur()
    print("End Orion_empire")