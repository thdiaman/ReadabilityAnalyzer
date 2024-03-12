# ReadabilityAnalyzer
ReadabilityAnalyzer is a python wrapper of the readability tool by Scalabrino et al. (relevant paper available [here](https://doi.org/10.1002/smr.1958)), which also incorporates the models of Buse & Weimer (relevant paper available [here](https://doi.org/10.1109/TSE.2009.70)) and Posnett (relevant paper available [here](https://doi.org/10.1145/1985441.1985454)). Original tool by Scalabrino et al. can be found in [this link](https://dibt.unimol.it/report/readability/).

## Prerequisites
The python library requirements include standard python libraries as well as the javalang python library. This may be installed using the command `pip install javalang==0.13.0`

The library requires Java to be installed to the system (tested with Java 11). Also, the rsm.jar and readability.classifier files of the readability tool of Scalabrino et al. (avalable in [this page](https://dibt.unimol.it/report/readability/)) must be added in a folder of the system (in the default properties file it is assumed that they are present in the folder tools of the project).

The code can be used as a library in Python. To run it, one must first correctly assign the properties in file properties.py. These include the following:
- path to the Java executable of the installed JRE/JDK (java.exe)
- path to the RSM.jar file of the readability tool
- path to a directory where temporary files are created.

## Usage
The library can be imported into python source code simply by adding the readabilityanalyzer.py and javafileanalyzer.py files in the same directory as the project, importing and initializing the ReadabilityAnalyzer class. After that, one can call one of the following methods:
- `analyze_method`: analyzes a Java method
- `analyze_class`: analyzes a Java class
- `analyze_file`: analyzes a Java file

In all three cases, a temporary file is created in the temporary directory give in the properties file. The file is overriden in every execution. To remove the file, one can call the `cleanup` function of the ReadabilityAnalyzer class.

The output is in json format, where the first level includes the model (Scalabrino, BW, Posnett) and the second level includes the metric itself. For each model, one can also see the readability value (as metric readability).

A full example of running a readability analysis in a method, a class, and a file is provided in file readabilityanalyzer_test.py
