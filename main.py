from html_parser import *
from trie import Trie
from graph import Graph
from _collections import OrderedDict


# Svaki cvor (VERTEX) ce kao svoj elemenat imati recnik, ciji ce kljuc biti naziv fajla, a vrednost ce biti njegov Trie
# Svaki TrieNode, pored reci, ce sadrzati i ime fajla iz kojeg je rec izvucena, kao i listu koja predstavlja okruzenje te reci
# Prvo se moraju stvoriti svi Vertexi (cvorovi), a zatim se spoje sa Edges
# linkovi_fajlova - kljuc: naziv_fajla, vrednost: lista svih naziva linkova iz tog fajla
# objekti_cvorova - kljuc: naziv_fajla, vrednost: objekat Vertex za taj fajl
# broj linkova u nekom fajlu je 218, 217 ??!?!?!
# moguce je koriscenje graf.vertices() umesto objekti_cvorova, kasno sam primetio da ta metoda postoji :/

GREEN = "\033[92m"
ENDC = '\033[0m'
words_autocomplete = []
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEPARATOR = os.path.sep
parser = Parser()
# Usmeren graf
graf_fajlova = Graph(True)
file_links_dict = {}
objekti_cvorova = {}


def start_app():
    load_files(BASE_DIR + SEPARATOR + "python-3.8.3-docs-html")
    fill_edges()
    print("Broj cvorova je : ", graf_fajlova.vertex_count())
    print("Broj ivica je : ", graf_fajlova.edge_count())
    cui()


def load_files(path):
    # ucitavanje svih HTML fajlova
    # stavljanje u Graph i Trie

    for file in os.listdir(path):
        if file.startswith("."):
            continue
        if file.endswith(".html"):
            filepath = path + SEPARATOR + file
            file_links, word_list = parser.parse(filepath)
            if not word_list:  # ako je prazan fajl
                continue
            fill_autocomplete(word_list)
            filename = return_filename(filepath)

            # vrati podatke za Edges (ivice)
            link_filenames = get_link_filenames(file_links)
            file_links_dict[filename] = link_filenames

            # stvori Trie za date reci
            file_trie = fill_trie(word_list, filename)

            # Vertex (cvor)
            vertex_elem = {filename: file_trie}
            vertex = graf_fajlova.insert_vertex(vertex_elem)
            objekti_cvorova[filename] = vertex
        elif not os.path.isfile(path + SEPARATOR + file) and not (re.search("^.*.(js|JS|inv|INV|doc|DOC|pdf|PDF)$", file)):
            load_files(path + SEPARATOR + file)

def fill_autocomplete(word_list):
    for word in word_list:
        if word.lower() not in words_autocomplete:
            words_autocomplete.append(word.lower())

def return_filename(filepath):
    split_filepath = filepath.split(SEPARATOR)
    return split_filepath[-1]

def get_link_filenames(file_links):
    link_filename = []
    for link in file_links:
        split_link = link.split(SEPARATOR)
        if split_link[-1] not in link_filename:
            link_filename.append(split_link[-1])
    return link_filename

def fill_trie(word_list, filename):
    trie = Trie()
    for i in range(len(word_list)):  # mora po indeksu da bih znao gde je data rec u listi
        if not word_list[i]:
            continue
        word = word_list[i].lower()
        surrounding_words = get_surrounding_words(word_list, i)
        trie.insert(word, filename, surrounding_words)
    return trie

def get_surrounding_words(word_list, index):
    i = index
    surrounding_words = []

    # okruzenje reci je lista reci koje su oko te reci u HTML fajlu, povratna vrednost - lista reci

    if i in range(len(word_list) - 20, len(word_list)):
        for j in range(len(word_list) - 20, len(word_list)):
            surrounding_words.append(word_list[j])
        return surrounding_words

    else:
        for j in range(i, i + 20):
            surrounding_words.append(word_list[j])
        return surrounding_words


