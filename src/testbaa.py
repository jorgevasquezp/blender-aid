import blenderaidapi

server = blenderaidapi.Server(("localhost", 8080))
productions = server.getProductions()
print(productions)

productions = server.getProductions(name="YF")
print(productions)

production = server.getActiveProduction()
print(production)

for file in production.getFiles():
    print(file)

for missinglink in production.getMissingLinks():
    print(missinglink)
    for match in missinglink.getPossibleMatches():
        print(" - "+str(match))