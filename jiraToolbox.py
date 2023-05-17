# -*- coding: utf-8 -*-

import json, os

try:
	import requests
	from requests.auth import HTTPBasicAuth

except:
	print('Lib "requests" is not present. Installing Library with pip...')
	os.system('pip install requests')	
	try:
		import requests
		from requests.auth import HTTPBasicAuth
		
		print('importation of lib "requests" completed with sucessfully (after installation)')

	except:
		print('installation of "requests" failed. Contact the developer for help. Ending program...')
		quit()

class JiraAPI(object):
	def __init__(self, atlassianHost, atlassianEmail, atlassianToken):
		self.atlassianHost = atlassianHost
		self.atlassianEmail = atlassianEmail
		self.atlassianToken = atlassianToken
		
	def invokeJiraAPI(self, httpMethod, url, payload):
		
		basic = HTTPBasicAuth(self.atlassianEmail, self.atlassianToken)
		
		return requests.request(
								method= httpMethod,
								url= url, 
								data=json.dumps( payload ), 
								headers= {
									"Content-Type": "application/json"
									
										},
								auth = basic
								
								).text

	def deleteIssue(self, issueId):
		url = self.atlassianHost+'/rest/api/2/issue/'+issueId
				
		payload = {}
		
		result = invokeJiraAPI( 'DELETE', url , payload)
		
		print (result)
		
		result = json.loads(result)
		
		print (result.get('key'))
		if (result.get('key')) != "":
			return result.get('key')

	def createIssue(self, projectCode, summary, description, issueType):
		url = self.atlassianHost+'/rest/api/2/issue/'
				
		payload = {
			"fields": {
			   "project":
			   {
				  "key": projectCode
			   },
			   "summary": summary,
			   "description": description,
			   "issuetype": {
				  "name": issueType #Bug, Story, Epic
			   }
		   }
		}
		
		result = self.invokeJiraAPI('POST', url, payload)

		print (result)
		
		result = json.loads(result)
		
		print (result.get('key'))
		if (result.get('key')) != "":
			return result.get('key')

	def createSubtask(self, projectCode, parentIssueKey, summary, description):
		url = self.atlassianHost+'/rest/api/2/issue/'
		
		payload = {
		
			"fields": {
			
				"parent": {
				"key": parentIssueKey
				
				},
		
			
			   "project":
			   {
				  "key": projectCode
			   },
			   "summary": summary,
			   "description": description,
			   "issuetype": {
				  "name": "Subtarefa",
				  "subtask": True,
			   }
		   }
		}
		
		result = self.invokeJiraAPI('POST', url, payload)

		result = json.loads(result)
		
		print (result.get('key'))
		if (result.get('key')) != "":
			return result.get('key')


	def createIssueAndAssign(self, projectCode, summary, description, issueType, assigneeAccountId):
		
		createdIssue = self.createIssue(projectCode,summary,description,issueType)
		
		result = self.assigneeIssue(createdIssue, assigneeAccountId) 
		
		print (result)
		
		result = json.loads(result)
		
		print (result.get('key'))
		if (result.get('key')) != "":
			return result.get('key')

	def getUserInfoByEmail(self, emailJiraUser):
		url = self.atlassianHost+'/rest/api/2/user/search?query=' + emailJiraUser
				
		result = self.invokeJiraAPI( 'GET', url, '')
		
		result = json.loads(result)
		
		if (result[0].get('accountId') != "" and result[0].get('displayName') != ""):
			return result[0]

	def assigneeIssue(self, issueJiraNumber, accountId):
		url = self.atlassianHost+'/rest/api/2/issue/'+issueJiraNumber
		
		payload = {
			"fields": {
				"assignee":{"accountId": accountId }
			}
		}
		
		print ( self.invokeJiraAPI('PUT', url, payload))
		
		print ('assigneeIssue: updated assignee for issue '+issueJiraNumber+'. New value is: '+accountId)

	def updateIssue(self, issueJiraNumber, fieldList):
		url = self.atlassianHost+'/rest/api/2/issue/'+issueJiraNumber
		
		payload = {
			"fields": {
				"summary": fieldList[0],
				"description": fieldList[1]
			}
		}
		
		print (self.invokeJiraAPI('PUT', url, payload))
		
		print ('updateIssue: issue '+issueJiraNumber+' has been updated with this info: '+str(fieldList))

	def getIssueData(self, issueId):
		url = self.atlassianHost+'/rest/api/2/issue/'+issueId
				
		payload = {}
		
		result = self.invokeJiraAPI( 'GET', url, payload)
				
		result = json.loads(result)
		
		return result

	def cloneIssue(self, issueJiraNumber, destinyProject):
		templateIssueFields = self.getIssueData(issueJiraNumber)
		
		print('cloning ->',issueJiraNumber)
		
		summary = templateIssueFields.get('fields').get('summary')
		description = templateIssueFields.get('fields').get('description')
		issueType = templateIssueFields.get('fields').get('issuetype').get('name')
		
		print('this template issue contains the next information:')
		print('summary:',summary)
		print('description:',description)
		print('issueType:',issueType)
		
		parentKey = self.createIssue(destinyProject, summary, description, issueType)
		print('Jira parent issue has been created ->',parentKey)
		
		tmpSubtasks = templateIssueFields.get('fields').get('subtasks')

		for subtask in tmpSubtasks:
			subtaskFullData = self.getIssueData(subtask.get('key'))		
			
			newSubtaskKey = self.createSubtask(destinyProject, parentKey, subtaskFullData.get('fields').get('summary'), subtaskFullData.get('fields').get('description'))
			
			print ('new subtask created ->', newSubtaskKey,'parent ->',parentKey)
			
		return parentKey

	def executeJql(self, query):
		
		url = self.atlassianHost+'/rest/api/2/search?jql='+query
		
		payload = {}
		
		result = self.invokeJiraAPI( 'GET', url, payload)
				
		result = json.loads(result)
		
		return result
