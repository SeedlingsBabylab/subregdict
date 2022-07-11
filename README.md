> :warning: I (Zhenya) made a few updates in July, 11. Check it they are still necessary. See the commit message for more information.

# subregdict

This script ranks hour long subregions in cha files based on the maximum ctc/cvc average values from lena5min files.

It will generate a csv with a list of the top ranked regions, their onsets/offsets, and their corresponding timestamps in
the associated cha file. There is also an included script which will call subrdict.py as a batch process over an entire directory.

## usage:

> :warning: **Runs in Python 2!!!**

##### subrdict.py
```
$: python subrdict.py [lena.cha_file] [lena5min.csv] [silences.txt]
```

##### batch_subrdict.py

```
$: python batch_subrdict.py [dir]
```
