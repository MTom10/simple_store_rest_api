"""
blocklist.py

This file contains the blosklist of JWT tokens.

will be imported by app and the logout resource so that tokens can be added to the blocklist when the user logs out

change it later to DP ro redit as set will be erased after app reset !
"""

BLOCKLIST  = set()