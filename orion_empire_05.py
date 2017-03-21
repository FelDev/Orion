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
    
VERSION 4
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
        return Id.id

class Vue():
    def __init__(self,parent,ip,nom,largeur=800,hauteur=600):
        self.root=Tk()
        self.root.title(os.path.basename(sys.argv[0]))
        self.root.protocol("WM_DELETE_WINDOW", self.fermerfenetre)
        self.nocol=0
        self.parent=parent
        self.modele=None
        self.nom=None
        self.largeur=largeur
        self.hauteur=hauteur
        self.images={}
        self.vueactive=None
        self.infoactive=None
        self.cadreactif=None
        self.cadreetatactif=None
        self.maselection=None
        self.creercadres(ip,nom)
        self.changecadre(self.cadresplash)
        
    def creercadres(self,ip,nom):
        self.creercadresplash(ip, nom)
        self.creercadrelobby()
        self.cadrejeu=Frame(self.root,bg="blue")
        self.modecourant=None
        self.modes={}
            
    def changeinfo(self,info,etend=0):
        if self.infoactive:
            self.infoactive.pack_forget()
        self.infoactive=info
        if etend:
            self.infoactive.pack(expand=1,fill=BOTH)
        else:
            self.infoactive.pack()
        

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
        self.nbetoile=Entry(bg="pink")
        self.nbetoile.insert(0, 100)
        self.largeurespace=Entry(bg="pink")
        self.largeurespace.insert(0, 5000)
        self.hauteurespace=Entry(bg="pink")
        self.hauteurespace.insert(0, 5000)
        self.btnlancerpartie=Button(text="Lancer partie",bg="pink",command=self.lancerpartie,state=DISABLED)
        self.canevaslobby.create_window(440,240,window=self.listelobby,width=200,height=400)
        self.canevaslobby.create_window(200,200,window=self.largeurespace,width=100,height=30)
        self.canevaslobby.create_window(200,250,window=self.hauteurespace,width=100,height=30)
        self.canevaslobby.create_window(200,300,window=self.nbetoile,width=100,height=30)
        self.canevaslobby.create_window(100,300,window=self.modeauto,width=100,height=30)
        self.canevaslobby.create_window(200,400,window=self.btnlancerpartie,width=100,height=30)
       
    def voirsysteme(self):
        s=self.modes["systeme"]
        s.initsysteme()
        self.changemode(s)
        
    def voirplanete(self):
        s=self.modes["planete"]
        s.initsysteme()
        self.changemode(s)
        
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
        largeurjeu=self.largeurespace.get()
        hauteurjeu=self.hauteurespace.get()
        modeauto=int(self.modeauto.get())
        if largeurjeu :
            largeurjeu=int(largeurjeu)
        else:
            largeurjeu=None
        if hauteurjeu :
            hauteurjeu=int(hauteurjeu)
        else:
            hauteurjeu=None
        self.parent.lancerpartie(largeurjeu,hauteurjeu,modeauto)
        
    def affichelisteparticipants(self,lj):
        self.listelobby.delete(0,END)
        for i in lj:
            self.listelobby.insert(END,i)

    def afficherinitpartie(self,mod):
        self.nom=self.parent.monnom
        self.modele=mod
        self.largeur=mod.largeur
        self.hauteur=mod.hauteur
        
        self.modes["galaxie"]=VueGalaxie(self)
        self.modes["systeme"]=VueSysteme(self)
        self.modes["planete"]=VuePlanete(self)
        
        g=self.modes["galaxie"]
        g.labid.config(text=self.nom)
        g.labid.config(fg=mod.joueurs[self.nom].couleur)
        
        g.chargeimages()
        g.afficherdecor() #pourrait etre remplace par une image fait avec PIL -> moins d'objets
        self.changecadre(self.cadrejeu,1)
        self.changemode(self.modes["galaxie"])
        
    
                
    def fermerfenetre(self):
        # Ici, on pourrait mettre des actions a faire avant de fermer (sauvegarder, avertir etc)
        self.parent.fermefenetre()
        
