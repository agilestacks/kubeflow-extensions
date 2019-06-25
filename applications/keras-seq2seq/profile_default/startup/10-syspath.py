import sys, glob
for p in glob.iglob('components/*/src', recursive=True):
    sys.path.insert(0, p)
