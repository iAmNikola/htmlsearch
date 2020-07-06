class TrieNode:
    def __init__(self, value):
        self.value = value
        self.children = {}
        self.end_here = False
        self.file_path = None
        self.surroundings = []
        self.broj_ponavljanja = 0


class Trie:
    def __init__(self):
        self.root = TrieNode(None)

    def insert(self, word, file_path, surroundings):
        # ubaci rec u trie, argument: word, povratna_vrednost: void
        parent = self.root
        for i, char in enumerate(word):
            if char not in parent.children:
                parent.children[char] = TrieNode(char)
            parent = parent.children[char]
            if i == len(word) - 1:
                parent.end_here = True
                # ovako nesto da se zna u kojem je fajlu?
                parent.file_path = file_path
                # ovako nesto da se zna sta je oko te reci
                parent.surroundings.append(surroundings)
                parent.broj_ponavljanja += 1

    def search(self, word):
        # pronadji rec u trie, argument: word, povratna_vrednost: boolean
        parent = self.root
        for char in word:
            if char not in parent.children:
                return 0, []
            parent = parent.children[char]
        return parent.broj_ponavljanja, parent.surroundings

    def starts_with(self, prefix):
        # autocomplete
        parent = self.root
        for char in prefix:
            if char not in parent.children:
                return False
            parent = parent.children[char]
        return True
