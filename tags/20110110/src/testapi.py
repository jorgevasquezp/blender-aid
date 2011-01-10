# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
#
# (c) 2010, At Mind B.V. - Jeroen Bakker, Monique Dewanchand
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

