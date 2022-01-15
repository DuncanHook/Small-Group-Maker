import sys
import math
import itertools
import networkx as nx


#import matplotlib.pyplot as plt
#import matplotlib as mpl

#FUNCTIONS

############################################################
#                     graphCreation()                      #
# creates edges for the graph if they dont exist already.  #
# based on previously weeks added edges. Also sets up the  #
# groups for a given week. Uses in-degree to determine how #
# many people have visited a house before                  #
############################################################

def graphCreation(members, weeklyGroups, maxMembers, week):
    availableMembers = sorted(G.in_degree, key=lambda x: x[1]) #members in order of in-degree
    inDegrees = [lis[1] for lis in availableMembers]            #list of in degrees
    availableNames = [lis[0] for lis in availableMembers]
    buffer = math.floor(maxMembers/2)   #this ensures that there is room in the groups for extra people

    #sets up this weeks container for the groups.
    groupNames = []
    weight = []
    for i in range(weeklyGroups):
        group = []
        weight.append(0)
        for j in range(maxMembers + buffer):
            group.append(0)
        groupNames.append(group)            #groupNames[row][column], groupnames[row][0] = group weight, groupnames[row][1] = host
    
    #redundant check just in case, skips to end of function if every node has
    #been visited by every other node using the in-degrees.
    if(inDegrees[0] != len(members) - 1):
        i = 0
        with open("smallgroups.txt", "a") as appendFile:
            appendFile.write("WEEK " + str(week) + "\n")
        appendFile.close() 

        while i < weeklyGroups:                 #rows
            
            groupNames[i][0] = (availableNames[i])
            currentIndex = 1
            j = i + 1

            if(availableNames[i].find(",") != -1):
                weight[i] += 2
            else:
                weight[i] += 1

            while weight[i] < maxMembers and j < len(availableNames):      #columns
                
                if(G.has_edge(availableNames[j], availableNames[i]) != True): #check if edge already exists, otherwise move on
                    G.add_edge(availableNames[j], availableNames[i])            #add edge if it doesnt exist.
                    if(availableNames[j].find(",") != -1):
                        weight[i] += 2
                    else:
                        weight[i] += 1
                    groupNames[i][currentIndex] = (availableNames[j])
                    availableMembers.pop(j)
                    availableNames.pop(j)
                    currentIndex += 1
                else:
                    j += 1
  
            i += 1        
    else:
        return   

    #deal with empty groups and missing members. 
    #ensures every individual has been added to a group.
    while len(availableMembers) > weeklyGroups:
        #print("MISSING " + str(len(availableMembers) - weeklyGroups) + " MEMBERS!!!!!!!")   
        shortGroup = -1
        i = 0
        while i < weeklyGroups:
            if groupNames[i][1] == 0:
                shortGroup = i
                emptyGroups(availableNames, weeklyGroups, shortGroup,
                            groupNames, weight, availableMembers)
                break
            i += 1

        atMinCapacity = True
        for item in weight:
            if item < maxMembers:
                atMinCapacity = False
        if atMinCapacity != True:    
            for idx, val in enumerate(weight):
                shortGroup = -1
                if val < maxMembers:
                    shortGroup = idx
                    shortGroups(availableNames, weeklyGroups, shortGroup, 
                    groupNames, weight, availableMembers)
        else:
            i = 0
            lastAdded = -1
            while i < weeklyGroups:
                for idx, val in enumerate(groupNames[i]):
                    if lastAdded == i:
                        continue
                    elif val == 0:
                        lastAdded = i
                        minCapacityGroups(availableNames, weeklyGroups, i, 
                        groupNames, weight, availableMembers, idx)
                            
                i += 1
                    

    printWeeklyGroups(weeklyGroups,groupNames)
    return
#########################################################
#                  intakeUserFile()                     #
# this function takes in a user input for a file name.  #
#  Validatest that the file actually exists before      #
# continuing the program                                #
#########################################################
def intakeUserFile():
    while True:
        user_file = input("Please input church member file name: ")
        try:
            my_file = open(user_file, "r")
        except OSError:
            print("Error accessing file, please try again: ")
        else:
            return my_file

