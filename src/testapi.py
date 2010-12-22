import blenderaidapi as api
server = api.Server(("localhost", 8080))

print ("Add production")
server.addProduction("Yo Frankie!", "/tmp/yf", "http://192.168.1.12/svn/yofrankie", "jbakker", "zx098zx")
production = server.getProductions()[0]
print ("Activate production")
production.activate()
print ("Find file")
file = production.getFiles(name="frankie.blend")[0]
print("Rename file")
file.rename("frankiemomo.blend")
file = production.getFiles(name="frankiemomo.blend")[0]
element = file.getElements(name="GRFlyingSquirrel")[0]
references = element.getReferencesTo()
for reference in references:
    print(reference)
print("Rename element")
element.rename("GRFrankie")
    
print ("Find file")
file = production.getFiles(name="frankie_testlevel.blend")[0]
print("Move file")
file.move("levels")

directories = production.getDirectories()
print(directories)
print(directories[0].getFiles()[0])

link = production.getMissingLinks()[2]
print(link)
matches = link.getPossibleMatches()
for match in matches:
    print(match)
    if match.match == 1.0:
        match.fix()
        break