class Perspective(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent.cadrejeu)
        self.parent=parent
        self.largeur=self.parent.largeur
        self.hauteur=self.parent.hauteur
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
        
        self.canevas.config(scrollregion=(0,0,self.parent.largeur,self.parent.hauteur))
        
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
        
        self.labid.bind("<Button>",self.identifierplanetemere)
        self.btncreervaisseau=Button(self.cadreetataction,text="Creer Vaisseau",command=self.creervaisseau)
        self.btncreervaisseau.pack()
        
        self.btncreerstation=Button(self.cadreetataction,text="Creer Station",command=self.creerstation)
        self.btncreerstation.pack()
        
        self.btnvuesysteme=Button(self.cadreetataction,text="Voir systeme",command=self.voirsysteme)
        self.btnvuesysteme.pack(side=BOTTOM)
        
        self.btnvuesysteme2=Button(self.cadreetataction,text="salut les gars",command=self.voirsysteme)
        self.btnvuesysteme2.pack(side=BOTTOM)
        
        
        self.lbselectecible=Label(self.cadreetatmsg,text="Choisir cible",bg="darkgrey")
        self.lbselectecible.pack()
    
    def voirsysteme(self):
        if self.maselection:
            self.parent.voirsysteme()
            
    def creerimagefond(self): #NOTE - au lieu de la creer a chaque fois on aurait pu utiliser une meme image de fond cree avec PIL
        imgfondpil = Image.new("RGBA", (self.parent.largeur,self.parent.hauteur),"black")
        draw = ImageDraw.Draw(imgfondpil) 
        for i in range(self.parent.largeur*2):
            x=random.randrange(self.parent.largeur)
            y=random.randrange(self.parent.hauteur)
            draw.ellipse((x,y,x+1,y+1), fill="white")
        self.images["fond"] = ImageTk.PhotoImage(imgfondpil)
        self.canevas.create_image(self.parent.largeur/2,self.parent.hauteur/2,image=self.images["fond"])
            
    def chargeimages(self):
        im = Image.open("./images/chasseur.png")
        self.images["chasseur"] = ImageTk.PhotoImage(im)
        
    def afficherdecor(self):
        self.creerimagefond()
        self.affichermodelestatique()

    def affichermodelestatique(self): 
        mini=self.parent.largeur/200
        for i in self.modele.systemes:
            t=i.etoile.taille*3
            #print(t)
            self.canevas.create_oval(i.x-t,i.y-t,i.x+t,i.y+t,fill="grey80",
                                     tags=(i.proprietaire,"systeme","id_"+str(i.id),"inconnu"))
            
            #self.canevas.create_text(i.x-t,i.y-t,text=str(i.id),fill="white")
            
        for i in self.modele.joueurscles:
            couleur=self.modele.joueurs[i].couleur
            m=2
            for j in self.modele.joueurs[i].systemescontroles:
                t=j.etoile.taille*3
                self.canevas.create_oval(j.x-t,j.y-t,j.x+t,j.y+t,fill=couleur,
                                     tags=(i,"systeme","id_"+str(j.id),"possession",len(j.planetes),j.etoile.type))
                
                self.minimap.create_oval((j.x/mini)-m,(j.y/mini)-m,(j.x/mini)+m,(j.y/mini)+m,fill=couleur)
                
    # ************************ FIN DE LA SECTION D'AMORCE DE LA PARTIE
                
    def identifierplanetemere(self,evt): 
        j=self.modele.joueurs[self.parent.nom]
        couleur=j.couleur
        x=j.systememere.x
        y=j.systememere.y
        id=j.systememere.id
        t=10
        self.canevas.create_oval(x-t,y-t,x+t,y+t,dash=(3,3),width=2,outline=couleur,
                                 tags=(self.parent.nom,"selecteur","id_"+str(id),""))
        xx=x/self.largeur
        yy=y/self.hauteur
        ee=self.canevas.winfo_width()
        ii=self.canevas.winfo_height()
        eex=int(ee)/self.largeur/2
        self.canevas.xview(MOVETO, xx-eex)
        eey=int(ii)/self.hauteur/2
        self.canevas.yview(MOVETO, yy-eey)
        #self.canevas.yview(MOVETO, yy+eey)
        
    def creervaisseau(self): 
        print("CREER VAISSEAU",self.maselection)
        self.parent.parent.creervaisseau(self.maselection[2][3:])
        self.maselection=None
        self.canevas.delete("selecteur")
    
    def creerstation(self):
        print("Creer station EN CONSTRUCTION")
        
        
    def afficherpartie(self,mod):
        self.canevas.delete("artefact")
        self.canevas.delete("pulsar")
        self.afficherselection()
        
        for i in mod.joueurscles:
            i=mod.joueurs[i]
            for j in i.vaisseaux:
                x2,y2=hlp.getAngledPoint(j.angletrajet,8,j.x,j.y)
                x1,y1=hlp.getAngledPoint(j.angletrajet,4,j.x,j.y)
                x0,y0=hlp.getAngledPoint(j.angleinverse,4,j.x,j.y)
                x,y=hlp.getAngledPoint(j.angleinverse,7,j.x,j.y)
                self.canevas.create_line(x,y,x0,y0,fill="yellow",width=3,
                                         tags=(j.proprietaire,"vaisseau","id_"+str(j.id),"artefact"))
                self.canevas.create_line(x0,y0,x1,y1,fill=i.couleur,width=4,
                                         tags=(j.proprietaire,"vaisseau","id_"+str(j.id),"artefact"))
                self.canevas.create_line(x1,y1,x2,y2,fill="red",width=2,
                                         tags=(j.proprietaire,"vaisseau","id_"+str(j.id),"artefact"))
                
        for i in mod.pulsars:
            t=i.taille
            self.canevas.create_oval(i.x-t,i.y-t,i.x+t,i.y+t,fill="orchid3",dash=(1,1),
                                                 outline="maroon1",width=2,
                                     tags=(i.proprietaire,"pulsar","id_"+str(i.id),"inconnu"))
            
    def changerproprietaire(self,prop,couleur,systeme): 
        id=str(systeme.id)
        lp=self.canevas.find_withtag("id_"+id)
        self.canevas.itemconfig(lp[0],fill=couleur)
        t=(prop,"systeme","id_"+id,"possession",len(systeme.planetes),systeme.etoile.type)
        self.canevas.itemconfig(lp[0],tags=t)
               
    def afficherselection(self):
        if self.maselection!=None:
            joueur=self.modele.joueurs[self.parent.nom]
            if self.maselection[1]=="systeme":
                for i in joueur.systemescontroles:
                    if i.id == int(self.maselection[2][3:]):
                        x=i.x
                        y=i.y
                        t=10
                        self.canevas.create_oval(x-t,y-t,x+t,y+t,dash=(2,2),
                                                 outline=joueur.couleur,
                                                 tags=("select","selecteur"))
            elif self.maselection[1]=="vaisseau":
                for i in joueur.vaisseaux:
                    if i.id == int(self.maselection[2][3:]):
                        x=i.x
                        y=i.y
                        t=10
                        self.canevas.create_rectangle(x-t,y-t,x+t,y+t,dash=(2,2),
                                                      outline=joueur.couleur,
                                                      tags=("select","selecteur"))
      
    def cliquervue(self,evt):
        self.changecadreetat(None)
        
        t=self.canevas.gettags(CURRENT)
        #if t:
            
        if t and t[0]==self.parent.nom:
            #self.maselection=self.canevas.find_withtag(CURRENT)#[0]
            self.maselection=[self.parent.nom,t[1],t[2]]  # prop, type, id; self.canevas.find_withtag(CURRENT)#[0]
            print(self.maselection,t)
            if t[1] == "systeme":
                self.montresystemeselection()
            elif t[1] == "vaisseau":
                self.montrevaisseauxselection()
        elif "systeme" in t and t[0]!=self.parent.nom:
            if self.maselection:
                # attribuer cette systeme a la cible du vaisseau selectionne
                self.parent.parent.ciblerdestination(self.maselection[2][3:],t[2][3:])
            print("Cette systeme ne vous appartient pas - elle est a ",t[0])
            self.maselection=None
            self.lbselectecible.pack_forget()
            self.canevas.delete("selecteur")
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
        self.maselection=None
        self.btncreervaisseau=Button(self.cadreetataction,text="Creer Vaisseau",command=self.creervaisseau)
        self.btncreervaisseau.pack()
        
        self.btncreerstation=Button(self.cadreetataction,text="Creer Station",command=self.creerstation)
        self.btncreerstation.pack()
        self.btnvuesysteme=Button(self.cadreetataction,text="Voir planete",command=self.voirplanete)
        self.btnvuesysteme.pack(side=BOTTOM)
        
        self.lbselectecible=Label(self.cadreetatmsg,text="Choisir cible",bg="darkgrey")
        self.lbselectecible.pack()
    
    def voirplanete(self):
        print("VA atterrir sur la planete")
            
    def initsysteme(self):
        print("SYSTEME",self.parent.modecourant.maselection)
        s=self.parent.modecourant.maselection
        j=self.parent.modele.joueurs[s[0]]
        sysid=int(s[2][3:])
        for i in j.systemescontroles:
            if i.id==sysid:
                self.affichesysteme(i)
    
    def affichesysteme(self,i):
        x=self.largeur/2
        y=self.hauteur/2
        n=20
        self.canevas.create_oval(x-n,y-n,x+n,y+n,fill="yellow")
        for p in i.planetes:
            print(p)
            x,y=hlp.getAngledPoint(p.angle,p.distance,i.x,i.y)
            print(x,y)
            n=p.taille
            self.canevas.create_oval(x-n,y-n,x+n,y+n,fill="red")
            x,y=hlp.getAngledPoint(p.angle,20,100,100)
            n=2
            self.minimap.create_oval(x-n,y-n,x+n,y+n,fill="red")
        
        xx=x/self.largeur
        yy=y/self.hauteur
        ee=800 #self.canevas.winfo_width()
        ii=600 #self.canevas.winfo_height()
        eex=int(ee)/self.largeur/2
        self.canevas.xview(MOVETO, xx-eex)
        eey=int(ii)/self.hauteur/2
        self.canevas.yview(MOVETO, yy-eey)
        print(x,y,xx,yy,ee,ii,eex,eey)
            
        
    def creerimagefond(self): #NOTE - au lieu de la creer a chaque fois on aurait pu utiliser une meme image de fond cree avec PIL
        imgfondpil = Image.new("RGBA", (self.parent.largeur,self.parent.hauteur),"black")
        draw = ImageDraw.Draw(imgfondpil) 
        for i in range(self.parent.largeur*2):
            x=random.randrange(self.parent.largeur)
            y=random.randrange(self.parent.hauteur)
            draw.ellipse((x,y,x+1,y+1), fill="white")
        self.images["fond"] = ImageTk.PhotoImage(imgfondpil)
        self.canevas.create_image(self.parent.largeur/2,self.parent.hauteur/2,image=self.images["fond"])
            
    def chargeimages(self):
        im = Image.open("./images/chasseur.png")
        self.images["chasseur"] = ImageTk.PhotoImage(im)
        
    def afficherdecor(self):
        self.creerimagefond()
        self.affichermodelestatique()

    def affichermodelestatique(self): 
        mini=self.parent.largeur/200
        for i in self.modele.systemes:
            t=i.etoile.taille*3
            #print(t)
            self.canevas.create_oval(i.x-t,i.y-t,i.x+t,i.y+t,fill="grey80",
                                     tags=(i.proprietaire,"systeme","id_"+str(i.id),"inconnu"))
            
            #self.canevas.create_text(i.x-t,i.y-t,text=str(i.id),fill="white")
            
        for i in self.modele.joueurscles:
            couleur=self.modele.joueurs[i].couleur
            m=2
            for j in self.modele.joueurs[i].systemescontroles:
                t=j.etoile.taille*3
                self.canevas.create_oval(j.x-t,j.y-t,j.x+t,j.y+t,fill=couleur,
                                     tags=(i,"systeme","id_"+str(j.id),"possession",len(j.planetes),j.etoile.type))
                
                self.minimap.create_oval((j.x/mini)-m,(j.y/mini)-m,(j.x/mini)+m,(j.y/mini)+m,fill=couleur)
                
    # ************************ FIN DE LA SECTION D'AMORCE DE LA PARTIE
                
    def creervaisseau(self): 
        print("CREER VAISSEAU",self.maselection)
        self.parent.parent.creervaisseau(self.maselection[2][3:])
        self.maselection=None
        self.canevas.delete("selecteur")
    
    def creerstation(self):
        print("Creer station EN CONSTRUCTION")
        
        
    def afficherpartie(self,mod):
        self.canevas.delete("artefact")
        self.canevas.delete("pulsar")
        self.afficherselection()
        
        for i in mod.joueurscles:
            i=mod.joueurs[i]
            for j in i.vaisseaux:
                x2,y2=hlp.getAngledPoint(j.angletrajet,8,j.x,j.y)
                x1,y1=hlp.getAngledPoint(j.angletrajet,4,j.x,j.y)
                x0,y0=hlp.getAngledPoint(j.angleinverse,4,j.x,j.y)
                x,y=hlp.getAngledPoint(j.angleinverse,7,j.x,j.y)
                self.canevas.create_line(x,y,x0,y0,fill="yellow",width=3,
                                         tags=(j.proprietaire,"vaisseau","id_"+str(j.id),"artefact"))
                self.canevas.create_line(x0,y0,x1,y1,fill=i.couleur,width=4,
                                         tags=(j.proprietaire,"vaisseau","id_"+str(j.id),"artefact"))
                self.canevas.create_line(x1,y1,x2,y2,fill="red",width=2,
                                         tags=(j.proprietaire,"vaisseau","id_"+str(j.id),"artefact"))
                
        for i in mod.pulsars:
            t=i.taille
            self.canevas.create_oval(i.x-t,i.y-t,i.x+t,i.y+t,fill="orchid3",dash=(1,1),
                                                 outline="maroon1",width=2,
                                     tags=(i.proprietaire,"pulsar","id_"+str(i.id),"inconnu"))
            
    def changerproprietaire(self,prop,couleur,systeme): 
        id=str(systeme.id)
        lp=self.canevas.find_withtag("id_"+id)
        self.canevas.itemconfig(lp[0],fill=couleur)
        t=(prop,"systeme","id_"+id,"possession",len(systeme.planetes),systeme.etoile.type)
        self.canevas.itemconfig(lp[0],tags=t)
               
    def afficherselection(self):
        if self.maselection!=None:
            joueur=self.modele.joueurs[self.parent.nom]
            if self.maselection[1]=="systeme":
                for i in joueur.systemescontroles:
                    if i.id == int(self.maselection[2][3:]):
                        x=i.x
                        y=i.y
                        t=10
                        self.canevas.create_oval(x-t,y-t,x+t,y+t,dash=(2,2),
                                                 outline=joueur.couleur,
                                                 tags=("select","selecteur"))
            elif self.maselection[1]=="vaisseau":
                for i in joueur.vaisseaux:
                    if i.id == int(self.maselection[2][3:]):
                        x=i.x
                        y=i.y
                        t=10
                        self.canevas.create_rectangle(x-t,y-t,x+t,y+t,dash=(2,2),
                                                      outline=joueur.couleur,
                                                      tags=("select","selecteur"))
      
    def cliquervue(self,evt):
        self.changecadreetat(None)
        
        t=self.canevas.gettags(CURRENT)
        #if t:
            
        if t and t[0]==self.parent.nom:
            #self.maselection=self.canevas.find_withtag(CURRENT)#[0]
            self.maselection=[self.parent.nom,t[1],t[2]]  # prop, type, id; self.canevas.find_withtag(CURRENT)#[0]
            print(self.maselection,t)
            if t[1] == "systeme":
                self.montresystemeselection()
            elif t[1] == "vaisseau":
                self.montrevaisseauxselection()
        elif "systeme" in t and t[0]!=self.parent.nom:
            if self.maselection:
                # attribuer cette systeme a la cible du vaisseau selectionne
                self.parent.parent.ciblerdestination(self.maselection[2][3:],t[2][3:])
            print("Cette systeme ne vous appartient pas - elle est a ",t[0])
            self.maselection=None
            self.lbselectecible.pack_forget()
            self.canevas.delete("selecteur")
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
        