def fill_edges():
    for key in file_links_dict.keys():
        for link_filename in file_links_dict[key]:
            if link_filename in objekti_cvorova:
                graf_fajlova.insert_edge(objekti_cvorova[key], objekti_cvorova[link_filename], link_filename)


def cui():
    while True:
        menu_print()
        func = choose_option()
        func()

def menu_print():
    print("1. Standardno pretrazivanje (Unos reci i logickih operatera)\n"
          "2. Upotreba fraza\n"
          "3. Autocomplete\n"
          "4. Izlazak")

def choose_option():
    choices = {"1": search_input,
               "2": phrase_input,
               "3": autocomplete_input,
               "4": quit
               }
    while True:
        choice = input("Izaberite opciju: ")
        attribute = choices.get(choice)
        if attribute:
            return attribute
        else:
            print("{0} nije validan izbor.".format(choice))


def phrase_input():
    words = []
    phrase = input("Unesite frazu za pretrazivanje: ")
    phrase_words = phrase.split(" ")
    for i in range(len(phrase_words)):
        words.append(phrase_words[i].lower())
    search_phrase(words)


def search_phrase(words):
    found_phrases = {}
    search_word = words[0]
    for key in objekti_cvorova:
        vertex_trie = objekti_cvorova[key]._element[key]
        _, surrounding_words = vertex_trie.search(search_word)
        num_phrases = 0
        iterated_surrounding = []
        for surr_word in surrounding_words:
            if surr_word not in iterated_surrounding:
                iterated_surrounding.append(surr_word)
                for i in range(len(surr_word)):
                    if surr_word[i].lower() == search_word:
                        phrase_found = True
                        for j in range(1, len(words)):
                            if i + j not in range(len(surr_word)):
                                phrase_found = False
                                break
                            if words[j] != surr_word[i + j]:
                                phrase_found = False
                                break
                        if phrase_found:
                            num_phrases += 1
        found_phrases[key] = num_phrases
    print_phrase_result(found_phrases)


def print_phrase_result(found_phrases):
    sorted_dict = OrderedDict(sorted(found_phrases.items(), key=lambda x: x[1]))
    for key in sorted_dict:
        if sorted_dict[key] != 0:
            print("U fajlu " + key + ", uneta fraza se pojavila " + str(found_phrases[key]) + " puta.")
            print("----------------------------------------------")


def search_input():
    while True:
        valid_input = True
        words = input("Unesite reci koje zelite da pretrazite u fajlovima: ")
        word_list = words.split(" ")
        if word_list[0] in ["AND", "OR", "NOT"]:
            print("Logicki operator ne moze biti na prvom mestu!")
            continue
        elif word_list[-1] in ["AND", "OR", "NOT"]:
            print("Logicki operator ne moze biti na poslednjem mestu!")
            continue
        else:
            for i in range(len(word_list)-1):
                j = i + 1
                if (word_list[i] in ["AND", "OR", "NOT"]) and (word_list[j] in ["AND", "OR", "NOT"]):
                    print("Dva logicka operatora ne mogu stojati jedan pored drugog!")
                    valid_input = False
                    break
        if valid_input:
            break
    while True:
        n_pages = input("Unesite broj stranica koje zelite da vam se prikazu: ")
        if not n_pages.isnumeric():
            print("Neispravan unos!")
            continue
        break
    search_words_in_files(word_list, n_pages)

