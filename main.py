from parser import Parser
import os
from trie import Trie
from graph import Graph
from _collections import OrderedDict
import sys


# Svaki cvor (VERTEX) ce kao svoj elemenat imati recnik, ciji ce kljuc biti naziv fajla, a vrednost ce biti njegov Trie
# Svaki TrieNode, pored reci, ce sadrzati i ime fajla iz kojeg je rec izvucena, kao i listu koja predstavlja okruzenje te reci
# Prvo se moraju stvoriti svi Vertexi (cvorovi), a zatim se spoje sa Edges
# linkovi_fajlova - kljuc: naziv_fajla, vrednost: lista svih naziva linkova iz tog fajla
# objekti_cvorova - kljuc: naziv_fajla, vrednost: objekat Vertex za taj fajl
# broj linkova u nekom fajlu je 218, 217 ??!?!?!
# moguce je koriscenje graf.vertices() umesto objekti_cvorova, kasno sam primetio da ta metoda postoji :/

reci_za_autocomplete = []
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEPARATOR = os.path.sep
parser = Parser()
# Usmeren graf
graf_fajlova = Graph(True)
linkovi_fajlova = {}
objekti_cvorova = {}


def pocetak_programa():
    ucitaj_sve_fajlove(BASE_DIR + SEPARATOR + "html_fajlovi")
    upisi_edgeove()
    print("Broj cvorova je : ", graf_fajlova.vertex_count())
    print("Broj ivica je : ", graf_fajlova.edge_count())

    cui()


def cui():
    print("Dobrodosli u search engine.")
    while True:
        print("Odaberite opciju pretrazivanja: ")
        print("0 - standardno pretrazivanje (Unos reci i logickih operatera)")
        print("1 - upotreba fraza")
        print("2 - autocomplete")
        print("3 - izlazak")
        odabir_pretrage = input()
        if odabir_pretrage == "0":
            unos_reci_pretrazivanja()
        elif odabir_pretrage == "1":
            unos_fraza()
        elif odabir_pretrage == "2":
            unos_autocomplete()
        elif odabir_pretrage == "3":
            sys.exit(0)
        else:
            print("Neispravan unos!")


def unos_autocomplete():
    uneti_prefiks = input("Unesite prefiks za koji hocete da se obavi autocomplete: ")
    while True:
        broj_reci_za_prikaz = input("Unesite koliko reci zelite da vam se prikaze: ")
        if not broj_reci_za_prikaz.isnumeric():
            print("Neispravan unos broja reci.")
        else:
            lista_reci = pronadji_autocomplete(uneti_prefiks, broj_reci_za_prikaz)
            ispisi_autocomplete(lista_reci)
            break


def ispisi_autocomplete(lista_reci):
    print("Pronadjene reci: ")
    for rec in lista_reci:
        print(rec)
    print("-----------------")


def pronadji_autocomplete(uneti_prefiks, broj_reci_za_prikaz):
    lista_reci = []
    prefiks_za_pretragu = uneti_prefiks.lower()
    for rec in reci_za_autocomplete:
        if (rec.startswith(prefiks_za_pretragu)) and (rec not in lista_reci):
            lista_reci.append(rec)
            if len(lista_reci) == int(broj_reci_za_prikaz):
                break
    return lista_reci


def unos_fraza():
    reci_fraze_lower = []
    fraza = input("Unesite frazu za pretrazivanje: ")
    reci_fraze = fraza.split(" ")
    for i in range(len(reci_fraze)):
        reci_fraze_lower.append(reci_fraze[i].lower())
    pretrazi_frazu(reci_fraze_lower)


