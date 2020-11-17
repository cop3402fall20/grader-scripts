# grader-scripts


## Usage

Run the following command: `python3 testSimplec.py path/to/your/repo path/to/the/tests keepBinaries compileAndCheckRetValue`

Example: `python3 testSimplec.py /vagrant/simplec-compiler-josh /vagrant/tests-cases-public/proj1 true true` 

Set the second to last arg to true if you are using precompiled binaries from ealier projects
Set the last arg to false for projects 1-2 and true for 3-4. It will compile your assembly output with gcc, run the binary, and check for the return value


Sample output:

```
# building your simplec compiler
Build succeeded
Testing example.simplec: Failure. See example.simplec.diff for diff and example.simplec.out for output.
Testing functioncall1.simplec: Success!
Testing simple.simplec: Success!
Testing ifelse.simplec: Success!
Testing if.simplec: Success!
Testing assign.simplec: Success!
Testing quicksort.simplec: Failure. See quicksort.simplec.diff for diff and quicksort.simplec.out for output.
Testing binary_ops.simplec: Success!
Testing call.simplec: Success!
Testing math1.simplec: Success!
Testing read.simplec: Failure. See read.simplec.diff for diff and read.simplec.out for output.
Testing digitcount.simplec: Success!
Testing battleship.simplec: Failure. See battleship.simplec.diff for diff and battleship.simplec.out for output.
Testing negation.simplec: Success!
Testing badtype.simplec: Success!
Testing sudoku.simplec: Failure. See sudoku.simplec.diff for diff and sudoku.simplec.out for output.
11 / 16 test casing passing. 
```