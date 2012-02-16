import sys, re, NLPlib

#ROOT_PATH = '/u/cs401/'
ROOT_PATH = ''

def remove_html_tags(s):
    '''Returns a string with all HTML from string, s, removed.'''

    return re.sub(r'\s*<(.|\s)*?>', r'', s)  # *? means not greedy

def convert_html_entities(s):
    '''Returns a string with common HTML entities in s converted into their proper from.'''

    s = re.sub(r'&quot;', r'"', s)
    s = re.sub(r'&amp;', r'&', s)
    s = re.sub(r'&nbsp;', r' ', s)
    s = re.sub(r'&lt;', r'<', s)
    s = re.sub(r'&gt;', r'>', s)
    return s

def remove_urls(s):
    '''Returns a string with all URLS from string, s, replaced with a placeholder
    ___URL___. The number of links one shares in tweets is a valuable attribute,
    and it'd be counter-productive to throw this information away!'''

    pattern = r'(?i)(https?\://)?[a-z0-9][\w\-]*(\.[a-z]{2,3})+(\/[\w\:\-#%&\?\/]+)?'
    return re.sub(pattern, r'___URL___', s)

def get_words_from_file(file_path):
    '''Given a file at file_path, return a hash of the words separated by
    new line characters in the file.'''

    fp = open(file_path, "r")
    word_list = fp.read().split("\n")
    word_hash = {}
    for word in word_list:
        if word: word_hash[word] = 1
    fp.close()

    return word_hash

def trim_between(s):
    '''Return string s with all consecutive whitespace removed, as removed whitespace
    at beginning and end of s'''

    s = re.sub(r'(\t)+', r'\1', s.strip())
    s = re.sub(r'( )+', r'\1', s)
    s = re.sub(r'(\n)+', r'\1', s)
    return s

ABBREV_HASH = {}
PN_ABBREV_HASH = {}
MALE_NAMES_HASH = {}
FEMALE_NAMES_HASH = {}
LAST_NAMES_HASH = {}
EMOTICONS_HASH = {}

def separate_sentences(s):
    '''Return string s, with all sentences on separate lines, based on the following
    heuristics from "Foundations of Statistical Natural Language Processing", 4.2.4.'''
    global ABBREV_HASH ,PN_ABBREV_HASH, MALE_NAMES_HASH, FEMALE_NAMES_HASH, LAST_NAMES_HASH

    # Trim and remove consecutive spaces
    s = trim_between(s)

    # Make sure ., ?, and ! are separated by spaces
    # E.g., "hello.bye" => "hello. bye" and "hello...bye" => "hello... bye"
    # This will make it easier later to see what words/characters precede/follow
    # this kind of punctuation and decide whether or not it's a sentence boundary.
    # We need the {2,} because sentences don't grammatically end with single-letter
    # words and we can use this prevent spaces between acronyms. This doesn't work in
    # cases like "how are u?blah", "do this k?blah".
    s = re.sub(r'([^\.\?!\s]{2,})([\.\?!]+)([^\.\?!\s]+)', r'\1\2 \3', s)

    # The following are hashes and will allow for fast lookup.
    # We store the variables outside function definition in case this function is called
    # more than once - we don't want to redo expensive tasks.
    if not ABBREV_HASH: ABBREV_HASH = get_words_from_file(ROOT_PATH+'Wordlists/abbrev.english')
    if not PN_ABBREV_HASH: PN_ABBREV_HASH = get_words_from_file(ROOT_PATH+'Wordlists/pn_abbrev.english')
    if not MALE_NAMES_HASH: MALE_NAMES_HASH = get_words_from_file(ROOT_PATH+'Wordlists/maleFirstNames.txt')
    if not FEMALE_NAMES_HASH: FEMALE_NAMES_HASH = get_words_from_file(ROOT_PATH+'Wordlists/femaleFirstNames.txt')
    if not LAST_NAMES_HASH: LAST_NAMES_HASH = get_words_from_file(ROOT_PATH+'Wordlists/lastNames.txt')

    # Used for determining if we're within a quotation or parantheses.
    open_quotes = 0
    open_brackets = 0

    words = s.split(' ')
    W = len(words)

    new_s = ''
    for i in range(0, W):

        word = words[i]
        word_length = len(word)
        next_word = words[i+1] if i+1 < W else ''

        # Make this lower case and strip punctuation as we'll be comparing to it word lists.
        next_word_cmp = re.sub(r'(?i)[^a-z]+', r'', next_word.lower()) # this may be used a lot
        
        open_quotes += word.count('"') % 2
        open_brackets += max(0, word.count('(') - word.count(')')) # this isn't perfect, but good enough.
        
        # Check if word ends in something like ".","...","!?!?!","?","!",etc.
        #if re.match(r'[!\?\.]$', word):
        if word_length and word[word_length-1] in ['!','?','.']:
            # Need to decide whether we add a new line character or not
            # or to separate a . from preceeding characters
            separate_punc = True 
            B = "\n"

            # Remove boundary if punctuation is followed by quotation mark.
            # We keep track if we're "inside" a quotation for better accuracy.
            if next_word and next_word[0] == '"' and open_quotes > 0:
                # Remove quote from next word and add it to this one
                words[i+1] = words[i+1][1:]
                word += '"'
                open_quotes -= 1
                B = ''
            
            # Like the previous case except with bracket
            elif next_word and next_word[0] == ')' and open_brackets > 0:
                words[i+1] = words[i+1][1:]
                word += ')'
                open_brackets -= 1
                B = ''
            
            # Remove boundary if preceded by pronoun abbreviation (like "vs." or "Dr.") and followed by name.
            if next_word and word in PN_ABBREV_HASH and next_word[0].isupper() and (next_word_cmp in MALE_NAMES_HASH or next_word_cmp in FEMALE_NAMES_HASH or next_word_cmp in LAST_NAMES_HASH):
                B = ''
                separate_punc = False

            # Remove boundary if preceded by normal abbreviation (like "Feb." or "Blvd.") and not followed by uppercase letter.
            elif next_word and word in ABBREV_HASH and not next_word[0].isupper():
                B = ''
                separate_punc = False
            
            elif re.match(r'^[\.\?!]+$', next_word):
                B = ''
            
            elif i == 0 and re.match(r'^[\.\?!]+$', word):
                B = ''

            # Remove boundary if we have ! or ? and and followeded by lowercase letter or known name.
            #elif next_word and word[word_length-1] in ['!', '?'] and (next_word[0].islower() or next_word_cmp in MALE_NAMES_HASH or next_word_cmp in FEMALE_NAMES_HASH):
            #    B = ''
                        
            if separate_punc:
                word = re.sub(r'([\.\?!]+)', r' \1', word)
            
        
        else:
            B = ''

        # Check if emoticon is embedded in word:
        word = parse_emoticons(word)

        if len(new_s) and new_s[len(new_s)-1] != "\n":
            new_s += ' '
        new_s += word + B
    
    return new_s