def pretrazi_frazu(reci_fraze):
    recnik_pronadjenih_fraza = {}
    rec_za_pretragu = reci_fraze[0]
    for key in objekti_cvorova:
        trie_cvora = (objekti_cvorova[key]._element)[key]
        broj_unesene_reci_u_fajlu, okruzenje_unesene_reci_u_fajlu = trie_cvora.search(rec_za_pretragu)
        broj_fraza = 0
        lista_vec_obidjenih_okolina = []
        for jedno_okruzenje in okruzenje_unesene_reci_u_fajlu:
            if jedno_okruzenje not in lista_vec_obidjenih_okolina:
                lista_vec_obidjenih_okolina.append(jedno_okruzenje)
                for i in range(len(jedno_okruzenje)):
                    if jedno_okruzenje[i].lower() == rec_za_pretragu:
                        fraza_je_pronadjena = True
                        for j in range(1, len(reci_fraze)):
                            if i + j not in range(len(jedno_okruzenje)):
                                fraza_je_pronadjena = False
                                break
                            if reci_fraze[j] != jedno_okruzenje[i + j]:
                                fraza_je_pronadjena = False
                                break
                        if fraza_je_pronadjena:
                            broj_fraza += 1
        recnik_pronadjenih_fraza[key] = broj_fraza
    ispisi_rezultate_fraza(recnik_pronadjenih_fraza)


def ispisi_rezultate_fraza(recnik_pronadjenih_fraza):
    sortirani_recnik = OrderedDict(sorted(recnik_pronadjenih_fraza.items(), key=lambda x: x[1]))
    for key in sortirani_recnik:
        if sortirani_recnik[key] != 0:
            print("U fajlu " + key + ", uneta fraza se pojavila " + str(recnik_pronadjenih_fraza[key]) + " puta.")
            print("----------------------------------------------")


def unos_reci_pretrazivanja():
    # provera unosa
    while True:
        ispravan_unos = True
        reci_za_pretrazivanje_string = input("Unesite reci koje zelite da pretrazite u fajlovima: ")
        lista_reci = reci_za_pretrazivanje_string.split(" ")
        if lista_reci[0] == "AND" or lista_reci[0] == "OR" or lista_reci[0] == "NOT":
            print("Logicki operator ne moze biti na prvom mestu!")
            ispravan_unos = False
        elif lista_reci[len(lista_reci) - 1] == "AND" or lista_reci[len(lista_reci) - 1] == "OR" or lista_reci[
            len(lista_reci) - 1] == "NOT":
            print("Logicki operator ne moze biti na poslednjem mestu!")
            ispravan_unos = False
        else:
            for i in range(1, len(lista_reci)):
                j = i - 1
                if (lista_reci[j] == "AND" or lista_reci[j] == "OR" or lista_reci[j] == "NOT") and (
                        lista_reci[j + 1] == "AND" or lista_reci[j + 1] == "OR" or lista_reci[j + 1] == "NOT"):
                    print("Ne mogu dva logicka operatora stojati jedan pored drugog!")
                    ispravan_unos = False
                    break
        if ispravan_unos:
            break
    while True:
        broj_stranica_za_prikaz = input("Unesite broj stranica koje zelite da vam se prikazu na ekranu: ")
        if not broj_stranica_za_prikaz.isnumeric():
            print("Neispravan unos broja stranica za prikaz!")
        else:
            break
    # recnik_reci_za_pretrazivanje, odnos_logickih_operatora_i_reci = obradi_podatke(reci_za_pretrazivanje_string)
    spisak_reci_i_operatora = reci_za_pretrazivanje_string.split(" ")
    pretrazi_fajlove_standardno_pretrazivanje(spisak_reci_i_operatora, broj_stranica_za_prikaz)


