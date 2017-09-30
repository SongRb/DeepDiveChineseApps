# DeepDive Spouse Example with Chinese Support
## Introduction
This app aims to take the official DeepDive tutorial [Extracting mentions of spouses from the news](http://deepdive.stanford.edu/example-spouse) and change input into 100 Chinese news articles.  
## Prerequisite
DeepDive 0.8.0  
Postgresql 9.6  
Elasticsearch 5.5.0  
## Chinese NIP Configuration
Please run `echo "postgresql://$USER@$HOSTNAME:5432/deepdive_spouse_$USER" >db.url`
first.  
Then, download `stanford-srparser-2014-10-23-models.jar` and `stanford-chinese-corenlp-2016-01-19-models.jar` from stanford NLP website and put them under `udf/bazzar/parser/lib/`.  
Under `udf/bazzar/parser/`, please run `sbt/sbt stage` to rebuild the project. To test out, you can run `./run.sh -p 8080`, and POST anything to port 8080 to see the result.
You can use a tool with GUI like http-tool in Mozilla Firefox.  

## Run the Project
This project tries to use original project configuration as much as possible. But some changes in project command are necessary:  
The project compilation command  

    deepdive compile  

are only required to executed at startup.
In Section 1.1, to load raw input data:
Change

    deepdive do articles  

into  

    deepdive create table articles
    deepdive load articles input/news-100.tsv.bz2
    
In Section 2.1, we replace people name list from DBpedia to manual label from 100 new articles.
So no SQL queries are need, you can run  

    deepdive create table spouses_dbpedia
    deepdive load spouses_dbpedia input/spouse_dbpedia.csv.bz2
    
and continue with next query:  

    deepdive query '| 20 ?- spouses_dbpedia(name1, name2).'
    
## Issue
### Java Memory Error
If you encountered `java.lang.OutOfMemoryError` or similar error in NLP processing, 
please view `/udf/bazaar/parser/run.sh` and change `3g` in `export JAVA_OPTS="-Xmx3g -Dfile.encoding=UTF-8"`
into a lower number.
### Command Re-execution
If you want to execute a command twice due to previous abortion or modification, 
sometimes the data are not updated completely even with `deepdive redo`.  
To resolve that issue, you can keep track of `run/<run_date>/<run_time>/plan.sh`
and check whether done time of some command is not changed. 
If so, you may have to run that command with `deepdive redo` or `deepdive do` 
even they are not included in tutorial.  
When I want to execute `deepdive do has_spouse` again 
due to changes in `udf/supervise_spouse.py`, nothing happened. 
But run `deepdive do spouse_label__0` can refresh the project status.  
### User-defined Function Debugging
Because of DeepDive's own rules, user-defined function under `udf/`
will take one row from database as input and return several rows
which will be passed to other function immediately. 
If you want to view debug information, do not use `print` or `stdout`, 
use `logging` module instead.

## Reference
1.[DeepDive Documentation](http://deepdive.stanford.edu/#documentation)  
2.[qiangsiwei/DeepDive_Chinese](https://github.com/qiangsiwei/DeepDive_Chinese)  





   








