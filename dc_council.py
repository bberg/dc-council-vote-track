__author__ = 'benberg'
import os
import csv
import requests
from pprint import pprint as pp
import re
import json
import pdf2image
import pytesseract
from pytesseract import Output
import argparse
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle
import datetime

# Deprecated
def getVoteDetailsByCouncilPeriod(councilPeriodId,rowLimit=100,offset=0):
    payload = '{"councilPeriodId": '+str(councilPeriodId)+',}'
    res = callAPI('LegislationVoteDetails/'+str(rowLimit)+"/"+str(offset),type='post',payload=payload)
    return res,rowLimit,offset

# Deprecated
def getVotesSimple(councilPeriodId):
    res_text = ""
    rowOffset = 0
    rowLimit = 30000
    fullResults = ""
    while (res_text != "[]"):
        print("Getting rows "+str(rowOffset)+" through "+str(rowLimit+rowOffset))
        res = getVoteDetailsByCouncilPeriod(councilPeriodId,rowLimit,rowOffset)
        res_text = res[0].text
        if (res_text != "[]"):
            fullResults=fullResults[:-1]+","
            fullResults+=res_text[1:]
        rowOffset += rowLimit
        # print(res[0].text)
    fullResults = "["+fullResults[1:]
    # print(fullResults)
    results = json.loads(fullResults)
    print(len(results), "results")
    votes = {}
    for i in results:
        if i['legislationNumber']+"-"+i['description'] not in votes:
            votes[i['legislationNumber']+"-"+i['description']]={
                'title' : i['title']
                ,'legislationNumber': i['legislationNumber']
                ,'description': i['description']
                ,'voteType': i['voteType']
                ,'voteResult': i['voteResult']
                ,'voteDate': i['voteDate']
                ,'voteDateForSearch':i['voteDateForSearch']
                ,'introducerId':i['introducerId']
                ,'memberVote':i['memberVote']
                ,'votes':{}
            }
        votes[i['legislationNumber']+"-"+i['description']]['votes'][i['councilMember']] = i['memberVote']

    # pp(votes)
    simpleVotes = []
    for key,val in votes.items():
        simple = val['votes']
        simple['name'] = key
        simple['title'] = val['title']
        simple['voteDateForSearch']=val['voteDateForSearch']
        simpleVotes.append(simple)

    print(len(simpleVotes), "votes")
    # pp(simpleVotes)

    keys = []
    for i in simpleVotes:
        for key,val in i.items():
            if key not in keys:
                keys.append(key)

    print("fields:", keys)

    with open(councilPeriodId+'.csv', 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(simpleVotes)

# Generic utility for calls to LIMS APIs
def callAPI(api,type='get',payload=''):
    headers = {'Authorization':token}
    baseURL = 'https://lims.dccouncil.us/api/v2/PublicData/'
    delayBetweenRequests = .3
    global lastAPIrequest
    td = (datetime.datetime.now() - lastAPIrequest).total_seconds()
    if td < delayBetweenRequests:
        print("Rate limited, waiting. Programmed delay between requests: "+str(delayBetweenRequests)+" seconds")

    while((datetime.datetime.now() - lastAPIrequest).total_seconds() < delayBetweenRequests):
        pass

    if type =='post':
        headers['Content-Type'] = "application/json-patch+json"
        res = requests.post(baseURL+api,payload,headers=headers)

    else:
        res = requests.get(baseURL+api,headers=headers)

    if res.status_code != 200:
        for item in res:
            print(item)
    else:
        lastAPIrequest = datetime.datetime.now()
        return res

# Gets a list of council members for a period
def getCouncilMembers(councilPeriodId):
    res = callAPI("members/"+councilPeriodId)
    members = []
    data = json.loads(res.text)
    for i in data:
        members.append(i['name'])
    return members

# For processing individual bills
class Bill:
    def getLegislationDetails(self):
        res = callAPI('LegislationDetails/'+str(self.id))
        self.data = json.loads(res.text)

    def reformatVotes(self,pdfVotes):
        votes = []
        for v in pdfVotes:
            found = False
            for official_name in self.councilMembers:
                if re.search(v['name'],official_name,re.IGNORECASE):
                    found = True
                    votes.append({
                        "councilMember":official_name
                        ,"vote":v['vote']
                    })
            if found == False:
                print("ERROR FINDING COUNCILMEMBER VOTER NAME LOOKUP")
                print(v)
        voteDetails = {
            'voteType':'unknown'
            # TODO extract vote type
            ,'voteResult':'unknown'
            # TODO extract vote result
            ,'votes':votes
        }
        return voteDetails

    def processActions(self):
        if self.data['actions'] != None:
            if len(self.data['actions'])>0:
                for i in range(0,len(self.data['actions'])):
                    self.getActionResults(i)
            self.incorporateNewActions()

    def getActionResults(self,actionID):
        thisAction = self.data['actions'][actionID]
        thisAction['voteProcessingType'] = ''
        if thisAction['attachment']!=None and thisAction['attachment']!='None':
            thisAction['pdf_path'] = thisAction['attachment'].split('LIMS/')[1].replace("/","_")
            path_strings = thisAction['attachment'].split('LIMS/')[1].split("/")
            thisAction['lims_bill_code'] = path_strings[0]
            thisAction['lims_meeting_id'] = path_strings[1]
            thisAction['lims_type'] = path_strings[2]
            thisAction['lims_str'] = path_strings[3]
        else:
            thisAction['voteProcessingType'] = 'noAttachment'

        if thisAction['voteDetails'] == None and thisAction['voteProcessingType'] != 'noAttachment':
            print("Attempting PDF Decoding for "+thisAction['pdf_path'])
            thisAction['voteProcessingType'] = 'decodeFromPDFAttempt'
            response = requests.get(thisAction['attachment'])
            if response.status_code == 200:
                with open(thisAction['pdf_path'], 'wb') as f:
                    f.write(response.content)
            res = readPDF(thisAction['pdf_path'])
            if len(res)==0:
                thisAction['voteProcessingType'] = 'decodeFromPDFNoResult'
            if len(res)>0:
                # first we'll process the first result, then we'll check for subsequent votes and process those
                thisAction['voteProcessingType'] = 'decodeFromPDFSuccess'
                thisAction['pdf_extracted_title']= res[0]['title']
                thisAction['pdf_extracted_votes']= res[0]['votes']
                thisAction['voteDetails'] = self.reformatVotes(thisAction['pdf_extracted_votes'])
            if len(res)>1:
                for i in res[1:]:
                    newAction = thisAction.copy()
                    newAction['voteProcessingType'] = 'decodeFromPDFMultipleVote'
                    newAction['pdf_extracted_title']= i['title']
                    newAction['pdf_extracted_votes']= i['votes']
                    newAction['voteDetails'] = self.reformatVotes(newAction['pdf_extracted_votes'])
                    self.newActions.append(newAction)
        else:
            thisAction['voteProcessingType'] = 'LIMSProvided'
            thisAction['pdf_extracted_title']= ''
            thisAction['pdf_extracted_votes']= {}

        #     overwrite the data object with the updates
        self.data['actions'][actionID] = thisAction

    def incorporateNewActions(self):
        for i in self.newActions:
            self.data['actions'].append(i)

    def __init__(self,id):
        self.id = id
        self.getLegislationDetails()
        self.councilMembers = councilMembers
        self.newActions = []

# Loading the name of each bill in a council period
def getBulkData(categoryId, councilPeriodId):
    res = callAPI("/BulkData/"+str(categoryId)+"/"+str(councilPeriodId),type='post')
    data = json.loads(res.text)
    return data

# Gets list of bills
def getListOfBills(type,councilId):
    data = getBulkData(type,councilId)
    listOfBills = listBillsFromBulkData(data)
    return listOfBills

# Transforms bills into list of dicts
def listBillsFromBulkData(data):
    billList = []
    for i in data:
        billList.append({
            "status":"unprocessed"
            ,"legislationNumber":i['legislationNumber']
        })
    return billList

# Load bill status from CSV
def loadBillListFromCSV(type,councilId):
    bills = []
    with open(billListFilename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bills.append(row)
    return bills

# Update CSV with Bill Status
def writeBillStatusToCSV(type,councilId,listOfBills):
    keys = listOfBills[0].keys()
    with open(billListFilename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=keys)
        writer.writeheader()
        writer.writerows(listOfBills)

# For each bill, get bill details from LIMS and run analysis of PDF to determine voting record if needed
def processListOfBills(type,councilPeriodId,billList):
    for index,billToProcess in enumerate(billList):
        thisLegislationNumber = billToProcess['legislationNumber']
        if billToProcess['status'] == 'unprocessed':
            print("processing: ", thisLegislationNumber)
            b = Bill(thisLegislationNumber)
            b.processActions()
            with open (os.path.join(dataDir,councilDir,(thisLegislationNumber+".pkl")),'wb') as output:
                pickle.dump(b,output,pickle.HIGHEST_PROTOCOL)
            billToProcess['status'] = 'saved'
            billList[index] = billToProcess
            writeBillStatusToCSV(type,councilPeriodId,billList)

# Returns a list of
def outputListOfBillsResults(type,councilPeriodId,billList):
    allActionsList = []
    for index,billToProcess in enumerate(billList):
        thisLegislationNumber = billToProcess['legislationNumber']
        if billToProcess['status'] == 'unprocessed':
            print("ERROR - LIST NOT FULLY PROCESSED, run processListOfBills first")
            print("unprocessed: ", thisLegislationNumber)
            break

        if billToProcess['status'] == 'saved':
            print("outputting: ", thisLegislationNumber)
            thisBillActionList = outputLegislation(type,councilPeriodId,thisLegislationNumber)
            print ("found "+str(len(thisBillActionList))+" actions for "+thisLegislationNumber)
            for a in thisBillActionList:
                allActionsList.append(a)

    keys = []
    for i in allActionsList:
        for key,val in i.items():
            if key not in keys:
                keys.append(key)

    print("fields:", keys)

    with open(outputFilename, 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(allActionsList)

    # TODO consider updating status on bill list once output
    # billToProcess['status'] = 'output'
    # billList[index] = billToProcess
    # writeBillStatusToCSV(type,councilPeriodId,billList)

# For a processing a single bill, returns a list of all bill and action details as a 1-layer Dict for each action on the bill; or if there were no actions, returns just a single list item with details for the bill
def outputLegislation(type,councilPeriodId,legislationNumber):
    with open (os.path.join(dataDir,councilDir,(legislationNumber+".pkl")),'rb') as input:
        b = pickle.load(input)
    outputListByActions = []
    outputDict = {}
    # Just pull these simple fields through directly
    simpleBillFields = [
        'additionalInformation'
        ,'atTheRequestOf'
        ,'category'
        ,'coSponsors'
        ,'committeeHearing'
        ,'committeeMarkup'
        ,'committeeReReferral'
        ,'committeeReferralDate'
        ,'committeesReferredTo'
        ,'committeesReferredToWithComments'
        ,'congressionalReview'
        ,'councilPeriodId'
        ,'introducers'
        ,'introductionDate'
        ,'introductionPublicationDate'
        ,'legislationDocument'
        ,'legislationId'
        ,'legislationNumber'
        ,'linkedLegislation'
        ,'mayoralReview'
        ,'otherDocuments'
        ,'placeOfIntroduction'
        ,'placeRead'
        ,'resolutionDetails'
        ,'shortDescription'
        ,'status'
        ,'subCategory'
        ,'title'
        ,'vendorName'
        ,'withdrawnBy'
        ,'withdrawnDate'
    ]
    for simpleBillField in simpleBillFields:
        if simpleBillField in b.data:
            outputDict[simpleBillField] = str(b.data[simpleBillField])
        else:
            outputDict[simpleBillField] = ''

    outputActionDict = {}
    actionFields = [
        'action'
        ,'actionDate'
        ,'attachment'
        ,'attachmentType'
        ,'lims_bill_code'
        ,'lims_meeting_id'
        ,'lims_str'
        ,'lims_type'
        ,'pdf_extracted_title'
        ,'pdf_extracted_votes'
        ,'pdf_path'
        ,'videoLink'
        ,'voteProcessingType'
    ]
    voteFields = [
        'voteResult'
        'voteType'
    ]

    if "actions" in b.data and b.data['actions'] != None:
        for action in b.data['actions']:
            outputActionDict = {}
            for actionField in actionFields:
                if actionField in action:
                    outputActionDict[actionField] = str(action[actionField])
                else:
                    outputActionDict[actionField] = ''


            if action['voteDetails'] != None:
                for voteField in voteFields:
                    if voteField in action['voteDetails']:
                        outputActionDict[voteField] = action['voteDetails'][voteField]
                    else:
                        outputActionDict[voteField] = ''


                if 'votes' in action['voteDetails']:
                    votes = action['voteDetails']['votes']
                    if votes != None:
                        for voter in votes:
                            outputActionDict[voter['councilMember']] = voter['vote']

            thisOutputDict = {}
            thisOutputDict.update(outputDict)
            thisOutputDict.update(outputActionDict)
            outputListByActions.append(thisOutputDict)

    else:
        for actionField in actionFields:
            outputActionDict[actionField] = ''
        thisOutputDict = {}
        thisOutputDict.update(outputDict)
        thisOutputDict.update(outputActionDict)
        outputListByActions.append(thisOutputDict)

    return outputListByActions

# Read a PDF and return vote results if votes were recorded in the pdf
def readPDF(filename,debug=False):
    filenameBase = filename.split('.')[0]
    if debug == True:
        from PIL import ImageDraw

    # Open the PDF
    file = open(filename, 'rb')
    votes = []
    img = pdf2image.convert_from_path(filename)
    for page_num,this_page in enumerate(img):
        # Run OCR on the image to get the locations of various elements
        data = pytesseract.image_to_data(this_page,output_type=Output.DICT)
        if page_num == 9:
            x = 2+2
        if 'RollCall.html' in data['text']:
            subPage = this_page.copy()
            subPage = subPage.crop((0,375,subPage.width,451))
            title = pytesseract.image_to_string(subPage)

            # These were set by trial and error
            x_offset = 27
            y_offset = 5


            # Get column header x-location for different vote outcomes
            vote_x_axis = {}
            for i in ['Yes','No','Present','Absent']:
                index = data['text'].index(i)
                vote_x_axis[i] = (data['left'][index] + (data['width'][index]/2))+x_offset


            # Get row y-location for each councilmember
            # TODO fix for councilmembers with multiple word names (Robert & Trayon white)
            councilmembers = []
            nextFlag = False
            for index, value in enumerate(data['text']):
                if (nextFlag == True):
                    councilmembers.append({
                        "name":value
                        ,"index":index
                        ,"y-loc": (data['top'][index] + (data['height'][index]/2))+y_offset
                    })
                if (value == "COUNCILMEMBER" or value == "CHAIRMAN" or value == "CHAIRWOMAN"):
                    nextFlag = True
                else:
                    nextFlag = False


            rgb_im = this_page.convert('RGB')
            if debug == True:
                draw = ImageDraw.Draw(rgb_im)

            # for each councilmember
            for c in councilmembers:
                c['vote'] = 'Unknown'

                # for each vote outcome
                for key,value in vote_x_axis.items():

                    # get the color of the pixel at the location where the vote would be marked
                    c[key] = rgb_im.getpixel((value,c['y-loc']))

                    # If the pixel value for this dot isn't close to being blank, then mark this dot as the vote
                    if c[key][0] + c[key][1] + c[key][2] < 700:
                        if (c['vote'] == 'Unknown'):
                            c['vote'] = key
                        else:
                            print("ERROR MULTIPLE VOTES MARKED")

                    if debug == True:
                        draw.ellipse((value-2,c['y-loc']-2,value+2,c['y-loc']+2), fill=128)

            if debug == True:
                del draw
                rgb_im.save(filenameBase+'.png')
            print(title)
            votes.append({
                'title':title
                ,'votes':councilmembers
            })

        else:
            print("no votes on page "+str(page_num))

    # pp(votes)
    return votes

if __name__ == "__main__":
    # TODO feature to update a bill if last update is older than a specified date or duration

    parser = argparse.ArgumentParser()
    parser.add_argument("token",type=str,help="LIMS access token, Get your token from https://lims.dccouncil.us/developerRegistration")
    parser.add_argument("councilPeriodId", type=str, help="Council Period ID, https://lims.dccouncil.us/api/help/index.html#!/PublicData/GetCouncilPeriods, default=24 (2021-2022)",default="24")
    parser.add_argument("legislationType", type=str, help="Legislation Type, see https://lims.dccouncil.us/api/help/index.html#!/PublicData/GetLegislationCategories, default=1 (Bill)",default="1")

    args = parser.parse_args()
    type = args.legislationType
    councilPeriodId = args.councilPeriodId
    token = args.token

    # Setup global variables
    global lastAPIrequest
    lastAPIrequest = datetime.datetime.now()
    billListFilename = "listOfBills_"+str(type)+"_"+str(councilPeriodId)+'.csv'
    outputFilename = "outputListOfVotes_"+str(type)+"_"+str(councilPeriodId)+'.csv'
    councilMembers = getCouncilMembers(councilPeriodId)
    dataDir = 'data'
    councilDir = type+"_"+councilPeriodId
    councilDataDir = os.path.join(dataDir,councilDir)
    dirs = [
        dataDir
        ,councilDataDir
    ]
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)

    # If this is our first time running with the current type & council period, set up!
    if not os.path.exists(billListFilename):
        listOfBills = getListOfBills(type,councilPeriodId)
        writeBillStatusToCSV(type,councilPeriodId,listOfBills)

    # Process the bills
    billList = loadBillListFromCSV(type,councilPeriodId)
    processListOfBills(type,councilPeriodId,billList)

    # Clean up the output data into a single flat CSV
    billList = loadBillListFromCSV(type,councilPeriodId)
    outputListOfBillsResults(type,councilPeriodId,billList)

    # TESTING ===================================
    # outputLegislation(type,councilPeriodId,"B23-0760")
    # getVotesSimple(councilPeriodId)






