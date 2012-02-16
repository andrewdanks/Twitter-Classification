import sys, re

#ROOT_PATH = '/u/cs401/'
ROOT_PATH = ''

# We use the TAGS/TOKENS dict to categorize different tags/tokens that will later be used for counting
# in build_arff_class(). We store these as hash maps and given that they will be accessed a
# considerable number of times, it would be much faster than simply using lists.

TAGS = {}
TAGS['adverbs']                     = {'RB':1, 'RBR':1, 'RBS':1}
TAGS['common_nouns']                = {'NN':1, 'NNS':1}
TAGS['proper_nouns']                = {'NNP':1, 'NNPS':1}
TAGS['wh_words']                    = {'WDT':1, 'WP':1, 'WP$':1, 'WRB':1}
TAGS['past_tense_verbs']            = {'VBD':1}
TAGS['commas']                      = {',':1}
TAGS['emoticons']                   = {'EMOT':1}
TAGS['numbers']                     = {'NUM':1}

TOKENS = {}
TOKENS['first_person_pronouns']     = {'I':1, 'me':1, 'my':1, 'mine':1, 'we':1, 'us':1, 'our':1, 'ours':1}
TOKENS['second_person_pronouns']    = {'you':1, 'your':1, 'yours':1, 'u':1, 'ur':1, 'urs':1}
TOKENS['third_person_pronouns']     = {'he':1, 'him':1, 'his':1, 'she':1, 'her':1, 'hers':1, 'it':1, 'its':1, 'they':1, 'them':1, 'their':1, 'theirs':1}
TOKENS['future_tense_verbs']        = {"'ll":1, "will":1, "gonna":1}
TOKENS['dashes']                    = {'-':1}
TOKENS['ellipses']                  = {'...':1}
TOKENS['colons']                    = {';':1, ':':1}
TOKENS['links']                     = {'___URL___':1}


# Allocate the TOKENS structure for token categorized in files:

token_type_and_data = {'coordinating_conjunctions':'Wordlists/Conjunct',
                       'first_person_pronouns':'Wordlists/First-person',
                       'second_person_pronouns':'Wordlists/Second-person',
                       'third_person_pronouns':'Wordlists/Third-person',
                       'slang_acronyms':'Wordlists/Slang',
                       'female_first_names':'Wordlists/femaleFirstNames.txt',
                       'male_first_names':'Wordlists/maleFirstNames.txt',
                       'last_names':'Wordlists/lastNames.txt'}

for token_type in token_type_and_data:
    TOKENS[token_type] = {}
    file_path = token_type_and_data[token_type]
    fp = open(ROOT_PATH+file_path, "r")
    word_list = fp.read().split("\n")
    for word in word_list:
        if word: TOKENS[token_type][word] = 1
    fp.close()

# ARFF attribute notes:
#
# colons: includes both colons and semi-colons
# upper_case_words:  Words all in upper case (2+ letters long)
# average_sentence_length: Average length of sentences (in tokens)
# average_tokens_length: Average length of tokens in chars, excluding punctuation

ARFF_ATTRIBUTES = [ # These attributes are used for counting and should be defined in the TAGS/TOKENS dict.
                    # It's possible that they may have additional heuristics for counting.
                   'first_person_pronouns',
                   'second_person_pronouns',
                   'third_person_pronouns',
                   'past_tense_verbs',
                   'common_nouns',
                   'proper_nouns',
                   'adverbs',
                   'wh_words',
                   'slang_acronyms',
                   'future_tense_verbs', # this also uses a custom heuristic
                   'coordinating_conjunctions',
                   'commas',
                   'dashes',
                   'ellipses',
                   'colons',
                   'links',
                   'emoticons',
                   'numbers',
                    # The following attributes will use custom heuristics for counting.
                   'full_names',
                   'mentions',
                   'hashtags',
                   'upper_case_words',
                   'consecutive_exclaimation_points_question_marks',
                   'sentences',
                   'average_sentence_length',
                   'average_tokens_length']


