from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
# Create your views here.
from rapp.forms import FichierForm
import xlrd
import os
import random
from rapp.models import *
from django.contrib.auth.models import User
#import pyexcel.ext.xls
#import pyexcel.ext.xlsx

APP_DIR = os.path.dirname(__file__)  # get current directory
#file_path = os.path.join(APP_DIR, 'baz.txt')  || File path to use in searching uploaded's file


def uploadFile(f,name="fich.xls"):
    with open(APP_DIR+"/files/"+name,'wb+') as des:
        for chunk in f.chunks():
            des.write(chunk)


#SOGEBANK's method for operations
def getValidLineSOGEBANK(sheet):
    fil = []
    for line in range(sheet.nrows):
            row = sheet.row_values(line)
            # print(row)
            #6,7,9,13,14 important Lines in SOGEBANK's sheet
            if line > 11:
                if not ((row[6] == '') and (row[7] == '') and (row[9] == '') and (row[13] == '') and (row[15] == '') and (row[18] == '')):
                    # print(row[6]+"|"+row[7]+"|"+row[9]+"|"+row[13]+"|"+row[15]+"<br />")
                    # print(row[18])
                    tmp = [row[6],row[7],row[9],row[13],row[15],row[18]]
                    # print(tmp)
                    fil.append(tmp)
    return fil


def putInLineSOGEBANK(tab): #Put in line SOGEBANK's file important infomations
    final = []
    for i in range(len(tab)):
        if i > 0:
            if tab[i][3] == '':
                sov = tab[i]
            else:
                sov[3]=tab[i][3]
                sov[5]=tab[i][5]
                final.append(sov)
    #Removing '-' sign preventing convertion to fload
    for z in range(len(final)):
        if final[z][3] == '-':
            final[z][3] = '0'
        if final[z][4] == '-':
            final[z][4] = '0'
    #Removing '-' sign preventing convertion to fload
    return final


def handle_SOGEBANK(sheet):
    return putInLineSOGEBANK(getValidLineSOGEBANK(sheet))

def getDateSOGE(chaine):
    ll= chaine.split("/")#pas correct a cause du test 16
    return "{0}-{1}-{2}".format("2016",ll[1],ll[0])
#SOGEBANK's method for operations


#Quickbooks version test handling
def getDateQuickBooks(chaine):
    # tra = chaine.replace("'","")
    if chaine != '':
        ll = chaine.split("/")
        return "{0}-{1}-{2}".format(ll[2],ll[0],ll[1])
    else:
        return "1111-01-11"
def handle_QuickBooksv1(sheet):
    all = []
    for z in range(sheet.nrows):
            if z > 4:
                all.append(sheet.row_values(z))
    return all
#Quickbooks version test handling



#Comparaison
def convertingTOFloat(values):
    try:
        if(values == ''):
            return 0.00
        else:
            v = float(values)
            return v
    except:
        if(values.find(',')!=-1 and values.find('.')!=-1):
            if(values.find(',')<values.find('.')):
                corValues = values.replace(",","")
                return float(corValues)
        elif values.find(',')!=-1 :
            r1 = values.replace(" ", "")
            r2 = r1.replace(",", ".")
            return float(r2)

def convertingTOFloatBis(values):
    try:
        if(values == ''):
            return 0.00
        else:
            v = float(values)
            return v
    except:
        r1 = values.replace(",", "")
        return float(r1)


