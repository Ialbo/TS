#!/usr/bin/env python
# Copyright (C) 2010 Ion Torrent Systems, Inc. All Rights Reserved

from djangoinit import *
from iondb.rundb import models


def add_location(locStr):
    """Checks if a location exists and creates a location
    called <locStr> if none exist. """
    loc = models.Location.objects.all()
    for l in loc:
        if l.name in locStr:
            print("Location exists: %s" % l.name)
            return

    loc = models.Location(name=locStr)
    loc.save()
    print("Location Saved: %s" % locStr)
    return


def add_fileserver(location, directory):
    """Creates a default fileserver called <location> with directory
    <directory> if one does not exist"""
    fs = models.FileServer.objects.all()

    for f in fs:
        if f.name in location:
            print("FileServer exists: %s" % f.name)
            return

    # Get models.Location matching location string
    locs = models.Location.objects.all()
    for loc in locs:
        if "Home" in loc.name:
            f = models.FileServer(
                name=location, comments="", filesPrefix=directory, location=loc
            )
            f.save()
            print("Fileserver Added: %s" % location)
            return
    return


if __name__ == "__main__":
    """
    Adds a FileServer object.
    Defaults to the 'Home' location which is created by default elsewhere.
    """
    import sys
    import traceback

    try:
        label = sys.argv[1]
        dir = sys.argv[2]
    except Exception:
        print("ERROR in %s" % sys.argv[0])
        print("Usage: %s <location string> <directory>" % sys.argv[0])
        sys.exit(1)

    try:
        add_location("Home")
    except Exception:
        print("Adding Location Failed")
        print(traceback.format_exc())
        sys.exit(1)

    try:
        add_fileserver(label, dir)
    except Exception:
        print("Adding FileServer Failed")
        print(traceback.format_exc())
        sys.exit(1)
