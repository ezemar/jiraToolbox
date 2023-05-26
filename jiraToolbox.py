# -*- coding: utf-8 -*-

import json, os, inspect

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
		try:
		
			basic = HTTPBasicAuth(self.atlassianEmail, self.atlassianToken)
		
			response = requests.request(
								method= httpMethod,
								url= url, 
								data=json.dumps( payload ), 
								headers= {
									"Content-Type": "application/json"
									
										},
								auth = basic
								
								)
			#print (response.text)
			if response.status_code != 200:
				print(inspect.stack()[0][3]+': the module received a HTTP STATUS error code. Request was >', httpMethod, url, 'check the payload and url. Details:',response.text )
				raise Exception
			
			else:
				return(response).text
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')			

	def deleteIssue(self, issueId):
		try:
			url = self.atlassianHost+'/rest/api/2/issue/'+issueId		
			payload = {}
			result = invokeJiraAPI( 'DELETE', url , payload)
			#print (result)
			result = json.loads(result)
			print (result.get('key'))
			if (result.get('key')) != "":
				return result.get('key')	
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')

	def createIssueWithAttachments(self, projectCode, summary, description, issueType, attachmentsJsonObject):
		try:
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
				   },
				   "attachment" : attachmentsJsonObject
			   }
			}
			result = self.invokeJiraAPI('POST', url, payload)
			print (result)
			result = json.loads(result)
			print (result.get('key'))
			if (result.get('key')) != "":
				return result.get('key')	
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')

	def createIssue(self, projectCode, summary, description, issueType):
		try:
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
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')

	def createSubtask(self, projectCode, parentIssueKey, summary, description):
		try:
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
			#print (result.get('key'))
			if (result.get('key')) != "":
				return result.get('key')	
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')

	def createIssueAndAssign(self, projectCode, summary, description, issueType, userEmail):
		try:
			accountId = self.getUserInfoByEmail(userEmail)
			createdIssue = self.createIssue(projectCode,summary,description,issueType)
			result = self.assigneeIssue(createdIssue, accountId) 
			print (result)
			result = json.loads(result)
			print (result.get('key'))
			if (result.get('key')) != "":
				return result.get('key')	
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')

	def getUserInfoByEmail(self, emailJiraUser):
		try:
			url = self.atlassianHost+'/rest/api/2/user/search?query=' + emailJiraUser		
			result = self.invokeJiraAPI( 'GET', url, '')
			result = json.loads(result)
			if len(result) > 0:
				if (result[0].get('accountId') != "" and result[0].get('displayName') != ""):
					return result[0]
			else:
				print(inspect.stack()[0][3]+': exception while executing the function the user "'+emailJiraUser+'" does not exists!')
				raise Exception	
		except Exception as details:
			print(inspect.stack()[0][3]+': exception while executing the function!', details)

	def assignIssue(self, issueJiraNumber, userEmail):
		try:
			url = self.atlassianHost+'/rest/api/2/issue/'+issueJiraNumber
			if userEmail != '':
				accountId = self.getUserInfoByEmail(userEmail).get('accountId')

				payload = {
					"fields": {
						"assignee":{"accountId": accountId }
					}
				}
			else:
				payload = {
					"fields": {
						"assignee":{"name": None }
					}
				}
				
			print ( self.invokeJiraAPI('PUT', url, payload))
			
			if userEmail != '':
				print ('assignIssue: issue '+issueJiraNumber+'. New assignee value is: '+accountId+' ('+userEmail+')')
			else:
				print ('assignIssue: issue '+issueJiraNumber+'. New assignee value is: None')
	
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')
				
	def updateIssue(self, issueJiraNumber, fieldList):
		try:
			url = self.atlassianHost+'/rest/api/2/issue/'+issueJiraNumber
			
			payload = {
				"fields": {
					"summary": fieldList[0],
					"description": fieldList[1]
				}
			}
			
			print (self.invokeJiraAPI('PUT', url, payload))
			print ('updateIssue: issue '+issueJiraNumber+' has been updated with this info: '+str(fieldList))
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')
			
	def getIssueData(self, issueId):
		try:
			url = self.atlassianHost+'/rest/api/2/issue/'+issueId		
			payload = {}
			result = self.invokeJiraAPI( 'GET', url, payload)		
			result = json.loads(result)
			return result
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')

	def cloneIssue(self, issueJiraNumber, destinyProject):
		try:
			templateIssueFields = self.getIssueData(issueJiraNumber)
			print('cloning ->',issueJiraNumber)
			if not templateIssueFields.get('fields').get('issuetype').get('subtask'):
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
			
			elif templateIssueFields.get('fields').get('issuetype').get('subtask'):
				raise Exception('Error while cloning this issue. the type of issue is "subtask" and to clone an subtask, you need execute the cloneSubtask() function')
			
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')

	def assignIssueAndSubtasks(self, issueJiraNumber, userEmail):
		try:
			self.assigneeIssue(issueJiraNumber, userEmail);
			subtasksShortDataList = self.getIssueData(issueJiraNumber).get('fields').get('subtasks')
			for subtask in subtasksShortDataList:
				self.assigneeIssue(subtask.get('key') , userEmail);
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')
			
	def executeJql(self, query):
		try:
			url = self.atlassianHost+'/rest/api/2/search?jql='+query
			payload = {}
			result = self.invokeJiraAPI( 'GET', url, payload)	
			result = json.loads(result)
			return result
		except:
			print(inspect.stack()[0][3]+': exception while executing the function!')