def comparingFiles(quickBv1,sogebank):
    Cmp = []
    CmpDepot = []
    InCmp = []
    incomes = [{"rsp":"NO"}]
    for i in range(len(quickBv1)):#QuickBooks
            occEquality = 0 #Count the number of occurence when comparing
            occEqualityDepot = 0
            occInfo = {}
            occInfoDepot = {}
            lisSoge = []
            lisSogeDepot =[]
            for j in range(len(sogebank)):#SOGEBANK
                if quickBv1[i][2] == 'Expense':
                    if (convertingTOFloat(quickBv1[i][9])*-1) == convertingTOFloat(sogebank[j][3]):
                        occEquality+=1 #Know the number of Occurence
                        dicQuicks = {'Transaction':quickBv1[i][2],'Name':quickBv1[i][5],'Split':quickBv1[i][8],'Amount':convertingTOFloat(quickBv1[i][9])*-1}
                        lisSoge.append({'DateEff':sogebank[j][0],'Cheque':sogebank[j][1],'Description':sogebank[j][2],'Debit':sogebank[j][3],'Credit':sogebank[j][4]})

                        # dict = {'Transaction':quickBv1[i][2],'Name':quickBv1[i][5],'Split':quickBv1[i][8],'Amount':convertingTOFloat(quickBv1[i][9])*-1,'Date Eff':sogebank[j][0],'Cheque':sogebank[j][1],'Description':sogebank[j][2],'Debit':sogebank[j][3],'Credit':sogebank[j][4]}
                        # print(str(quickBv1[i][2])+" "+str(quickBv1[i][4])+" "+str(quickBv1[i][5])+" "+str(quickBv1[i][8])+" "+str(quickBv1[i][9])+" "+str(sogebank[j][0])+" "+str(sogebank[j][1])+" "+str(sogebank[j][2])+" "+str(sogebank[j][3])+" "+str(sogebank[j][4]))
                        occInfo = {
                        'occ': occEquality,
                        'dicQuicks':dicQuicks,
                        'corres': lisSoge
                        }
                    else:
                        # dict2 = {'Transaction':quickBv1[i][2],'Name':quickBv1[i][5],'Split':quickBv1[i][8],'Amount':convertingTOFloat(quickBv1[i][9])*-1,'Date Eff':sogebank[j][0],'Cheque':sogebank[j][1],'Description':sogebank[j][2],'Debit':sogebank[j][3],'Credit':sogebank[j][4]}
                        dict2 = {'Transaction':quickBv1[i][2],'Name':quickBv1[i][5],'Split':quickBv1[i][8],'Amount':convertingTOFloat(quickBv1[i][9])*-1}
                        if len(InCmp) >= 1:
                            # print("Je suis Ayiti")
                            if InCmp[len(InCmp)-1]['Amount'] != convertingTOFloat(quickBv1[i][9])*-1:
                                print(InCmp[len(InCmp)-1]['Amount'],quickBv1[i][9])
                                InCmp.append(dict2)#Thinking About
                        else:
                            print(len(InCmp))
                            InCmp.append(dict2)#Thinking About
                elif quickBv1[i][2] == 'Income':#They are no incomes values for testing
                        incomes.append({"rsp":"Yes"})
                elif quickBv1[i][2] == 'Deposit':
                    if (convertingTOFloat(quickBv1[i][9])) == convertingTOFloat(sogebank[j][4]):
                        occEqualityDepot+=1 #Know the number of Occurence
                        dicQuicksDepot = {'Transaction':quickBv1[i][2],'Name':quickBv1[i][5],'Split':quickBv1[i][8],'Amount':convertingTOFloat(quickBv1[i][9])*-1}
                        lisSogeDepot.append({'Date Eff':sogebank[j][0],'Cheque':sogebank[j][1],'Description':sogebank[j][2],'Debit':sogebank[j][3],'Credit':sogebank[j][4]})
                        print(quickBv1[i][9]+" "+sogebank[j][4])
                        # dict = {'Transaction':quickBv1[i][2],'Name':quickBv1[i][5],'Split':quickBv1[i][8],'Amount':convertingTOFloat(quickBv1[i][9])*-1,'Date Eff':sogebank[j][0],'Cheque':sogebank[j][1],'Description':sogebank[j][2],'Debit':sogebank[j][3],'Credit':sogebank[j][4]}
                        # print(str(quickBv1[i][2])+" "+str(quickBv1[i][4])+" "+str(quickBv1[i][5])+" "+str(quickBv1[i][8])+" "+str(quickBv1[i][9])+" "+str(sogebank[j][0])+" "+str(sogebank[j][1])+" "+str(sogebank[j][2])+" "+str(sogebank[j][3])+" "+str(sogebank[j][4]))
                        occInfoDepot = {
                        'occ': occEquality,
                        'dicQuicks':dicQuicks,
                        'corres': lisSogeDepot
                        }

            if len(occInfo) != 0:#Adding found Occurences
                Cmp.append(occInfo)#Recoit les Occurences
            if len(occInfoDepot) != 0:
                CmpDepot.append(occInfoDepot)
    rslt = []
    rslt.append({'cmp':Cmp,'incmpExp':InCmp,'incomes':incomes,'depotCmp':CmpDepot})
    return rslt

# def comparingFromDB()
#Comparaison