class VuePlanete(Perspective):
    def __init__(self,parent):
        pass
    
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
        
class Planete():
    def __init__(self,parent,type,dist,taille,angle):
        self.id=Id.prochainid()
        self.parent=parent
        self.proprietaire="inconnu"
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
        self.x=x
        self.y=y
        self.etoile=Etoile(self,x,y)
        self.planetes=[]
        self.creerplanetes()
        
    def creerplanetes(self):
        systemeplanetaire=random.randrange(5) # 4 chance sur 5 d'avoir des planetes
        if systemeplanetaire:
            nbplanetes=random.randrange(12)
            print(nbplanetes)
            for i in range(nbplanetes):
                type=random.choice(["roc","gaz","glace"])
                distsol=random.randrange(200)/10 #distance en unite astronomique 150000000km
                taille=random.randrange(50)/10 # en masse solaire
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
        self.x=self.base.x+self.base.etoile.taille/2+self.taille
        self.y=self.base.y
        self.taille=16
        self.cargo=0
        self.energie=100
        self.vitesse=5 #0.5
        self.cible=None 
        
    def avancer(self):
        rep=None
        if self.cible:
            x=self.cible.x
            y=self.cible.y
            self.x,self.y=hlp.getAngledPoint(self.angletrajet,self.vitesse,self.x,self.y)
            if hlp.calcDistance(self.x,self.y,x,y) <=self.vitesse+self.cible.etoile.taille+self.taille/2:
                rep=self.cible
                self.base=self.cible
                self.cible=None
            return rep
        
    def ciblerdestination(self,p):
        self.cible=p
        self.angletrajet=hlp.calcAngle(self.x,self.y,p.x,p.y)
        self.angleinverse=math.radians(math.degrees(self.angletrajet)+180)
        dist=hlp.calcDistance(self.x,self.y,p.x,p.y)
        print("Distance",dist," en ", int(dist/self.vitesse))
    
