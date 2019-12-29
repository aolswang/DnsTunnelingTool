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
            self.dict = LettersDomainsLookup(words_file_path)
        # if machine == "client" and technique == "byIp":
        #     self.dict = LettersWordsLookup()
        if machine == "server" and technique == "byDomain":
            self.dict = DomainsLettersLookup(words_file_path)
        # if machine == "server" and technique == "byIp":
        #     self.dict = WordsLettersLookup()
    def transform(self,word):
        return self.dict.transform(word)


class LettersDomainsLookup:
    def __init__(self,domains_path):
        self.domains_path = domains_path
        self.letters_domains_dict = dict()
        self.letters_occurences_dict = dict()
        domains = pd.read_csv(self.domains_path,sep=",",names=["Idx","Domain"])
        for i in range(0,letters_num):
            self.letters_domains_dict[letters[i]] = domains["Domain"][i].strip(" ").translate(str.maketrans('','','1234567890'))
            self.letters_occurences_dict[letters[i]] = 1
        print(self.letters_domains_dict)
        print(self.letters_occurences_dict)


    def transform(self,letter):
         try:
            self.letters_occurences_dict[letter] =  self.letters_occurences_dict[letter]+1
            print("occ changed from "+  str(self.letters_occurences_dict[letter]-1) +"to " +str(self.letters_occurences_dict[letter]))
            domain = self.letters_domains_dict[letter].split(".")
            domain_name = domain[0]
            new_domain_name = domain_name+str(self.letters_occurences_dict[letter])
            new_domain = self.letters_domains_dict[letter].replace(domain_name,new_domain_name)
            return new_domain
         except:
             print("bad letter: "+letter)


'''
save in this dict the original length of the domain name instead of occurnces
'''
class DomainsLettersLookup:
    def __init__(self,domains_path):
        self.domains_path = domains_path
        self.domains_letters_dict = dict()
        self.domains_original_size_dict = dict()
        domains = pd.read_csv(self.domains_path,sep=",",names=["Idx","Domain"])
        for i in range(0,letters_num):
            self.domains_letters_dict[(domains["Domain"][i]).strip(" ").translate(str.maketrans('','','1234567890'))] = letters[i]
            self.domains_original_size_dict[(domains["Domain"][i]).strip(" ").translate(str.maketrans('','','1234567890'))] = len(((domains["Domain"][i]).strip(" ").translate(str.maketrans('','','1234567890')).split("."))[0])
        print(self.domains_letters_dict)
        print(self.domains_original_size_dict)


    def transform(self,domain):
         try:
            original_domain_name = domain.strip(" ").translate(str.maketrans('','','1234567890'))
            # correct = self.domains_letters_dict[domain][0:len(self.domains_letters_dict[domain])-1]
            # print((self.domains_letters_dict[domain])[0:len(self.domains_letters_dict[domain])-1])
            # return (self.domains_letters_dict[domain])[0:len(self.domains_letters_dict[domain])-1]
            return self.domains_letters_dict[original_domain_name]
         except:
             print("bad domain: "+domain)







# class WordsLettersLookup:
#
# class LettersWordsLookup:

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