def parse_emoticons(s):
    '''Iterate through the word(s) checking for emoticons and surrounding
    them with | to differentiate them from other words/punctuation
    Example: Hello:) becomes Hello |:)|'''

    global EMOTICONS_HASH
    if not EMOTICONS_HASH: EMOTICONS_HASH = get_words_from_file('Wordlists/Emoticons')

    # it's possible there are spaces within word, and we don't want to parse
    # emoticons that are attached to words. For example, don't want to parse
    # s: in "first names: ..."
    words = s.split(' ')
    new_word = ''
    for word in words:
        for emot in EMOTICONS_HASH.keys():
            if word.strip().upper() == emot.upper():
                word = ' |'+emot+'| '
        new_word += ' ' + word

    return new_word[1:]

def separate_contractions(s):
    '''Return the string s with contractions/clitics separated.
    Examples: I've -> I 've  I'm -> I 'm  abc's -> abc 's isn't-> is n't Chris' -> Chris '
    '''

    words = s.split(' ')
    endings = {"'ve":" 've",
               "'m":" 'm",
               "'s":" 's",
               "n't":" n't",
               "s'":"s '",
               "'d": " 'd",
               "'ll":" 'll",
               "'re":" 're"}

    W = len(words)
    new_s = ''
    for w in words:
        for (ending, replacement) in endings.items():
            if w.endswith(ending):
                w = w.replace(ending, replacement)
                break
        new_s += ' ' + w
    return new_s[1:]


def separate_tokens(s):
    '''Return the string that is s but with all tokens separated by spaces.
    Characters in [!?.]+ should already be separated in separated_sentences func.'''

    # Separate punctuation except [.?!'@#-|]
    # We ignore punctuation surrounded by | as a "hack" to prevent
    # the separation of emoticons. Regex isn't powerful enough
    # for this so we do a loop.
    new_s = ''
    S = len(s)
    for x in range(0, S):
        add = s[x]
        if re.match(r'[^\w\.!\?\'@#\-\|]', s[x]) and (x == 0 or s[x-1] != '|') and (x+1>=S or s[x+1] != '|'):
            add = ' '+s[x]+' ' 
        new_s += add
    s = new_s

    # Separate contractions
    s = separate_contractions(s)

    # Properly separate dashes
    s = re.sub(r' ([\-]+) ', r' \1 ', s)

    # Separate @ and # if not mention or hashtag
    s = re.sub(r'(#|@)\W+', r' \1 ', s)

    # Isolate @xxx and #xxx if mention or hashtag
    s = re.sub(r'([#@]\w+)', r' \1 ', s)

    # Isolate URLs
    s = re.sub(r'(___URL___)', r' \1 ', s)

    # Trim and remove consecutive spaces
    s = trim_between(s)

    return s


