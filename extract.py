# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 16:03:22 2017

@author: CKAN
"""

import support

groups = support.getGroups() 
questions = support.getData('Questions')
questionaires = support.getData('Questionaires')
qdtype = support.getData('QDataType')
qredundancy = support.getData('QRedundancy')
qconstraints = support.getData('QConstraints')
answerid = support.getAnswerID()
answers = support.getData('Answers')
answers_num = support.getData('Answers_Number')
links = support.getData('LinkTable')
profileid = support.getProfileID()
profilesummary = support.getData('ProfileSummaryTable')

tablenames = ['groups', 'questions', 'questionaires', 'qdtype', 'qredundancy', 'qconstraints', 'answerid', 'answers', 'answers_num', 'links', 'profileid' ,'profilesummary']
tabledata = [groups, questions, questionaires, qdtype, qredundancy, qconstraints, answerid, answers, answers_num, links, profileid, profilesummary]

support.saveTables(tablenames, tabledata)
support.anonAns()