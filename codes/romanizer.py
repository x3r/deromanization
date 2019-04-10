import sys


def followed_by_vowel(x):
    vowels = ['া','ি','ী','ু','ূ','ে','ো','ৈ','ৌ','ৃ', '্']
    return x in vowels


def get_top_mapping(char_map):
	tokens = char_map.split(',')
	if len(tokens) > 0:
		tokens[0]
	return char_map

def romanize(m_file, in_file, out_file):
    maps = open(m_file, 'r', encoding='utf-8')
    wfile = open(out_file, 'w')
    ifile = open(in_file, 'r',encoding='utf-8')
    mapping_begin = {}
    mapping_mid = {}
    mapping_end = {}
    total = 0
    count = 0
    for line in maps:
        tokens = line.split('\t')
        mapping_begin[tokens[0]] = tokens[1].strip()
        mapping_mid[tokens[0]] = tokens[2].strip()
        mapping_end[tokens[0]] = tokens[3].strip()
        
    for line in ifile:
        line = line.strip()
        out = ''
        for idx in range(len(line)):
            c = line[idx]
            #print(c)
            if c in mapping_begin:
                #print(mapping_begin[c])
                if idx==len(line)-1:
            	    out += get_top_mapping(mapping_end[c])
                else:
            	    if line[idx+1]==' ':
            	        out +=get_top_mapping(mapping_end[c])
            	    elif idx> 0 and ((line[idx-1] == '্' and line[idx] == 'য') or (line[idx+1] == '়' and line[idx] == 'য')):
            	        if followed_by_vowel(line[idx+1]):
            	            out += 'y'
            	        else:
            	            out += 'ya'
            	    elif followed_by_vowel(line[idx+1]) or (line[idx+1] == 'প' and line[idx] == 'স') or (line[idx+1] == 'ল' and line[idx] == 'ম'):
            	        out += get_top_mapping(mapping_mid[c])
            	    else:
            	        out += get_top_mapping(mapping_begin[c])
            elif c == ' ' or c=='\n':
                out += c
        wfile.write(out+'\n')
    wfile.close()


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('usage:', sys.argv[0], 'mapping input output')
        exit(0)
    romanize(sys.argv[1], sys.argv[2], sys.argv[3])