def search_words_in_files(word_list, n_pages):
    # HEURISTIKA: 50*broj ponavljanja reci u fajlu + broj ivica + broj_unesene_reci_u_fajlovima_koji_linkuju
    # recnik_rezultata_heuristike: {rec:{naziv_fajla:[vrednost_heuristike, okolina_reci], ....}, rec2: {}}
    if ("AND" not in word_list) and ("NOT" not in word_list) and ("OR" not in word_list):
        heuristics = {}
        for word in word_list:
            all_files = {}
            for key in objekti_cvorova:
                all_files[key] = []
            heuristics[word] = all_files
        for word in word_list:
            for k in objekti_cvorova:
                search_word = word.lower()
                vertex_trie = objekti_cvorova[k]._element[k]
                num_repeats, surrounding_words = vertex_trie.search(search_word)
                vertex_edges = graf_fajlova.incident_edges(objekti_cvorova[k], False)
                num_edges = 0
                edges = []
                for edge in vertex_edges:
                    num_edges += 1
                    edges.append(edge)
                edge_vertex = {}
                for edge in edges:
                    file_vertex = edge._origin
                    key = list(file_vertex._element.keys())
                    value = file_vertex._element[key[0]]  # Trie
                    edge_vertex[key[0]] = value
                num_repeats_all_link_files = 0
                for key1 in edge_vertex.keys():
                    link_file_trie = edge_vertex[key1]
                    num_repeats_link_file, _ = link_file_trie.search(search_word)
                    num_repeats_all_link_files += num_repeats_link_file
                heuristic_value = 50 * num_repeats + num_edges + num_repeats_all_link_files
                if num_repeats == 0:
                    heuristics[word][k].append(0)
                else:
                    heuristics[word][k].append(heuristic_value)
                heuristics[word][k].append(surrounding_words)
        word_not_found = True
        for word in heuristics:
            for filename in heuristics[word]:
                if heuristics[word][filename][0] > 50:
                    word_not_found = False
                    break
            if word_not_found:
                suggest_word(word)
                return
        show_search_data(heuristics, n_pages)
    else:
        operand_words = [word_list[0], word_list[2]]
        if word_list[1] == "AND":
            filenames = first_AND_check(operand_words)
        elif word_list[1] == "OR":
            filenames = first_OR_check(operand_words)
        else:
            filenames = first_NOT_check(operand_words)
        if not filenames:
            print("Ne postoji nijedan fajl sa datim kriterijumima!")
            return
        else:
            if len(word_list) > 3:
                for i in range(3, len(word_list), 2):
                    operator = word_list[i]
                    word = word_list[i + 1]
                    if operator == "AND":
                        filenames = AND_check(filenames, word)
                        if not filenames:
                            print("Ne postoji nijedan fajl sa datim kriterijumima!")
                            return
                    elif operator == "OR":
                        filenames = OR_check(filenames, word)
                        if not filenames:
                            print("Ne postoji nijedan fajl sa datim kriterijumima!")
                            return
                    elif operator == "NOT":
                        filenames = NOT_check(filenames, word)
                        if not filenames:
                            print("Ne postoji nijedan fajl sa datim kriterijumima!")
                            return
        words = []
        for i in range(0, len(word_list), 2):
            words.append(word_list[i])
        show_search_data_with_operators(words, filenames, n_pages)