def pretrazi_fajlove_standardno_pretrazivanje(spisak_reci_i_operatora, broj_stranica_za_prikaz):
    # HEURISTIKA: broj_unesene_reci_u_fajlu + broj_ivica + broj_unesene_reci_u_fajlovima_koji_linkuju
    # recnik_rezultata_heuristike: {rec:{naziv_fajla:[vrednost_heuristike, okolina_reci], ....}, rec2: {}}
    if ("AND" not in spisak_reci_i_operatora) and ("NOT" not in spisak_reci_i_operatora) and (
            "OR" not in spisak_reci_i_operatora):
        recnik_rezultata_heuristike = {}
        for rec in spisak_reci_i_operatora:
            recnik_svih_fajlova = {}
            for key in objekti_cvorova:
                recnik_svih_fajlova[key] = []
            recnik_rezultata_heuristike[rec] = recnik_svih_fajlova
        for rec in spisak_reci_i_operatora:
            for key1 in objekti_cvorova:
                rec_za_pretragu = rec.lower()
                trie_cvora = (objekti_cvorova[key1]._element)[key1]
                broj_unesene_reci_u_fajlu, okruzenje_unesene_reci_u_fajlu = trie_cvora.search(rec_za_pretragu)
                generator_ivica = graf_fajlova.incident_edges(objekti_cvorova[key1], False)
                broj_ivica = 0
                ivice = []
                for ivica in generator_ivica:
                    broj_ivica += 1
                    ivice.append(ivica)
                svi_cvorovi_ivica = {}
                for objekat_ivice in ivice:
                    cvor_pocetnog_fajla_ivice = objekat_ivice._origin
                    kljuc = list(cvor_pocetnog_fajla_ivice._element.keys())
                    vrednost = cvor_pocetnog_fajla_ivice._element[kljuc[0]]
                    svi_cvorovi_ivica[kljuc[0]] = vrednost
                broj_unesene_reci_u_fajlovima_koji_linkuju = 0
                for key2 in svi_cvorovi_ivica:
                    trie_cvora_ivice = svi_cvorovi_ivica[key2]
                    broj_unesene_reci_u_linkovanom_fajlu, okruzenje_unesene_reci_u_linkovanom_fajlu = trie_cvora_ivice.search(
                        rec_za_pretragu)
                    broj_unesene_reci_u_fajlovima_koji_linkuju += broj_unesene_reci_u_linkovanom_fajlu
                vrednost_heuristike = 50 * broj_unesene_reci_u_fajlu + broj_ivica + broj_unesene_reci_u_fajlovima_koji_linkuju
                if broj_unesene_reci_u_fajlu == 0:
                    recnik_rezultata_heuristike[rec][key1].append(0)
                else:
                    recnik_rezultata_heuristike[rec][key1].append(vrednost_heuristike)
                recnik_rezultata_heuristike[rec][key1].append(okruzenje_unesene_reci_u_fajlu)
        rec_nije_pronadjena = True
        for rec in recnik_rezultata_heuristike:
            for naziv_fajla in recnik_rezultata_heuristike[rec]:
                if recnik_rezultata_heuristike[rec][naziv_fajla][0] > 49:
                    rec_nije_pronadjena = False
                    break
            if rec_nije_pronadjena:
                predlozi_rec(rec)
                return
        prikazi_podatke_standardnog_pretrazivanja(recnik_rezultata_heuristike, broj_stranica_za_prikaz)
    else:
        lista_pocetnih_reci = [spisak_reci_i_operatora[0], spisak_reci_i_operatora[2]]
        if spisak_reci_i_operatora[1] == "AND":
            nazivi_fajlova = prva_provera_AND(lista_pocetnih_reci)
        elif spisak_reci_i_operatora[1] == "OR":
            nazivi_fajlova = prva_provera_OR(lista_pocetnih_reci)
        elif spisak_reci_i_operatora[1] == "NOT":
            nazivi_fajlova = prva_provera_NOT(lista_pocetnih_reci)
        if not nazivi_fajlova:
            print("Ne postoji nijedan fajl sa datim kriterijumima!")
            return
        else:
            if len(spisak_reci_i_operatora) > 3:
                for i in range(3, len(spisak_reci_i_operatora), 2):
                    operator = spisak_reci_i_operatora[i]
                    rec = spisak_reci_i_operatora[i + 1]
                    if operator == "AND":
                        nazivi_fajlova = provera_AND(nazivi_fajlova, rec)
                        if not nazivi_fajlova:
                            print("Ne postoji nijedan fajl sa datim kriterijumima!")
                            return
                    elif operator == "OR":
                        nazivi_fajlova = provera_OR(nazivi_fajlova, rec)
                        if not nazivi_fajlova:
                            print("Ne postoji nijedan fajl sa datim kriterijumima!")
                            return
                    elif operator == "NOT":
                        nazivi_fajlova = provera_NOT(nazivi_fajlova, rec)
                        if not nazivi_fajlova:
                            print("Ne postoji nijedan fajl sa datim kriterijumima!")
                            return
        lista_reci = []
        for i in range(0, len(spisak_reci_i_operatora), 2):
            lista_reci.append(spisak_reci_i_operatora[i])
        ispis_na_ekran_standardno_pretrazivanje_sa_operatorima(lista_reci, nazivi_fajlova, broj_stranica_za_prikaz)