def fix_token_tag(token, tag):
    '''Given token and tag, override the tag'''

    # We don't want ___URL___ to count as noun or other part of speech
    if token == '___URL___':
        tag = 'URL'
    
    elif is_hash_tag_or_mention(token):
        tag = 'MENTIONHASH'
    
    elif re.match(r'^[\.]{2,}$', token):
        tag = '...'
        
    elif re.match(r'^[\-]+$', token):
        tag = '-'
    
    elif token in ['i', 'u']:
        tag = 'PRP'

    elif token == 'ppl':
        tag = 'NNS'

    # Check if token is some form of number with commas or decimal digits (not perfect)
    elif token.isdigit() or re.match(r'^(\d,?)+(\.\d+)?$', token):
        tag = 'NUM'
    
    # The tagger tags things like !!!, !?!? as NN. It should be tagged as . instead
    # because it marks the end of a sentence.
    elif re.match(r'^[!\?]{2,}$', token):
        tag = '.'
    
    elif re.match(r'\|.{2,3}\|', token):
        token = token.replace('|', '')
        tag = 'EMOT'
    
    return token, tag

def tag_tokens(tagger, tokens):

    tokens = trim_between(tokens)

    send = tokens.strip().split(' ')
    tags = tagger.tag(send)

    tagged_tweet = ''
    L = len(send)
    for i in range(0, L):
        if send[i] == "\n":
            tagged_tweet += "\n"
        else:
            token, tag = fix_token_tag(send[i], tags[i])
            tagged_tweet += token + '/'+ tag
            if i+1 < L: tagged_tweet += ' '
        i += 1

    return tagged_tweet

def is_hash_tag_or_mention(token):
    '''Return true if the given string is of the form #abc or @abc.'''

    return re.match(r'^[@#]\w+$', token)

def get_token_and_tag(token_tag):
    '''Return the token and tag separated. This is safer than split in case
    we the token is a /. But we know that tags do not contain slashes. So we
    use rfind to see where to divide the string.'''

    separator_index = token_tag.rfind('/')
    return token_tag[0:separator_index], token_tag[separator_index+1:]

def remove_hash_tags(tweet):
    '''Return tweet with all hash tags and mentions removed except those
    that fit in a sentence grammatically'''

    new_tweet = ''

    sentences = tweet.split("\n")
    S = len(sentences)
    for s in range(0, S):
        sentence = sentences[s]
        tokens = sentence.split(' ')
        T = len(tokens)
        for i in range(0, T):
            add_token = True
            token, tag = get_token_and_tag(tokens[i])
            # We only consider removing hashtag or mention if at beginning of sentence or end of tweet.
            if is_hash_tag_or_mention(token):

                # If hash/mention is at beginning of sentence
                if i == 0 and i+1 < T:
                    next_token, next_tag = get_token_and_tag(tokens[i+1])
                    if next_token[0].isupper() or next_tag not in ['POS','TO','VBZ','VBN','VBG','VBD','VB','RB','MD','CC']:
                        add_token = False
                # If hash/mention is in its own sentence
                elif i == 0 and i+1 == T:
                    add_token = False
                # If hash/mention is on the last line
                elif s+1 == S:
                    if i > 0:
                        prev_token, prev_tag = get_token_and_tag(tokens[i-1])
                        if prev_tag in ['.', 'MENTIONHASH', '...', 'URL']:
                            add_token = False
                    elif i+1 < T:
                        next_token, next_tag = get_token_and_tag(tokens[i+1])
                        if next_token in ['MENTIONHASH']:
                            add_token =  False
            if i > 0: new_tweet += ' '
            if add_token: new_tweet += tokens[i]
        if s+1 < S: new_tweet += "\n"

    return trim_between(new_tweet)


if __name__ == '__main__':

    args = sys.argv

    if len(args) < 3:
        print "usage: python " + args[0] + " path/to/tweets path/to/output"
        sys.exit()

    fp = open(args[1])
    tweets = fp.read().strip().split("\n")
    
    tagger = NLPlib.NLPlib()

    fp_write = open(args[2], "w+")

    i = 0
    for tweet in tweets:

        tweet = convert_html_entities(tweet)
        tweet = remove_urls(tweet)
        tweet = remove_html_tags(tweet)
        tweet = separate_sentences(tweet)
        tweet = separate_tokens(tweet)
        tweet = tag_tokens(tagger, tweet)
        tweet = remove_hash_tags(tweet)

        fp_write.writelines(("\n|\n" if i > 0 else "") + tweet) 
        i += 1

    fp_write.close()
    fp.close()
    