def show_search_data(heuristic, n_pages):
    result_num = 1
    total_heuristic = {}
    loaded_filenames = []
    for key in heuristic:
        for filename in heuristic[key]:
            total_heuristic[filename] = 0
        break
    for key in heuristic:
        for filename in heuristic[key]:
            total_heuristic[filename] += heuristic[key][filename][0]
    heuristic_value_list = list(total_heuristic.values())
    print_n = True
    while print_n:
        for i in range(int(n_pages)):
            if int(n_pages) > len(heuristic_value_list):
                print("Nemoguce prikazati naredne " + n_pages + " stranice!")
                return
            max_heuristika = max(heuristic_value_list)
            heuristic_value_list.remove(max_heuristika)
            for filename in total_heuristic:
                if total_heuristic[filename] == max_heuristika and filename not in loaded_filenames:
                    max_heuristic_file = filename
                    loaded_filenames.append(filename)
                    break
            num_iter_files = 0
            for word in heuristic:
                for filename in heuristic[word]:
                    if max_heuristic_file == filename:
                        num_iter_files += 1
                        print_string = ""
                        surrounding_words = heuristic[word][filename][1]
                        for surr_word in surrounding_words:
                            for j in range(len(surr_word)):
                                if surr_word[j].lower() == word:
                                    surr_word[j] = GREEN + surr_word[j].upper() + ENDC
                                if j == len(surr_word) - 1:
                                    print_string += surr_word[j] + "\n"
                                else:
                                    print_string += surr_word[j] + " "
                            print_string += "--------------------------------------------------------------\n"
                        if not print_string:
                            print_string += "Ne postoji zapis ove reci u datom fajlu," \
                                               " ostale reci imaju ogromnu prednost u heuristici ili je operator OR koristen"
                        print("+++++++++++++++++++++++++++++++++++")
                        print("Rec:" + word)
                        print("Redni broj rezultata: " + str(result_num) + ".")
                        print("Fajl: " + max_heuristic_file)
                        print("Isecci svih pojavljivanja reci:\n" + print_string)
                        if num_iter_files == len(heuristic):
                            result_num += 1
        while True:
            choice = input("Unesite 0 ako zelite da izadjete iz ispisa, 1 ako zelite prikaz narednih N ispisa: ")
            if choice == "0":
                print_n = False
                break
            if choice == "1":
                break
            else:
                print("Neispravan unos!")

def show_search_data_with_operators(words, filenames, n_pages):
    heuristics = {}
    for word in words:
        all_files_dict = {}
        for key in objekti_cvorova:
            for filename in filenames:
                if key == filename:
                    all_files_dict[key] = []
        heuristics[word] = all_files_dict
    for word in words:
        for k in objekti_cvorova:
            if k in heuristics[word]:
                search_word = word.lower()
                vertex_trie = objekti_cvorova[k]._element[k]
                num_repeats, surrounding_words = vertex_trie.search(search_word)
                vertex_edges = graf_fajlova.incident_edges(objekti_cvorova[k], False)
                num_edges = 0
                edges = []
                for edge in vertex_edges:
                    num_edges += 1
                    edges.append(edge)
                edge_vertex = {}
                for edge in edges:
                    file_vertex = edge._origin
                    key = list(file_vertex._element.keys())
                    value = file_vertex._element[key[0]]
                    edge_vertex[key[0]] = value
                num_repeats_all_link_files = 0
                for key2 in edge_vertex:
                    link_file_trie = edge_vertex[key2]
                    num_repeats_link_file, _ = link_file_trie.search(search_word)
                    num_repeats_all_link_files += num_repeats_link_file
                heuristic_value = 50 * num_repeats + num_edges + num_repeats_all_link_files
                if num_repeats == 0:
                    heuristics[word][k].append(0)
                else:
                    heuristics[word][k].append(heuristic_value)
                heuristics[word][k].append(surrounding_words)
                # heuristics: {rec:{naziv_fajla:[vrednost_heuristike, okolina_reci], ....}, rec2: {}}
    word_not_found = True
    for word in heuristics:
        for filename in heuristics[word]:
            if heuristics[word][filename][0] > 220:
                word_not_found = False
                break
        if word_not_found:
            suggest_word(word)
            return
    show_search_data(heuristics, n_pages)


def suggest_word(word):
    word_suggestions = []
    check_word = word[:-1]
    check_word = check_word.lower()
    for word in words_autocomplete:
        if word.lower().startswith(check_word):
            word_suggestions.append(word)
    if len(check_word) == 1:
        return word_suggestions
    if not word_suggestions:
        suggest_word(check_word)
    else:
        print("Da li ste mozda mislili na ove reci: ")
        for i in range(len(word_suggestions)):
            if i == 6:
                break
            print("    - "+word_suggestions[i])
        return