def ispis_na_ekran_standardno_pretrazivanje_sa_operatorima(lista_reci, nazivi_fajlova, broj_stranica_za_prikaz):
    recnik_rezultata_heuristike = {}
    for rec in lista_reci:
        recnik_svih_fajlova = {}
        for key in objekti_cvorova:
            for naziv_fajla in nazivi_fajlova:
                if key == naziv_fajla:
                    recnik_svih_fajlova[key] = []
        recnik_rezultata_heuristike[rec] = recnik_svih_fajlova
    for rec in lista_reci:
        for key1 in objekti_cvorova:
            if key1 in recnik_rezultata_heuristike[rec]:
                rec_za_pretragu = rec.lower()
                trie_cvora = (objekti_cvorova[key1]._element)[key1]
                broj_unesene_reci_u_fajlu, okruzenje_unesene_reci_u_fajlu = trie_cvora.search(rec_za_pretragu)
                generator_ivica = graf_fajlova.incident_edges(objekti_cvorova[key1], False)
                broj_ivica = 0
                ivice = []
                for ivica in generator_ivica:
                    broj_ivica += 1
                    ivice.append(ivica)
                svi_cvorovi_ivica = {}
                for objekat_ivice in ivice:
                    cvor_pocetnog_fajla_ivice = objekat_ivice._origin
                    kljuc = list(cvor_pocetnog_fajla_ivice._element.keys())
                    vrednost = cvor_pocetnog_fajla_ivice._element[kljuc[0]]
                    svi_cvorovi_ivica[kljuc[0]] = vrednost
                broj_unesene_reci_u_fajlovima_koji_linkuju = 0
                for key2 in svi_cvorovi_ivica:
                    trie_cvora_ivice = svi_cvorovi_ivica[key2]
                    broj_unesene_reci_u_linkovanom_fajlu, okruzenje_unesene_reci_u_linkovanom_fajlu = trie_cvora_ivice.search(
                        rec_za_pretragu)
                    broj_unesene_reci_u_fajlovima_koji_linkuju += broj_unesene_reci_u_linkovanom_fajlu
                vrednost_heuristike = 50 * broj_unesene_reci_u_fajlu + broj_ivica + broj_unesene_reci_u_fajlovima_koji_linkuju
                if broj_unesene_reci_u_fajlu == 0:
                    recnik_rezultata_heuristike[rec][key1].append(0)
                else:
                    recnik_rezultata_heuristike[rec][key1].append(vrednost_heuristike)
                recnik_rezultata_heuristike[rec][key1].append(okruzenje_unesene_reci_u_fajlu)
                # recnik_rezultata_heuristike: {rec:{naziv_fajla:[vrednost_heuristike, okolina_reci], ....}, rec2: {}}
    rec_nije_pronadjena = True
    for rec in recnik_rezultata_heuristike:
        for naziv_fajla in recnik_rezultata_heuristike[rec]:
            if recnik_rezultata_heuristike[rec][naziv_fajla][0] > 220:
                rec_nije_pronadjena = False
                break
        if rec_nije_pronadjena:
            predlozi_rec(rec)
            return
    prikazi_podatke_standardnog_pretrazivanja(recnik_rezultata_heuristike, broj_stranica_za_prikaz)


def predlozi_rec(rec):
    lista_reci_predloga = []
    rec_provere = rec[:-1]
    rec_provere = rec_provere.lower()
    for rec in reci_za_autocomplete:
        if rec.lower().startswith(rec_provere):
            lista_reci_predloga.append(rec)
    if len(rec_provere) == 1:
        return lista_reci_predloga
    if not lista_reci_predloga:
        predlozi_rec(rec_provere)
    else:
        print("Da li ste mozda mislili na sledecu/e rec/i: ")
        for rec in lista_reci_predloga:
            print(rec)
        return


def provera_AND(nazivi_fajlova, rec):
    nazivi_fajlova_za_datu_rec = []
    fajlovi_ispunjavajucih_kriterijuma = []
    for key in objekti_cvorova:
        rec = rec.lower()
        trie_cvora = (objekti_cvorova[key]._element)[key]
        broj_unesene_reci_u_fajlu, okruzenje_unesene_reci_u_fajlu = trie_cvora.search(rec)
        if broj_unesene_reci_u_fajlu != 0:
            nazivi_fajlova_za_datu_rec.append(key)
    for naziv_fajla in nazivi_fajlova_za_datu_rec:
        if naziv_fajla in nazivi_fajlova:
            fajlovi_ispunjavajucih_kriterijuma.append(naziv_fajla)
    return fajlovi_ispunjavajucih_kriterijuma