class Joueur():
    def __init__(self,parent,nom,systememere,couleur):
        self.id=Id.prochainid()
        self.parent=parent
        self.nom=nom
        self.systememere=systememere
        self.systememere.proprietaire=self.nom
        self.couleur=couleur
        self.systemescontroles=[systememere]
        self.vaisseaux=[]
        self.actions={"creervaisseau":self.creervaisseau,
                      "ciblerdestination":self.ciblerdestination}
        
    def creervaisseau(self,id):
        for i in self.systemescontroles:
            if i.id==int(id):
                v=Vaisseau(self.nom,i)
                self.vaisseaux.append(v)
                return 1
        
    def ciblerdestination(self,ids):
        idori,iddesti=ids
        for i in self.vaisseaux:
            if i.id== int(idori):
                for j in self.parent.systemes:
                    if j.id== int(iddesti):
                        #i.cible=j
                        i.ciblerdestination(j)
                        return
        
    def prochaineaction(self):
        global modeauto
        for i in self.vaisseaux:
            if i.cible:
                rep=i.avancer()
                if rep:
                    if rep.proprietaire=="inconnu":
                        rep.proprietaire=self.nom
                        self.systemescontroles.append(rep)
                        self.parent.changerproprietaire(self.nom,self.couleur,rep)
            
            elif modeauto:
                p=random.choice(self.parent.systemes)
                i.ciblerdestination(p)
                
        if len(self.vaisseaux)<modeauto:
            print("DEMANDE AUTO ",self.parent.parent.cadre,self.nom,len(self.vaisseaux))
            self.creervaisseau(str(self.systememere.id))   
    
