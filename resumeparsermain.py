import nltk, os, subprocess, code, glob, re, traceback, sys, inspect
from pprint import pprint
import json
import zipfile
import csv
import spacy
from csv import DictWriter
from csv import writer
from pdfconverter import convertPDFToText
from nltk.corpus import stopwords
from pyresparser import ResumeParser




class exportToCSV:

    def __init__(self, fileName='resultsCSV.csv', resetFile=False):
        headers = [ 'FILE NAME',
                    'NAME',
                    'EMAIL',
                    'PHONE',
                    'Skills',
                    'DEGREES',
                    'Experience',
                    'Total Experience'
                    ]
        if not os.path.isfile(fileName) or resetFile:
            # Will create/reset the file as per the evaluation of above condition
            with open('resultsCSV.csv', 'w', newline='') as csvfile:
                csvfile.close()
        with open('resultsCSV.csv', 'r+', newline='') as csvfilein: ########### Open file if file already present
            inString = csvfilein.read()
            csvfilein.close()
        if len(inString) <= 0: ######### If File already exsists but is empty, it adds the header
            csvfile = open(fileName, 'r+')
            csvfile.write(','.join(headers)+'\n')
            csvfile.close()

    def write(self, infoDict):

        with open('resultsCSV.csv', 'a+') as write_obj:


            #print (infoDict)
            writer = csv.writer(write_obj)


            Filename = infoDict['fileName']
            Name = infoDict['name']
            Email = infoDict['email']
            Phone = infoDict['number']
            Skills = infoDict['skills']
            Education = infoDict['education']
            Experience = infoDict['experience']
            TotalExperience = infoDict['totalexperience']

            #print(Filename,Name,Email,Phone,Skills,Education)
            try:
                writer.writerow([Filename,Name,Email,Phone,Skills,Education,Experience,TotalExperience])
            except:
                writer.writerow("FAILED_TO_WRITE")




class Parse():
    # List (of dictionaries) that will store all of the values
    # For processing purposes

    information=[]
    inputString = ''
    tokens = []
    lines = []
    sentences = []

    def __init__(self, verbose=False):
        print('Starting Programme')
        fields = ["name", "address", "email", "phone", "mobile", "telephone", "residence status","experience","degree","education","skills"]
        pdf_files = glob.glob("resumes/*.pdf")


        files = set(pdf_files )
        files = list(files)
        print ("%d files identified" %len(files))
        print(files)
        print(pdf_files)
        for f in files:
            print("Reading File %s"%f)
            # info is a dictionary that stores all the data obtained from parsing
            info = {}

            self.inputString, info['extension'] = self.readFile(f)
            info['fileName'] = f

            self.tokenize(self.inputString)

            info['email']=self.getEmail(self.inputString, info)

            info['number']=self.getPhone(self.inputString, info)

            info['name']=self.getName(f)

            info['totalexperience']=self.getTotalExperience(f)

            info['experience']=self.getExperience(f)

            info['education']=self.extract_education(self.inputString,info)

            info['skills']=self.getSkills(f)

            csv = exportToCSV()
            csv.write(info)
            self.information.append(info)
            #print (info)

    def readFile(self, fileName):

        extension = fileName.split(".")[-1]
        if extension == "pdf":
            return convertPDFToText(fileName), extension

        else:
            print ('Unsupported format')
            return '', ''


    def preprocess(self, document):

        try:

            try:
                document = document.decode('ascii', 'ignore')
            except:
                document = document.encode('ascii', 'ignore')

            lines = [el.strip() for el in document.split("\n") if len(el) > 0]
            lines = [nltk.word_tokenize(el) for el in lines]
            lines = [nltk.pos_tag(el) for el in lines]
            sentences = nltk.sent_tokenize(document)
            sentences = [nltk.word_tokenize(sent) for sent in sentences]
            tokens = sentences
            sentences = [nltk.pos_tag(sent) for sent in sentences]

            dummy = []
            for el in tokens:
                dummy += el
            tokens = dummy
            return tokens, lines, sentences
        except Exception as e:
            print (e)

    def tokenize(self, inputString):
        try:
            self.tokens, self.lines, self.sentences = self.preprocess(inputString)
            return self.tokens, self.lines, self.sentences
        except Exception as e:
            print (e)

    def getEmail(self, inputString, infoDict, debug=False):


        email = None
        try:
            pattern = re.compile(r'\S*@\S*')
            matches = pattern.findall(inputString) # Gets all email addresses as a list
            email = matches
        except Exception as e:
            print (e)

        if debug:
            print ("\n", pprint(infoDict), "\n")
            code.interact(local=locals())
        return email

    def getPhone(self, inputString, infoDict, debug=False):


        number = None
        try:
            pattern = re.compile(r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')

            match = pattern.findall(inputString)

            match = [re.sub(r'[,.]', '', el) for el in match if len(re.sub(r'[()\-.,\s+]', '', el))>6]

            match = [re.sub(r'\D$', '', el).strip() for el in match]

            match = [el for el in match if len(re.sub(r'\D','',el)) <= 15]

            try:
                for el in list(match):

                    if len(el.split('-')) > 3: continue
                    for x in el.split("-"):
                        try:

                            if x.strip()[-4:].isdigit():
                                if int(x.strip()[-4:]) in range(1900, 2100):

                                    match.remove(el)
                        except:
                            pass
            except:
                pass
            number = match
        except:
            pass

        #infoDict['phone'] = number

        if debug:
            print ("\n", pprint(infoDict), "\n")
            code.interact(local=locals())
        return number


    def getName(self,f):
            data = ResumeParser(f).get_extracted_data()
            candidate_name = data.get('name','No Name Found')
            return candidate_name

    def getSkills(self, f):
        data = ResumeParser(f).get_extracted_data()
        candidate_skills = data.get('skills','No skills found')
        return candidate_skills

    def getExperience(self,f):
        data = ResumeParser(f).get_extracted_data()
        experience = data.get('experience','No experience found')
        return experience

    def getTotalExperience(self,f):
        data = ResumeParser(f).get_extracted_data()
        total_experience = data.get('total_experience','No experience found')
        return total_experience

    def extract_education(self,inputString,infoDict):
        nlp = spacy.load('en_core_web_sm')

            # Grad all general stop words
        STOPWORDS = set(stopwords.words('english'))
        EDUCATION = [
                'BE','B.E.', 'B.E', 'BS', 'B.S',
                'ME', 'M.E', 'M.E.', 'MS', 'M.S',
                'BTECH', 'B.TECH', 'M.TECH', 'MTECH',
                'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
                    ]
        nlp_text = nlp(inputString)
    # Sentence Tokenizer
        nlp_text = [sent.string.strip() for sent in nlp_text.sents]
        edu = {}
    # Extract education degree
        for index, text in enumerate(nlp_text):
            for tex in text.split():
            # Replace all special symbols
                tex = re.sub(r'[?|$|.|!|,]', r'', tex)
                if tex.upper() in EDUCATION and tex not in STOPWORDS:
                    edu[tex] = text + nlp_text[index + 1]
    # Extract year
        education = []
        for key in edu.keys():
            year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
            if year:
                education.append((key, ''.join(year[0])))
                #print( education)
                #infoDict['education'] = education
            else:
                education.append(key)
                #infoDict['education'] = education
                #print( education)
        return education






if __name__ == "__main__":
    verbose = False
    if "-v" in str(sys.argv):
        verbose = True
    p = Parse(verbose)