#Load xlsx's Saved Content to the database
def loadFilesContents2DB(quickBv1,sogebank,sogeIDF,quickIDF):
    # print(quickBv1)
    for i in range(len(quickBv1)):
        # print(quickBv1[i])
        # print(quickBv1[i])
        qui = contenuQUICKBOOKS(date = getDateQuickBooks(quickBv1[i][1]), type_transaction = quickBv1[i][2], name = quickBv1[i][5], num = quickBv1[i][3], posting = quickBv1[i][4], memo = quickBv1[i][6], account = quickBv1[i][7], split = quickBv1[i][8], montant = convertingTOFloat(quickBv1[i][9]), cfFile = quickIDF)
        qui.save()

    for i in range(len(sogebank)):
        so = contenuSOGEBANK(date = getDateSOGE(sogebank[i][0]) , no_cheque = sogebank[i][1] , description = sogebank[i][2] , debit = convertingTOFloatBis(sogebank[i][3]) , crebit = convertingTOFloatBis(sogebank[i][4]) , solde = convertingTOFloatBis(sogebank[i][5]), cfFile = sogeIDF)
        so.save()
#Load xlsx's Saved Content to the database

#NamesFilesFUnnctions
def namesFiles(filename):
    chif = [1,2,3,4,5,6,7,8,9,0]
    lettr = ['a','A','b','B','c','C','d','D','e','E']
    chaine = ""
    for i in range(6):
        chx = random.randrange(0,9,3)
        chaine+= str(chif[chx])
        chaine+= str(lettr[(chx+3)%10])
    r = filename.split('.',1)

    nomFile = chaine+"."+r[1]

    return nomFile
#NamesFilesFUnnctions


def excel_handle(request):
    if request.method == 'POST':
        # print(request.POST['cmpname'])
        vldNameSog = namesFiles(str(request.FILES['soge']))
        vldNameQuick = namesFiles(str(request.FILES['quick']))

        uploadFile(request.FILES['soge'],vldNameSog)#uploadSogeFiles
        uploadFile(request.FILES['quick'],vldNameQuick)#uploadQuickBooks

        sogB = linkSOGEBANK(name = vldNameSog)
        sogB.save()
        quickB = linqQUICKBOOKS(name = vldNameQuick)
        quickB.save()

        c = linkSOGEBANK.objects.get(name= vldNameSog)
        b = linqQUICKBOOKS.objects.get(name= vldNameQuick)

        #getConnectedUser
        user = User.objects.get(username="admin") #Charge uniquement les comparaison de l'utilisateur admin
        #getConnectedUser
        clian = clients.objects.get(compte = user)
        #CreateLink for comparaison between files
        compC = comparaison(nomComparaison = request.POST['cmpname'],cf_link_SOGEBANK=c, cf_link_QUICKBOOKS=b,ended=0,own_by = clian)
        compC.save()

        #CreateLink for comparaison between files


        # print(quickB)
        return HttpResponse("<strong>Telechargement du fichier reussi retourne au <a href='/excel/dashboard/'>Dashboard</a></strong>")
    else:
        return render(request,'app/crapp.html',{})


def main(request):
    return render(request,'app/test.html')

def createRapp(request):
    return render(request,'app/crapp.html',{})

def dashboard(request):
    return render(request,'app/dashboard.html',{})

def showTables(request):
    compp = comparaison.objects.all()
    for ass in compp:
        print(ass.nomComparaison+" "+str(ass.id))
    return render(request,'app/showAll.html',{'all':compp})

def descripComp(request,indice):
    comp = comparaison.objects.get(id = int(indice))
    sogeFile = comp.cf_link_SOGEBANK.name
    quickFile = comp.cf_link_QUICKBOOKS.name
    sogeIDF = comp.cf_link_SOGEBANK
    quickIDF = comp.cf_link_QUICKBOOKS
    print(sogeFile+" "+quickFile)

    adr1 = os.path.join(APP_DIR, 'files/'+sogeFile)
    adr2 = os.path.join(APP_DIR, 'files/'+quickFile)

    so = xlrd.open_workbook(adr1)
    qb = xlrd.open_workbook(adr2)

    soI = so.sheet_by_index(0)
    qbI = qb.sheet_by_index(0)

    soge = handle_SOGEBANK(soI)
    qq = handle_QuickBooksv1(qbI)

    zz = comparingFiles(qq,soge)
    loadFilesContents2DB(qq,soge,sogeIDF,quickIDF)#chargement du contenu du fichier dans la table correspondant

    egal = zz[0]['cmp']
    inegal = zz[0]['incmpExp']
    depotC = zz[0]['depotCmp']
    rev = zz[0]['incomes']
    return render(request,'app/show.html',{'ine':inegal,'equal':egal,'dep':depotC,'revenue':rev})
    # return JsonResponse({'ss':comparingFiles(qq,soge)})
