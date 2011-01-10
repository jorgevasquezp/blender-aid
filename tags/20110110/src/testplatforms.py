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
# (c) 2009, At Mind B.V. - Jeroen Bakker, Monique Dewanchand
import unittest
import os


class Platform(unittest.TestCase):
    def runt(self, version):
        print("testing on python"+version+" platform.")
        self.assertTrue(os.system("python"+version+" testscenarios.py") ==0)
        self.assertTrue(os.system("python"+version+" testsvn.py") ==0)
    def testPython25(self):
        self.runt("2.5")
    def testPython26(self):
        self.runt("2.6")
    def testPython30(self):
        self.runt("3.0")
    def testPython31(self):
        self.runt("3.1")
        
        
if __name__ =='__main__':
    #os.argv.append("-v")
    unittest.main()