#####################################################
#                 intakeGroupSize()                 #
# Takes in the user input for maximum group size of #
# a given set of people. Ensures that the value     #
# given is numerical before continuing.             #
#####################################################
def intakeGroupSize(message):
    while True:
        try:
            givenSize = int(input(message))
        except ValueError:
            print("Not an integer, please try again.")
        else:
            return givenSize

###############################################################
#                   emptyGroups()                             #
# This function is called after the initial groups are set    #
# up by graphCreation(). This is called when a group only     #
# contains the host in it. This will check if there are any   #
# other empty groups, and then check to see if the host of    #
# the checked group hasn't visited the original host we are   #
# looking at. Otheriwse this will add people  to the empty    #
# group. It will prioritize people who haven't visited the    #
# host, but will add those who have already visited in order  #
# to fill out the group.                                      #
###############################################################

def emptyGroups(availableNames, weeklyGroups, emptyGroup, 
                groupNames, weight, availableMembers):
    i = 0
    while i < len(availableNames):
        if i < weeklyGroups:
            if(G.has_edge(availableNames[i], availableNames[emptyGroup]) != True and 
                i != emptyGroup and groupNames[i][1] == 0):
                G.add_edge(availableNames[i], availableNames[emptyGroup])            #add edge if it doesnt exist.
                if(availableNames[i].find(",") != -1):
                    weight[emptyGroup] += 2
                    weight[i] -= 2
                else:
                    weight[emptyGroup] += 1
                    weight[i] -= 1
                groupNames[emptyGroup][1] = (availableNames[i])
                    #replace index with unused name in list
                groupNames[i][0] = availableNames[weeklyGroups]
                availableMembers.pop(weeklyGroups)
                availableNames.pop(weeklyGroups)
                return
        elif(G.has_edge(availableNames[i], availableNames[emptyGroup]) != True):
            G.add_edge(availableNames[i], availableNames[emptyGroup])
            if(availableNames[i].find(",") != -1):
                weight[emptyGroup] += 2
            else:
                weight[emptyGroup] += 1
            groupNames[emptyGroup][1] = (availableNames[i])
            availableMembers.pop(i)
            availableNames.pop(i)
            return        
        i += 1 

    #This section deals with non Unique Groups    
    j = weeklyGroups
    while j < len(availableNames):
        if(G.has_edge(availableNames[j], availableNames[emptyGroup]) != True):
            print("I SHOULDN'T BE HERE")
        elif(G.has_edge(availableNames[j], availableNames[emptyGroup]) == True):
            if(availableNames[j].find(",") != -1):
                weight[emptyGroup] += 2
            else:
                weight[emptyGroup] += 1
            groupNames[emptyGroup][1] = (availableNames[j])
            availableMembers.pop(j)
            availableNames.pop(j)
            return
        j += 1        


################################################################
#                      shortGroups()                           #
# This function is called after the initial groups are set     #
# up by graphCreation(). This will be called when a group      #
# hasnt reached minimum size yet (I.E. if the group only has   #
# 4 people, but the group size is 5, this function will be     #
# called). Prioritizes people who haven't yet visited the host #
# But will add those who have already visited if necessary     #
################################################################

def shortGroups(availableNames, weeklyGroups, shortGroup, 
                groupNames, weight, availableMembers):
    
    for idx, val in enumerate(groupNames[shortGroup]):
        if val != 0:
            continue
        else:
            j = weeklyGroups
            while j < len(availableNames):
                if(G.has_edge(availableNames[j], availableNames[shortGroup]) != True):
                    G.add_edge(availableNames[j], availableNames[shortGroup])            #add edge if it doesnt exist.
                    if(availableNames[j].find(",") != -1):
                        weight[shortGroup] += 2
                    else:
                        weight[shortGroup] += 1
                    groupNames[shortGroup][idx] = (availableNames[j])
                    #replace index with unused name in list
                    availableMembers.pop(weeklyGroups)
                    availableNames.pop(weeklyGroups)
                    return
                elif(G.has_edge(availableNames[j], availableNames[shortGroup]) == True):
                    if(availableNames[j].find(",") != -1):
                        weight[shortGroup] += 2
                    else:
                        weight[shortGroup] += 1
                    groupNames[shortGroup][idx] = (availableNames[j])
                    availableMembers.pop(j)
                    availableNames.pop(j)
                    return
                j += 1   


