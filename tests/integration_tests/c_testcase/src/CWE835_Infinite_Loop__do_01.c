/*
 * @description Infinite Loop - do..while()
 * 
 * */

#include "std_testcase.h"

#ifndef OMITBAD

void CWE835_Infinite_Loop__do_01_bad() 
{
    int i = 0;
    
    /* FLAW: Infinite Loop - do..while() with no break point */
    do
    {
        printIntLine(i);
        i = (i + 1) % 256;
    } while(i >= 0);    // SCRUB_IGNORE_WARNING_CODEQL
}

#endif /* OMITBAD */


#ifndef OMITGOOD

static void good1() 
{
    int i = 0;

    do
    {
        /* FIX: Add a break point for the loop if i = 10 */
        if (i == 10) 
        { 
            break; 
        }
        printIntLine(i);
        i = (i + 1) % 256;
    } while (i >= 0);    // lgtm
}

void CWE835_Infinite_Loop__do_01_good() 
{
    good1();
}

#endif /* OMITGOOD */

/* Below is the main(). It is only used when building this testcase on 
 * its own for testing or for building a binary to use in testing binary 
 * analysis tools. It is not used when compiling all the testcases as one 
 * application, which is how source code analysis tools are tested. 
 */

#ifdef INCLUDEMAIN

int main(int argc, char * argv[]) 
{
    /* seed randomness */
    srand( (unsigned)time(NULL) );

#ifndef OMITGOOD
    printLine("Calling good()...");
    CWE835_Infinite_Loop__do_01_good();
    printLine("Finished good()");
#endif /* OMITGOOD */

#ifndef OMITBAD
    printLine("Calling bad()...");
    CWE835_Infinite_Loop__do_01_bad();
    printLine("Finished bad()");
#endif /* OMITBAD */

    return 0;
} 

#endif