class Modele():
    def __init__(self,parent,joueurs,xy):
        self.parent=parent
        self.largeur,self.hauteur=xy
        self.joueurs={}
        self.joueurscles=joueurs
        self.actionsafaire={}
        self.pulsars=[]
        self.systemes=[]
        self.terrain=[]
        self.creersystemes()
        
    def creersystemes(self):
        bordure=10
        for i in range(150):
            x=random.randrange(self.largeur-(2*bordure))+bordure
            y=random.randrange(self.hauteur-(2*bordure))+bordure
            self.systemes.append(Systeme(x,y))
        
        for i in range(20):
            x=random.randrange(self.largeur-(2*bordure))+bordure
            y=random.randrange(self.hauteur-(2*bordure))+bordure
            self.pulsars.append(Pulsar(x,y))
            
        np=len(self.joueurscles)
        planes=[]
        while np:
            p=random.choice(self.systemes)
            if p not in planes:
                planes.append(p)
                self.systemes.remove(p)
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
                print("actionafaire",i)
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
    def lancerpartie(self,largeurjeu,hauteurjeu,mode): # reponse du bouton de lancement de simulation (pour celui qui a parti le serveur seulement)
        rep=self.serveur.lancerpartie(largeurjeu,hauteurjeu,mode) 
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
            print("REP",rep)
            self.modele=Modele(self,rep[1][0][1],rep[1][0][2]) # on cree le modele
            modeauto=int(rep[1][0][3])
            self.vue.afficherinitpartie(self.modele)
            print(self.monnom,"LANCE PROCHAINTOUR")
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
            
    def creervaisseau(self,systeme):
        self.modele.creervaisseau(systeme)
        #self.actions.append([self.monnom,"creervaisseau",""])
        
    def ciblerdestination(self,idorigine,iddestination):
        self.actions.append([self.monnom,"ciblerdestination",[idorigine,iddestination]])
        
    def changerproprietaire(self,nom,couleur,systeme):
        self.vue.modecourant.changerproprietaire(nom,couleur,systeme)
        
if __name__=="__main__":
    c=Controleur()
    print("End Orion_mini")