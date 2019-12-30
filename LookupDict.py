import pandas as pd
import re


letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2',
           '3','4','5','6','7','8','9',',',' ','/','.','\n']
letters_num = len(letters)
digits = ['1','2','3','4','5','6','7','8','9','0']



'''
@Params:
    technique: byDomain|byIp
    machine: server|client 
    words_file_path: path to the words or domains you work with
@Methods:
    transform(word):
                    @Params:  word|domain_name|character
                    @Return the matching value in dict according to the usecase.( e.g client converting a char to domain_name )
@Description: create the LookupDict object on the dns server or client and choose the current 
              usecase (byIp and byDomain). LookupDict will create the dict in the right way
'''
class LookupDict:
    def __init__(self,machine,technique,words_file_path):
        if machine == "client" and technique == "byDomain":
            self.dict = LettersWordsLookup(words_file_path)
        if machine == "client" and technique == "byIp":
             self.dict = LettersDomainsLookup(words_file_path)
        if machine == "server" and technique == "byDomain":
            self.dict = WordsLettersLookup(words_file_path)
        # if machine == "server" and technique == "byIp":
        #     self.dict = WordsLettersLookup()
    def transform(self,word):
        return self.dict.transform(word)


class LettersDomainsLookup:
    def __init__(self, domains_path):
        self.domains_path = domains_path
        self.letters_domains_dict = dict()
        domains = pd.read_csv(self.domains_path, sep=",", names=["Idx", "domains"])
        for i in range(0, letters_num):
            self.letters_domains_dict[letters[i]] = domains["domains"][i].strip(" ").translate(str.maketrans('', '', '1234567890'))
        # print(self.letters_domains_dict)
        # print(self.letters_occurences_dict)

    def transform(self, letter):
        try:
            domain = self.letters_domains_dict[letter].split(".")
            domain_name = domain[0]
            new_domain_name = domain_name
            new_domain = self.letters_domains_dict[letter].replace(domain_name, new_domain_name)
            # print("occ changed from "+  str(self.letters_occurences_dict[letter]-1) +"to " +str(self.letters_occurences_dict[letter]))
            return new_domain
        except:
            print("bad letter: " + letter)






'''
save in this dict the original length of the domain name instead of occurnces
'''
#class DomainsLettersLookup:



class WordsLettersLookup:
    def __init__(self,words_path):
        self.words_path = words_path
        self.words_letters_dict = dict()
        self.words_original_size_dict = dict()
        words = pd.read_csv(self.domains_path,sep=",",names=["Idx","Words"])
        for i in range(0,letters_num):
            self.words_letters_dict[(words["Words"][i]).strip(" ").translate(str.maketrans('','','1234567890'))] = letters[i]
            self.words_original_size_dict[(words["Words"][i]).strip(" ").translate(str.maketrans('','','1234567890'))] = len(((words["Words"][i]).strip(" ").translate(str.maketrans('','','1234567890')).split("."))[0])
        print(self.words_letters_dict)
        print(self.words_original_size_dict)


    def transform(self,word):
         try:
            original_word_name = word.strip(" ").translate(str.maketrans('','','1234567890'))
            # correct = self.domains_letters_dict[domain][0:len(self.domains_letters_dict[domain])-1]
            # print((self.domains_letters_dict[domain])[0:len(self.domains_letters_dict[domain])-1])
            # return (self.domains_letters_dict[domain])[0:len(self.domains_letters_dict[domain])-1]
            return self.words_letters_dict[original_word_name]
         except:
             print("bad domain: "+word)


class LettersWordsLookup:
    def __init__(self, words_path):
        self.words_path = words_path
        self.letters_words_dict = dict()
        self.letters_occurences_dict = dict()
        words = pd.read_csv(self.words_path, sep=",", names=["Idx", "Words"])
        for i in range(0, letters_num):
            self.letters_words_dict[letters[i]] = words["Words"][i].strip(" ").translate(str.maketrans('', '', '1234567890'))
            self.letters_occurences_dict[letters[i]] = 0
        # print(self.letters_domains_dict)
        # print(self.letters_occurences_dict)

    def transform(self, letter):
        try:
            word = self.letters_words_dict[letter].split(".")
            word_name = word[0]
            if self.letters_occurences_dict[letter] == 0:
                new_word_name = word_name
            else:
                new_word_name = word_name + str(self.letters_occurences_dict[letter])
            new_word = self.letters_words_dict[letter].replace(word_name, new_word_name)
            self.letters_occurences_dict[letter] = self.letters_occurences_dict[letter] + 1
            # print("occ changed from "+  str(self.letters_occurences_dict[letter]-1) +"to " +str(self.letters_occurences_dict[letter]))
            return new_word
        except:
            print("bad letter: " + letter)

#
# mydict = LookupDict("client","byDomain","domains.csv")
# hisdict = LookupDict("server","byDomain","domains.csv")
# word1c = mydict.transform('g')
# word2c = mydict.transform('o')
# word3c = mydict.transform('o')
# word4c = mydict.transform('g')
# word5c = mydict.transform('l')
# word6c = mydict.transform('e')
# word1s = hisdict.transform('about.com')
# word2s = hisdict.transform('adobe.com')
# word3s = hisdict.transform('adobe.com')
# word4s = hisdict.transform('about.com')
# word5s = hisdict.transform('accounts.google.com')
# word6s = hisdict.transform('abc.net.au')
#
#
#
# print(word6s)
# print(word3s)