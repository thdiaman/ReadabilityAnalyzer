import io    
import os
import math
import subprocess
from subprocess import PIPE, STDOUT
from javafileanalyzer import extract_method_texts

class ReadabilityAnalyzer(object):
    """
    Class used as a python binding to the RSM readability tool by Scalabrino et al. It contains functions
    for parsing java code and extracting readability metrics from java projects, classes and methods.
    """
    def __init__(self, path_to_Java_exe, path_to_RSM_jar, path_to_RSM_temp_dir):
        """
        Initializes this extractor.
        
        :param path_to_Java_exe: the path to the Java executable.
        :param path_to_RSM_jar: the path to the rsm.jar executable java archive.
        :param path_to_RSM_temp_dir: the path to the RSM temp directory for files.
        """
        self.path_to_Java_exe = path_to_Java_exe
        self.path_to_RSM_jar = os.path.abspath(path_to_RSM_jar)
        self.path_to_RSM_temp_dir = os.path.abspath(path_to_RSM_temp_dir)
        if not os.path.exists(self.path_to_RSM_temp_dir):
            os.makedirs(self.path_to_RSM_temp_dir)

    def run_analysis(self, filepath):
        """
        Runs a readability analysis on a file given as input. This is an internal (private) method
        and should not be used. Use functions analyze_file, analyze_class, analyze_method instead.
        
        :param filepath: the path of the file to be analyzed.
        """
        cmd = [self.path_to_Java_exe, "-cp", self.path_to_RSM_jar, "it.unimol.readability.metric.runnable.ExtractMetrics", filepath]
        proc = subprocess.Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=os.path.dirname(self.path_to_RSM_jar))
        results = {"Scalabrino": {}, "BW": {}, "Posnett": {}} # , "Dorn": {}
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            line = line.strip()

            # Split and handle result
            if ":" in line:
                metric, result = line.split(":")[0], line.split(":")[1]
                try: result = float(result)
                except: result = None

            if line.startswith("New") and not line.startswith("New Text Coherence"): # minor correction to remove not used metric
                # Handle Scalabrino metrics
                metric = metric[4:]
                metric_category = "Scalabrino"
                # Get metric name and metric type
                if metric.endswith("MIN"): metric_name, metric_type = metric[:-4], "minimum"
                elif metric.endswith("MAX"): metric_name, metric_type = metric[:-4], "maximum"
                elif metric.endswith("AVG"): metric_name, metric_type = metric[:-4], "average"
                elif metric.endswith("Standard"): metric_name, metric_type = metric[:-9], "standard"
                elif metric.endswith("Normalized"): metric_name, metric_type = metric[:-11], "normalized"
                else: metric_name, metric_type = metric, None

            elif line.startswith("BW"):
                # Handle BW metrics
                metric = metric[3:]
                metric_category = "BW"
                # Get metric name and metric type
                if metric.startswith("Avg"): metric_name, metric_type = metric[4:], "average"
                elif metric.startswith("Max"): metric_name, metric_type = metric[4:], "maximum"
                if metric_name == "indentation length": metric_name = "indentation" # minor correction to keep the same names for metrics

            elif line.startswith("Posnett"):
                # Handle Posnett metrics
                metric = metric[8:]
                metric_category = "Posnett"
                # Get metric name and metric type
                metric_name, metric_type = metric, None

            # elif line.startswith("Dorn"):
            #     # Handle Dorn metrics
            #     metric = metric[5:]
            #     metric_category = "Dorn"
            #     # Get metric name and metric type
            #     if metric.startswith("Visual X"): metric_name, metric_type = metric[9:], "x"
            #     elif metric.startswith("Visual Y"): metric_name, metric_type = metric[9:], "y"
            #     else: metric_name, metric_type = metric, None

            else:
                continue

            # Create id for metric
            metric_id = "".join(m if m.isalnum() else "_" for m in metric_name.lower())

            if metric_type:
                # Normalize metrics
                metric_id += "_" + metric_type
                metric_name += " " + metric_type[0].upper()
                if len(metric_type) > 1: metric_name += metric_type[1:]
    
                if metric_type and metric_id not in results[metric_category]:
                    results[metric_category][metric_id] = {}

            # Add result to results
            results[metric_category][metric_id] = result

        # Compute also BuseWeimer readability
        cmd = [self.path_to_Java_exe, "-cp", self.path_to_RSM_jar, "raykernel.apps.readability.eval.Main"]
        proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=os.path.dirname(self.path_to_RSM_jar))
        with open(filepath, 'r') as infile:
            filecontents = infile.read()
            methodtexts = ""
            for methodtext in extract_method_texts(filecontents):
                methodtexts += methodtext + "\n###\n"
            
            stdout = proc.communicate(input=str.encode(methodtexts))[0]
            readabilities = []
            for line in stdout.decode().splitlines():
                try:
                    readabilities.append(float(line))
                except:
                    pass
            proc.kill()
        try:
            results["BW"]["readability"] = sum(readabilities) / len(readabilities)
        except:
            results["BW"]["readability"] = None

        # Compute also Scalabrino readability
        cmd = [self.path_to_Java_exe, "-jar", self.path_to_RSM_jar, filepath]
        proc = subprocess.Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=os.path.dirname(self.path_to_RSM_jar))
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            line = line.strip()
            line = line.split("\t")
            if len(line) > 1:
                try:
                    result = float(line[1])
                    results["Scalabrino"]["readability"] = result
                except:
                    results["Scalabrino"]["readability"] = None

        # Compute also Posnett readability
        z = 8.87 - 0.033 * results["Posnett"]["volume"] + 0.4 * results["Posnett"]["lines"] - 1.5 * results["Posnett"]["entropy"]
        results["Posnett"]["readability"] = 1/(1 + math.exp(z))

        return results

    def analyze_file(self, inputfile):
        """
        Runs a readability analysis on a file given as input.
        
        :param inputfile: the path of the file to be analyzed.
        """
        filename = os.path.join(self.path_to_RSM_temp_dir, "temp.java")
        with open(filename, 'w') as outfile:
            with open(inputfile, 'r') as infile:
                inputclass = infile.read()
            outfile.write(inputclass.replace('\t', '    ') + "\n")
        return self.run_analysis(filename)

    def analyze_class(self, inputclass):
        """
        Runs a readability analysis on a class given as input.
        
        :param inputclass: the class to be analyzed as a string.
        """
        filename = os.path.join(self.path_to_RSM_temp_dir, "temp.java")
        with open(filename, 'w') as outfile:
            outfile.write(inputclass.replace('\t', '    ') + "\n")
        return self.run_analysis(filename)

    def analyze_method(self, inpumethod):
        """
        Runs a readability analysis on a method given as input.
        
        :param inputclass: the method to be analyzed as a string.
        """
        filename = os.path.join(self.path_to_RSM_temp_dir, "temp.java")
        with open(filename, 'w') as outfile:
            outfile.write("class MyClass{\n\n")
            outfile.write(inpumethod.replace('\t', '    ') + "\n")
            outfile.write("}\n")
        return self.run_analysis(filename)

    def cleanup(self):
        """
        Removes the temporary file created by this analyzer. Thsi function has to be called,
        otherwise the temporary files remain in the file system.
        """
        filename = os.path.join(self.path_to_RSM_temp_dir, "temp.java")
        try:
            os.remove(filename)
        except OSError:
            pass
