# SAP HANATimer
A scripts that times and records SAP HANA's query times


### DESCRIPTION:  
HANATimer executes continously a query and records the overall times and the server times. This can be useful in scenarios like:  
1. You want to understand if runtime is even over time or if there are certain time frames with significant response time increases.  
2. You want to see if runtimes suffer from specific scenarios, e.g. an increased delta storage or a high resource consumption.  

See also SAP Note SAP Note [2634449](https://launchpad.support.sap.com/#/notes/=2634449).


### DISCLAIMER:
ANY USAGE OF HANATIMER ASSUMES THAT YOU HAVE UNDERSTOOD AND AGREED THAT:  
1. HANATimer is NOT SAP official software, so normal SAP support of HANATimer cannot be assumed  
2. HANATimer is open source
3. HANATimer is provided "as is"  
4. HANATimer is to be used on "your own risk"  
5. HANATimer is a one-man's hobby (developed, maintained and supported only during non-working hours)
6. All HANATimer documentations have to be read and understood before any usage:  
* SAP Note [2634449](https://launchpad.support.sap.com/#/notes/=2634449)
* The .pdf file hanatimer.pdf
* All output from executing    `python hanatimer.py --help`
