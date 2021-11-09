#"""
#Maze 
#Created on Thu Sep  5 17:02:52 2019
#Author: Juan Vanegas Maya
#"""
import copy
import random
import cgi, cgitb
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
cgitb.enable()
    
form = cgi.FieldStorage( )

cols=int(form.getvalue('cols'))
rows=int(form.getvalue('rows'))
backgroundColor=form.getvalue('bkgndclr')
textColor=form.getvalue('textclr')
print("Content-type: text/html\n\n")


def mazeGen(rows, cols) :
    mazeString=""
    try :
       (rows, cols) = (rows, cols) # accepts 2 command line arguments
    except (ValueError, IndexError) :
       print("2 command line arguments expected...")
       print("Usage: python maze.py rows cols")
       print("       minimum rows >= 15 minimum cols >= 15 / maximum rows <= 25 maximum cols <= 25")
       quit( )
    try :
       assert rows >= 15 and rows <= 25 and cols >= 15 and cols <= 25
    except AssertionError :
       print("Error: maze dimensions must be at least 15 x 15 and no greater than 25 x 25 ...")
       print("Usage: python maze.py rows cols")
       print("       minimum rows >= 15 minimum cols >= 15 / maximum rows <= 25 maximum cols <= 25")
       quit( )
    
    rows-=1
    cols-=1
    (blank, roof, wall, corner) = ' -|+'
    M = str(roof * int(cols / 2))
    n = random.randint(1, (int(cols / 2)) * (int(rows / 2) - 1))
    
    for i in range(int(rows / 2)) :
       e = s = t = ''
       N = wall
       if i == 0 :
          t = '@'  # add entry marker '@' on first row first col only
       # end if
       for j in range(int(cols / 2)) :
          if i and(random.randint(0, 1) or j == 0) :
             s += N + blank
             t += wall
             N = wall
             M = M[1 : ] + corner
          else :
             s += M[0] + roof
             if i or j :
                t += blank  # add blank to compensate for '@' on first row only
             # end if
             N = corner
             M = M[1 : ] + roof
          # end if / else
          n -= 1
          t += ' #' [n == 0]
       # end for
       if cols & 1 :
          s += s[-1]
          t += blank
          e = roof
       # end if
       mazeString+=s + N + '\n' + t + wall +'\n'
    # end for
    
    if rows & 1 :
       mazeString+=t + wall+'\n'
    # end if
    mazeString+=roof.join(M) + e + roof + corner+'\n'
    return mazeString
#Create a 2D Array
def createMazeMatrix(mazeString, rows, cols):
    mazeTempArray=[]
    mazeArray=[]
    mazeString=mazeString.replace("\n","")
    for i in range(0,len(mazeString),cols):
        for j in range(0,cols):
            mazeTempArray.append(mazeString[j+i])
        mazeArray.append(mazeTempArray[i:i+cols])
    return(mazeArray)
    
def traverseMaze(maze):
    searchReference="123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    searchPathCharacters=''
    east=1
    north=0
    stackPosition=[]
    searchPath=[]
    while maze[east+1][north]!='#' and maze[east][north+1]!='#':
        if maze[east][north+1]==' ':
            coord=[east,north+1]
            stackPosition.append([coord, 'N'])
        if maze[east+1][north]==' ': 
            coord=[east+1,north]
            stackPosition.append([coord, 'E']) 
        if maze[east+1][north]!=' ' and maze[east][north+1]!=' ':
            while stackPosition[-1][0][0]==stackPosition[-2][0][0] or stackPosition[-2][0][1]==stackPosition[-1][0][1]:
                stackPosition.pop()
            stackPosition.pop()
        east=stackPosition[-1][0][0]
        north=stackPosition[-1][0][1]
        searchPath.append([east,north,stackPosition[-1][-1]])
    pathCounter=0
    for i in range(0,len(searchPath)-1):
        searchPathCharacters+=searchReference[pathCounter]
        maze[searchPath[i][0]][searchPath[i][1]]=searchReference[pathCounter]
        if searchPath[i][-1]!=searchPath[i+1][-1] or searchPath[i+1][0]<searchPath[i][0]:#differenceEast1!=differenceEast2 and differenceNorth1!=differenceNorth2:
            pathCounter+=1
    maze[searchPath[i+1][0]][searchPath[i+1][1]]=searchReference[pathCounter]
    searchPathCharacters+=searchReference[pathCounter]
    #Add two last coordinates
    if stackPosition[-1][-1]=='N' :
        lastCoord=[east,north+1]
        stackPosition.append([lastCoord, 'N'])
        if maze[stackPosition[-1][0][0]][stackPosition[-1][0][1]]!='#':
            lastCoord=[east,north+2]
            stackPosition.append([lastCoord, 'N'])
    elif stackPosition[-1][-1]=='E':
        lastCoord=[east+1,north]
        stackPosition.append([lastCoord, 'E'])
        if maze[stackPosition[-1][0][0]][stackPosition[-1][0][1]]!='#':
            lastCoord=[east+2,north]
            stackPosition.append([lastCoord, 'E'])
    #Direction determining
    i=len(stackPosition)
    j=1
    while i>0:
        i-=1
        if stackPosition[i][0][0]!=stackPosition[i-1][0][0] and stackPosition[i][0][1]!=stackPosition[i-1][0][1]:
            if i!=0:
                stackPosition.pop(i-1)       
            i-=1
    directions=''
    for direction in stackPosition:
        directions+=direction[-1]
    newMaze=''
    for item in maze:
        newMaze+=''.join(item)+'\n'
    spaces=0
    posibilities=0
    for item in newMaze:
        if item==' ':
            spaces+=1
        if item!='-' or item!='|' or item!='+':
            posibilities+=1
    totalSearches=(posibilities-spaces)/posibilities       
    return newMaze, directions,searchPathCharacters,totalSearches
#Send email function
def sendEmail(finalMazeSolved,toaddr):
    fromaddr = "fromemail@gmail.ca"      # modify    
    msg = MIMEMultipart( )
    
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "HTML Maze Solution"         # modify
    
    body = str(finalMazeSolved[0])+"\n"
    body+="Directions: "+finalMazeSolved[1]+"\n"
    body+="Path: "+finalMazeSolved[2]+"\n"
    body+="Total Search percentage: "+str(finalMazeSolved[3])+"%"
    body.replace(" ","\s")
    msg.attach(MIMEText(body,'plain'))
    
    
    server = smtplib.SMTP('outlook.office365.com', 587)
    server.starttls( )
    server.login(fromaddr, "password")  # modify
    text = msg.as_string( )
    server.sendmail(fromaddr, toaddr, text)
    server.quit( )
    return True

print("<html><head><title>cgi script...</title></head>\n")
print("<body><pre>\n")
print("<style type=\"text/css\"> \
 body { background-color: ",backgroundColor,";color: ",textColor,"} \
</style>")
toaddr =form.getvalue('email')
mazeString=mazeGen(rows, cols)
mazeArray=createMazeMatrix(mazeString, rows, cols)
newMaze = copy.deepcopy(mazeArray)
finalMazeSolved=traverseMaze(newMaze)
finalMaze=finalMazeSolved[0]
directions=finalMazeSolved[1]
searchPath=finalMazeSolved[2]
print(finalMaze)
print("Maze Dimensions:(",cols,",",rows,")")
print("		Directions:",directions)
print("		Path:",searchPath)
print("     Total Searche percentage: ",finalMazeSolved[3]," %")
if sendEmail(finalMazeSolved,toaddr):
    print("Email was sent")
print("</pre></body></html>\n")