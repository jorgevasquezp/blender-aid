import hotshot
import hotshot.stats
import indexer

def test():
    production=indexer.getActiveProduction()
    indexer.deleteElements(production[0])
    indexer.updateIndex(production[0])
    
prof = hotshot.Profile("blendfile")
benchtime = prof.runcall(test)
prof.close()
stats = hotshot.stats.load("blendfile")
stats.strip_dirs()
stats.sort_stats('time', 'calls')
stats.print_stats(20)
