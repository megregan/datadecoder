#!/usr/bin/env python
# coding: utf-8

# In[353]:


from collections import Counter

# Read in encrypted and common dictionary words
with open('as_encrypted.txt','r') as source:
    encrypted = source.read()
common_words_string = 'the of and to in a is that for it as was with be by on not he i this are or his from at which but have an had they you were their one all we can her has there been if more when will would who so no when make can like time no just him know take people into year your good some could them see other than then now look only'


# In[354]:


# common_words is a list of the 75 most common word in English 
common_words = common_words_string.upper().split()


# In[355]:


# en_words_common is a list of the 50 most common words in en_words_common
en_split = (encrypted.translate({ord(i): None for i  in '.,:;_-'})).split()
en_words_common = [word for word,num in Counter(en_split).most_common(50)]


# Here I'm making my decoding dictionary. It'll send encrypted letters to their lowercase version. When I have decoded some letters, they will be sent to their uppercase true value. This will make it easy to investigate specific encoded letters as I'll be able to follow them throughout the text. It'll also allow me to partially decrypt the text as it'll be easy to differentiate between decoded and encoded letters. 

# In[356]:


# Here I make my decoding dictionary. It will map all non alphabetic characters to themselves 
# and all the encoded characters to the the lower case version of themselves.
alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
decoded_dict = dict(zip(alphabet,[letter.lower() for letter in alphabet]))
not_letters = {sym for sym in set(encrypted) if not sym.isalpha()}
decoded_dict.update({sym:sym for sym in not_letters})


# In[357]:


def decode_list(en_word_list):
    """ Returns list of decoded words when given a list """
    return[''.join(word) for word in [[decoded_dict[letter] for letter in word] for word in en_word_list]]


# In[358]:


decoded_words = decode_list(en_words_common)
decoded_text = decode_list(en_split)


# I reasoned that there would be an overlap between the list of the 75 most common words in English and the 50 most common words in the encoded text. I wanted to make a function that could map the most common encoded words to potential matches in the most common words in English. The match function does this, it accepts a list of encoded words that have been passed through the decoded_dict and returns that original list and a list of the potential matches for each word in the original list. 
# 
# To be in this match list the common word must be the same length as the partially/fully encoded word. If there is a known letter in the word then the potential match must have that same letter in the same index. For example, 'Acv' can only be matched to words that start with 'A'. Unknown encoded letters cannot be mapped to letters that are already matched to encoded letters. The mapping of the letters in the encoded word to the letters in the common word must be one to one, one encoded letter is sent to one letter. This means that 'Acv' could not be matched to 'ALL' as then both 'C' and 'V' would be sent to 'L'. Equally 'Avv' could not be matched to 'AND' as then 'V' would be sent to both 'N' and 'D'

# In[359]:


def match(l):
    def word_match(w):
        """ Finds a list of potential matches for a partially/fully encoded word
        Starts by eliminating all common words that are not the same length as the partially/fully encoded word (w) """
        matches = [word for word in common_words if len(word) == len(w)]
        
        # If the letter in w is upper then it is a decoded letter so that same letter must be in the same index in all matches
        # If the letter is lowercase then it is encrypted and can be mapped to any letter that is not already mapped to an encoded letter
        for i in range(len(w)):
            if (w[i]).isupper() == True:
                matches = [word for word in matches if word[i] == w[i]]
            else:
                matches = [word for word in matches if  word[i] not in decoded_dict.values()]
        # Making a copy of the current matches so that I can iterate over them which removing items if the mapping isn't one to one
        matches_copy = [word for word in matches] 
        map_dict = {}
        # I iterate through all the words in the matches list and then through all the letters in each match.
        # If it is the first time the letter appears in a word then the match is removed if that encoded letter is being sent to a letter that already has another encoded letter mapped to it.
        # If the letter has appeared in the word before then the word is removed if that encoded letter is not being mapped to the same letter as it was previously
        for match in matches_copy:
            map_dict.clear()
            for i in range(len(match)):
                if w[i] not in map_dict:
                    if match[i] not in map_dict.values():
                        map_dict[w[i]] = match[i]
                    else:
                        matches.remove(match)
                        break
                else:
                    if map_dict[w[i]] == match[i]:
                        continue 
                    else: 
                        matches.remove(match)
                        break  
        return(matches)
    # Retruns a list of tuples where the first item in the tuple is an encoded word and the second item is a list of the potential matches for that word.
    return([(word,word_match(word)) for word in l])