def provera_OR(nazivi_fajlova, rec):
    nazivi_fajlova_za_datu_rec = []
    for key in objekti_cvorova:
        rec = rec.lower()
        trie_cvora = (objekti_cvorova[key]._element)[key]
        broj_unesene_reci_u_fajlu, okruzenje_unesene_reci_u_fajlu = trie_cvora.search(rec)
        if broj_unesene_reci_u_fajlu != 0:
            nazivi_fajlova_za_datu_rec.append(key)
    for naziv_fajla in nazivi_fajlova_za_datu_rec:
        if naziv_fajla not in nazivi_fajlova:
            nazivi_fajlova.append(naziv_fajla)
    return nazivi_fajlova


def provera_NOT(nazivi_fajlova, rec):
    nazivi_fajlova_za_datu_rec = []
    fajlovi_ispunjavajucih_kriterijuma = []
    for key in objekti_cvorova:
        rec = rec.lower()
        trie_cvora = (objekti_cvorova[key]._element)[key]
        broj_unesene_reci_u_fajlu, okruzenje_unesene_reci_u_fajlu = trie_cvora.search(rec)
        if broj_unesene_reci_u_fajlu == 0:
            nazivi_fajlova_za_datu_rec.append(key)
    for naziv_fajla in nazivi_fajlova_za_datu_rec:
        if naziv_fajla in nazivi_fajlova:
            fajlovi_ispunjavajucih_kriterijuma.append(naziv_fajla)
    return fajlovi_ispunjavajucih_kriterijuma


def prva_provera_AND(lista_reci):
    lista_fajlova_prve_reci = []
    lista_fajlova_druge_reci = []
    povratna_lista_fajlova = []
    redni_broj_reci = 0
    for rec in lista_reci:
        redni_broj_reci += 1
        for key in objekti_cvorova:
            rec_za_pretragu = rec.lower()
            trie_cvora = (objekti_cvorova[key]._element)[key]
            broj_unesene_reci_u_fajlu, okruzenje_unesene_reci_u_fajlu = trie_cvora.search(rec_za_pretragu)
            if broj_unesene_reci_u_fajlu != 0 and redni_broj_reci == 1:
                lista_fajlova_prve_reci.append(key)
            elif broj_unesene_reci_u_fajlu != 0 and redni_broj_reci == 2:
                lista_fajlova_druge_reci.append(key)
    for fajl1 in lista_fajlova_prve_reci:
        for fajl2 in lista_fajlova_druge_reci:
            if (fajl1 == fajl2) and (fajl1 not in povratna_lista_fajlova):
                povratna_lista_fajlova.append(fajl1)
    return povratna_lista_fajlova


def prva_provera_OR(lista_reci):
    lista_fajlova_prve_reci = []
    lista_fajlova_druge_reci = []
    povratna_lista_fajlova = []
    redni_broj_reci = 0
    for rec in lista_reci:
        redni_broj_reci += 1
        for key in objekti_cvorova:
            rec_za_pretragu = rec.lower()
            trie_cvora = (objekti_cvorova[key]._element)[key]
            broj_unesene_reci_u_fajlu, okruzenje_unesene_reci_u_fajlu = trie_cvora.search(rec_za_pretragu)
            if broj_unesene_reci_u_fajlu != 0 and redni_broj_reci == 1:
                lista_fajlova_prve_reci.append(key)
            elif broj_unesene_reci_u_fajlu != 0 and redni_broj_reci == 2:
                lista_fajlova_druge_reci.append(key)
    for fajl1 in lista_fajlova_prve_reci:
        if fajl1 not in povratna_lista_fajlova:
            povratna_lista_fajlova.append(fajl1)
    for fajl2 in lista_fajlova_druge_reci:
        if fajl2 not in povratna_lista_fajlova:
            povratna_lista_fajlova.append(fajl2)
    return povratna_lista_fajlova