##################################################################
#                    minCapacityGroups()                         #
# This function is called after the initial groups are set       #
# up by graphCreation(). This is called when all of the groups   #
# for a given week have the minimum amount of members, but there #
# are still people who haven't been assigned to a group. This    #
# will prioritize people who haven't visited the hosts house,    #
# but will ensure all people are added to a group, even if they  #
# have already visited the hosts house                           #
##################################################################

def minCapacityGroups(availableNames, weeklyGroups, group, 
                    groupNames, weight, availableMembers, member):   
    j = weeklyGroups
    while j < len(availableNames):
                if(G.has_edge(availableNames[j], availableNames[group]) != True):
                    G.add_edge(availableNames[j], availableNames[group])            #add edge if it doesnt exist.
                    if(availableNames[j].find(",") != -1):
                        weight[group] += 2
                    else:
                        weight[group] += 1
                    groupNames[group][member] = (availableNames[j])
                    #replace index with unused name in list
                    availableMembers.pop(weeklyGroups)
                    availableNames.pop(weeklyGroups)
                    return
                elif(G.has_edge(availableNames[j], availableNames[group]) == True):
                    if(availableNames[j].find(",") != -1):
                        weight[group] += 2
                    else:
                        weight[group] += 1
                    groupNames[group][member] = (availableNames[j])
                    availableMembers.pop(j)
                    availableNames.pop(j)
                    return
                j += 1     

########################################################
#               printWeeklyGroups                      #
# This is called after every individual has been       #
# assigned to a group. This function writes all of the #
# groups for a given week to the output file.          #
########################################################

def printWeeklyGroups(weeklyGroups, groupNames):
    with open("smallgroups.txt", "a") as appendFile:                #print group to file.
        k = 0
        while k < weeklyGroups:
            appendFile.write("GROUP " + str(k+1) + ": (HOST) = ")
            for item in groupNames[k]:
                if item != 0 and item == groupNames[k][0]:
                    appendFile.write("%s " % item)
                elif item != 0:
                    appendFile.write("| %s " % item)
            if k + 1 == weeklyGroups:
                appendFile.write("\n\n")
            else:
                appendFile.write("\n")
            k+=1
    appendFile.close() 
    return


###############################################
#           Main Block of Code                #
###############################################

#retrieve filename and open the file
my_file = intakeUserFile()
content = my_file.read()

members_list = content.split()  #create list of members
my_file.close()                 #close file

#ensures that all entities in the file are distinct.
for i, j in itertools.combinations(members_list, 2):
    if i == j:
        print("Please ensure all names are wholly distinct")
        print(i + " is repeated.")
        sys.exit()

#create graph container
G = nx.DiGraph()

#create nodes
i = 0
while i < len(members_list):
    G.add_node(members_list[i])
    i += 1

#determine maximum theoretical group size
maxGroupSize = math.floor(len(members_list)/2)
#ask user what size group they want
maxGroupSizeDialogue = "What size of small groups? No larger than " + str(maxGroupSize) + " members:"

#validates that the group size is at least 2, and is under the maximum group size
groupSize = intakeGroupSize(maxGroupSizeDialogue)
while(groupSize > maxGroupSize or groupSize <= 1):
    if(groupSize > maxGroupSize):
        print("Please input smaller integer.")
        groupSize = intakeGroupSize(maxGroupSizeDialogue)
    elif(groupSize <= 1):
        print("Please input a larger group size.")
        groupSize = intakeGroupSize(maxGroupSizeDialogue)
groupsPerWeek = math.floor(len(members_list)/groupSize)

#creates output file
CreateFile = open("smallgroups.txt", "w+")
CreateFile.write("Smallgroups by Week\n")
CreateFile.close()
#starts at week 1
weekNumber = 1

#creates initial in-degree list for graph creation to use
currentInDegrees = [lis[1] for lis in sorted(G.in_degree, key=lambda x: x[1])]

#sets up groups for the week and sets up the graph. 
while currentInDegrees[0] != len(members_list) -1:
    graphCreation(members_list, groupsPerWeek,groupSize, weekNumber)
    #update the week number
    weekNumber += 1
    #update in-degree list for graph creation purposes
    currentInDegrees = [lis[1] for lis in sorted(G.in_degree, key=lambda x: x[1])]

#tell user where to find the output.
print("See smallgroups.txt for your assignments!")