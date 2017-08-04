# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: CKAN
"""

import fetch_support as f

groups = f.getGroups() 
questions = f.getData('Questions')
questionaires = f.getData('Questionaires')
qdtype = f.getData('QDataType')
qredundancy = f.getData('QRedundancy')
qconstraints = f.getData('QConstraints')
answerid = f.getAnswerID()
answers = f.getData('Answers')
answers_num = f.getData('Answers_Number')
links = f.getData('LinkTable')
profileid = f.getProfileID()
profilesummary = f.getData('ProfileSummaryTable')

tablenames = ['groups', 'questions', 'questionaires', 'qdtype', 'qredundancy', 'qconstraints', 'answerid', 'answers', 'answers_num', 'links', 'profileid' ,'profilesummary']
tabledata = [groups, questions, questionaires, qdtype, qredundancy, qconstraints, answerid, answers, answers_num, links, profileid, profilesummary]

f.saveTables(tablenames, tabledata)
f.anonAns()