def prva_provera_NOT(lista_reci):
    lista_fajlova_prve_reci = []
    lista_fajlova_druge_reci = []
    povratna_lista_fajlova = []
    redni_broj_reci = 0
    for rec in lista_reci:
        redni_broj_reci += 1
        for key in objekti_cvorova:
            rec_za_pretragu = rec.lower()
            trie_cvora = (objekti_cvorova[key]._element)[key]
            broj_unesene_reci_u_fajlu, okruzenje_unesene_reci_u_fajlu = trie_cvora.search(rec_za_pretragu)
            if broj_unesene_reci_u_fajlu != 0 and redni_broj_reci == 1:
                lista_fajlova_prve_reci.append(key)
            elif broj_unesene_reci_u_fajlu == 0 and redni_broj_reci == 2:
                lista_fajlova_druge_reci.append(key)
    for fajl1 in lista_fajlova_prve_reci:
        for fajl2 in lista_fajlova_druge_reci:
            if (fajl1 == fajl2) and (fajl1 not in povratna_lista_fajlova):
                povratna_lista_fajlova.append(fajl1)
    return povratna_lista_fajlova


def prikazi_podatke_standardnog_pretrazivanja(recnik_rezultata_heuristike, broj_stranica_za_prikaz):
    redni_broj_rezultata = 1
    recnik_ukupne_heuristike = {}
    lista_vec_ucitanih_fajlova = []
    for rec1 in recnik_rezultata_heuristike:
        for naziv_fajla1 in recnik_rezultata_heuristike[rec1]:
            recnik_ukupne_heuristike[naziv_fajla1] = 0
        break
    for rec2 in recnik_rezultata_heuristike:
        for naziv_fajla2 in recnik_rezultata_heuristike[rec2]:
            recnik_ukupne_heuristike[naziv_fajla2] += recnik_rezultata_heuristike[rec2][naziv_fajla2][0]
    lista_rezultata_heuristike = list(recnik_ukupne_heuristike.values())
    ispisuj_sledecih_n_resenja = True
    while ispisuj_sledecih_n_resenja:
        for i in range(int(broj_stranica_za_prikaz)):
            if int(broj_stranica_za_prikaz) > len(lista_rezultata_heuristike):
                print("Nemoguce prikazati naredne " + broj_stranica_za_prikaz + " stranice!")
                return
            max_heuristika = max(lista_rezultata_heuristike)
            lista_rezultata_heuristike.remove(max_heuristika)
            for naziv_fajla in recnik_ukupne_heuristike:
                if recnik_ukupne_heuristike[
                    naziv_fajla] == max_heuristika and naziv_fajla not in lista_vec_ucitanih_fajlova:
                    fajl_trenutne_max_heuristike = naziv_fajla
                    lista_vec_ucitanih_fajlova.append(naziv_fajla)
                    break
            broj_prolazaka_kroz_fajlove = 0
            for rec3 in recnik_rezultata_heuristike:
                for naziv_fajla3 in recnik_rezultata_heuristike[rec3]:
                    if fajl_trenutne_max_heuristike == naziv_fajla3:
                        broj_prolazaka_kroz_fajlove += 1
                        isecci_za_ispis = ""
                        lista_reci_isecaka = recnik_rezultata_heuristike[rec3][naziv_fajla3][1]
                        for lista in lista_reci_isecaka:
                            for i in range(len(lista)):
                                if lista[i].lower() == rec3:
                                    lista[i] = "==" + lista[i].upper() + "=="
                                if i == len(lista) - 1:
                                    isecci_za_ispis += lista[i] + "\n"
                                else:
                                    isecci_za_ispis += lista[i] + " "
                            isecci_za_ispis += "--------------------------------------------------------------\n"
                        if not isecci_za_ispis:
                            isecci_za_ispis += "Ne postoji zapis ove reci u datom fajlu," \
                                               " ostale reci imaju ogromnu prednost u heuristici ili je operator OR koristen"
                        print("+++++++++++++++++++++++++++++++++++")
                        print("Rec:" + rec3)
                        print("Redni broj rezultata: " + str(redni_broj_rezultata) + ".")
                        print("Fajl: " + fajl_trenutne_max_heuristike)
                        print("Isecci svih pojavljivanja reci:\n" + isecci_za_ispis)
                        if broj_prolazaka_kroz_fajlove == len(recnik_rezultata_heuristike):
                            redni_broj_rezultata += 1
        while True:
            odabir = input("Unesite 0 ako zelite da izadjete iz ispisa, 1 ako zelite prikaz narednih N ispisa: ")
            if odabir == "0":
                ispisuj_sledecih_n_resenja = False
                break
            if odabir == "1":
                break
            else:
                print("Neispravan unos!")