# I then created some other functions that would help me best use match.
# Containing returns all the words in a list containing a particular character. This will allow me to find all instances of a particular encoded letter if I use a lowercase letter as an argument.

# In[360]:


def containing(letter, text):
    """ Returns a list of all the words in a text that contain a given character """
    return([word for word in text if word.count(letter) >= 1])


# This function will let me test my guesses by replacing all instances of a letter with another letter. 

# In[361]:


def replace(orig, new, text):
    """ Returns a list of words where all the occurrences of a given character are replaced with a new character """
    return([word.replace(orig, new) for word in containing(orig, text)])    


# This function will be very useful as I begin to decode letters. You send as arguments a partially or fully encoded word and that word decoded. It then updates the decoded dict with all the new mappings. It also updates the list of decoded words by decoding the encrypted words with the updated dictionary.

# In[362]:


def update(en_word, word):
    """ Updates the decoded_dict when. Takes an encoded word that has been passed through the decoded dict (en_word) and the 
     fully decoded version of that word. Also updates decoded_words by decoding all the words with the updated decoded dict """
    global decoded_words
    decoded_dict.update(dict([(en.upper(),de.upper()) for (en,de) in list(zip(en_word,word)) if en.isupper()==False]))
    decoded_words = decode_list(en_words_common)


# The blank function is useful in that it returns a list of all the words in decoded_words that only have one encrypted letter left in them. These are the words where the match function can be very effective as if it finds a match if is quite likely to be right.

# In[363]:


def blank():
    """ Returns a subset of decoded_words where there is only one encoded word left in the word """
    return([word for word in decoded_words if sum([1 for char in word if char.isupper()==False]) == 1])


# In[364]:


ordered_char = 'e t a o i n s r h l d c u m f p g w y b v k x j q z'.upper()
char_dict = dict(zip(ordered_char.split(),range(1,27)))
order_dict = dict(zip(range(1,27),ordered_char.split()))
en_chars = (encrypted.translate({ord(i): None for i  in ' .,:;_-'}))
en_char_sorted = Counter(en_chars).most_common(26)
en_char_dict = {pair[0]:en_char_sorted.index(pair)+1 for pair in en_char_sorted}
en_order_dict = {en_char_sorted.index(pair)+1:pair[0] for pair in en_char_sorted}
char1 = 't o a w b c d s f m r h i y e g l n p u j k'.upper().split()
char1_dict = dict(zip(char1,range(1,27)))
order1_dict = dict(zip(range(1,27),char1))
en_words = (encrypted.translate({ord(i): None for i  in '.,:;_-'})).split()
en_char1 = Counter([word[0] for word in en_words]).most_common(26)
en_char_dict1 = {pair[0]:en_char1.index(pair)+1 for pair in en_char1}
en_order_dict1 = {en_char1.index(pair)+1:pair[0] for pair in en_char1}
en_char_dict1.update(dict(zip([char for char in alphabet if char not in en_char_dict1],list(range(24,27)))))


# In[365]:


def compare(enletter,letter):
    print('general frequency',(en_char_dict[enletter],enletter),(char_dict[letter],letter))
    print('1nd letter frequency',(en_char_dict1[enletter],enletter),(char1_dict[letter],letter))


# In[366]:


compare('E','T'),compare('A','H'),compare('W','E')


# The most common English word is 'THE' and most common word in the encoded words was 'EAW'. The frequencies of the encoded letters and the decoded letters also matched well. I deduced they were the same word. 

# In[367]:


en_words_common[0],common_words[0]


# In[368]:


update('eaw','THE')


# In[369]:


match(containing('g',decoded_words))


