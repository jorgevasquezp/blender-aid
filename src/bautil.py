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
# (c) 2009, At Mind B.V. - Jeroen Bakker

# This file is used to support python 2.5.
# blender-aid uses some python 2.6 specific functions.
# in this file these functions will get a python 2.5 variant.
# using exception handling on the import
# functions will be redirected to this file
# --- see example
#try:
#    from os.path import relpath as _relpath
#except:
#    print("python < 2.6: import custom relpath")
#    from bautil import relpath as _relpath
# --- end example

#original code:
# relpath.py (http://code.activestate.com/recipes/302594/)
# R.Barran 30/08/2004
# adaptions:
# in python 2.6 the target does not exist is not implemented
# in blender-aid the check has to be removed as the missing links will
# not have a target

import os

def relpath(target, base=os.curdir):
    """
    Return a relative path to the target from either the current dir or an optional base dir.
    Base can be a directory specified either as absolute or relative to current dir.
    """
# --- removed from original source
#    if not os.path.exists(target):
#        raise OSError, 'Target does not exist: '+target
# --- end remove

    if not os.path.isdir(base):
        raise OSError('Base is not a directory or does not exist: '+base)

    base_list = (os.path.abspath(base)).split(os.sep)
    target_list = (os.path.abspath(target)).split(os.sep)

    # On the windows platform the target may be on a completely different drive from the base.
    if os.name in ['nt','dos','os2'] and base_list[0] != target_list[0]:
        raise OSError('Target is on a different drive to base. Target: '+target_list[0].upper()+', base: '+base_list[0].upper())

    # Starting from the filepath root, work out how much of the filepath is
    # shared by base and target.
    for i in range(min(len(base_list), len(target_list))):
        if base_list[i] != target_list[i]: break
    else:
        # If we broke out of the loop, i is pointing to the first differing path elements.
        # If we didn't break out of the loop, i is pointing to identical path elements.
        # Increment i so that in all cases it points to the first differing path elements.
        i+=1

    rel_list = [os.pardir] * (len(base_list)-i) + target_list[i:]
    return os.path.join(*rel_list)