def ucitaj_sve_fajlove(putanja):
    # ucitavanje svih HTML fajlova
    # stavljanje u Graph i Trie

    for fajl in os.listdir(putanja):
        if fajl.startswith("."):
            continue
        if fajl.endswith(".html"):
            putanja_fajla = putanja + SEPARATOR + fajl
            lista_linkova_fajla, lista_reci_fajla = parser.parse(putanja_fajla)
            if not lista_reci_fajla:  # ako je prazan fajl
                continue
            dopuni_autocomplete(lista_reci_fajla)
            naziv_fajla = vrati_naziv_fajla(putanja_fajla)

            # vrati podatke za Edges (ivice)
            nazivi_linkova_fajlova = vrati_nazive_linkova_fajla(lista_linkova_fajla)
            linkovi_fajlova[naziv_fajla] = nazivi_linkova_fajlova

            # stvori Trie za date reci
            trie_fajla = popuni_trie_datog_fajla(lista_reci_fajla, naziv_fajla)

            # Vertex (cvor)
            elemenat_cvora = {naziv_fajla: trie_fajla}
            cvor = graf_fajlova.insert_vertex(elemenat_cvora)
            objekti_cvorova[naziv_fajla] = cvor
        elif not os.path.isfile(putanja + SEPARATOR + fajl) and not (
                re.search("^.*.(js|JS|inv|INV|doc|DOC|pdf|PDF)$", fajl)):
            ucitaj_sve_fajlove(putanja + SEPARATOR + fajl)


def upisi_edgeove():
    print("---------------")
    print("Upisani cvorovi!")

    # upis Edge-ova
    for key in linkovi_fajlova:
        for naziv_linka in linkovi_fajlova[key]:
            if naziv_linka in objekti_cvorova:
                graf_fajlova.insert_edge(objekti_cvorova[key], objekti_cvorova[naziv_linka], naziv_linka)

    print("Upisane ivice!")
    print("---------------")
    print()


def popuni_trie_datog_fajla(lista_reci_fajla, naziv_fajla):
    trie = Trie()
    for i in range(len(lista_reci_fajla)):  # mora po indeksu da bih znao gde je data rec u listi
        if not lista_reci_fajla[i]:
            continue
        rec = lista_reci_fajla[i].lower()
        lista_okruzenja_reci = napravi_okruzenje_date_reci(lista_reci_fajla, i)
        trie.insert(rec, naziv_fajla, lista_okruzenja_reci)
    return trie


def dopuni_autocomplete(lista_reci):
    for rec in lista_reci:
        if rec.lower() not in reci_za_autocomplete:
            reci_za_autocomplete.append(rec.lower())


def napravi_okruzenje_date_reci(lista_reci_fajla, i):
    lista_okruzenje_reci = []

    # okruzenje reci je lista reci koje su oko te reci u HTML fajlu, povratna vrednost - lista reci

    if i in range(len(lista_reci_fajla) - 20, len(lista_reci_fajla)):
        for j in range(len(lista_reci_fajla) - 20, len(lista_reci_fajla)):
            lista_okruzenje_reci.append(lista_reci_fajla[j])
        return lista_okruzenje_reci

    else:
        for j in range(i, i + 20):
            lista_okruzenje_reci.append(lista_reci_fajla[j])
        return lista_okruzenje_reci


def vrati_nazive_linkova_fajla(lista_linkova_fajla):
    nazivi_linkova = []
    for link in lista_linkova_fajla:
        podaci_linka = link.split(SEPARATOR)
        if podaci_linka[-1] not in nazivi_linkova:
            nazivi_linkova.append(podaci_linka[-1])
    return nazivi_linkova


def vrati_naziv_fajla(putanja_fajla):
    podaci_putanje_fajla = putanja_fajla.split(SEPARATOR)
    return podaci_putanje_fajla[-1]


if __name__ == '__main__':
    pocetak_programa()