def create_data_point(tweet, class_name):
    '''Create and return a data point for the arff file.'''

    # This is what we'll return
    data = ''

    # We use this dictionary to initialize all the attributes that will be in the arff line
    # for this class.
    attributes = {}
    for a in ARFF_ATTRIBUTES:
        attributes[a] = 0

    num_tokens = 0
    token_length_sum = 0

    # Sentences are assumed to be separated by new-line characters, as per the ttwt specification.
    attributes['sentences'] = len(tweet.split("\n"))

    tokens = tweet.split(' ')
    
    # Here we keep track of previously seen tags and tokens. Elements will be
    # of the form [token, tag]. We don't have to worry about size/memory as tweets
    # are assumed to be a maximum of 144 characters.
    # E.g., previous_tokens = [['green', 'JJ'], ['took', 'VBD']]
    previous_tokens = []

    for i in range(len(tokens)):

      t = tokens[i]

      token, tag = get_token_and_tag(t)
      token_length = len(token)
      previous_tokens.append([token, tag])
      
      # Don't count punctuation for avg token length
      if not re.match(r'^\W+$', token):
        num_tokens += 1
        token_length_sum += token_length

      # Check what type of tag it is and count it.

      for tag_type in TAGS:
        if tag in TAGS[tag_type] and tag_type in attributes:
          attributes[tag_type] += 1
      
      for tag_type in TOKENS:
        if token in TOKENS[tag_type] and tag_type in attributes:
          attributes[tag_type] += 1
      
      # Keep track other attributes:
      
      # Future tense verbs:
      # We already keep track of 'll, will, gonna, etc. above. Now we must count
      # "going+to+VB"
      if i > 1 and tag == 'VB' and previous_tokens[i-2][0].lower() == 'going' and previous_tokens[i-1][0].lower() == 'to':
        attributes['future_tense_verbs'] += 1

      if token_length >= 2 and token.isupper() and token.isalpha():
        attributes['upper_case_words'] += 1

      # Check if we see hashtag used grammatically:
      elif tag == 'MENTIONHASH' and token[0] == '#':
        attributes['hashtags'] += 1

      # Check if we see mention used grammatically:
      elif tag == 'MENTIONHASH' and token[0] == '@':
        attributes['mentions'] += 1

      # Check if we encounter a first name + last name. First/Name must begin with capital letter
      if i > 0 and token_length and len(previous_tokens[i-1][0]) and previous_tokens[i-1][0][0].isupper() \
       and token[0].isupper() and (previous_tokens[i-1][0].lower() in TOKENS['male_first_names'] \
       or previous_tokens[i-1][0].lower() in TOKENS['female_first_names']) and token.lower() in TOKENS['last_names']:
        attributes['full_names'] += 1
      
      # Count consecutive ! and ?
      if re.match(r'[!\?]{2,}', token):
        attributes['consecutive_exclaimation_points_question_marks'] += 1

    if num_tokens > 0:
      attributes['average_sentence_length'] = float(attributes['sentences']) /  num_tokens
      attributes['average_tokens_length'] = float(token_length_sum) / num_tokens
    # otherwise they are already set to 0

    data += "".join([str(attributes[attr]) + ',' for attr in ARFF_ATTRIBUTES])
    data += class_name

    return data


def build_arff_class(class_name, files, max_num_tweets):
    '''Given a list of file paths, create one line for the @DATA section that contains all the numbers
    for each attribute in the order of ARFF_ATTRIBUTES, separated by commas, along with the class name.
    Only the first max_num_tweets are considered. If it is 0, it considers all of them.'''

    arff = ""
    tweet_number = 1

    for f in files:
        fp = open(f)
        tweets = fp.read().split("\n|\n")
        tweet_number = 0

        for tweet in tweets:

            if max_num_tweets and tweet_number >= max_num_tweets:
                break
              
            arff += create_data_point(tweet, class_name) + "\n"
            tweet_number += 1

        fp.close()

    return arff


def get_token_and_tag(token_tag):
    '''Return the token and tag separated. This is safer than split in case
    we the token is a /. But we know that tags do not contain slashes. So we
    use rfind to see where to divide the string.'''

    separator_index = token_tag.rfind('/')
    return token_tag[0:separator_index], token_tag[separator_index+1:]



if __name__ == '__main__':

    args = sys.argv
    A = len(args)

    # The last argument is the output file
    output_file = args[A-1]
    args = args[:A-1]
    output_fp = open(output_file, "w+")

    # Check if we have a limit
    if len(args) > 1 and args[1][0] == '-':
        max_num_tweets = int(args[1][1:])
        rest = args[2:]
    else:
        max_num_tweets = None
        rest = args[1:]

    class_names = []
    data = ''

    # Loop through the rest of the arguments
    for r in rest:

        # Check if a class name is provided
        s1 = r.split(':')
        class_name = s1[0]
        file_names = s1[1] if len(s1) > 1 else s1[0]

        class_names.append(class_name)
        file_names_list = file_names.split('+')

        data += build_arff_class(class_name, file_names_list, max_num_tweets) + "\n"

    write_buffer = "@RELATION " + output_file + "\n\n"
    for a in ARFF_ATTRIBUTES:
        write_buffer += "@ATTRIBUTE "+a+" NUMERIC\n"

    write_buffer += "@ATTRIBUTE class {"+','.join(class_names)+"}\n\n@DATA\n"
    write_buffer += data

    output_fp.write(write_buffer)
    # print write_buffer  # use this for testing


