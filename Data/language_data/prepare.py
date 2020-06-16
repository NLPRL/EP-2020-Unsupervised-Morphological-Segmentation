# python script to prepare the datasets for our program
# command
# find . -maxdepth 1 -not -name "*.py" -type f -printf "%f " | python prepare.py

languages = ['mayo', 'mexicanero', 'nahuatl', 'wixarika']
sets = ['train', 'dev', 'test']
for l in languages:
	wordfile = open('./processed/' + l + '.train_set', 'w', encoding='utf-8')
	trainset = open('./processed/' + l + '.test_set', 'w', encoding='utf-8')
	dicfile = open('./processed/' + l + '.test_set.dic', 'w', encoding='utf-8')
	for s in sets:
		file1 = l + '-task2-' + s + '_src'
		file2 = l + '-task2-' + s + '_trg'
		for line1, line2 in zip(open(file1, 'r', encoding='utf-8'), open(file2, 'r', encoding='utf-8')):
			line1 = line1.replace(' ', '')
			line1 = line1.replace('+', 'ɨ')
			line1 = line1.replace('!', ' ')
			line2 = line2.replace(' ', '')
			line2 = line2.replace('+', 'ɨ')
			line2 = line2.replace('!', ' ')
			wordfile.write(line1)
			if s != 'train':
				trainset.write(line1)
				dicfile.write(line1[:-1] + '\t' + line2)