# I decided I would send a list of the common encoded words that contained a letter of interest to match. Then I could compare what letters the letter of interest was mapped to in the matches. If the letter of interest was being consistently mapped to one letter then I could deduce that that was the true match. For example, below we can see, for every word with matches, 'g' is being sent to 'A' in at least one of the potential matches. Therefore, I deduced that 'G' is 'A'. I repeated this process for different letters.

# In[370]:


match(containing('g',decoded_words))


# In[371]:


update('g','A')


# I use the blank function to get new letters to try to decode. It's more likely that the match function will be able to find a single correct match for these words than for words with lots of unknowns. It's also easier to see by eye what letter should replace the encoded letter to make a word. Below I saw the word 'ApE' in the blank list and decided to try and find discover what 'p' was.

# In[372]:


blank()


# In[373]:


match(containing('p',decoded_words))


# In[374]:


update('p','R')


# In[375]:


blank()


# In[376]:


match(containing('m',decoded_words))


# In[377]:


update('m','O')


# In[378]:


blank()


# In[379]:


match(containing('y',decoded_words))


# In[380]:


update('y','S')


# In[381]:


blank()


# In[382]:


match(containing('l',decoded_words))


# In[383]:


update('l','W')


# In[384]:


blank()


# In[385]:


match(containing('o',decoded_words))


# In[386]:


update('o','I')


# In[387]:


blank()


# In[388]:


match(containing('n',decoded_words))


# In[389]:


update('n','F')


# In[390]:


blank()


# In[391]:


match(containing('f',decoded_words))


# In[392]:


update('Afq','AND')


# In[393]:


blank()


# In[394]:


match(containing('x',decoded_words))


# In[395]:


update('X','B')


# In[396]:


blank()


# In[397]:


match(containing('b',decoded_words))


# In[398]:


update('ErERb','EVERY')


# In[399]:


blank()


# In[400]:


match(containing('h',decoded_words))


# In[401]:


update('SOhIETb','society')


# In[402]:


blank()


# In[403]:


update('k','U')


# In[404]:


blank()


# In[405]:


update('USEFUu','USEFUL')
blank()


# In[406]:


(containing('j',decoded_words))


# In[407]:


update('j','P')
blank()


# In[408]:


update('s','M')
blank()


# In[409]:


match(containing('x',decoded_words))


# In[410]:


update('x','B')


# In[411]:


blank()


# In[412]:


match(containing('d',decoded_words))


# For some of the less common letters there were no/very little words in the most common encoded words that contained them. So, I searched for all the words that contained them in the whole text. Given I already had so many letters decoded it was easy to see what letter they should be mapped to. I also made to functions to help me. Remaining gives a list of the potential letters the encoded letter of interest could be mapped to. Remaining_en gives a list of all the encoded letters that have not been mapped to a letter yet. 

# In[413]:


def remaining_en():
    """ Returns a list of encoded letters which have not been mapped to real letters """
    return([letter for letter in alphabet if decoded_dict[letter].upper() == letter])


# In[414]:


def remaining():
    """ Returns a list of letters where their encoded letter is unknown
        uses global decoded_dict and global alphabet """
    return([letter for letter in alphabet if letter not in [char for char in list(decoded_dict.values()) if char.isupper() == True]])


# In[415]:


decoded_text = decode_list(en_split)


# In[416]:


remaining()


# In[417]:


containing('d',decoded_text)


# In[418]:


replace('d','K', decoded_text)


# In[419]:


update('d','K')


# In[420]:


remaining_en()


# In[421]:


containing('c',decoded_text)


# In[422]:


update('cUDzMENT','judgement')
update('SUxcECT','subject')


# In[423]:


remaining_en()


# In[424]:


containing('i',decoded_text)


# In[425]:


update('i','Q')


# In[426]:


containing('t',decoded_text)


# In[427]:


update('t','X')


# In[428]:


remaining_en()


# In[429]:


remaining()


# I mapped V to Z through process of elimination. I now have a complete decoding dictionary that I can use to fully decode the encoded text.

# In[430]:


update('v','Z')


# In[431]:


decrypted = ''.join([decoded_dict[letter] for letter in encrypted])
decrypted[:100]

