from unittest import TestCase
import xmlParse

files = [['sample.xml',[('terms.txt', 'termscomp.txt'),('tweets.txt', 'tweetscomp.txt'),('dates.txt', 'datescomp.txt')]],
         ['samplesbig.xml',[('terms.txt', 'termscompbig.txt'),('tweets.txt', 'tweetscompbig.txt'),('dates.txt','datescompbig.txt')]]]


class TestMain(TestCase):
    def test_main(self):
        for file in files:
            xmlParse.main(file[0])
            for check in file[1]:
                with open(check[0]) as f1, open(check[1]) as f2:
                    for line in f1.readlines():
                        line2 = f2.readline()
                        try:
                            assert line == line2
                        except:
                            print(line+" != "+line2)