def first_AND_check(operand_words):
    word0_files = []
    word1_files = []
    result_files = []
    word_index = 0
    for word in operand_words:
        word_index += 1
        for key in objekti_cvorova:
            search_word = word.lower()
            vertex_trie = objekti_cvorova[key]._element[key]
            num_repeats, _ = vertex_trie.search(search_word)
            if num_repeats != 0 and word_index == 1:
                word0_files.append(key)
            elif num_repeats != 0 and word_index == 2:
                word1_files.append(key)
    for filename0 in word0_files:
        for filename1 in word1_files:
            if (filename0 == filename1) and (filename0 not in result_files):
                result_files.append(filename0)
    return result_files

def AND_check(filenames, word):
    files_for_word = []
    result_files = []
    for key in objekti_cvorova:
        word = word.lower()
        vertex_trie = objekti_cvorova[key]._element[key]
        num_repeats, _ = vertex_trie.search(word)
        if num_repeats != 0:
            files_for_word.append(key)
    for filename in files_for_word:
        if filename in filenames:
            result_files.append(filename)
    return result_files


def first_OR_check(operand_words):
    word0_files = []
    word1_files = []
    result_files = []
    word_index = 0
    for word in operand_words:
        word_index += 1
        for key in objekti_cvorova:
            search_word = word.lower()
            vertex_trie = objekti_cvorova[key]._element[key]
            num_repeats, _ = vertex_trie.search(search_word)
            if num_repeats != 0 and word_index == 1:
                word0_files.append(key)
            elif num_repeats != 0 and word_index == 2:
                word1_files.append(key)
    for filename in word0_files:
        if filename not in result_files:
            result_files.append(filename)
    for filename in word1_files:
        if filename not in result_files:
            result_files.append(filename)
    return result_files

def OR_check(filenames, word):
    files_for_word = []
    for key in objekti_cvorova:
        word = word.lower()
        vertex_trie = objekti_cvorova[key]._element[key]
        num_repeats, _ = vertex_trie.search(word)
        if num_repeats != 0:
            files_for_word.append(key)
    for filename in files_for_word:
        if filename not in filenames:
            filenames.append(filename)
    return filenames


def first_NOT_check(operand_words):
    word0_files = []
    word1_files = []
    result_files = []
    word_index = 0
    for word in operand_words:
        word_index += 1
        for key in objekti_cvorova:
            search_word = word.lower()
            vertex_trie = objekti_cvorova[key]._element[key]
            num_repeats, _ = vertex_trie.search(search_word)
            if num_repeats != 0 and word_index == 1:
                word0_files.append(key)
            elif num_repeats == 0 and word_index == 2:
                word1_files.append(key)
    for filename0 in word0_files:
        for filename1 in word1_files:
            if (filename0 == filename1) and (filename0 not in result_files):
                result_files.append(filename0)
    return result_files

def NOT_check(filenames, word):
    files_for_word = []
    result_files = []
    for key in objekti_cvorova:
        word = word.lower()
        vertex_trie = objekti_cvorova[key]._element[key]
        num_repeats, _ = vertex_trie.search(word)
        if num_repeats == 0:
            files_for_word.append(key)
    for filename in files_for_word:
        if filename in filenames:
            result_files.append(filename)
    return result_files


def autocomplete_input():
    prefix = input("Unesite prefiks za koji hocete da se obavi autocomplete: ")
    while True:
        show_n_words = input("Unesite koliko reci zelite da vam se prikaze: ")
        if not show_n_words.isnumeric():
            print("Neispravan unos broja reci.")
        else:
            words = find_autocomplete(prefix, show_n_words)
            print_autocomplete(words)
            break

def find_autocomplete(prefix, suggestion_limit):
    words_suggest = []
    prefix = prefix.lower()
    for word in words_autocomplete:
        if (word.startswith(prefix)) and (word not in words_suggest):
            words_suggest.append(word)
            if len(words_suggest) == int(suggestion_limit):
                break
    return words_suggest

def print_autocomplete(word_list):
    print("Pronadjene reci: ")
    for word in word_list:
        print("    - " + word)
    print()


if __name__ == '__main__':
    start_app()
