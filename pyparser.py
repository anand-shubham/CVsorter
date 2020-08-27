from pyresparser import ResumeParser
data = ResumeParser(r'D:\Resume Classifier\Spacy Resume\resumes\my-resume.pdf').get_extracted_data()
print(data)
